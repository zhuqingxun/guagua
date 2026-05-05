---
description: "PRD: 阶段 A - 桌面级双足陪伴机器人 sim2real 复刻与真机行走"
status: in-progress
created_at: 2026-05-02T00:17:41
updated_at: 2026-05-05T18:00:00
archived_at: null
related_files:
  - docs/handoff-2026-05-01-kickoff.md
  - docs/robot-thinking-handoff.md
  - docs/openduckmini-knowledge-from-share-2026-05-04.md
  - rpiv/plans/plan-m0.md
  - rpiv/todo/m0w1-dev-env.md
  - rpiv/todo/m0w2-deepread-and-mujoco.md
  - rpiv/todo/m2-purchase-decision.md
---

# 阶段 A PRD：呱呱 sim2real 复刻与真机行走

> 阶段 A 是呱呱项目的"学习期"，6 个月（M0-M6，13 周，130 小时）走通整条 sim→训→ONNX→Pi Zero 2W→真机的工程链路。
>
> 本 PRD 是阶段 A 总纲，下游 plan 文件按 milestone 拆解。

## 1. 背景

呱呱（guagua）= 基于 OpenDuck Mini V2 的桌面级双足陪伴机器人。上游 [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini) 是 Antoine Pirrone (Pollen Robotics) 主导的开源 BDX 复刻项目。本仓库在硬件 + Runtime 之上叠加自定义应用层（性格、关系建模、对话/视觉/动作高层调度）。

阶段 A 不做应用层任何工作，**只做底层 sim2real 复刻**。应用层从阶段 B 开始。

## 2. 阶段 A 硬性目标

### 2.1 驱动力（已锁定）
**彻底掌握技术栈**：MuJoCo + PPO + ONNX + Pi Zero 2W 部署整条链路亲手走一遍。呱呱这个载体是手段，不是走不起来也不影响阶段 A 过关——但对"走起来"有量化下限（见 2.2）。

### 2.2 M6 验收门（硬性下限）
**地面 ≥ 2 步真机走，视频为证**。

不达标即阶段 A 不过关，按 M6 决策门处理（见 §6）。

### 2.3 「软件先行」原则（核心调整）
M0-M2 全部为零硬件投入的软件期。**M2 末设决策门**——软件链路验证通过后才下单爱折腾整机进入硬件期。

**Why**：避免 M0 即下单 ¥4199 后 M0-M2 软件学不动的预算+心理双重沉没成本。每周 10 小时 hobbyist 约束下，软件链路本身已是非平凡挑战；若软件这关过不了，硬件就是闲置。

**How to apply**：M0-M2 任何 PRD/plan 里**不出现"采购"任务**。M2 决策门通过后才发 m2-purchase 订单 todo。

## 3. 范围与非范围

### 3.1 范围（IN）
- MuJoCo 仿真环境搭建（基于 `Open_Duck_Playground`）
- 参考动作生成（基于 `Open_Duck_reference_motion_generator`）
- PPO 训练（仿真里跑通，能站、最好能走）
- ONNX 模型导出
- Pi Zero 2W 真机部署（`Open_Duck_Mini_Runtime`）
- 真机标定（舵机零点、IMU、足底压力）
- sim2real gap 分析与缩小（域随机化、参数标定）
- 硬件采购仅一次：爱折腾整机或散件（M2 决策门后）

### 3.2 非范围（OUT，留给阶段 B）
- 视觉感知（深度相机、人体检测）
- 语音交互（Whisper、Edge TTS、LLM）
- VLA 模型部署
- 长期记忆系统（Qdrant / Neo4j）
- 表情系统、双臂、上肢
- 主控升级到 Orin Nano（M6 后阶段 B 处理）
- 自定义性格 / 关系建模

## 4. 硬件路径（已锁定）

### 4.1 选型决策结论

