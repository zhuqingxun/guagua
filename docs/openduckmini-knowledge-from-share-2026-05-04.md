# OpenDuckMini 知识沉淀（来源：claude.ai 分享对话 2026-05-03 ~ 05-04）

> 来源 URL：https://claude.ai/share/cd37998c-8480-4122-bf94-772044fdc347
> 提取日期：2026-05-05
> 对话规模：23 轮（user + assistant 各 23 条），原文约 12.9 万字符
> 提取方式：通过 Chrome MCP 在已登录的 claude.ai 页面用 console.log 分块读取（WebFetch 被 403 拒绝）
>
> 本文目的：把整段对话沉淀为面向 guagua 项目的技术知识库，不做新决策，只保留事实与已经达成的工程理解。后续 PRD / plan / 选型如果引用任何一段，请优先回到此文档查证。

---

## 0. 关键人物与立场

- **用户身份**：嵌入式通信设备 R&D 老兵，已搭好科学上网，关注 NeuroMemory / 本地化 AI / 古琴-人文气质这条主线，对"会改 RL 训练 = 你拥有这个机器人"有共鸣。
- **关心的对象**：apirrone (Pollen Robotics) 的 `Open_Duck_Mini` 项目，以及国内"爱折腾（佛山市爱折腾信息技术有限公司，AIZHETENG / ncnynl.com）"做的本土化套件。
- **对话基调**：用户连续 23 轮追问从硬件到模型到分层架构到情绪到 ONNX 再到爱折腾的"调重心"话术，整段对话本质是一个**为购买 + 二次开发 OpenDuckMini 做的尽调**，与 guagua 项目的 M0-M1 阶段（应用层定位、上游引入策略、是否买现成套件）高度相关。

---

## 1. OpenDuckMini 原版硬件架构（apirrone 的 v2）

### 1.1 BOM 三件套

| 部件 | 规格 / 型号 | 在系统里的角色 |
|------|-------------|----------------|
| **主控** | Raspberry Pi Zero 2W | 1GHz 四核 Cortex-A53，512MB RAM，65×30mm；BCM2710A1；Wi-Fi 2.4GHz + BT 4.2；功耗 1-2W；只跑 ONNX 推理，不训练 |
| **关节** | Feetech ST3215（STS3215）× 14 | TTL 半双工串行总线（菊花链，多 ID 共一根线）；可读位置/速度/负载/电压/温度/电流；扭矩 19~30kg·cm；金属齿轮；价格约 14 EUR/个，是开源人形里 Dynamixel 的廉价替代 |
| **IMU** | Bosch BNO055 | 3 轴 acc + 3 轴 gyro + 3 轴 mag = 9 轴；内置 ARM Cortex-M0 协处理器做传感器融合；I²C 接口 |

**还有一颗常被忽略的硬件**：USB-TTL 舵机控制板。Pi 不能直接驱动 ST3215 总线，必须有这块板做电平转换 + 总线供电管理。Pi 的唯一一个 USB-OTG 已被它占用。

**两颗 SG90**（爱折腾说"2 个辅助舵机"，原版也有）：

- 用途：驱动**头顶左右两根天线（antenna / ear）**——迪士尼 BDX 原版的标志性表情元素。
- 为什么不用 ST3215：成本低（¥5-8 vs ¥80-100）、重量轻（9g vs 60g，不增加头部惯量影响平衡）、不需力反馈。
- 通讯通道：和 ST3215 总线**完全分开**，走 PWM（典型方案是 Pi 的 I²C → PCA9685 → SG90，BNO055 已占 I²C 但 PCA9685 是不同地址，可共线）。
- 在 RL 中的角色：**完全不在 RL 输出里**，是开环纯表达性自由度。源码注释 `"remove neck head and antennas"` 就是奖励函数计算时把这些表达性关节排除掉。

### 1.2 控制循环（50Hz 闭环）

```
每个控制周期 (~20ms):
  1. 读 BNO055     → gyro(3), accel(3)
  2. 读 ST3215 总线 → 10 腿关节 qpos, qvel
  3. 读脚底接触开关 → contacts(2)
  4. 推进相位计数器 → imitation_phase(2)
  5. 取手柄        → command(7)
  6. 拼 77 维 obs，送入 ONNX MLP
  7. 输出 10 维 action ∈ [-1,1]
  8. motor_targets = default + action × 0.25，做速度限幅
  9. 头部 4 关节直接用 command[3:7]（开环）
  10. 14 个目标位置一次性写到舵机总线
  11. 滚动更新 last_action / last_last_action / last_last_last_action
```

### 1.3 设计取舍（"够用就好"哲学）

| 维度 | 该项目选择 | 高端方案 | 取舍逻辑 |
|------|------------|----------|----------|
| 主控 | Pi Zero 2W (~$15) | Jetson Orin NX | 不跑视觉/VLA，只跑小策略 |
| 关节 | Feetech ST3215 (~€14/个) | Dynamixel XM430 | 反馈带宽差一截，价格 1/5 |
| 姿态 | BNO055 内置融合 | 自写 EKF + 高精度 IMU | 牺牲精度换开发简单 |

> 这套架构成立的前提是**RL 策略在仿真里学出对硬件不完美的鲁棒性（domain randomization）**，否则换成传统 MPC 这套硬件根本压不住——这就是为什么这个项目和 RL 强绑定。

---

## 2. RL 策略：77 → 10 的 MLP

### 2.1 网络结构（Actor-only 推理网络）

- 类型：普通 MLP，纯前馈、无循环、无视觉
- 结构：`Linear → Swish` × 隐层（默认 `[256, 256]`） → `Linear` 输出 `act_size*2 维（loc + log_std）` → 取前一半 `loc → tanh → action ∈ [-1, 1]`
- 部署时：Critic、log_std、observation normalization 的 mean/std 都已经折叠进 ONNX，Pi 上只跑一次前向。
- 参数量：估算 ~88,330，文件 300-500KB。
- 来源：`apirrone/Open_Duck_Playground` 主分支 + `Open_Duck_Mini_Runtime` v2 分支，配套权重文件 `BEST_WALK_ONNX_2.onnx`。

### 2.2 Action（输出，10 维）

**关键反直觉点**：14 个 ST3215，但 RL 只输出腿部 10 维。

| 索引 | 关节 |
|------|------|
| 0–4 | 左腿：hip_yaw, hip_roll, hip_pitch, knee, ankle |
| 5–9 | 右腿：hip_yaw, hip_roll, hip_pitch, knee, ankle |

剩下的 4 个头部关节（neck_pitch, head_pitch, head_yaw, head_roll）**不由策略输出**，由用户从手柄/程序通过 command 直接给定目标角。这是设计选择：头部表达性是开环、人为控制；腿部走路才需要 RL 闭环。

**输出语义**：

```python
motor_targets = default_actuator + action * action_scale     # action_scale = 0.25
# 然后用 max_motor_velocity = 5.24 rad/s 做速度限幅
```

也就是说网络输出是**相对默认姿态的偏移系数**，不是力矩、不是速度——是位置控制 + PD 由舵机内部完成的范式（对廉价舵机最友好）。

### 2.3 Observation（输入，77 维）

