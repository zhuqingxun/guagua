---
title: M0-W1 开发环境 + 教程通读首轮 + 社区准入（10h）
type: todo
status: completed
priority: high
created_at: 2026-05-01
updated_at: 2026-05-05T20:30:00
milestone: M0-W1
time_estimate: 10h（5/5 实际 P0 全过；P1 滚到 W2）
related_files:
  - rpiv/plans/plan-m0.md
  - rpiv/requirements/prd-stage-a.md
  - rpiv/todo/m0w2-deepread-and-mujoco.md
  - sim/README.md
---

# M0-W1：环境 + 通读首轮 + 社区（10h，剩 ~7h）

> 对应 `rpiv/plans/plan-m0.md` §4 W1 任务表。本周完成的具体可勾选清单。
>
> P0 = 必做；P1 = 建议本周做，最迟拖到 W2 上半周。

## 5/5 状态修订（重要）

5/5 摸底发现用户在 WSL 早已做过预热（4/22 ~ 5/3）：
- `~/openduck-warmup/` uv 项目已建 + W&B hello world 已跑
- `~/mujoco-3.3.1/` 二进制 + simulate viewer 跑过 humanoid 等
- `~/my_robot_2/` 含 OpenDuck V2 全套 STL + robot.xml
- GitHub `zhuqingxun/Open_Duck_*` 4 仓库 isFork=true
- 5/5 装好 uv 0.11.9，迁移 warmup 入 `D:/CODE/guagua/sim/`，`uv sync` 通过

**因此 W1-1/W1-2/W1-4/W1-5 实质已完成**，本周剩余只有教程类（W1-6/W1-7/W1-8）+ Discord（W1-3）+ viewer GUI 手动确认。详情见 plan-m0.md §0。

## 任务清单（按推荐时序）

### 5/5 已完成段（无需再做）

- [x] **[P0] W1-4 WSL2 Ubuntu 24.04 + uv ✅ 5/5 完成**
  - WSL Ubuntu 24.04.2 LTS + Python 3.12.3
  - uv 0.11.9 装在 `~/.local/bin/uv`
  - 验证：`wsl -d Ubuntu -- bash -c '~/.local/bin/uv --version'` → `uv 0.11.9 (x86_64-unknown-linux-gnu)`

- [x] **[P0] W1-5 MuJoCo 装好（基础部分）✅ 5/5 完成；viewer GUI 待手动确认**
  - mujoco 3.8.0 在 `D:/CODE/guagua/sim/.venv` 通过 `uv sync`
  - `sim/scripts/verify_mujoco.py` 通过（mujoco 模块 + viewer 模块 importable + 模型 step OK）
  - 早期备用：`~/mujoco-3.3.1/bin/simulate ~/my_robot_2/robot.xml`（5/2 已跑过）
  - **GUI 弹窗手动验证步骤**（剩余 ~5 分钟）：
    ```bash
    cd /mnt/d/CODE/guagua/sim && uv run python -m mujoco.viewer
    ```
    预期 GLFW 窗口弹出可见默认场景 + 鼠标可转视角。失败排查见 plan-m0.md §11

- [x] **[P0] W1-1 W&B 账号 + hello world ✅ 5/3 已完成**
  - openduck-warmup/hello_wandb.py（已迁入 `sim/hello_wandb.py`）
  - wandb run-20260503_003754 dashboard 有数据
  - project 名 `guagua-warmup`（保留，不破坏旧 dashboard）

- [x] **[P0] W1-2 Fork apirrone 4 仓库 ✅ 4/22-30 已完成**
  - GitHub `zhuqingxun/Open_Duck_Mini` `_Runtime` `_Playground` `_reference_motion_generator`
  - 全部 `isFork: true`（`gh repo view --json isFork` 验证）
  - 默认分支：Mini/Runtime = **v2**（注意不是 main）；Playground/motion = main

### 待做：周二/三/四/末

- [x] **[P0] W1-3 加入 Open Duck Mini Discord（0.5h）⛔ 5/5 用户放弃**
  - 用户曾尝试注册未成功
  - PRD §M0 把 Discord 列为"卡 > 2 周时求助"非必备渠道，不影响后续任务
  - 替代渠道：ncnynl 微信群（购整机后入）+ 上游 GitHub Issue
  - **状态**：abandoned（不再追）

### W1-6 ncnynl 27 篇通读（5/5 用户已基本完成）

- [x] **[P0] W1-6 ncnynl 27 篇通读 ✅ 5/5 用户告知主要文件已读过**
  - 用户原话："这个任务我已经完成差不多了，我主要的文件都已经读过"
  - 接受 partial 完成；待验证问题清单 ≥ 5 不再硬性要求 W1 完成
  - **延后到 W2-2**：W2 重点章节深读（系统安装 / 仿真环境 / 训练 / sim2real）时整理问题清单一并入 `docs/m0-handoff-notes.md`
  - 原 W1-6a/6b/6c 三段细分作废

- [ ] **[P1] W1-7a Frank Fu 中文博客 上半（0.5h）**
  - 入口：https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
  - 重点：Python 环境陷阱章节（与 W1-4/W1-5 验证对照）
  - **验收**：开头到环境章节读完

### 待用户确认：W1-7 Frank Fu / W1-8 子豪兄

- [ ] **[P1] W1-7 Frank Fu 中文博客（1.5h）**
  - 入口：https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
  - 重点：Python 环境陷阱章节 + reward 设计 + RL 算法章节
  - **验收**：全文读完 + 至少 3 条 reward 设计相关问题入清单

- [ ] **[P1] W1-8 子豪兄 B 站视频 BV1hxZnYfEjo 看完（0.5h）**
  - 入口：https://www.bilibili.com/video/BV1hxZnYfEjo/
  - 视频时长 ~30min，1.5x 速看完
  - **验收**：看完，记录与 ncnynl 不一致的点 ≥ 1 条

## W1 验收门（5/5 自检）

- [x] **WSL2 内 MuJoCo 模块 OK**（W1-5 ✅，viewer GUI 待手动确认 ~5min）
- [x] **W&B 个人 dashboard 有 hello world 曲线**（W1-1 ✅，5/3 完成）
- [x] **GitHub 个人主页有 4 个 apirrone fork**（W1-2 ✅，4/22-30 完成）
- [x] **Discord** ⛔ 5/5 用户放弃（W1-3，注册未成功，PRD 列为非必需渠道，不影响进度）
- [x] **ncnynl 27 篇基本通读**（W1-6 ✅，5/5 用户告知主要文件已读，问题清单延后到 W2-2）
- [ ] Frank Fu + 子豪兄通读完（W1-7 + W1-8，P1 待用户确认）

**W1 状态汇总（5/5）**：所有 P0 任务已实质完成（含 Discord 用户主动放弃），W1 验收门已过 5/6 项。可直接转 W2。剩余 P1（Frank Fu + 子豪兄）滚到 W2 处理。

## 红线（W1 期间）

- ❌ 不下任何硬件订单（PRD §2.3 软件先行）
- ❌ 不 `git submodule add` 任何上游仓库（PRD §5.2 M2 决策门后才加；W1 想看上游代码用临时 clone 到 `~/code/upstream-readonly/`）
- ❌ 不在 `D:/CODE/guagua/` 下提交 venv / 大文件（沿用 .gitignore）
- ❌ 不预先优化目录结构（W2-1 才建 `sim/`，W1 不动仓库结构）

## 与 plan-m0 的对应

W1 任务 1:1 对应 `rpiv/plans/plan-m0.md` §4 W1-1 ~ W1-8。验收门以本文件为准（plan 里是计划，本文件是执行 + 勾选）。