| 项 | 决策 | 来源 |
|----|------|------|
| 主控 | **Raspberry Pi Zero 2W** | 与上游 apirrone v2 100% 一致，爱折腾整机内置 |
| 舵机 | **Feetech ST3215-C018 12V 18kg·cm × 14** + SG90 × 2 | 爱折腾整机配置（仅舵机比上游 7.4V 升一档）|
| IMU | BNO055 9 轴 | 上游一致 |
| 相机 | Pi Camera V2 800万 | 阶段 A 不用，阶段 B 视觉用得到 |
| 电源 | 11.1V 1500mAh 3S 锂聚 + UBEC 12→5V | 爱折腾整机内置 |
| 来源 | **爱折腾智能机器人**（淘宝 id=946801761316，店铺 4.8 分）| 27 篇 ncnynl 教程作者直接背书 |

### 4.2 SKU 已锁定：整机版 ¥4199（2026-05-05 决策）

**结论**：买爱折腾「12V 强劲动力标准版」整机，¥4199 含税包邮。M2 决策门通过即下单，不再走散件路径。

**Why（替换原默认散件方案）**：
1. **每周 10h hobbyist 时间约束**：散件组装 10-20h 等于挤占 M3 全部预算，挤压 sim2real 联调时间
2. **学习目标可在软件链路达到**：阶段 A 真正的"彻底掌握"在 MuJoCo + PPO + ONNX + sim2real gap 闭环上，硬件组装是周边技能，不构成核心增量
3. **整机出厂含 py-xiaozhi 客户端 + xiaozhi.me 后端打通**，与 System 2 演进路径 S0 起点（用爱折腾出厂栈跑通整机）对齐
4. **失去的 ncnynl「硬件组装」章节实战价值**：通过深读 + 拆装 1-2 个舵机维修场景补偿，不影响 M5 调标定参数

**保留作为 M2 决策门触发的备选**：仅当 M2 末耗时 ≤ 50h（远低于 70h 上限）且用户明确想多吃硬件经验时才考虑回切散件 ¥3900；默认不重启此讨论。

### 4.3 阶段 A → 阶段 B 主控升级路径
M6 真机走通后，阶段 B（M7+）切到 Jetson Orin Nano 8GB（+¥3500）。Pi Zero 2W 单板 ~¥150，sunk cost 低；硬件升级动作和能力升级动作（接 VLA / 视觉 / 语音）天然绑定。

## 5. 软件路径（已锁定）

### 5.1 教程主对标（按优先级）

| 优先级 | 资源 | 用途 |
|--------|------|------|
| 🥇 主跟 | **ncnynl.com 爱折腾的 27 篇 OpenDuckMini 系列** | 国内最深、最系统、含真实 bug 排查、与硬件供应商同一作者 |
| 🥈 印证 | Frank Fu 英文博客 + YouTube | 跨视角校验，sim2real 部分有详细 reward 设计说明 |
| 🥉 入口 | 同济子豪兄 B 站 BV1hxZnYfEjo | 开篇导论建立心理预期，**不指望它教跑通** |
| 备用 | APX103/Open_Duck_Mini fork（中文翻译）| 上游英文 README 看不懂时对照 |
| 兜底 | 上游 apirrone Discord (2648 stars 社区) | 卡 > 2 周时求助 |

### 5.2 上游仓库引入方式
M2 决策门前不加 submodule（用户已锁定空仓启动）。M3 开始按需 `git submodule add` 到 `vendor/`：
- `vendor/Open_Duck_Mini/`
- `vendor/Open_Duck_Mini_Runtime/`
- `vendor/Open_Duck_Playground/`
- `vendor/Open_Duck_reference_motion_generator/`

### 5.3 工具链
- 包管理：`uv`（用户既有习惯）
- 仿真：MuJoCo 3.x（PC 端 WSL2 Ubuntu）
- 训练框架：MuJoCo Playground（基于 Brax + JAX）
- 实验管理：Weights & Biases
- 配置管理：Hydra
- 板载（M3+）：JetPack 不适用，改用 Raspberry Pi OS Lite 64-bit + ONNX Runtime CPU
- 主开发机：Huawei MateBook Pro Windows 11 + WSL2 Ubuntu 24.04 + Cursor + Claude Code

