# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目当前阶段

**2026-05-01 启动期，仓库尚未 `git init`，无代码、无 vendor/ submodule。** 任何"build / test / run"命令都不适用——别凭模板假设已有 Python 包或 firmware 工程。

接续工作的会话**第一件事**应当读 `docs/handoff-2026-05-01-kickoff.md`，里面记录了：
- 项目身份（呱呱 = 桌面级双足陪伴机器人，OpenDuck Mini 应用层）
- **已做出的决策**（远端策略、目录布局、上游引入方式，不要重新讨论）
- **未决问题**（submodule 范围、GitHub 可见性、claude.ai 思考导入），必须用 AskUserQuestion 与用户确认

## 上游硬件原型是 multi-repo 生态，不是单仓库

OpenDuck Mini 由 Antoine Pirrone (Pollen Robotics) 主导，活跃仓库分散在 4 个：

| 仓库 | 角色 | 是否必装 |
|------|------|---------|
| `apirrone/Open_Duck_Mini` | 硬件设计 (机械/电子/BOM) | 主仓库，必装 |
| `apirrone/Open_Duck_Mini_Runtime` | 实机控制运行时 | 想动起来必装 |
| `apirrone/Open_Duck_Playground` | Mujoco RL 仿真训练 | 自训策略才需要 |
| `apirrone/Open_Duck_reference_motion_generator` | 参考动作生成器 | 自定义动作才需要 |

GitHub **没有独立的 v2 仓库**，v2 是主仓库内部的迭代——不要去搜 `Open_Duck_Mini_v2`。

引入方式：`git submodule add` 到 `vendor/<repo>`，跟随上游升级独立，避免 fork 同步成本。**submodule 范围用户尚未拍板，未确认前禁止 `git submodule add`**。

## 远端策略（红线）

- **只 push GitHub `origin`**（`git@github.com:zhuqingxun/guagua.git`）
- Gitee remote 仅 `git remote add gitee` 注册，**禁止主动 `git push gitee`**——由 `D:/CODE/OS/tools/sync-gitee.ps1` 每日 13:30 自动镜像
- 上一会话已踩过这条红线被用户纠正，不要重蹈

## 文档分层（与全局规范一致）

- `docs/`：持久化设计文档（硬件清单、软件架构、决策记录、上游策略、handoff 快照）
- `rpiv/`：过程文件，按 `requirements/ → plans/ → execute*/ → validation/ → archived/` 流转，与全局 CLAUDE.md 的 RPIV 工作流对齐
- 用户说"保存文档"默认指 `docs/`；写代码前必须先走 PRD → plan → execute → validate，不跳阶段

## 本仓库的角色边界

`guagua/` 是**应用层**，**不重写**上游的硬件设计或底层运动控制。本仓库自己写：
- 性格/交互风格（拟人化设定）
- 用户关系建模（陌生 → 熟悉的演化）
- 对话/视觉/动作的高层调度
- 与用户其他工具链整合（NeuroMem / aixue 等）

底层依赖统一通过 `vendor/` submodule 复用上游。任何"是不是该改硬件参数 / 重写电机控制"的冲动，先确认是否能在上游或应用层解决。

## 接口边界（红线，2026-05-05 锁定）

guagua 应用层与底层 / 上层之间的接口栈是三层：

```
LLM (System 2) → MCP 工具调用 → [guagua 应用层契约] → Skill Layer (本地 Python) → 7 维 command → RL 50Hz ONNX → 14 ST3215 + 2 SG90
```

**guagua 的真正交付物 = MCP 工具集 + JSON Schema + 表情关键帧 YAML + 性格 system prompt**——不是调度引擎，不是控制器。

**禁止**（违反就会回到"重新训练 sim2real"地狱）：
- ❌ 应用层代码直接产 7 维 command 数字
- ❌ 修改 50Hz RL 控制循环
- ❌ 修改/重训 ONNX 权重
- ❌ 在 Pi Zero 2W 上跑 LLM 推理

详情见 memory `project_contracts.md` 和 `docs/openduckmini-knowledge-from-share-2026-05-04.md`。

## System 2 演进路径（不跳级）

System 2 走 4 个子阶段：

- **S0** 跑通整机：装机后直接用爱折腾出厂的 py-xiaozhi → xiaozhi.me 后端，整套不动
- **S1** 自家优化 v1：替换 MCP 工具集为自家版本（人格 / 表情 / 人文动作风格），后端仍用虾哥
- **S2** 自家优化 v2：切到自建 xiaozhi-esp32-server + 自家 DeepSeek/Qwen API key
- **S3+** 本地大脑：Mac Mini 本地 LLM + NeuroMemory 集成

每一步都有可工作版本。**禁止跳过 S0 直接做"自家完整版"**——会陷入装配 + 软件双线调试。详情见 memory `project_strategy.md`。

## 不要假设的事

- 不要假设已有 `pyproject.toml` / `package.json` / `platformio.ini`——项目还没代码
- 不要凭记忆写上游仓库 URL，用 `gh search repos --owner=apirrone duck` 现查（上游可能改名/迁移）
- 不要假设 `vendor/` 已存在
- 不要假设有 `.git/`——切过来第一次操作前用 `git status` 确认
