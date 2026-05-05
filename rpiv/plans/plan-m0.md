---
description: "Plan: M0 仿真工具链 + 教程预读 (W1+W2 共 20h)"
status: in-progress
created_at: 2026-05-05T18:00:00
updated_at: 2026-05-05T18:00:00
archived_at: null
related_files:
  - rpiv/requirements/prd-stage-a.md
  - rpiv/todo/m0w1-dev-env.md
  - rpiv/todo/m0w2-deepread-and-mujoco.md
  - docs/openduckmini-knowledge-from-share-2026-05-04.md
---

# M0 Plan：仿真工具链 + 教程预读（20h，W1+W2）

> 对应 PRD §6 M0 章节。M0 是阶段 A「软件先行」期的第一站，零硬件投入，目标是让 WSL2 上 MuJoCo viewer 跑起来 + 教程心中有数 + 上游 4 仓库 fork 完成。
>
> M0 不要求训练任何东西，不要求上游 ONNX 在 MuJoCo 里走起来——那是 M1 的事。

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

| # | 任务 | 工时 | P | 验收 |
|---|------|------|---|------|
| W1-1 | W&B 个人账号注册 + 任意 hello world script 上传 1 条曲线 | 0.5h | P0 | dashboard 能看到曲线 |
| W1-2 | Fork apirrone 4 仓库到 `zhuqingxun/` | 0.5h | P0 | GitHub 个人主页 fork 标识可见 |
| W1-3 | 加入 OpenDuck Mini Discord（https://discord.gg/UtJZsgfQGe）+ self-intro | 0.5h | P0 | Discord 已加入并发送自我介绍 |
| W1-4 | WSL2 Ubuntu 24.04 验证 + uv 装好（系统级） | 0.5h | P0 | `uv --version` 在 WSL2 中正常 |
| W1-5 | MuJoCo 3.x 装好 + viewer 跑通默认场景 | 1.5h | P0 | `python -c "import mujoco; mujoco.viewer.launch()"` 弹窗能看到机器人 |
| W1-6 | ncnynl 27 篇通读首轮（每篇 7-10 min 速览，标记疑问） | 4h | P0 | 全部过完 + 待验证问题清单 ≥ 5 条（手记） |
| W1-7 | Frank Fu 中文博客通读（重点：Python 环境陷阱章节） | 1.5h | P1 | 1 份要点笔记 + 至少 3 条 reward 设计相关问题入清单 |
| W1-8 | 子豪兄 B 站视频 BV1hxZnYfEjo 看完 | 1h | P1 | 看完，记录与 ncnynl 不一致的点 |

**W1 总工时**：P0 = 7.5h / P1 = 2.5h / 合计 10h

### 4.1 W1 内部依赖

```
W1-4 (WSL2/uv) ──→ W1-5 (MuJoCo)
W1-1, W1-2, W1-3, W1-6, W1-7, W1-8  (相互独立)
```

W1-4 → W1-5 是仅有的硬依赖。其他全部并行可启动。

### 4.2 W1 推荐时序（按一周拆 5 个时段）

| 时段 | 任务 | 工时 | 心理负载 |
|------|------|------|---------|
| 周一晚（高能量） | W1-4 + W1-5 | 2h | 装环境，新事多 |
| 周二晚 | W1-1 + W1-2 + W1-3 | 1.5h | 账号操作，机械 |
| 周三晚 | W1-6 (ncnynl 1-10 篇) | 2h | 教程通读 |
| 周四晚 | W1-6 (ncnynl 11-20 篇) + W1-7 上半 | 2h | 教程通读 + Frank Fu 部分 |
| 周末（连续 2.5h） | W1-6 (ncnynl 21-27 篇) + W1-7 下半 + W1-8 | 2.5h | 收尾 + 子豪兄视频 |

## 5. W2 任务表（第 2 周，10h）

| # | 任务 | 工时 | P | 验收 |
|---|------|------|---|------|
| W2-1 | 创建 `sim/` 子目录 + uv 项目骨架（pyproject.toml + .venv + ruff/mypy）| 1.5h | P0 | `cd sim && uv sync` 无错；`uv run python -c "import mujoco; print(mujoco.__version__)"` 输出版本号 |
| W2-2 | ncnynl 重点章节深读：「系统安装」「仿真环境」「训练」「sim2real」 | 3h | P0 | 4 章节笔记入 `docs/m0-handoff-notes.md` |
| W2-3 | Frank Fu reward 设计章节 + RL 算法章节深读 | 2h | P0 | reward 函数公式抄一遍 + 笔记入交付文档 |
| W2-4 | W&B 跑 1 次完整 hello world 训练曲线（用 sklearn / pytorch 任意小例子）| 1h | P1 | dashboard 上有完整 epoch 曲线 |
| W2-5 | 写 `docs/m0-handoff-notes.md`：待验证问题表 + 上游"最小可跑配置"摘要 + 教程要点 | 2h | P0 | 文件 commit 入 git，含 ≥ 10 条问题 + 上游 README 摘要 |
| W2-6 | M0 自我评审 + 决定 M1 起步顺序 | 0.5h | P0 | 在 plan-m0.md 末尾追加「M0 复盘」段落 + 起 plan-m1.md 草稿 |

**W2 总工时**：P0 = 9h / P1 = 1h / 合计 10h

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