## 6. Milestone 与决策门

时间约束：**10 小时/周 × 13 周 = 130 小时**，task 粒度按"1 任务 ≈ 2 小时"切分。

### M0（第 1-2 周，20 小时）：仿真工具链 + 教程预读
**目标**：本地仿真环境跑起来，对全流程心中有数。
- WSL2 Ubuntu 24.04 + uv 环境
- MuJoCo 3.x 安装 + viewer 打开默认场景
- Fork 上游 4 仓库到 zhuqingxun
- W&B 账号注册
- 加入 OpenDuck Discord
- ncnynl 27 篇通读 1 遍 + 标记 ≥ 5 个待验证问题
- Frank Fu 博客读完 + 笔记
- 子豪兄 B 站视频看完
- **本阶段交付**：手记笔记 1 份（PC 上、未入仓）+ 上游仓库 fork 完成
- **零硬件投入**

### M1（第 3-4 周，20 小时）：参考动作 + 仿真加载
**目标**：把上游官方 demo 在自己机器上跑通。
- `Open_Duck_reference_motion_generator` 装好（Placo IK 依赖）
- 生成几条参考动作（站立、原地踏步、前进）
- `Open_Duck_Playground` 装好
- MuJoCo 加载 OpenDuckMini V2 URDF（**禁止改 URDF**）
- 用上游预训练 ONNX 在仿真里走
- **本阶段交付**：仿真录屏 1 段（机器人在 MuJoCo 里走路）+ 笔记 1 份记录"上游能跑的最小配置"
- **零硬件投入**

### M2（第 5-6 周，20 小时）：自训策略 + 决策门
**目标**：用上游 reward 自己训一个能站的策略，验证整条软件链路。
- 跑通 PPO 训练（仿真 100 个 episode 起步）
- 训出一个能"站立 ≥ 5 秒不倒"的策略（先不要求走）
- 导出 ONNX
- 在 PC 上验证 ONNX 推理（CPU 模式延迟基线值，作为 M4 Pi Zero 2W 实测对照基线）
- W&B 上至少 1 次完整训练曲线

**🚨 M2 末决策门（必过）**：
1. ✅ 仿真训练能完整跑通一次
2. ✅ ONNX 导出无误，PC 推理正常
3. ✅ 至少能让仿真机器人站稳 5 秒
4. ✅ 累计耗时 ≤ 70 小时（不超 M0-M2 预算的 175%）

**4 项全过 → 进 M3，下单爱折腾整机版 ¥4199**（SKU 已锁定，见 §4.2；执行 todo 见 `rpiv/todo/m2-purchase-decision.md`）。
**任一项不过 → 触发 M2 降级**（见 §7.2）。

### M3（第 7-8 周，20 小时）：硬件到货 + 整机调试 + Runtime 源码
**前提**：M2 决策门通过，整机已下单（爱折腾发货 48 小时 + 顺丰 2-3 天 = 一周内到）。

- 开箱跑爱折腾出厂 py-xiaozhi → xiaozhi.me demo（1-2 小时）→ 验证整机功能完好
- 剩余 16-18h 用于读 Open_Duck_Mini_Runtime 源码 + 拆解出厂软件栈（PRD 锁定整机版后省下的 10-15h 组装时间转移到此处）
- 树莓派 OS Lite 64-bit 验证（出厂已烧录，确认版本可对齐）
- SSH + I2C + ONNX Runtime CPU 装好
- **本阶段交付**：整机硬件本体可控（舵机能动、IMU 能读、SSH 能进）+ Runtime 源码阅读笔记 1 份

### M4（第 9-10 周，20 小时）：sim2real 第一次过桥
- 舵机零点标定（`find_soft_offsets.py`）
- IMU 标定（`calibrate_imu.py`）
- 把 M2 的"站立"策略部署到 Pi Zero 2W
- **🎯 关键测量：实测 Pi Zero 2W 上 ONNX 推理延迟**
- 悬空机器人（纸箱+绳索吊起）跑策略，记录 IMU/舵机/足底数据
- 数据落盘到 `data/real_robot_logs/YYYYMMDD_HHMM_<test>.{bag,h5}`
- **本阶段交付**：Sim2Real Gap 分析报告 1 页 + 真机数据日志

