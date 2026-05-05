---
title: M0-W1 开发环境 + 教程通读首轮 + 社区准入（10h）
type: todo
status: in-progress
priority: high
created_at: 2026-05-01
updated_at: 2026-05-05T19:00:00
milestone: M0-W1
time_estimate: 10h（5/5 修订后剩 ~7h）
related_files:
  - rpiv/plans/plan-m0.md
  - rpiv/requirements/prd-stage-a.md
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

- [ ] **[P0] W1-3 加入 Open Duck Mini Discord（0.5h）**
  - https://discord.gg/UtJZsgfQGe
  - 完成 onboarding（接受规则）+ 在 `#introductions` 频道自我介绍（中文/英文均可，提及 hobbyist 背景 + 在跟 ncnynl 教程）
  - **验收**：自我介绍消息已发出

### 周三晚（教程通读 part 1，2h）— W1-6 上半

- [ ] **[P0] W1-6a ncnynl 27 篇通读 第 1-10 篇（2h）**
  - 入口：https://www.ncnynl.com/
  - 速览每篇 7-10 min，重点：每篇标题 + 核心结论 + 图表
  - 在本地（**不入 git**，PRD §M0 标注「手记」）记录笔记，模板：
    ```
    第 N 篇《标题》
    - 核心结论：
    - 与已知冲突点：
    - 待验证问题：
    ```
  - **验收**：第 1-10 篇全部过完，待验证问题清单累计 ≥ 2 条

### 周四晚（教程通读 part 2，2h）— W1-6 下半 + W1-7 上半

- [ ] **[P0] W1-6b ncnynl 27 篇通读 第 11-20 篇（1.5h）**
  - **验收**：累计 20 篇，问题清单 ≥ 4 条

- [ ] **[P1] W1-7a Frank Fu 中文博客 上半（0.5h）**
  - 入口：https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
  - 重点：Python 环境陷阱章节（与 W1-4/W1-5 验证对照）
  - **验收**：开头到环境章节读完

### 周末（连续段，2.5h）— W1-6 收尾 + W1-7 下半 + W1-8

- [ ] **[P0] W1-6c ncnynl 27 篇通读 第 21-27 篇（1h）**
  - **验收**：27 篇全过；待验证问题清单 ≥ 5 条（PRD §M0 硬指标）

- [ ] **[P1] W1-7b Frank Fu 博客 下半（1h）**
  - 重点：reward 设计 + RL 算法章节
  - **验收**：全文读完，记录 ≥ 3 条 reward 设计相关问题入清单

- [ ] **[P1] W1-8 子豪兄 B 站视频 BV1hxZnYfEjo 看完（0.5h）**
  - 入口：https://www.bilibili.com/video/BV1hxZnYfEjo/
  - 视频时长 ~30min，1.5x 速看完
  - **验收**：看完，记录与 ncnynl 不一致的点 ≥ 1 条

## W1 验收门（周日晚自检）

- [x] **WSL2 内 MuJoCo 模块 OK**（W1-5 ✅，viewer GUI 待手动确认 ~5min）
- [x] **W&B 个人 dashboard 有 hello world 曲线**（W1-1 ✅，5/3 完成）
- [x] **GitHub 个人主页有 4 个 apirrone fork**（W1-2 ✅，4/22-30 完成）
- [ ] Discord 已加入 + self-intro（W1-3，待做）
- [ ] ncnynl 27 篇全通读 + 问题清单 ≥ 5（W1-6，待用户确认进度）
- [ ] Frank Fu + 子豪兄通读完（W1-7 + W1-8，待用户确认进度）

P0 全过 → todo 状态改 `completed`，进入 W2（`m0w2-deepread-and-mujoco.md`）
P0 未全过 → 本 todo 保持 `in-progress`，把缺项滚到 W2 同时记录原因

## 红线（W1 期间）

- ❌ 不下任何硬件订单（PRD §2.3 软件先行）
- ❌ 不 `git submodule add` 任何上游仓库（PRD §5.2 M2 决策门后才加；W1 想看上游代码用临时 clone 到 `~/code/upstream-readonly/`）
- ❌ 不在 `D:/CODE/guagua/` 下提交 venv / 大文件（沿用 .gitignore）
- ❌ 不预先优化目录结构（W2-1 才建 `sim/`，W1 不动仓库结构）

## 与 plan-m0 的对应

W1 任务 1:1 对应 `rpiv/plans/plan-m0.md` §4 W1-1 ~ W1-8。验收门以本文件为准（plan 里是计划，本文件是执行 + 勾选）。
