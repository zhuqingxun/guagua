---
description: "Plan: M0 仿真工具链 + 教程预读 (5/5 完成, 实际 ~3h vs 预算 20h)"
status: archived
created_at: 2026-05-05T18:00:00
updated_at: 2026-05-14T22:49:19
archived_at: 2026-05-14T22:49:19
related_files:
  - rpiv/requirements/prd-stage-a.md
  - rpiv/todo/m0w1-dev-env.md
  - rpiv/todo/m0w2-deepread-and-mujoco.md
  - rpiv/plans/plan-m1.md
  - docs/openduckmini-knowledge-from-share-2026-05-04.md
  - docs/m0-handoff-notes.md
  - docs/seller-chat-aizheteng.md
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
| W1-3 | OpenDuck Mini Discord onboarding + self-intro | 0.5h | P0→放弃 | ⛔ 5/5 用户放弃 | 用户曾尝试注册未成功；PRD 列为"卡 > 2 周时求助"非必备渠道；替代用 ncnynl 微信群 + 上游 GitHub Issue |
| W1-4 | WSL2 + uv | 0.5h | P0 | ✅ 5/5 已完成 | uv 0.11.9 装在 `~/.local/bin/uv`（WSL Ubuntu 24.04.2 + Python 3.12.3） |
| W1-5 | MuJoCo 装好 + viewer 跑通 | 1.5h | P0 | ✅ 5/5 完整通过 | (a) `~/mujoco-3.3.1/bin/simulate` 跑过 humanoid/car/mug；(b) `sim/scripts/verify_mujoco.py` 通过；(c) **5/5 22:30 viewer GUI 弹窗验证通过**（WSLg 半启动状态，`wsl --shutdown` 重启后 X11 socket 起来，截图为证）|
| W1-6 | ncnynl 27 篇 | 4h | **P2 按需** | ✅ 5/5 用户已基本完成 | 用户告知主要文件已读；按 memory `feedback_doc_reading_not_blocker`，"问题清单 ≥ 5 条"硬指标已废除 |
| W1-7 | Frank Fu 中文博客 | 1.5h | **P2 按需** | ✅ 5/5 用户已读完 | 用户告知 Frank Fu 已读完（含 W2-3 reward 章节）；遇到具体问题时回查 |
| W1-8 | 子豪兄 B 站视频 BV1hxZnYfEjo | 1h | **P2 按需** | ⏳ 非阻塞 | 心理预期参考，看不看不影响 W1 过门 |

**W1 状态汇总（5/5 最终版，应用「文档不阻塞」原则）**：
- ✅ P0 全过：W1-1 / W1-2 / W1-4 / W1-5
- ✅ P2 教程类（按需，不卡阻塞）：W1-6 ncnynl 已基本完成 / W1-7 Frank Fu 已读完 / W1-8 子豪兄随时看
- ⛔ 放弃：W1-3 Discord（注册未成功，非必备）

**W1 已彻底过门**，m0w1-dev-env.md status `completed`。剩余 viewer GUI 5min 手动验证滚到 W2。

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
| W2-2 | ncnynl 重点章节深读 | 3h | **P2 按需** | ✅ 已基本完成 | 按 memory `feedback_doc_reading_not_blocker`，不阻塞；M2 训练遇问题时回查具体章节 |
| W2-3 | Frank Fu reward + RL 章节 | 2h | **P2 按需** | ✅ 用户已读完 | 与 W1-7 同源，已读完；遇 reward 不收敛时回查 |
| W2-4 | W&B 跑 1 次真训练曲线（PyTorch MNIST 等）| 1h | **P2 deferred** | ⏸️ 推迟到 M2 | W&B 集成已被 W1-1 hello_wandb.py 100 步假数据曲线证明可用；M2 PPO 真训练时自然过门，不在 M0 重复验证 |
| W2-5 | 写 `docs/m0-handoff-notes.md` 交付文档 | 2h | P0 | ⏳ | 文件 commit 入 git；含上游"最小可跑配置"+ Pi 3B+ 改造影响 + M1 起步建议；问题清单移除硬指标，按需收 |
| W2-6 | M0 复盘 + plan-m1.md 草稿 | 0.5h | P0 | ⏳ | 复盘段 + plan-m1.md commit |

**W2 总工时（5/5 修订）**：P0 = 4h（W2-1 已完成 1.5h + W2-5 写交付 2h + W2-6 复盘 0.5h）/ P1 = 1h（W2-4 真训练）/ P2 教程按需不卡（W2-2/W2-3 已基本完成）/ **剩余约 3.5h**

### 5.1 W2 内部依赖

```
W2-1 (sim/ 骨架) ──→ W2-4 (W&B 训练验证可放此项目下)
W2-2, W2-3        (相互独立，可并行)
W2-2, W2-3, W2-1 ──→ W2-5 (交付文档基于全部输入)
W2-5             ──→ W2-6 (复盘基于交付文档)
```

## 6. M0 验收门（W2 末必过，5/5 修订移除文档阅读硬指标）