| 段 | 维度 | 含义 | 数据来源 |
|---|---|---|---|
| `gyro` | 3 | 躯干角速度（IMU 本体系） | BNO055 |
| `accelerometer` | 3 | 躯干线加速度（含重力 + ax+1.3 偏置补偿） | BNO055 |
| `command` | **7** | 用户指令（实际是 7 维，不是 joystick.py 注释的 3） | 手柄 / 脚本 |
| `joint_angles - default` | 10 | 10 个腿关节当前角度相对默认姿态偏差 | ST3215 总线 |
| `joint_vel * dof_vel_scale` | 10 | 10 个腿关节角速度（缩放后） | ST3215 总线 |
| `last_action` | 10 | 上一步策略输出 | 内部缓存 |
| `last_last_action` | 10 | 上上步 | 内部缓存 |
| `last_last_last_action` | 10 | 再上一步 | 内部缓存 |
| `motor_targets` | 10 | 当前下发给舵机的目标位置 | 内部缓存 |
| `contacts` | 2 | 左右脚是否触地 | 脚底微动开关 |
| `imitation_phase` | 2 | `[sin(φ), cos(φ)]` 步态相位 | 内部相位计数器 |

**合计：3+3+7+10+10+10+10+10+10+2+2 = 77**

> 注：joystick.py 注释里 command 标 `# 3` 是历史遗留没改。看 mujoco_infer.py 部署侧拼的就是 7 维，所以部署期 obs 维度是 77。

### 2.4 Command 7 维详细

```
command[0] = lin_vel_x        前进速度命令, m/s, 范围 ±0.15
command[1] = lin_vel_y        横移速度命令, m/s, 范围 ±0.20
command[2] = ang_vel_yaw      转向角速度, rad/s, 范围 ±1.0
command[3] = neck_pitch       颈俯仰目标角
command[4] = head_pitch       头俯仰目标角
command[5] = head_yaw         头偏航目标角
command[6] = head_roll        头滚转目标角
```

**这 7 个数字就是整个系统的"语义接口"**——后续讨论 System 2 / 云端 / MCP / 情绪表达，几乎都围绕"谁来填这 7 个数"展开。

### 2.5 imitation_phase（项目精髓）

迪士尼 BDX 论文用了 imitation reward：训练时给一个参考运动轨迹（由 `Open_Duck_reference_motion_generator` 生成的多项式步态），奖励策略去模仿。`imitation_phase = [sin(2π·φ), cos(2π·φ)]` 把循环相位编码成 2 维连续值，告诉策略"现在该处于步态周期的哪个位置"。手柄按 LB（冲刺）就是把 `phase_frequency_factor` 调大，φ 推进得更快。

### 2.6 三段历史动作的设计（关键 sim2real 技巧）

obs 里塞了 `last/last_last/last_last_last_action`（共 30 维），没有用关节速度历史也没用 IMU 历史。目的：

1. **让策略隐式感知舵机延迟和动力学**——廉价 ST3215 的实际响应和指令之间有 latency，网络可以从"我前几步给了什么、现在状态如何"反推舵机真实行为。
2. **给无状态 MLP 提供时间上下文**（代替 LSTM）。

仓库 sim2real.md 明说："用便宜的、难建模、力又不强的舵机让 sim2real 变得困难"——把动作历史塞进 obs 是廉价但有效的补偿。

### 2.7 Asymmetric Actor-Critic

训练时 Critic 用的是 `privileged_state`（在 actor obs 基础上加了真实 linvel、root height、actuator force、feet velocity、足空中时间、完整参考运动等共特权信息），**Actor 只用 77 维，部署只用 Actor**。这就是为什么板上无须知道躯干线速度——它是 partially observed 学出来的。

> 这是一个对比标杆：Berkeley Humanoid / Booster T1 等方案常见"用学习到的状态估计器估 base linvel 喂给 actor"，但 Open Duck Mini 的 Actor 直接放弃 linvel，靠 IMU + 关节 + 历史 + phase 的组合"硬估"——为了在 Pi Zero 2W 上把推理压到极简。

---

## 3. System 1 / System 2 分层架构

整段对话最重要的一根主线。

### 3.1 为什么端到端 VLA 直接换掉 MLP 行不通

三个原因：

1. **频率根本接不上**：Open Duck Mini MLP 在 Pi Zero 2W 上跑 50Hz（20ms 一帧）。VLA 是另一个数量级——π0（30 亿参数）在 AGX Thor 上 46ms 即 22Hz；Orin NX 16GB（100 TOPS Ampere）跑 π0 比 Thor 慢 2-3 倍，实际 8-10Hz。8-10Hz 对双足腿部控制是致命的，一个步态周期（~0.5s）只剩 4-5 帧，没法做扰动恢复。LiteVLA-Edge 在 AGX Orin（60W）上 150.5ms 即 6.6Hz。
2. **数据根本拿不到**：VLA 需要（图像，语言，动作）三元组的大规模演示数据。OpenVLA 用了 970K 条机器人轨迹，π0 用了多个机器人本体的几千小时遥操作。Open Duck Mini 的本体和主流 humanoid 完全不同，跨本体迁移效果存疑。
3. **双足平衡的物理约束 VLA 不擅长**：腿足平衡需要高频率（≥50Hz）、低延迟低抖动（jitter < 1ms）、动作连续性（避免 chunk 切换的 jerk）。VLA 擅长语义和长时序规划，不擅长毫秒级反馈控制。

**业界已经收敛**：Gemini Robotics、GR00T、NaVILA、WholeBodyVLA 全部走分层 VLA：慢 System 2 给抽象指令，快 System 1 做关节控制。NaVILA 让 VLA 输出"前进 75cm"这样的语言形式中层动作，由 RL 策略执行。

### 3.2 正确的双系统架构

```
┌─────────────────────────────────────────────────────────┐
│  System 2 (慢, 5-10Hz):     VLA / VLM                   │
│  输入:  RGB 摄像头 + 麦克风/文本指令 + 任务上下文       │
│  输出:  中层指令(三选一)                                │
│         a) 速度命令: [vx, vy, ωz, head_pose]            │
│         b) 离散技能 token: {walk, turn_left, look_at,…} │
│         c) latent embedding(向 System 1 传 hidden state)│
│  位置:  Jetson Orin NX / Mac Studio / 云端              │
└─────────────────────────────────────────────────────────┘
                         ↓ 中层指令
┌─────────────────────────────────────────────────────────┐
│  System 1 (快, 50Hz):       现有的 77→10 MLP (升级版)   │
│  输入:  IMU + 关节状态 + 接触 + 历史动作 + 中层指令     │
│  输出:  10 维腿部 action delta(完全沿用)                │
│  位置:  Pi Zero 2W                                      │
└─────────────────────────────────────────────────────────┘
```

**关键洞察**：现有 77→10 MLP **一行不用改**就已经是 System 1。它的 obs 里那个 7 维 command 就是 System 2 的输出接口——把 NaVILA 的"前进 75cm"语义压成连续向量即可。

### 3.3 obs/action 扩展三档（按改动从轻到重）

| 梯度 | obs | action | 训练需求 |
|------|-----|--------|---------|
| **A. 最小改动** | 不动（77 维） | 不动（10 维） | 不动 |
| **B. 共享中间表示** | 77 + K 维 task embedding | 不变 | 冻结底层，训接口层 + LoRA 微调 VLM |
| **C. 重新设计** | + RGB token (256) + 语言 token | 10 → ~30+（手臂 6-7 自由度 × 2 + 夹爪） | 网络 MLP → transformer + diffusion/flow，需 大量数据 |

**只有梯度 C 需要换机器人**（OpenDuckMini 没有手臂、夹爪、摄像头、麦克风原生集成）。

### 3.4 算力位置 ≠ 安装位置（用户的关键顿悟）

用户在第 25 轮抓到的核心：

> "system2 我其实不需要跟鸭子的本体结合在一起，比如说未来我买了一个 Mac Studio 也可以作为 System 2"

✅ 完全正确。System 2 ↔ System 1 的接口（7 维 command）是物理位置无关的。可以从：

- 手柄发出（原版）
- 同一块板的另一个进程
- 同一房间的另一台机器（Wi-Fi/有线）
- 千里之外的服务器（云端）

