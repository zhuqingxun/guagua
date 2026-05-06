# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目当前阶段（5/6 更新）

阶段 A milestone 进度（口诀：**装/搬/训/拆/悬/缩/走** = M0/M1/M2/M3/M4/M5/M6）：

| Milestone | 状态 | 备注 |
|-----------|------|------|
| **M0 装工具看上游** | ✅ completed | sim/ 项目就绪 + 4 上游 fork + W&B + MuJoCo viewer 通过 |
| **M1 搬上游 demo** | 🚧 W3-1/2/3 ✅ / W4 待做 | motion_generator 跑通，第一条参考动作 .json 已生成 |
| M2 自训站立 5 秒 | 待开始 | 学 PPO + ONNX 导出（**学流程为主，训出来 ≈ 上游没关系**）|
| M3 整机开箱 | 5/8-5/10 到货后 | 爱折腾 PI3B+ 整机 + 小智附件 |
| M4-M6 | 后续 | 真机部署 → sim2real gap → 地面走 ≥ 2 步 |

**接续会话第一件事**：读 [`docs/m0-handoff-notes.md`](docs/m0-handoff-notes.md) —— M0 收尾文档，含上游最小可跑配置 + Pi 3B+ 改造影响 + M1 起步建议 + 4 处踩坑记录。次要参考：[`rpiv/plans/plan-m1.md`](rpiv/plans/plan-m1.md) 看 W3-4 状态 + W4 任务表。

## 上游硬件原型是 multi-repo 生态

OpenDuck Mini 由 Antoine Pirrone (Pollen Robotics) 主导，4 个活跃仓库：

| 仓库 | 默认分支 | 角色 |
|------|---------|------|
| `apirrone/Open_Duck_Mini` | **v2** | 硬件设计 + URDF + **预训练 `BEST_WALK_ONNX_2.onnx`** |
| `apirrone/Open_Duck_Mini_Runtime` | **v2** | 实机控制运行时（Pi 上跑） |
| `apirrone/Open_Duck_Playground` | main | Mujoco RL 仿真训练 |
| `apirrone/Open_Duck_reference_motion_generator` | main | 参考动作生成器（Placo IK） |

**注意**：Mini / Runtime 默认分支是 `v2`（不是 main），clone 时 `--branch v2`。GitHub 没有独立的 v2 仓库，v2 是主仓库分支。

**`vendor/` submodule 仍未加**：PRD §5.2 锁定 M2 决策门后才 `git submodule add`。M1 期间临时 clone 到 `~/code/upstream-readonly/` 只读阅读。

## 远端策略（红线）

- **只 push GitHub `origin`**（`git@github.com:zhuqingxun/guagua.git`）
- Gitee remote 仅注册不主动推，由 `D:/CODE/OS/tools/sync-gitee.ps1` 每日 13:30 自动镜像
- 已踩过此红线被纠正，不要重蹈

## 实购 SKU（5/5 下单，5/8-10 到货）

| | 实际 | PRD 原假设 |
|---|------|-----------|
| 主控 | **Raspberry Pi 3B+** | Pi Zero 2W |
| 商品 | 爱折腾「PI3B+ 整机版」¥5000 + 「实战派小智语音交互」¥250 | 「12V 强劲动力标准版」¥4199 |
| 订单号 | `3299974573941008764`（淘宝商品 id=`1009166204772`，注意不是旧版 `946801761316`）| - |
| 实付 | ¥5247.40 | - |

**Pi 3B+ vs Pi Zero 2W 影响**：A53 同内核 + 同 GPIO，软件栈直接复用；推理预期 < 20ms 直接 50Hz；功耗 4-7W vs 1-2W（爱折腾给配了航模电池补偿）。完整对账见 PRD §4.1 + [`docs/seller-chat-aizheteng.md`](docs/seller-chat-aizheteng.md)（18 张卖家聊天 OCR）。

## 当前资产清单（仓库内 + 仓库外）

```
D:/CODE/guagua/                       ← guagua 仓库 (git, push origin GitHub)
├── docs/                              持久化文档 (5 份, 含 m0-handoff / 卖家聊天 / 知识沉淀)
├── rpiv/                              过程文件
│   ├── requirements/prd-stage-a.md    阶段 A PRD (in-progress)
│   ├── plans/plan-m0.md               (completed) + plan-m1.md (in-progress)
│   └── todo/                          M0-W1/W2 + m2-purchase 等任务清单
└── sim/                               Python 项目 (uv 管理)
    ├── pyproject.toml                 mujoco 3.8.0 + wandb 0.26.1
    ├── hello_wandb.py                 W&B 验证脚本
    ├── scripts/verify_mujoco.py       W1-5 验收脚本
    └── .venv/                         (Linux Python, WSL 内)

WSL ~/                                 仓库外但接续会话需要知道
├── code/upstream-readonly/            5/6 W3-1 clone, 不在 git 里
│   ├── Open_Duck_Mini (v2)            含 BEST_WALK_ONNX_2.onnx
│   ├── Open_Duck_Mini_Runtime (v2)
│   ├── Open_Duck_Playground (main)
│   └── Open_Duck_reference_motion_generator (main)
│       └── recordings/*.json          5/6 W3-3 生成的参考动作 (10 秒走路轨迹)
├── mujoco-3.3.1/                      原生二进制 + simulate viewer (4/22 装的)
├── my_robot_2/                        OpenDuck V2 全套 STL + robot.xml (用户 4/28 备份)
└── openduck-warmup/                   原始预热项目, 已迁移到 sim/, 保留备份
```