**P0 阻塞门**（应用 memory `feedback_doc_reading_not_blocker`）：
- ✅ WSL2 内 MuJoCo 模块 OK（viewer GUI 弹窗手动验证 5min 即可）
- ✅ 上游 4 仓库已 fork 到 `zhuqingxun/`
- ✅ W&B dashboard 至少 1 条曲线（含 W1-1 + W2-4 真训练）
- ✅ `sim/` 子目录已建 + uv 项目可 sync + verify_mujoco.py 通过
- ✅ `docs/m0-handoff-notes.md` 已 commit（含上游"最小可跑配置"+ Pi 3B+ 改造影响 + M1 起步建议；问题清单不设硬指标，按需收）
- ✅ 累计耗时 ≤ 25h（M0 预算 20h + 25% buffer）

**P2 不卡阻塞**（按需，已废除"全部通读"硬指标）：
- ⛔ Discord 不强求（5/5 用户放弃）
- 📚 ncnynl / Frank Fu / 子豪兄 = 参考资源，遇问题回查

任一 P0 不过 → 阶段 A PRD §7.1 M0 决策门处理（最严重情形：止损退出，已沉没成本仅 ≤ 25h + ¥0）。

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| WSL2 MuJoCo OpenGL 渲染失败（headless 服务器/WSL 老版本）| 中 | 中 | fallback 到 `mujoco.MjData()` + matplotlib 截图，不强求 viewer GUI |
| `/mnt/d/...` 跨文件系统 IO 慢导致 uv sync 卡 | 低 | 低 | M0 阶段 sync 不频繁；若卡则改 `~/code/guagua-sim/` 临时位置（不影响 W1 验收） |
| ncnynl 27 篇阅读时间被低估 | ⛔ 已消除 | - | 5/5 改非阻塞（memory `feedback_doc_reading_not_blocker`），不再当 P0 看 |
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

## 10. M0 复盘（5/5 W2 完成追加）

### 10.1 实际工时 vs 预算
- 预算 20h（W1+W2）；实际 ~3h
- **节省 17h**，主要来源：用户 4/22-5/3 已有大量预热工作 + 教程类硬指标移除 + W2-4 deferred

### 10.2 最大坑（按耗时排序）
1. **未先核查 WSL 已有工作**（违反 multi-system-debugging.md 反模式 1）→ 第一波准备从零装环境，用户 2 次纠正后才扫到 ~/openduck-warmup 等。**已写入 memory project_existing_wsl_work**
2. **PRD 写作时假设上游 Pi Zero 2W**（5/2 写）→ 5/5 实购发现爱折腾全部离开 Pi Zero 2W（甚至"标准版"PI52G 也是 Pi 5）→ PRD 大改三轮（公开 vs 私下 SKU / 商品 id 1009166204772 vs 946801761316 / 主控影响 sim2real 链路）
3. **教程通读硬指标**（W1-6 问题清单 ≥ 5 / W2-2 章节深读 P0）违反用户工作偏好 → **已写入 memory feedback_doc_reading_not_blocker**
4. **WSLg 半启动**（X11 socket 缺失但 DISPLAY 已设）→ 第一时间没识别根因，险些往 GLFW 库出问题方向调；最后 `wsl --shutdown` 修复

### 10.3 给 M1 的节奏调整建议
- **M1 节奏可放松**：M0 节省 17h 滚 M1，但不强求吃掉，留给 M3+ 硬件期 buffer
- **M1 不要重复 M0 错**：装新东西前先 `wsl -d Ubuntu -- ls ~/`（项目 memory 已记录）
- **M1 第一周建议先做参考动作生成器**（依赖 Placo IK，最大风险点）→ 若卡 > 2 周触发求助
- **M1 期间硬件到货**（5/8-5/10）：可平行开 M3 开箱跑爱折腾出厂 py-xiaozhi → xiaozhi.me（System 2 S0 起点），不阻塞 sim 主线

详见 `rpiv/plans/plan-m1.md`。

## 11. W1-5 viewer GUI 手动验证（5/5 ✅ 通过）

5/5 22:30 用户在 WSL 内跑 `cd /mnt/d/CODE/guagua/sim && uv run python -m mujoco.viewer`，首次出现 `X11: Failed to open display :0` GLFW 错误。

**根因诊断**：WSLg 半启动状态——`/mnt/wslg/` 目录已挂载，`DISPLAY=:0 WAYLAND_DISPLAY=wayland-0` 已设，但 `/tmp/.X11-unix/` 空（无 X0 socket），weston compositor + Xwayland 进程都没起。

**修复**：PowerShell 跑 `wsl --shutdown` → 等 8 秒 → 重新进 WSL → 重跑 viewer 命令 → MuJoCo 3.8.0 GLFW 窗口正常弹出（File / Option / Simulation / History 面板齐全）。

**M0 经验沉淀**：WSLg 偶尔会半启动（DISPLAY/WAYLAND env 设了但 X11 socket 未创建），`wsl --shutdown` 完全重启 WSL VM 是经典修复。详见 `docs/m0-handoff-notes.md` §踩坑。