对 Pi Zero 2W 上的 RL 策略，这些情况它根本分不出来——只知道"command 寄存器里又来 7 个新数字了"。

### 3.5 四种 System 2 部署对比

| 方案 | 算力位置 | 延迟 | 隐私 | 离线 | 一次性成本 | 持续成本 | 适合 |
|------|----------|------|------|------|------------|----------|------|
| 云端 API | 阿里云/讯飞云 | 1-3s | ❌ 上传 | ❌ | 0 | API 费 | 起步、玩玩 |
| Mac Studio 本地 | 桌面工作站 | 0.3-1s | ✅ 本地 | ✅ | 25-50K | ~80W 电费 | 长期开发研究 |
| Jetson Orin NX 桌面 | 边缘小盒子 | 0.5-1.5s | ✅ | ✅ | 6K | ~25W 电费 | 嵌入式风格 |
| Jetson 装鸭子背上 | 机器人本体 | 0.3-1s | ✅ | ✅ 完全独立 | 6K + 电池升级 | - | 真正需要"机器人独立行动"时 |

**对 guagua 项目的隐含建议**（用户接受的演进路线）：

1. **阶段 1**（0 元）：MateBook Pro + 阿里云百炼 Qwen-VL 验证整端到端流程
2. **阶段 2**（~5K）：Mac Mini M4 16GB 当家庭 24h 大脑 + NeuroMemory 常驻服务器
3. **阶段 3**：只在"机器人要离开 Wi-Fi"或"VLA 高频闭环训练"时才把算力装到鸭子身上

### 3.6 Orin NX 性能边界（重要参数对照）

| 平台 | 内存 | 算力 | 跑得动什么 |
|------|------|------|-----------|
| Pi Zero 2W | 512MB | 几 GFLOPS | 当前 77→10 MLP @ 50Hz |
| Orin NX 8GB | 8GB | 70 TOPS | 现有 MLP + 小 VLM (<3B, 5-10Hz) 异步 |
| Orin NX 16GB | 16GB | 100 TOPS（Super Mode 157）| 现有 MLP + 中型 VLA (SmolVLA/Qwen2-VL-2B, 8-12Hz) |
| AGX Orin 64GB | 64GB | 275 TOPS | π0 / GR00T N1 量化版, 15-20Hz |
| AGX Thor | 128GB | 2070 TFLOPS FP4 | π0 全精度 22Hz、GR00T N1 流畅 |

GR00T N1 官方明确说推理需要 16GB+ VRAM，不列 Orin NX——是真跑不动。

**Orin NX 物理形态**：69.6×45 mm SoM（不是开发板，需载板），8 核 Arm Cortex-A78AE + 1024 CUDA + 32 Tensor (Ampere)，128-bit LPDDR5 102 GB/s，10-25W 可配置（Super Mode 40W），价格模块本身 $599（1000+），零售套件 800-1200 美元。

### 3.7 加东西会改变物理参数吗（randomize.py 已为你买保险）

`randomize.py` 在每个 episode 都做：

- **躯干质心扰动 ±5cm**（`body_ipos.at[TORSO_BODY_ID]`）
- **所有连杆质量 0.9~1.1 倍**（±10%）
- **躯干额外加重 ±100g**
- **关节摩擦、转子惯量(armature)、KP 增益 ±10%**

**判据**（三条经验法则）：

| 改动 | 在训练分布里吗？ | 需要重训吗？ |
|------|------------------|-------------|
| MAX98357 + 喇叭(~30g) 装躯干内 | ✅ < ±100g | 不需要 |
| Camera Module 3 (~5g) 装头部 | ✅ | 不需要 |
| 一根额外连接线 (~20g) | ✅ | 不需要 |
| **Orin NX 套装 (~300g) 装躯干** | ❌ 超 ±100g | 大概率需要 fine-tune |
| **Orin NX 装头顶** | ❌ 质心偏 > 5cm | 必须重训 |
| 加机械臂（改 URDF）| ❌ | 必须重训 + 改 XML |

**最聪明的设计是让 Orin NX 不在鸭子身上**——通过 Wi-Fi 异地协作，鸭子本体重量不变，完全不需要重训。这是 NaVILA、Gemini Robotics 这类工作的常见做法。

---

## 4. 部署 vs 训练：用现成 ONNX 够不够

### 4.1 不需要做的事（开源已替你做完）

- ❌ 不需要训练 RL 策略——`BEST_WALK_ONNX_2.onnx` 直接用
- ❌ 不需要跑 MuJoCo 仿真（仿真是训练时用的）
- ❌ 不需要设计奖励函数 / imitation reference motion 生成
- ❌ 不需要懂 PPO/RL 算法（部署时 RL 是黑盒）

### 4.2 必须做的事（5 件，不可跳）

1. **机械装配和零位校准**（★★★，最关键）：14 个舵机软件零位（180°）必须和机械零位对齐，否则 obs 里 `joint_angles - default` 全错。
2. **IMU 标定**（★★★）：每次上电后跑 `calibrate_imu.py`，把鸭子沿三个轴各种姿态旋转直到 `[3,3,3,3]`。**BNO055 的标定不会持久化**，每次冷启动都要重做（除非写代码存 EEPROM）。
3. **舵机参数烧录**（★★）：ID（1-14）、运行模式（位置控制）、角度限制、PID 增益、波特率（通常 1Mbps）。
4. **安装 runtime 软件栈**（★★）：Pi OS 64-bit（必须 64 位，ONNX runtime aarch64 需要）+ onnxruntime + rustypot + bno055 + `Open_Duck_Mini_Runtime` 仓库。在大陆下 onnxruntime ARM wheel 可能要折腾代理。
5. **控制设备连接**（★）：Xbox 蓝牙手柄配对，或写最简命令脚本。

### 4.3 强烈建议（不做也能跑）

- **A. 仿真预演**（30 分钟）：跑一遍 `mujoco_infer.py` 验证 ONNX 是好的、看参考行为
- **B. 安全绳/支架**：第一次走路必备，ST3215 摔狠了齿轮会打滑或滑丝
- **C. 控制频率核对**：`time.perf_counter()` 测循环周期，稳定在 20ms ± 1ms

### 4.4 时间预估（用户工程背景下）

| 阶段 | 时间 |
|------|------|
| 3D 打印所有件 | 8-15 小时 |
| 机械装配（含舵机调零位）| 4-8 小时 |
| 舵机 ID 烧录 + 参数配置 | 1-2 小时 |
| Pi Zero 2W 系统装 + runtime 部署 | 2-3 小时 |
| IMU 标定 + 软件联调 | 1-2 小时 |
| 第一次站立/走路调试 | 2-4 小时 |
| **合计** | **约 20-30 小时** |

预留 50% 缓冲。

### 4.5 自己改硬件后的训练流程（8 步）

1. 建新物理模型（CAD → URDF → MJCF）
2. 核对 obs/action 维度
3. 调整 randomize.py
4. 决定 fine-tune 还是从零（**注意：BEST_WALK_ONNX_2.onnx 是导出后产物，不能 resume；需要原始 brax checkpoint，找作者要**）
5. 跑训练 + 监控曲线（episode/sum_reward 应缓慢上升；30M steps 后还平就 debug）
6. 仿真验证
7. 导出 ONNX
8. 真机调试（2-5 轮迭代是常态）

### 4.6 RL 训练硬件门槛

| 改动规模 | 推荐硬件 | 时间 |
|---------|----------|------|
| 微调 | RTX 3060 12GB / Colab T4 | 1-3 小时 |
| 中等改动 | RTX 4080 / 4090 | 2-6 小时 |
| 大改 | RTX 4090 / A100 云租 | 6-24 小时 |
| 实验阶段反复试 | AutoDL / RunPod 4090 按时租 | 1-3 元/小时 |

