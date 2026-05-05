---
description: "Plan: M0 仿真工具链 + 教程预读 (W1+W2 共 20h) - 5/5 修订对齐 WSL 已有工作"
status: in-progress
created_at: 2026-05-05T18:00:00
updated_at: 2026-05-05T19:00:00
archived_at: null
related_files:
  - rpiv/requirements/prd-stage-a.md
  - rpiv/todo/m0w1-dev-env.md
  - rpiv/todo/m0w2-deepread-and-mujoco.md
  - docs/openduckmini-knowledge-from-share-2026-05-04.md
  - sim/README.md
---

# M0 Plan：仿真工具链 + 教程预读（20h，W1+W2）

> 对应 PRD §6 M0 章节。M0 是阶段 A「软件先行」期的第一站，零硬件投入，目标是让 WSL2 上 MuJoCo viewer 跑起来 + 教程心中有数 + 上游 4 仓库 fork 完成。
>
> M0 不要求训练任何东西，不要求上游 ONNX 在 MuJoCo 里走起来——那是 M1 的事。

## 0. 与既有工作的衔接（5/5 修订）

PRD 起草时假设从零开始；5/5 摸底发现用户在 WSL 里早已做过预热（4/22 ~ 5/3）：

| 既有 | 内容 | 影响的 plan-m0 任务 |
|------|------|---------------------|
| `~/mujoco-3.3.1/` | MuJoCo 原生二进制 + simulate viewer，bash history 跑过 humanoid/car/mug | W1-5 viewer 实质 ✅ |
| `~/openduck-warmup/` | uv 项目，pyproject 含 mujoco>=3.8.0 + wandb>=0.26.1，hello_wandb.py 已写并跑过实验 | W1-1/W1-5/W2-1 实质 ✅ |
| `~/my_robot_2/` | OpenDuck Mini V2 全套 STL mesh + robot.xml | M1 加载 V2 URDF 部分 ✅ |
| `~/my_robot/` | 4/22-25 早期实验，含 robot.urdf + compile 脚本 | 备查 |
| GitHub `zhuqingxun/Open_Duck_Mini` `_Runtime` `_Playground` `_reference_motion_generator` | 4 仓库全部 isFork=true（默认分支 Mini/Runtime=v2, Playground/motion=main）| W1-2 ✅ |
| `~/uv` 顶层目录 | 历史装 uv 残留（5/5 重新装为 0.11.9 in `~/.local/bin/uv`） | W1-4 ✅ |

**已完成迁移**：`~/openduck-warmup` 5 个核心文件（pyproject/uv.lock/.python-version/.gitignore/hello_wandb.py）已 cp 入 `D:/CODE/guagua/sim/`，pyproject [project].name 改为 `guagua-sim`，`uv sync` 重建 `.venv` 并验证（mujoco 3.8.0 + wandb 0.26.1）。原目录保留作备份。

**因此**：W1 真正剩余的工作主要是教程通读（W1-6/W1-7/W1-8）+ Discord 加群（W1-3）+ viewer GUI 手动看一眼。

## 1. M0 总体目标

| 维度 | 目标 |
|------|------|
| 工具链 | WSL2 Ubuntu 24.04 + uv + MuJoCo 3.x viewer 跑起来 |
| 教程认知 | ncnynl 27 篇通读 1 轮 + Frank Fu 精读 + 子豪兄看完，待验证问题清单 ≥ 5 |
| 社区准入 | OpenDuck Discord onboarding + ncnynl 微信群（购买后才入，本阶段先加 Discord）|
| 工具账号 | W&B 个人账号 + hello world dashboard |
| 上游仓库 | apirrone 4 仓库全部 fork 到 zhuqingxun |
| 硬件 | 零投入（PRD 「软件先行」原则） |
| 交付物 | `docs/m0-handoff-notes.md`：待验证问题表 + 上游"最小可跑配置"摘要 + 教程要点 |

## 2. 范围与边界

### 2.1 IN（M0 必做）
- 软件环境装配（WSL2/uv/MuJoCo）
- 教程通读 + 笔记
- 账号 + 社区 + Fork
- M0 交付文档（落 `docs/m0-handoff-notes.md`）

### 2.2 OUT（M0 不做，留给 M1）
- ❌ 不加 `vendor/` submodule（PRD §5.2 锁 M2 决策门后才加；M0 想看上游代码用 `git clone` 到 `~/code/upstream-readonly/` 临时目录只读阅读）
- ❌ 不跑上游 `Open_Duck_Playground` 训练（M1 任务）
- ❌ 不跑上游预训练 ONNX 推理（M1 任务）
- ❌ 不写自己的 RL 训练代码（M2 任务）
- ❌ 不下任何硬件订单（PRD §2.3「软件先行」原则）

## 3. 工作目录与代码位置（已确认）

