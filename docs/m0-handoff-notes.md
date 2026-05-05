# M0 交付文档（5/5 完成）

> 阶段 A M0 milestone（仿真工具链 + 教程预读）的成果总结，作为 M1 输入和未来会话冷启动参考。
>
> 对应 PRD §M0 + plan-m0.md。本文档不追求穷尽，聚焦**未来会话进来需要立即知道的事**。

## 1. M0 实际工时 vs 预算

| 项 | 预算 | 实际 |
|---|------|------|
| W1（环境/账号/教程） | 10h | **~1h**（W1-1/W1-2/W1-4/W1-5 实质都来自 4/22-5/3 已有工作；本次会话 5/5 只装 uv + 验证 viewer） |
| W2（深读/sim 骨架/交付） | 10h | **~2h**（W2-1 迁移 1.5h + 本文档 + plan-m1 起草） |
| **合计** | 20h | **~3h** |

**节省 17h** —— 主要来源：
- 用户 4/22-5/3 已有大量预热工作（`~/openduck-warmup` / `~/mujoco-3.3.1` / `~/my_robot_2` / GitHub fork 4 仓库）
- 应用「文档阅读不作为阻塞」原则后，教程类硬指标移除（feedback memory `feedback_doc_reading_not_blocker`）
- W2-4 W&B 真训练 deferred 到 M2 自然过门

剩余 17h 滚到 M1（参考动作生成 + 仿真加载上游官方 demo）。

## 2. M0 完成项 vs 跳过项

### 2.1 P0 完成
- ✅ WSL2 Ubuntu 24.04 + uv 0.11.9（5/5 装在 `~/.local/bin/uv`）
- ✅ MuJoCo 3.8.0 + viewer GUI 弹窗（WSLg 经 `wsl --shutdown` 重启后通过）
- ✅ GitHub `zhuqingxun/Open_Duck_Mini` `_Runtime` `_Playground` `_reference_motion_generator` 4 仓库 fork
- ✅ W&B 个人账号 + `guagua-warmup` project 100 步假数据曲线
- ✅ `D:/CODE/guagua/sim/` uv 项目骨架（迁移自 `~/openduck-warmup`，改名 `guagua-sim`）
- ✅ `sim/scripts/verify_mujoco.py` 验收脚本

### 2.2 P2 已基本完成（教程类，按需回查）
- ✅ ncnynl 27 篇主要章节
- ✅ Frank Fu 中文博客（含 reward 设计 + RL 算法章节）

### 2.3 主动放弃
- ⛔ Discord onboarding（注册未成功；PRD 列为非必备渠道）
- ⛔ 「ncnynl 问题清单 ≥ 5」「m0-handoff 问题清单 ≥ 10」硬指标（5/5 改非阻塞）

### 2.4 deferred 到 M2 / M3
- ⏸️ W2-4 W&B 真训练曲线 → M2 PPO 真训练时自然过门
- ⏸️ 子豪兄 B 站视频 → 想看时再看，不阻塞
- ⏸️ vendor/ submodule add → M2 决策门后

## 3. 上游"最小可跑配置"摘要（M1 输入）

### 3.1 上游 4 仓库（apirrone）
| 仓库 | 默认分支 | 角色 | M1+ 用法 |
|------|---------|------|---------|
| `Open_Duck_Mini` | **v2** | 硬件 + URDF | M1 加载 V2 URDF（`~/my_robot_2/robot.xml` 已有用户 4/28 备份）|
| `Open_Duck_Mini_Runtime` | **v2** | 实机控制 | M3+ 部署到 Pi 3B+ |
| `Open_Duck_Playground` | main | Mujoco RL 训练环境 | M1+ 仿真训练 |
| `Open_Duck_reference_motion_generator` | main | 参考动作生成（Placo IK）| M1 生成站立/原地踏步/前进参考轨迹 |

注意默认分支 Mini/Runtime = `v2`（不是 main），clone 时 `--branch v2`。

### 3.2 上游"最小可跑"链路（部署侧）
来自 `docs/openduckmini-knowledge-from-share-2026-05-04.md` §4.2：
1. 机械装配 + 零位标定（爱折腾整机省）
2. IMU 标定 `calibrate_imu.py`（每次冷启动重做，BNO055 不持久化）
3. 舵机参数烧录（ID/PID/波特率，爱折腾整机已烧）
4. Pi OS Lite 64-bit + onnxruntime + rustypot + bno055 + Runtime 仓库
5. Xbox 蓝牙手柄配对（爱折腾整机已配对，含手柄）

### 3.3 上游"最小可跑"链路（仿真侧）
M1 起，按以下顺序：
1. `Open_Duck_reference_motion_generator` 装好（依赖 Placo IK）→ 生成 ≥ 1 条参考动作
2. `Open_Duck_Playground` 装好 → MuJoCo 加载 V2 URDF
3. 用上游预训练 ONNX `BEST_WALK_ONNX_2.onnx` 在 MuJoCo 中走一遍（**不自训**，PRD M1 验收）
4. 录屏 + 笔记记录"上游能跑的最小配置"

## 4. Pi 3B+ 实购对 PRD 假设的影响

完整对账见 PRD §4.1 + `docs/seller-chat-aizheteng.md`。M1+ 工作时需要注意：