参考时间（2026 年实测）：A100 上四足训练 6 分钟；类人完整 200M steps 在 RTX 4090 上 56 分钟。**RL 训练在 2026 年不是几年前那种"集群跑几天"了。**

---

## 5. ONNX 文件格式

### 5.1 一句话定义

ONNX (Open Neural Network Exchange) = 神经网络模型的通用文件格式，任何框架训练的模型都可以导出，任何运行时都可以加载。类比 PDF 之于文档、MP3 之于音频。

### 5.2 文件内容三部分

1. **计算图**：算子节点 + 连接关系（MatMul、Add、Swish、Tanh 等）
2. **权重数据**：99% 文件大小，二进制 blob
3. **元数据**：输入输出形状、数据类型、版本号

### 5.3 在本项目中

- 训练：JAX / Brax 在 GPU
- 部署：onnxruntime 在 Pi 的 ARM CPU
- 中间靠 ONNX 文件接力。Pi 上从来没装过 JAX——装不下，只装 50MB 的 onnxruntime。

### 5.4 推理引擎可选（同一份 ONNX 跨平台）

| 引擎 | 适合 |
|------|------|
| onnxruntime | 跨平台通用（鸭子用这个）|
| TensorRT | NVIDIA GPU 极致性能 |
| CoreML | Apple 设备（可从 ONNX 转）|
| OpenVINO | Intel 优化 |
| NCNN | 腾讯出，Android/iOS 移动端 |
| MNN | 阿里出，移动端 |

### 5.5 四个常见坑

1. **opset 版本不兼容**：导出 opset 17，运行时只支持 opset 13 → `No schema registered for 'XXX'`
2. **动态形状支持差**：嵌入式推理引擎对 dynamic shape 支持差（鸭子 obs 形状 [1, 77] 永远不变，无此问题）
3. **训练框架的算子不在 ONNX 标准里**：如 `nn.LSTM`、自定义 CUDA kernel
4. **Brax/Flax/JAX → ONNX 生态不成熟**：`Open_Duck_Playground/playground/common/export_onnx.py` 是作者手写的导出代码，不是标准工具——你以后改完模型重新导出可能会发现导出代码本身要改

### 5.6 几个澄清

| 误解 | 事实 |
|------|------|
| "ONNX 是个推理引擎" | ❌ 它是文件格式，onnxruntime 才是引擎 |
| "ONNX 模型自动比原模型快" | ❌ 速度看运行时 |
| "ONNX 可以反向训练" | ❌ 主要为推理设计 |
| "ONNX 是某家公司产品" | 一半：Linux Foundation 旗下开放标准 |
| "导出 ONNX 会丢失精度" | 通常不会（FP32 → FP32 一致），除非主动量化 |
| "ONNX 模型可以加密保护" | 弱保护——文件结构公开，权重直接可读 |

---

## 6. 爱折腾（AIZHETENG）的本土化套件分析

### 6.1 公司背景

- 全名：佛山市爱折腾信息技术有限公司
- 成立：2016
- 网站：ncnynl.com
- 主营：长期做 ROS 教育套件（TurtleBot 风格科教机器人），OpenDuckMini 是产品线新成员
- 核心强项：ROS 培训 + 一对一技术支持服务

### 6.2 真实的"增量"——产品化工程，不是技术创新

**❌ 没新增硬件类别**——所有部件类型都在原版规划里。

**✅ 实际工作**：

1. 硬件选型和适配（国内供应链等价物，喇叭换"锅底喇叭"等）
2. 中文文档体系（15+ 篇教程从开箱到训练）
3. 套件化（打包邮寄，省 30+ 零件采购）
4. 实装"待完善"功能（原版 `expression_features` 全 false，实装眼睛 LED、扬声器、摄像头）
5. 集成 py-xiaozhi + MCP 语音方案

### 6.3 哪些是原版本来就有的（被爱折腾文档"增加"二字误导）

| 部件 | 爱折腾文档说"增加" | 真相 |
|------|--------------------|------|
| BNO055 | "增加了 BNO055 陀螺仪" | ❌ **原版核心硬件**——RL 策略 obs 第一项就是 gyro/accel，`Open_Duck_Mini_Runtime/setup.cfg` 写死 `adafruit-circuitpython-bno055==5.4.13` |
| 摄像头 | "增加树莓派摄像头" | ⚠️ 原版预留 + 爱折腾实装（v2 设计有 `camera: false` 占位符 + 头部 STL 件开孔）|
| 音频系统 | "增加音频系统" | ⚠️ 原版预留 README 提到 MAX98357 接线 + 爱折腾实装 |
| 天线 SG90 | - | ✅ 原版有 `antenna.part`、`left/right_antenna_holder.part` |

**判断"原版还是商家加"的三条线索**：

1. 看 RL obs 维度（出现在 obs 里 → 原版必备）
2. 看作者 GitHub 的 `setup.cfg` / `requirements.txt`（写明的库 → 原版）
3. 看配置文件占位符（`expression_features` 那种 true/false 开关 → 原版预留接口）

### 6.4 "陀螺仪实现姿态平衡"是话术

**精确版本**：

- BNO055 是**观测器**，不是**控制器**
- 真正"实现平衡"的是 RL 策略——88,330 参数 MLP 在仿真里学出的隐式平衡能力
- **没有跑任何传统控制算法**（无 PID、无 LQR、无 MPC、甚至没用 BNO055 自己的姿态融合输出）
- 实际只用了原始 `gyro + accel` 6 维（不用融合后的 roll/pitch/yaw），原因：① RL 想自己学融合；② 原始数据延迟更小；③ sim2real 一致性（仿真里没有"融合后姿态"概念）
- BNO055 的 ARM-M0 协处理器只在**标定阶段**有用（`calibrate_imu.py` 等 `[3,3,3,3]` 那个流程）

### 6.5 爱折腾"调重心"是关节零位偏移校准（joint_offsets）

**卖家原话**："主要就是把重心调好。每台机器都有差异。"

**真相**：

- ✅ 这件事真实存在，确实每台都要调
- ❌ 但不是真在调"物理重心"——物理重心由质量分布决定，装好就固定
- ✅ 调好后用同一个原版 ONNX，**完全不用重训**

**实际操作的是 `duck_config.json` 里的 14 个 `joints_offsets` 数字**：

```json
"joints_offsets": {
    "left_hip_yaw": 0.0,
    "left_hip_roll": 0.0,
    "left_hip_pitch": 0.0,
    "left_knee": 0.0,
    "left_ankle": 0.0,
    "neck_pitch": 0.0,
    "head_pitch": 0.0,
    "head_yaw": 0.0,
    "head_roll": 0.00,
    "right_hip_yaw": 0.0,
    "right_hip_roll": 0.0,
    "right_hip_pitch": 0.0,
    "right_knee": 0.0,
    "right_ankle": 0.0
}
```

**为什么必须每台调**：

1. 3D 打印件公差 ±0.2-0.5mm
2. ST3215 出厂齿轮初始角度 ±2-5°
3. 装配公差 ±2-3°/次
4. 舵机磁编码器零点漂移 ±1-2°
5. 14 个关节误差累积 → 整体姿态可能偏 5-10°

**校准原理**：

```python
def read_joint_angles():
    raw_angles = read_from_servos()
    calibrated_angles = raw_angles - joint_offsets  # 减偏移
    return calibrated_angles

def write_motor_targets(targets):
    actual_commands = targets + joint_offsets       # 加回偏移
    write_to_servos(actual_commands)
```

**校准 ≠ 重训**：