详见 memory `project_existing_wsl_work.md`。

## 常用命令

```bash
# WSL Ubuntu 内: 跑 mujoco viewer (验证 GUI)
cd /mnt/d/CODE/guagua/sim && uv run python -m mujoco.viewer

# WSL viewer 报 X11 fail 的修复 (PowerShell 内执行)
wsl --shutdown                          # 等 8-10 秒后重新进 WSL

# 重建 sim/ 虚拟环境
cd /mnt/d/CODE/guagua/sim && uv sync

# 跑参考动作生成 (W3-3 已做过, 想再生成时用)
cd ~/code/upstream-readonly/Open_Duck_reference_motion_generator
uv run scripts/auto_waddle.py --duck open_duck_mini_v2 --num 1 --output_dir recordings/

# git push (只推 origin, 不动 gitee)
git push origin master
```

**本机开发环境**（参考用，不是要求）：Windows 11 + WSL2 Ubuntu 24.04.2 + Python 3.12.3 + uv 0.11.9 装在 `~/.local/bin/uv`。

## 文档分层（与全局规范一致）

- `docs/`：持久化设计文档（硬件清单、软件架构、决策记录、上游策略、handoff 快照）
- `rpiv/`：过程文件，按 `requirements/ → plans/ → execute*/ → validation/ → archived/` 流转
- 用户说"保存文档"默认指 `docs/`；写代码前必须先走 PRD → plan → execute → validate

## 本仓库的角色边界

`guagua/` 是**应用层**，**不重写**上游的硬件设计或底层运动控制。本仓库自己写：

- 性格 / 交互风格（拟人化设定）
- 用户关系建模（陌生 → 熟悉的演化）
- 对话 / 视觉 / 动作的高层调度
- 与用户其他工具链整合（NeuroMem / aixue 等）

底层依赖通过 `vendor/` submodule 复用上游（M2 决策门后加）。任何"是不是该改硬件参数 / 重写电机控制"的冲动，先确认能否在上游或应用层解决。

## 接口边界（红线，5/5 锁定）

```
LLM (System 2) → MCP 工具调用 → [guagua 应用层契约] → Skill Layer (本地 Python) → 7 维 command → RL 50Hz ONNX → 14 ST3215 + 2 SG90
```

**guagua 真正交付物 = MCP 工具集 + JSON Schema + 表情关键帧 YAML + 性格 system prompt** —— 不是调度引擎，不是控制器。

**禁止**（违反就回到"重新训练 sim2real"地狱）：
- ❌ 应用层代码直接产 7 维 command 数字
- ❌ 修改 50Hz RL 控制循环
- ❌ 修改 / 重训 ONNX 权重
- ❌ 在 Pi 3B+ 上跑 LLM 推理（在 Mac Studio / 云端跑）

详情见 memory `project_contracts.md` + [`docs/openduckmini-knowledge-from-share-2026-05-04.md`](docs/openduckmini-knowledge-from-share-2026-05-04.md)。

## System 2 演进路径（不跳级）

System 2 走 4 个子阶段，与 System 1 (M0-M6) 正交：

- **S0** 跑通整机：装机后用爱折腾出厂 py-xiaozhi → xiaozhi.me 后端，整套不动 ← M3 到货后做
- **S1** 自家优化 v1：替换 MCP 工具集为自家版本（人格 / 表情 / 人文动作风格），后端仍用虾哥
- **S2** 自家优化 v2：切到自建 xiaozhi-esp32-server + 自家 DeepSeek/Qwen API key
- **S3+** 本地大脑：Mac Mini 本地 LLM + NeuroMemory 集成

每一步都有可工作版本。**禁止跳过 S0 直接做"自家完整版"**。详情见 memory `project_strategy.md`。

## 仍要避免的假设

- **vendor/ 仍不存在**：M2 决策门后才加 submodule，M1 期间用 `~/code/upstream-readonly/` 只读
- **不要凭记忆给上游仓库 URL**：用 `gh search repos --owner=apirrone duck` 现查
- **主控是 Pi 3B+ 不是 Pi Zero 2W**：上游文档/教程多假设 Pi Zero 2W，引用时换算
- **教程类任务非阻塞**：用户偏好遇到问题再查文档，不要列 P0 验收门（详见 memory `feedback_doc_reading_not_blocker`）
- **每个阶段完成主动互动确认理解**：不要默默推下一步，先总结 + 用 AskUserQuestion 检查（详见 memory `feedback_interactive_understanding_check`）