**M4 决策点**：实测延迟 < 33ms → M6 控制频率定 30Hz；< 20ms → 50Hz；> 33ms → 触发降级（控制频率改 20Hz / 用更小网络 / 改 ONNX provider）

### M5（第 11-12 周，20 小时）：sim2real gap 闭环
- 对比仿真 vs 真机的状态轨迹（IMU、关节位置）
- 调整 MuJoCo 物理参数（摩擦系数、电机延迟、质量分布）
- 加强域随机化范围
- 用真机数据再训一轮（保守、不激进）
- 真机站立 ≥ 30 秒不倒（先不走）
- **本阶段交付**：第 2 个 ONNX 策略（更鲁棒）+ 真机站立录像

### M6（第 13 周，10 小时）：地面行走验证 🦆
- 软垫上测试，前后泡沫保护（按 ncnynl 教程"问题2"建议）
- 步态参数渐进：原地踏步 → 慢速前进 → ≥ 2 步连续
- 录视频
- 写阶段 A 总结文档（含踩坑、参数配置、阶段 B 计划）

**🚨 M6 验收（硬性下限）**：
- ✅ 地面 ≥ 2 步真机走，视频为证 → 阶段 A 通过
- ❌ 不达标 → 触发 M6 决策门（见 §7.3）

### 阶段 A 「耦合点」清单（M6 验收附加项）

M6 验收除主指标外，下列 8 项必须全有，否则推迟阶段 B：

1. ✅ Pi Zero 2W 系统配置 + ONNX Runtime 流程（M3）
2. ✅ 自己改过至少一次 URDF（M5 调整时）
3. ✅ STS3215 12V 真实摩擦/延迟参数已标（M5）
4. ✅ `IMU → policy → servo` 控制环模块化代码（M4）
5. ✅ 所有真机数据落盘 ROS2 bag / HDF5（M4-M6）
6. ✅ Onshape→URDF 导出流程跑通至少 1 次（M5）
7. ✅ Hydra + W&B 实验管理（M2-M5）
8. ✅ 硬件故障日志（哪个舵机烧了、为什么、何时）

## 7. 决策门与降级方案

### 7.1 M0 始终不达标（最早 4 周后退出）
触发条件：M0 末仍无法在 WSL2 跑通 MuJoCo viewer。
应对：扩展 ncnynl 教程"训练环境配置"细节求助 Discord 或 ncnynl 微信群。仍无解则承认本项目暂不适合现阶段，止损（已投入 ≤ 40 小时 + ¥0 硬件）。

### 7.2 M2 决策门不过
触发条件：M2 末决策门 4 项有任一项不过。
应对（按严重度排序）：
- **轻度不过**（耗时超 70h 但其他 3 项 OK）：阶段 A 总周期延长到 16-18 周，硬件下单仍按计划
- **中度不过**（仿真不能站立但训练曲线在收敛）：再加 2 周（M2.5）调 reward / 网络结构，仍下单
- **重度不过**（PPO 训练完全不收敛 / ONNX 导出失败）：**暂停硬件下单**，用 4 周时间深入官方 demo + 子豪兄视频复刻，必要时降级到"用上游预训练 ONNX 直接部署，不自训"——把阶段 A 改为"理解 + 部署"而非"理解 + 训练 + 部署"

### 7.3 M6 验收门不过（地面 < 2 步）
触发条件：M6 末真机走不起来（成功率 < 30%）。
应对：
- 阶段 A 延长到 M9（再加 6 周）
- 重点查"耦合点 3"（舵机摩擦/延迟/回程间隙是否标准）+ "耦合点 6"（URDF 是否对应实物）
- 如延长后仍 < 30% → 接受 M6 验收"真机站稳 + 仿真能走"作为软退出（违背 M6 硬指标但保住阶段 A 学习目标）
- 阶段 B 不进，转入 M9-M12 主控升级 + 重新训练