- **仿真/训练代码工作目录**：WSL2 内挂载 `/mnt/d/CODE/guagua/`，所有 Python 项目（uv 虚拟环境 + 仿真脚本）放在 `D:/CODE/guagua/sim/`（W2 创建），跨 Win/WSL 同一 git 仓库
- **跨文件系统性能**：`/mnt/d/...` 比 WSL ext4 慢 5-10 倍，但 M0-M2 阶段 sim 训练只在 PC 上跑短任务，可接受；若 M2 训练耗时不可忍，再迁移到 `~/code/`
- **uv 虚拟环境**：`D:/CODE/guagua/sim/.venv`（uv 默认），不加入 git（已在 .gitignore）
- **临时只读 clone**（M0-M2 阅读上游代码用，不入 git）：`~/code/upstream-readonly/`
- **vendor/ submodule**：M2 决策门通过后才执行 `git submodule add`，M0 不动

## 4. W1 任务表（第 1 周，10h）

> 优先级：P0 必须本周完成；P1 建议本周完成，最迟拖到 W2 上半周

| # | 任务 | 工时 | P | 状态 | 验收 / 依据 |
|---|------|------|---|------|------|
| W1-1 | W&B 账号 + hello world | 0.5h | P0 | ✅ 5/3 已完成 | `~/openduck-warmup/hello_wandb.py` + `wandb/run-20260503_003754` 实验记录 |
| W1-2 | Fork apirrone 4 仓库 | 0.5h | P0 | ✅ 4/22-30 已完成 | `gh repo view zhuqingxun/Open_Duck_*` 4/4 isFork=true |
| W1-3 | OpenDuck Mini Discord onboarding + self-intro | 0.5h | P0 | ⏳ 待用户确认 | https://discord.gg/UtJZsgfQGe |
| W1-4 | WSL2 + uv | 0.5h | P0 | ✅ 5/5 已完成 | uv 0.11.9 装在 `~/.local/bin/uv`（WSL Ubuntu 24.04.2 + Python 3.12.3） |
| W1-5 | MuJoCo 装好 + viewer 跑通 | 1.5h | P0 | ✅ 多源已完成 | (a) `~/mujoco-3.3.1/bin/simulate` 跑过 humanoid/car/mug；(b) `sim/scripts/verify_mujoco.py` 通过（mujoco 3.8.0 + viewer 模块 importable + step OK）；GUI 弹窗手动验证见 §11 |
| W1-6 | ncnynl 27 篇通读首轮 + 问题清单 ≥ 5 | 4h | P0 | ⏳ 待用户确认 | 是否已读 / 进度多少 |
| W1-7 | Frank Fu 中文博客通读 | 1.5h | P1 | ⏳ 待用户确认 | 是否已读 |
| W1-8 | 子豪兄 B 站视频 BV1hxZnYfEjo | 1h | P1 | ⏳ 待用户确认 | 是否已看 |

**W1 状态汇总（5/5）**：
- 实质已完成：W1-1 / W1-2 / W1-4 / W1-5（基础部分）= 3h 等价工时
- 待用户确认：W1-3 / W1-6 / W1-7 / W1-8 = 7h 等价工时

如果 W1-6/W1-7/W1-8 教程也已读，则 W1 整体已完成 90%，本周可直接转 W2 收尾 + 提前进 M1。

### 4.1 W1 剩余推荐时序（按状态压缩）

5/5 已完成 W1-1/W1-2/W1-4/W1-5 后，本周剩余只需推教程类 + Discord：

| 时段 | 任务 | 工时 |
|------|------|------|
| 任选一晚 | W1-3 Discord onboarding | 0.5h |
| 周三晚 | W1-6a ncnynl 1-13 篇 | 2h |
| 周四晚 | W1-6b ncnynl 14-27 篇 + W1-7 上半 | 2.5h |
| 周末（连续 2h） | W1-7 下半 + W1-8 | 2h |

**剩余总工时 ~7h**。如果用户已部分读过教程，进一步压缩。

## 5. W2 任务表（第 2 周，10h）

| # | 任务 | 工时 | P | 状态 | 验收 / 依据 |
|---|------|------|---|------|------|
| W2-1 | `sim/` 子目录 + uv 项目骨架 | 1.5h | P0 | ✅ 5/5 已完成 | 迁移自 ~/openduck-warmup（5 文件），改名 guagua-sim，`uv sync` 通过，`verify_mujoco.py` 通过 |
| W2-2 | ncnynl 重点章节深读 4 章节 | 3h | P0 | ⏳ 视 W1-6 状态 | 4 章节笔记入 `docs/m0-handoff-notes.md` |
| W2-3 | Frank Fu reward + RL 章节深读 | 2h | P0 | ⏳ 视 W1-7 状态 | reward 函数公式抄一遍 + 笔记入交付文档 |
| W2-4 | W&B 跑 1 次真训练曲线（PyTorch MNIST 等）| 1h | P1 | ⏳ | dashboard 完整 epoch 曲线（W1-1 是 fake data 100 步，W2-4 要真训练） |
| W2-5 | 写 `docs/m0-handoff-notes.md` 交付文档 | 2h | P0 | ⏳ | 文件 commit 入 git，含 ≥ 10 条问题 + 上游 README 摘要 |
| W2-6 | M0 复盘 + plan-m1.md 草稿 | 0.5h | P0 | ⏳ | 复盘段 + plan-m1.md commit |