| 操作 | 改的是 | 工作量 | 效果 |
|------|--------|--------|------|
| `joint_offsets` 校准 | 配置文件 14 个数字 | 30 分钟 | 让真机姿态对齐训练假设 |
| 微调 fine-tune | ONNX 权重 | 几小时 GPU + 调试 | 让模型适应新硬件 |
| 重训 retrain | 完全重新跑 | 几小时-几天 GPU | 适应大改动 |

**原版作者就提供了 `find_offsets.py` 脚本**：手动摆"完美站立姿态"→ 读 14 个舵机当前角 → 写入 `duck_config.json`。

**重要附加事实**：原版作者也踩过 IMU 倒置坑，`duck_config.json` 里 `imu_upside_down: false` 字段是原版作者就设计的——爱折腾自己的鸭子也是倒装的，必须改成 `true` 才正常。

### 6.6 爱折腾的产品定位

> "原版项目的中国本地化套件 + 教育服务"

价值真实——把开源 hacker 项目变成商业可购买的可玩产品；但**不该被理解成"做了硬件创新"**。

**对用户的购买建议**：

- ✅ 想要语音交互 + 摄像头 + 套件化省事 → 爱折腾贵一点但合理
- ✅ 想要最便宜原汁原味 RL → 参考原版 BOM 自己采购
- 真正属于"爱折腾增量"的：**中文教程 + 国内供应链选型 + 套件化销售 + py-xiaozhi MCP 集成**

---

## 7. 爱折腾的语音方案：AI 小智 + 自定义 MCP

### 7.1 整体架构

```
┌─── 云端 (虾哥服务器 xiaozhi.me 或自建 xiaozhi-esp32-server) ────┐
│  大模型大脑: Qwen / DeepSeek                                    │
│  └ 工具调用决策 (基于 MCP tools/list)                            │
│  ASR (Doubao / FunASR)  TTS (EdgeTTS / 讯飞)  MCP 路由          │
└──────────────────────────┬─────────────────────────────────────┘
                           │ WebSocket (二进制 + JSON 文本)
                           │ Opus 编解码音频
                           ▼
┌──── Pi Zero 2W (鸭子身上) ──────────────────────────────────────┐
│  py-xiaozhi 客户端                                               │
│  - 麦克风采集 → Opus 编码 → 上传                                  │
│  - 接收 TTS 音频 → 解码 → 播放                                    │
│  - 接收 MCP 调用 → 路由到鸭子工具                                 │
│  - 状态机: IDLE → CONNECTING → LISTENING → SPEAKING             │
│                                                                  │
│  自定义 MCP 工具 (爱折腾自己写的 ~200-500 行 Python)              │
│  - duck_walk(direction, speed)                                   │
│  - duck_stop()                                                   │
│  - duck_turn(direction, angle)                                   │
│  - duck_set_emotion(emotion_name)                                │
│  - duck_show_eye(pattern)                                        │
│  - duck_play_action(action_name)                                 │
│  - duck_take_photo()                                             │
│  - ...                                                           │
│                                                                  │
│  RL System 1 (50Hz):  7 维 command → ONNX → 14 ST3215 + 2 SG90  │
└──────────────────────────────────────────────────────────────────┘
```

### 7.2 py-xiaozhi（树莓派版小智）

GitHub `huangjunsen0406/py-xiaozhi`。爱折腾大概率 fork 此项目。已实现：

1. **完整状态机**：`IDLE ─[唤醒词/按钮]─▶ CONNECTING ─▶ LISTENING ─[ASR完成]─▶ SPEAKING ─[播完]─▶ IDLE`
2. **WebSocket 协议**：
   - 二进制帧：OPUS 音频流（16/24kHz 单声道 60ms 帧）
   - JSON 文本帧：控制信令（hello、tts state、mcp 请求/响应）
3. **音频编解码**：libopus 实时（嵌入式标配）
4. **唤醒词**：Vosk / Snowboy / Porcupine 本地小模型

**初始化 hello 帧**：

```json
{
  "type": "hello",
  "version": 1,
  "features": { "mcp": true },
  "transport": "websocket",
  "audio_params": {
    "format": "opus",
    "sample_rate": 16000,
    "channels": 1,
    "frame_duration": 60
  }
}
```

`"features": { "mcp": true }` 关键——声明这鸭子支持 MCP，服务器才会发工具调用。

### 7.3 MCP 在这里的角色

不是简单"语音 ASR + LLM + TTS"，而是把所有 AI 重活甩到云端，本地只做轻活，**用 MCP 协议把鸭子的物理能力"暴露"给云端 LLM**。

**鸭子向云端 LLM 注册自己的能力清单**（`tools/list`）：

```json
{
  "type": "mcp",
  "payload": {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "result": {
      "tools": [
        {
          "name": "duck_walk",
          "description": "让鸭子向某个方向走",
          "inputSchema": {
            "type": "object",
            "properties": {
              "direction": {"type": "string", "enum": ["forward","backward","left","right"]},
              "speed": {"type": "number", "description": "速度 0.0 到 0.15 m/s"}
            }
          }
        },
        ...
      ]
    }
  }
}
```

**实际对话流程**（用户："前面有什么？去看看，然后告诉我你的感受"）：

```
1. ASR → 文字
2. LLM 理解：多步任务
3. LLM 决定调用工具序列：
   - duck_set_emotion("curious")
   - duck_walk("forward", 0.1)
   - (等几秒)
   - duck_stop()
   - duck_take_photo() → 看到桌子和水杯
   - duck_set_emotion("knowing")
   - TTS: "我看到一张桌子，上面有个水杯，看起来很普通呀"
4. 每个工具调用都通过 WebSocket 发给鸭子
```

### 7.4 自定义 MCP 工具骨架

```python
from mcp_server import register_tool

command = [0.0] * 7  # 共享 RL System 1 的 7 维

@register_tool(name="duck_walk", description="让鸭子向某个方向走")
async def duck_walk(direction: str, speed: float = 0.1):
    speed = max(-0.15, min(0.15, speed))  # 强制限幅
    if direction == "forward":   command[0] = speed; command[1] = 0.0
    elif direction == "backward": command[0] = -speed
    elif direction == "left":    command[1] = speed
    elif direction == "right":   command[1] = -speed
    return {"status": "ok", "current_speed": speed}

@register_tool(name="duck_stop", description="让鸭子停下来")
async def duck_stop():
    command[0] = command[1] = command[2] = 0.0
    return {"status": "stopped"}

@register_tool(name="duck_set_emotion", description="设置情绪表情(头+天线+眼睛)")
async def duck_set_emotion(emotion: str):
    asyncio.create_task(play_head_emotion(emotion))
    asyncio.create_task(play_antenna_emotion(emotion))
    eye_controller.set_pattern(emotion)
    return {"status": "ok", "emotion": emotion}

@register_tool(name="duck_take_photo", description="拍照并返回图像描述")
async def duck_take_photo():
    img = camera.capture()
    upload_url = mcp_session.get_vision_url()
    response = await upload_image(upload_url, img)
    return {"status": "ok", "description": response}
```

### 7.5 工程注意

1. **参数限幅必须**——LLM 偶尔幻觉，可能调 `duck_walk("forward", 100)`
2. **异步是关键**——`async def` + `await asyncio.sleep()`，禁用 `time.sleep()`（会卡音频流）
3. **工具响应 < 200ms**——长动作 `asyncio.create_task` 后台跑 + 立即返回
4. **共享内存接口**：用 `threading.Lock` / `asyncio.Lock` 保护 command 数组的并发写

### 7.6 推荐 LLM 输出格式（同时给 command + emotion + say）

```json
{
  "command": {
    "vx": 0.1, "vy": 0.0, "wz": 0.0,
    "neck_pitch": 0, "head_pitch": 0,
    "head_yaw": 0, "head_roll": 0
  },
  "emotion": "curious",
  "say": "前面这是什么?"
}
```