| 维度 | 默认假设 (Pi Zero 2W) | 实际 (Pi 3B+) | M1+ 影响 |
|------|---------------------|---------------|---------|
| CPU | A53 @ 1GHz | A53 @ 1.4GHz | ✅ 软件栈直接复用 |
| RAM | 512MB | 1GB | ✅ ONNX 加载更宽松 |
| GPIO | 40-pin | 40-pin | ✅ rustypot/bno055 不需改 |
| 推理延迟 | < 33ms 期望 | 预期 < 20ms | M4 决策门更宽松，大概率 50Hz |
| 上游 Runtime 镜像 | 原生支持 | 需自装 Pi 3B+ 镜像 | M3 多 1-2h（Pi OS Lite 通用）|
| 续航 | 1-2W 功耗 | 4-7W 功耗 | -50%（爱折腾给配了航模电池补偿）|
| 头灯 | 无 | 有（开关灯，左右不对称但不影响平衡）| 多一个 GPIO 输出可用 |
| 低压报警 | 无 | 内置模块 | 自动避免电池过放 |
| 主控位置 | 固定 | 改到肚子里 + 接线方便 | 后续改装更友好 |

## 5. 待验证问题（按需收，不强求 ≥ N 条）

未来 M1+ 实操时遇到了再回查教程；先列出几个最可能要问的：

1. **上游 v2 默认分支** vs main 分支的差异点（M1 clone 时确认 v2 是否为最新）
2. **`BEST_WALK_ONNX_2.onnx` 在 Pi 3B+ 实测推理延迟**（M4 关键测量点；PRD 假设 < 20ms）
3. **Placo IK 装在 Linux 容易吗**（M1 起步可能卡这一步，ncnynl 教程有讲）
4. **MuJoCo Playground vs Brax 关系**（上游用的是 brax + JAX 还是 PyTorch？影响训练侧 GPU 选型）
5. **爱折腾自写 MCP 仓库地址**（卖家说开源但没给链接，M3 接 py-xiaozhi 时再追问）
6. **小智软硬件开源仓库**（猜测是 huangjunsen0406/py-xiaozhi 系列，M3 时确认）

更多问题会在 M1+ 实操中自然涌现，遇到时回查 ncnynl / Frank Fu / share 文档对应章节即可。

## 6. 踩坑记录

### 6.1 WSLg 半启动 → `wsl --shutdown` 修复
**症状**：`mujoco.viewer` 报 `X11: Failed to open display :0` + GLFW init 失败，但 `echo $DISPLAY $WAYLAND_DISPLAY` 都有值。

**诊断**：
- `/tmp/.X11-unix/` 空（应有 X0 socket）
- `/mnt/wslg/` 已挂载但子目录 `.X11-unix` 也空
- `pgrep Xwayland` `pgrep weston` 都无（除 grep 自身）

**结论**：WSLg 目录挂上但**核心进程没起**——半启动状态。

**修复**：PowerShell 中 `wsl --shutdown` → 等 8-10 秒 → 重新进 WSL → WSLg 完整初始化。

**经验**：以后 WSL GUI 应用报"无法连接显示"，第一招就是 `wsl --shutdown` 完全重启，不要先怀疑代码或 GLFW 库。

### 6.2 默认假设 Pi Zero 2W 全错
PRD 写作时（5/2）按 docs/openduckmini-knowledge §1.1 假设上游 apirrone Pi Zero 2W；5/5 实购才发现爱折腾整机线**全部离开** Pi Zero 2W（标准版 PI52G 也是 Pi 5 2GB），用户主动选 PI3B+。

**经验**：写硬件 PRD 前**先核查供应商实际 SKU 列表**，不能直接套上游"参考"BOM。

### 6.3 WSL 内已有项目没先核查
首次开干 W1-4 装 uv 时，**没先扫 `~/openduck-warmup` 等目录**就准备从零装；用户纠正后才发现 mujoco/wandb/uv 早装好了。

**经验**：装环境类任务执行前必须先 `wsl -d Ubuntu -- bash -c 'ls ~/'` + 找已存在的相关项目，避免重复劳动。已写入 memory `project_existing_wsl_work`。

### 6.4 教程通读硬指标
W1-6 ncnynl 27 篇验收"问题清单 ≥ 5 条"+ W2-2/W2-3 章节深读 P0 硬指标 — 用户反馈："读文档不该作为阻塞点，遇到问题再读才有效"。

**经验**：hobbyist 项目里把"读完 X"列 P0 验收门是反模式；正确做法是"按需回查"。已写入 memory `feedback_doc_reading_not_blocker`。

## 7. 给 M1 的节奏建议

M0 节省了 17h 滚到 M1，建议 M1 节奏：

- **M1 实际可用 ~37h（M1 原 20h + M0 余 17h）**
- 但**不强求把 17h 都吃掉**，节省下来留给 M3 调试硬件 / M5 sim2real gap
- **M1 优先级**：①参考动作生成跑通 → ②上游 ONNX 在 MuJoCo 加载 V2 URDF 走一遍 → ③录屏作证
- **M1 不做的事**：不自训 / 不改 URDF / 不加 vendor submodule（M2 决策门后）

详见 `rpiv/plans/plan-m1.md` 草稿。

## 8. 维护说明

本文档随 M0 完成定稿。M1+ 阶段如发现 M0 输入有误（如某条上游事实变化），在文件顶部加"修订日期 + 变更摘要"段，不重写正文。