**W2 总工时**：P0 = 9h / P1 = 1h / 合计 10h（其中 W2-1 已完成 1.5h，剩 8.5h）

### 5.1 W2 内部依赖

```
W2-1 (sim/ 骨架) ──→ W2-4 (W&B 训练验证可放此项目下)
W2-2, W2-3        (相互独立，可并行)
W2-2, W2-3, W2-1 ──→ W2-5 (交付文档基于全部输入)
W2-5             ──→ W2-6 (复盘基于交付文档)
```

## 6. M0 验收门（W2 末必过）

- ✅ WSL2 内 MuJoCo viewer 能弹窗显示默认场景
- ✅ 上游 4 仓库已 fork 到 `zhuqingxun/`
- ✅ W&B dashboard 至少 1 条曲线
- ✅ Discord 已加入
- ✅ ncnynl 27 篇 + Frank Fu + 子豪兄全部通读
- ✅ `docs/m0-handoff-notes.md` 已 commit，含 ≥ 10 条待验证问题
- ✅ `sim/` 子目录已建 + uv 项目可 sync
- ✅ 累计耗时 ≤ 25h（M0 预算 20h + 25% buffer）

任一项不过 → 阶段 A PRD §7.1 M0 决策门处理（最严重情形：止损退出，已沉没成本仅 ≤ 25h + ¥0）。

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| WSL2 MuJoCo OpenGL 渲染失败（headless 服务器/WSL 老版本）| 中 | 中 | fallback 到 `mujoco.MjData()` + matplotlib 截图，不强求 viewer GUI |
| `/mnt/d/...` 跨文件系统 IO 慢导致 uv sync 卡 | 低 | 低 | M0 阶段 sync 不频繁；若卡则改 `~/code/guagua-sim/` 临时位置（不影响 W1 验收） |
| ncnynl 27 篇阅读时间被低估（实际 > 4h） | 高 | 中 | W1 P1 任务（Frank Fu/子豪兄）允许拖到 W2，先保 P0 ncnynl 通读 |
| MateBook Pro 内存 < 16GB 导致 MuJoCo viewer 卡顿 | 低 | 低 | 默认场景体量小不卡；M2 训练阶段才需要 GPU 加速，M0 不触发 |
| W&B 在国内访问慢/被墙 | 中 | 低 | 用户已搭科学上网，记录是否需要切 SSL fingerprint；alt: tensorboard 兜底 |

## 8. 交付物清单

W2 末，以下文件应入 git：

- `rpiv/plans/plan-m0.md`（本文件，W2-6 后追加复盘段）
- `rpiv/todo/m0w1-dev-env.md`（W1 完成后 status → completed）
- `rpiv/todo/m0w2-deepread-and-mujoco.md`（W2 完成后 status → completed）
- `docs/m0-handoff-notes.md`（M0 知识沉淀，输入 M1）
- `sim/pyproject.toml` + `sim/README.md`（uv 项目骨架）
- `rpiv/plans/plan-m1.md`（M1 起步草稿，由 W2-6 起）

## 9. M0 → M1 衔接

M1 任务（参考 PRD §M1，第 3-4 周 20h）将基于 M0 输出：

- M1 起步依赖 `sim/` 目录已就绪（W2-1）
- M1 第一步是把 `Open_Duck_reference_motion_generator` 和 `Open_Duck_Playground` clone 到 `~/code/upstream-readonly/` 后挑选脚本入 `sim/`（**仍不加 submodule**，等 M2 决策门）
- M1 不要再走 ncnynl 通读，重点章节直接定位

M1 plan 在 W2-6 起草初稿（不要求完成，初稿是为了让 M0 末尾对 M1 心中有数）。

## 10. M0 复盘（W2 末追加）

> 待 W2 完成后追加：实际工时 vs 预算、最大坑、下周 M1 节奏调整。

## 11. W1-5 viewer GUI 手动验证步骤（用户操作）

`verify_mujoco.py` 验证了 mujoco 模块层 OK，**但 viewer 弹窗 GUI 是否真能在 WSLg 下显示，需要用户手动跑一次确认**：

```bash
# WSL Ubuntu 内
cd /mnt/d/CODE/guagua/sim
uv run python -m mujoco.viewer
```

**预期**：弹出 GLFW 窗口，看到 mujoco 的默认场景（一个 humanoid 或空场景），可用鼠标转视角。

**失败排查**：
- WSLg 不支持：检查 `echo $DISPLAY`（应该是 `:0`）和 `echo $WAYLAND_DISPLAY`（应该是 `wayland-0`）
- 黑屏 / GLX 错误：试 `LIBGL_ALWAYS_INDIRECT=0 uv run python -m mujoco.viewer`
- fallback：用 `~/mujoco-3.3.1/bin/simulate ~/my_robot_2/robot.xml` 代替（用户 5/2 已验证可跑），不强求 Python viewer

确认后回写 W1-5 状态从「✅ 基础部分」升级为「✅ 完整通过」。