Pi 端三件事并行：

```python
def on_llm_response(response):
    rl_policy.set_command(response["command"])           # System 1
    emotion_machine.request_emotion(response["emotion"]) # 表演系统
    tts.speak(response["say"])                           # 喇叭
```

### 7.7 MCP 方案的"分层架构"位置

用户在第 39 轮抓到：

> "这套方案和我之前说的 system 1 和 system 2，所以还认为是一个架构吗？"

**严格答案**：

| 范式 | 接口形态 | 谁产 7 维 |
|------|---------|----------|
| A. 数值接口（之前讨论）| `{vx: 0.1, vy: 0, ...}` 直接数字 | LLM 直接 |
| B. 语义接口（爱折腾 MCP）| `duck_walk(direction="forward", speed=0.1)` | 本地工具函数翻译 |

```
范式 B 严格画就是 2.5 层：
  System 2 (LLM)
       ↓
  Skill Layer (工具函数)  ← 新加的一薄层
       ↓
  System 1 (RL)
```

**Skill Layer 又叫 Skill Library / Action Adapter / Tool Layer / Behavior Macro**——本质是**解释器**，把高层意图转成低层数值。学术上可叫 "System 1.5" 或 "Mid-level Controller"。

**Skill Layer 解决的四个真实问题**：

1. **LLM 不擅长产生连续精确数值**（会抖：vx 这次 0.08 下次 0.12）→ 输出 `"slow"` 标签 → 翻译器映射成固定 0.05
2. **LLM 不懂物理约束** → 翻译器硬限幅
3. **动作组合的复合性** → `duck_play_sequence([...])` + 内部 `asyncio.sleep` 时序，LLM 摆脱"每秒决策"
4. **能力扩展性** → 加新工具 = LLM 立即学会新技能（端到端方案需要训练数据）

### 7.8 学术分歧

| 派系 | 代表工作 | 主张 |
|------|---------|------|
| End-to-End | π0、OpenVLA、GR00T、RT-2、Diffusion Policy | 端到端学，无中间层 |
| Hierarchical / Skill-based | NaVILA、SayCan、Code as Policies、爱折腾 MCP | 人手工定义原子技能，LLM 选择和组合 |

**2025-2026 趋势**：行业在向技能派倾斜（特别是消费级/商用），因为：

- 端到端 VLA 还不够稳
- LLM 的 Function Calling 能力 2024 起爆炸式增长
- 安全性可解释性是商用硬需求

但学术界仍认为端到端是终极目标——只是工程上还没达到。

### 7.9 MCP 调用不是自然语言

**用户的用词需要校正**：

```
低抽象 ←──────────────────────────────────→ 高抽象

数值参数         结构化语义指令          自然语言
{vx: 0.1}    duck_walk(forward, 0.1)    "走快点"
   │                  │                    │
我们前面方案       MCP 方案            人类用户输入
                                      (LLM 内部处理)
```

MCP 选了"中间档"——既保留语义可解释性（像自然语言），又保留参数明确性（像数值）。

---

## 8. 表情系统（情绪表达）

### 8.1 核心认知

> 情绪系统**不是 AI**，是表演（principle of acting through pose）。LLM 输出情绪标签 → 程序查表执行动作脚本 → 用户感知"鸭子有情感"。

### 8.2 三个表达通道

| 通道 | 表达能力 | 信息带宽 | 用户解读难度 | 备注 |
|------|----------|----------|--------------|------|
| **脖子（头部 4 关节 ST3215）** | ★★★★★ | 高 | 本能识别，零学习 | 跨文化跨物种，最强 |
| 天线 SG90 | ★★★ | 中 | 需要"学" | 鸭子真没有天线 |
| 眼睛 LED | ★★ | 低 | 状态指示用 | 单色二值，仅亮/灭 |
| TTS 喇叭 | ★★★★ | 高 | 直接听懂 | - |

### 8.3 头部 4 关节情绪映射（最重要的资源）

**为什么脖子是最强情绪载体**：人/动物表达情绪头部姿态是第一信号——歪头=好奇、低头=顺从、抬头=警觉、摇头=否定、点头=肯定，跨文化跨物种、几亿年神经回路。

**关键架构事实**：头部 4 关节虽走 RL 的 command 接口，但 RL 不输出它们——`HEAD` 完全开环。情绪系统直接覆写 `command[3:7]` 安全，不冲突。

**情绪关键帧示例（节选）**：

```python
HEAD_EMOTION_SEQUENCES = {
    "curious": [  # 经典"狗式歪头"
        (0.0,  0.0,  0.0,  0.0,  0.3),
        (0.0,  0.1,  0.0,  0.4,  0.6),   # 微抬 + 歪向右肩
        (0.0,  0.1,  0.0,  0.4,  1.2),   # 长保持(关键!)
        (0.0,  0.0,  0.0,  0.0,  0.5),
    ],
    "thinking": [  # 抬头看天花板，知识分子鸭专用
        (0.2,  -0.3, 0.0,  0.0,  0.5),
        (0.2,  -0.3, 0.0,  0.1,  1.5),
        (0.0,  0.0,  0.0,  0.0,  0.6),
    ],
    "agree": [  # 双点头
        (0.0,  0.0,  0.0,  0.0,  0.2),
        (0.0,  0.3,  0.0,  0.0,  0.25),
        (0.0,  -0.05, 0.0, 0.0,  0.25),
        (0.0,  0.3,  0.0,  0.0,  0.25),
        (0.0,  0.0,  0.0,  0.0,  0.4),
    ],
    # disagree, confused, happy, sad, shy, alert, sleepy
    # 文人系列（配合用户人文偏好）：
    "contemplating": [(0.1, -0.15, 0.2, 0.15, 0.8), (0.1, -0.15, 0.2, 0.15, 2.5), (0.0, 0.0, 0.0, 0.0, 0.8)],
    "knowing": [...],  # 心领神会，缓慢闭目式微微点头
}
```

**工程注意**：

1. 单步姿态变化建议 < 0.3 弧度（约 17°）
2. 单步时长 ≥ 0.2 秒
3. 极端姿态保持时间不要太久（舵机会发热）
4. neck_pitch 向后仰太多（< -0.5 rad）可能让头撞背部结构件，先在仿真里验证物理可达
5. 走路时只用幅度小的姿态（< 0.2 rad）保守起见

### 8.4 天线 SG90 情绪库

```python
EMOTIONS = {
    "neutral":  (90,  90),    # 立直
    "happy":    (60, 120),    # 张开
    "curious":  (75,  75),    # 都微微前倾
    "alert":    (180, 180),   # 都竖直
    "sleepy":   (30,  30),    # 都耷拉
    "confused": (60, 120),    # 一高一低
    "shy":      (45, 135),
    "excited":  (120, 60),
}
```

**不要长时间满力堵转**——SG90 廉价塑料齿轮会烧。`alert` 竖到 180° 几秒后软件应该松到 175° 卸力。

### 8.5 眼睛 LED 现实

爱折腾鸭子的"眼睛"硬件：**两个普通 LED 灯珠 + 30mm 透明圆片做眼罩**，直连 GPIO23/24。

| 能做 | 不能做 |
|------|--------|
| 亮 / 灭 | 显示形状 (❤️、⚡️、X) |
| 软件 PWM 调亮度 | 显示颜色（单色 LED）|
| 闪烁（快/慢/呼吸）| 滚动文字 |
| 单/双眼独立控制（两个 GPIO）| 像素动画 |

**最实用定位：状态指示器 + 交互节拍器**，不是"表情屏"。

**状态指示器映射**：