## 8. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| WSL2 MuJoCo OpenGL 渲染问题 | 中 | 中 | 改用 headless 训练 + 本地 mp4 复盘（不开 viewer）|
| ONNX 在 Pi Zero 2W 推理 > 33ms | **高** | 高 | M4 实测后调控制频率到 30Hz / 20Hz |
| 12V 舵机域随机化范围不准（上游标定基于 7.4V）| 中 | 中 | M5 用真机数据重新标 friction/delay 参数 |
| 散件组装质量问题（螺丝松动、舵盘错位）| 中 | 中 | 按 ncnynl 教程"问题3"螺纹紧固剂 + 重检每个螺丝 |
| 每周 10h 实际只能投 5h | 中 | 高 | 允许阶段 A 拖到 18-20 周，不强行赶 |
| 上游仓库 breaking change（M0 后 push）| 低 | 中 | submodule 锁定具体 commit hash，不跟 master |
| Discord/微信群求助 > 1 周无回应 | 中 | 中 | 同时提多个渠道（Discord + ncnynl 微信群 + Issue）|

## 9. 资源依赖

### 9.1 硬资源
- WSL2 Ubuntu 24.04 + 16GB+ RAM PC（用户既有）
- W&B 免费账号
- 阿里云 GPU（M2 训练加速可选，~¥500 一次）
- M3 后：爱折腾整机 ¥3900-¥4199（含税包邮）+ 微信对接

### 9.2 软资源
- ncnynl.com 27 篇教程（公开免费）
- Frank Fu 博客（公开免费）
- ncnynl 爱折腾微信群（购买后入群）
- OpenDuck Discord（公开）
- 子豪兄 B 站 BV1hxZnYfEjo（公开免费）

### 9.3 时间预算
- 总：130 小时（13 周 × 10h）
- 硬性 buffer：M2/M6 决策门可触发各 2-4 周延长
- 实际可能拖到 16-20 周，PRD 不视为偏离

## 10. 阶段 A → 阶段 B 衔接

阶段 A 通过 M6 验收后立即启动阶段 B 的 brainstorm，不留断档。阶段 B 第一步：评估"耦合点 8 项"是否补足，未补足者列入 M7 补课计划。

阶段 B PRD（`prd-stage-b.md`）在阶段 A M5 时起草，M6 验收后定稿。

## 11. 附录：本 PRD 与 docs/robot-thinking-handoff.md 的差异

| 条目 | 路线图原方案 | 本 PRD（澄清后） | Why |
|------|------------|-----------------|-----|
| 主控 | Jetson Orin Nano 8GB | Pi Zero 2W（阶段 A）→ Orin Nano（阶段 B）| 上游运行时只支持 Pi 系；与"严格复刻"目标对齐 |
| 学习路径 | Frank Fu 主跟 | ncnynl 27 篇主跟 + Frank Fu 印证 | ncnynl 教程深度高 27×；与 Pi Zero 2W 实际部署对齐 |
| 硬件下单时机 | M0 第 1 周立即 | M2 决策门后（约 W6 末）| 软件先行，预算风险止损 |
| 硬件选型 | 自购 BOM 7100 元 + 打印机 2000 元 | 爱折腾整机 4199 元（2026-05-05 锁定）| 比自购便宜近 3000 元；省下 10-15h 组装时间转移到 Runtime 源码阅读 |
| BOM 总额（阶段 A）| ~9000 元 | 4199 元 + 1000 元杂项 + 800 元云资源 = ~6000 元 | 节省 30%+ |
| ONNX 推理延迟门 | < 20ms（基于 Orin Nano）| M4 实测 Pi Zero 2W，决定 30Hz/50Hz | 算力变了指标必须重审 |

变化非全盘推翻，原路线图 7 章硬件清单 + 5 章软件栈 + Sim2Real Gap 处理 + VLA 选型仍作为阶段 B 的输入。