| 状态 | 眼睛表现 |
|------|---------|
| 启动中 | 渐入 |
| RL 策略已加载 | 常亮 |
| Wi-Fi 断开 | 慢闪 |
| 听到唤醒词 | 突然亮起 |
| 正在录音 | 缓慢呼吸 |
| 正在思考(等 LLM) | 节奏脉冲 ← **关键状态**，避免 1-3s 延迟期间用户觉得卡住 |
| 正在说话(TTS) | 配合声音节奏闪烁 ← 视听同步 |

**升级路径**（如果将来真要 BDX 那种眼睛动画）：

| 方案 | 难度 | 效果 | 接口 |
|------|------|------|------|
| 当前(单 LED × 2) | ★ | 状态指示 | GPIO |
| 换 RGB LED | ★★ | + 颜色 | 3 GPIO 或 PWM |
| 两个 0.96/1.28 寸 OLED/LCD 圆屏（GC9A01 30-50 元/个）| ★★★ | 真实眼球动画 | SPI |

**`duck_config.json` 还有 `projector: false` 占位符**——爱折腾预留但未实现的"投射器/探照灯"功能（猜想：投眼睛形状或地面光斑）。

### 8.6 idle breathing（持续微动）

```python
class IdleBreathing(threading.Thread):
    """后台线程,持续给天线加 ±3° 的呼吸式微动"""
    # base_left/base_right 由情绪系统设定
    # 永远 ±3° sin 摆动，4 秒周期
    # 即使在 sleepy 状态也不停
    # 让鸭子永远看起来"活着"
```

**走路时叠加头部"呼吸式微动"**——参考鸽子走路一颠一颠：

```python
# 1.5s 周期左右摆头 ±0.05 rad
# 0.8s 周期上下点头 ±0.03 rad
# 让鸭子瞬间从"机器人走"变成"动物走"
```

### 8.7 情绪状态机（防抖动）

`min_dwell_time = 1.5s`（同一情绪至少持续 1.5s）+ 优先级仲裁（`alert > happy = curious > sleepy > neutral`）+ 高优先级可打断低优先级。

### 8.8 硬件事件直触发（不经过 LLM）

LLM 1.5s 响应延迟 → 摔在地上了。这些必须本地状态机直接触发：

- 触摸开关 → `excited`
- IMU pitch/roll > 30° → `alert`
- 电池 < 10% → `sleepy`
- 5 秒无人说话 → 渐入 idle 探索

**经典双层架构**——快速反射在本地，慢速决策在云端，合在一起像生物。

---

## 9. 给用户购买/路径决策的清晰建议（贯穿全对话）

### 9.1 演进路径（用户接受的）

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| 阶段 1 现在 | Pi Zero 2W + 14 ST3215 + IMU | 已有 BOM，能 work |
| 阶段 2 加感知反馈 | + CSI 摄像头 + I²S 扬声器（MAX98357A）| 几小时-1 天，不动主控 |
| 阶段 3 加语音/视觉智能 | + Mac Mini/Studio 当 System 2，Wi-Fi 联动 | 一个周末，不动 Pi |
| 阶段 4 端到端 VLA / 操作任务 | 整个换 Orin NX 或 AGX 主控 | 真正的"重新设计" |

**阶段 2 不需要重新设计硬件**——作者本来就在 BOM 留了 expression_features 位置。

### 9.2 加摄像头/语音的具体接法

**Pi Zero 2W 接口家底盘点**：

| 资源 | 已占用 |
|------|--------|
| USB OTG（唯一一个）| 接 ST3215 舵机控制板 |
| I²C (GPIO 2/3) | BNO055 IMU |
| UART (GPIO 14/15) | 通常给蓝牙（手柄）|
| **CSI 摄像头口** | 空闲 ✓ |
| **I²S (GPIO 18/19/21)** | 空闲 ✓（README 留给 MAX98357）|
| 剩余 GPIO | 一些（够 LED）|

**摄像头**：CSI 接 Pi Camera Module 3 (~$25) 或 OV5647，**不要用 USB 摄像头**（仅一个 USB 口已被占）。Zero 2W CSI 是 22-pin 0.5mm pitch，需 22-15 转接排线。

**扬声器**：I²S MAX98357A 3W Class-D（~$6）+ 28mm 全频小喇叭（$3-4），README 直接指定。`/boot/firmware/config.txt` 加 `dtoverlay=hifiberry-dac`。

**麦克风**：3 选 1，**推荐方案 C：麦克风外置到 Orin NX/Mac**——Pi Zero 2W 算力跑 Whisper-tiny 都吃力。Pi 只保留扬声器（本地反馈音效）。需要说话时让 System 2 合成 MP3 → Wi-Fi 推到 Pi → I²S 播放。

**电源加固（最容易出事）**：

| 设备 | 5V 峰值 |
|------|---------|
| Pi Zero 2W | 0.5-0.8A |
| Camera Module 3 | 0.25A |
| MAX98357A + 喇叭 | 1A 瞬时 |
| BNO055 | 50mA |
| 总计 | 2A 量级 |

MAX98357 响一声 1A 瞬时会拉低 5V 轨 → Pi brownout 重启（小机器人最常见故障）。两个对策：

1. MAX98357 VCC 端就近加 470µF 低 ESR + 100nF 陶瓷
2. Pi 5V 入口加 Schottky 二极管 + 470µF 防瞬态污染

### 9.3 实事求是的训练时间评估

| 阶段 | 难度 | 时间 | 硬件 |
|------|------|------|------|
| Colab 体验 RL | ★★ | 1 天 | 浏览器 |
| 本地跑通官方例子 | ★★★ | 1 周 | MateBook + WSL2 |
| 跑通 Open_Duck_Playground | ★★★★ | 1-2 周 | 任意 GPU |
| 改奖励函数实验 | ★★★★ | 持续 | 同上 |
| 改机器人结构重训 | ★★★★★ | 2-4 周 | RTX 4090 或云 |
| 第一次 sim2real 成功 | ★★★★★+ | 1-2 个月 | 真机 + GPU |

**最务实的建议**：先沿路线 A 做完前 4 步（Colab 上 6 分钟训出会走的四足）。等到真有需求改结构时再上手。**RL 工程的迭代速度比想象的快，2026 年训练时间已经从几天压缩到几十分钟，等你需要时再上手是合理的。**

### 9.4 强烈推荐的"第一晚-第五晚"周末路径（情绪系统）

1. 第一晚 2h：接好 PCA9685 + 2 SG90，跑通 `set_emotion('happy')` 让天线张开
2. 第二晚 2h：加 ease_to 平滑插值 + IdleBreathing 后台线程
3. 第三晚 2h：写好 EMOTION_SEQUENCES 字典 8-10 种情绪，每种 3-5 关键帧
4. 第四晚 2h：接 LLM——阿里云百炼 Qwen-VL 输出 JSON 含 emotion 字段，Pi 解析后调 play_emotion
5. 第五晚以后：迭代调每种情绪的时长和幅度——长期艺术活，越调越细致，像动画师调动作

---

## 10. 上游仓库与外部资源汇总

### 10.1 必看 4 仓库（apirrone）

| 仓库 | 角色 |
|------|------|
| `apirrone/Open_Duck_Mini` | 硬件设计（机械/电子/BOM）——主仓库 |
| `apirrone/Open_Duck_Mini_Runtime` | 实机控制运行时（v2 分支） |
| `apirrone/Open_Duck_Playground` | Mujoco RL 仿真训练 |
| `apirrone/Open_Duck_reference_motion_generator` | 参考动作生成器 |

GitHub **没有独立 v2 仓库**，v2 是主仓库内部迭代。

### 10.2 关键文件路径

- `Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py` — 训练环境定义
- `Open_Duck_Playground/playground/open_duck_mini_v2/mujoco_infer.py` — 推理参考
- `Open_Duck_Playground/playground/open_duck_mini_v2/randomize.py` — domain randomization 清单
- `Open_Duck_Playground/playground/common/export_onnx.py` — brax → ONNX 导出（手写非标准）
- `Open_Duck_Mini_Runtime/setup.cfg` — Python 依赖（`adafruit-circuitpython-bno055==5.4.13`、`onnxruntime`、`rustypot`、`openai==1.70.0`）
- `Open_Duck_Mini_Runtime/duck_config.json` / `example_config.json` — 含 `joints_offsets`（14 个）+ `imu_upside_down` + `expression_features`（eyes/projector/antennas/speaker/microphone/camera 6 项）
- `Open_Duck_Mini_Runtime` 里有 `find_offsets.py` 和 `prepare_robot.md`（标准装配/校准 SOP）
- 模型权重：`BEST_WALK_ONNX_2.onnx`（300-500KB）

### 10.3 第三方教程 / 参考

- **Frank Fu 博客**（frankfu）：`pypot` 打过 Feetech STS3215 支持补丁的分支；`i2cdetect -y 1` BNO055 检测；`calibrate_imu.py` 标定流程
- **Hackaday 报道**（2025-04）：明确说 BNO055 是"绝对方向 IMU"
- **CSDN**：引用同济子豪兄团队复现，提到"AI 小智语音交互"
- **mujoco_playground.org**：官方 Colab notebook（A100 上四足 6 分钟训完）

### 10.4 py-xiaozhi 生态

- `huangjunsen0406/py-xiaozhi` — 树莓派版小智客户端
- `xiaozhi.me` — 虾哥服务器（免费用 Qwen 实时模型）
- `xiaozhi-esp32-server` — 自建后端（完全本地化，可换成 DeepSeek/Qwen 自己的 API key）

### 10.5 学术对照工作

- **NaVILA**：腿足 VLA 不直接预测关节，而是分层。VLA 输出"前进 75cm"语言形式中层动作，由视觉运动 RL 策略执行
- **WholeBodyVLA**：loco-manipulation-oriented (LMO) RL 策略 + 离散命令接口
- **GR00T N1**：分成重型 System 2（高层规划）+ 轻型 System 1（低层动作生成）
- **π0 / OpenVLA / Diffusion Policy / RT-2**：端到端派代表
- **SayCan / Code as Policies**：技能派代表

---

## 11. 用户在对话中已表达的偏好与暗线

整理这些便于后续 PRD 时直接套用（不再重新讨论）：

1. **远端策略红线**（虽然分享对话没直接讨论，但与 guagua CLAUDE.md 一致）：只 push GitHub origin，Gitee 由 sync-gitee.ps1 自动镜像。
2. **System 2 算力位置偏好**：用户明确认可"不需要在鸭子身上"，未来 Mac Studio 当家庭大脑是认可方向。
3. **NeuroMemory 集成意图**：System 2 应该能直接读用户 Obsidian / NeuroMemory 数据库——这是用户在云端方案上选本地推理的真正动机。
4. **角色偏好**：人文气质（古琴、Su Dongpo），鸭子情绪表达更倾向"contemplating / wistful / knowing"这种沉静慢动作，而不是卡通活泼。
5. **学习态度**：用户接受"路线 A 做完前 4 步再说，等真要改结构时再做路线 B"——不要在 PRD 里安排"提前学 RL 训练"这种过度准备。
6. **对营销话术警觉**：明确接受了"BNO055 实现平衡是话术"、"调重心是 joint_offsets 校准"等校正——下次产品文档说类似话直接拆穿即可。
7. **接受爱折腾产品定位**：套件化省 20-30 小时装配，但不会高估其技术贡献。

---

## 12. 对 guagua 项目（应用层）的直接含义

> 以下结论是**从这段分享对话推导**给 guagua 的，便于后续 PRD/plan 引用，不构成新的项目决策。

1. **应用层 ≠ 重写硬件层**——guagua 的"性格 / 关系建模 / 调度"全部应该坐在 System 2 上，不应该碰 Pi Zero 2W 的 50Hz 循环。
2. **接口契约就是 7 维 command + emotion 标签 + say 文本**——guagua 应用层的输出格式建议直接对齐这个三元组，对底层 OpenDuckMini Runtime 友好。
3. **NeuroMemory 集成天然落在 System 2 一侧**——把"鸭子记得昨天的事"的能力放到 Mac Mini 进程里，不要试图让 Pi 端跑记忆系统。
4. **情绪/性格设计的真实落点是表演脚本库**，不是 AI——guagua 应该投资在**情绪关键帧 YAML 配置**上，而不是"训练情绪模型"上。
5. **是否买爱折腾整机**：是合理的 M0/M1 加速器（省 20-30 小时装配 + 提供 py-xiaozhi MCP 可借鉴代码），但要清楚他们的 RL 部分就是原版 ONNX，没改动。
6. **vendor/ submodule 引入策略**：4 个 apirrone 仓库未必都需要 vendor，按需引——优先 `Open_Duck_Mini` + `Open_Duck_Mini_Runtime`（应用层依赖）；`Playground` + `reference_motion_generator` 只在真要重训时引。
7. **scripts/ 应当包括** `find_offsets.py` 调用、`calibrate_imu.py` 调用、joint_offsets YAML 模板——这些是任何买回鸭子的人都要做的标准工作。
8. **不要试图自训 RL**——除非机械结构发生不可避免的变化（用户接受用户原话："不要为了'以后可能要改'而提前准备"）。

---

## 13. 待解决 / 未在对话中确认的问题

整段对话提到但用户没明确回答的悬而未决项：

1. 是否真买爱折腾的整机（淘宝 CZ057）作为 M0 加速器？还是按原版 BOM 自己采购？
2. NeuroMemory 集成的最早接入点是 M2 还是 M3？
3. System 2 硬件最终定型——Mac Mini M4（5K）还是直接上 Mac Studio？
4. 是否需要把语音方案的 LLM 从虾哥 xiaozhi.me 切到自建 xiaozhi-esp32-server + 自家 API key？
5. 表情/性格的 YAML 配置 schema 怎么和 cc 的 8 项耦合点门禁挂钩？
6. 8 项耦合点门禁里"声学 / 表达 / 感知"分别对应分享对话哪一段？需要在 PRD 里把这层映射做出来。

这些不在本知识文件解决——它们属于 PRD/plan 阶段的工作。

---

## 附：本文件来源元数据

- **提取时间**：2026-05-05 02:16 (UTC+8)
- **提取人**：Claude Opus 4.7（在 `D:/CODE/guagua/` 工作目录中）
- **原始 URL**：`https://claude.ai/share/cd37998c-8480-4122-bf94-772044fdc347`
- **提取过程**：WebFetch 被 403 拒绝 → Chrome MCP `tabs_create_mcp` + `navigate` + `javascript_tool` 通过 `console.log` 分块（每块 4000 字符）+ `read_console_messages` 按 `CHUNK_<offset>` 模式读回，共 33 个 chunk × 4000 字符 = 132000 字符（实际清洁后 129361 字符）
- **去除内容**：URL（替换为 `[URL]`）— claude.ai 引用块的链接已无原始域名，但本文件的事实陈述均经过整理而非直引
- **未保留**：原对话里的搜索调用提示（"Searched the web"）和 emoji 表情按钮 UI 元素

如需重新拉取，使用以下 PowerShell 简化提示词：

```
让 Claude 通过 Chrome MCP 打开该 URL，将页面内 [data-testid="user-message"] 的 47 个兄弟 div 按顺序提取，
chunked dump 到 console.log 后逐 chunk read_console_messages 取回。WebFetch 不可用。
```
