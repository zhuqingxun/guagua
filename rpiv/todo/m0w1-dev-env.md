---
title: M0-W1 开发环境 + 教程通读首轮 + 社区准入（10h）
type: todo
status: open
priority: high
created_at: 2026-05-01
updated_at: 2026-05-05T18:00:00
milestone: M0-W1
time_estimate: 10h
related_files:
  - rpiv/plans/plan-m0.md
  - rpiv/requirements/prd-stage-a.md
---

# M0-W1：环境 + 通读首轮 + 社区（10h）

> 对应 `rpiv/plans/plan-m0.md` §4 W1 任务表。本周完成的具体可勾选清单。
>
> P0 = 必做；P1 = 建议本周做，最迟拖到 W2 上半周。

## 任务清单（按推荐时序）

### 周一晚（高能量段，2h）— W1-4 + W1-5

- [ ] **[P0] W1-4 WSL2 Ubuntu 24.04 + uv 验证（0.5h）**
  - WSL2 已在用户 PC 上配好（全局 CLAUDE.md 已注明）
  - 命令：`wsl -d Ubuntu -- bash -c 'uname -a && cat /etc/os-release | head -3'`
  - 在 WSL 内装 uv：`curl -LsSf https://astral.sh/uv/install.sh | sh`（已装则跳过）
  - **验收**：`wsl -d Ubuntu -- bash -c 'uv --version'` 输出版本号

- [ ] **[P0] W1-5 MuJoCo 3.x 装好 + viewer 跑通（1.5h）**
  - 在 WSL2 内 `cd /mnt/d/CODE/guagua/`（确认能 cd 进去；M0 不在此处建项目，下周 W2-1 才建 sim/）
  - 临时验证用：`uv run --with mujoco python -c "import mujoco; print(mujoco.__version__)"`
  - viewer 验证：`uv run --with mujoco python -m mujoco.viewer`（GUI 弹窗能看到默认 humanoid 场景）
  - WSLg 默认能跑 GUI；若失败按 plan-m0.md §7 风险表 fallback 到 matplotlib 截图模式
  - **验收**：viewer 弹窗可见 humanoid，能用鼠标转视角

### 周二晚（账号机械操作，1.5h）— W1-1 + W1-2 + W1-3

- [ ] **[P0] W1-1 W&B 个人账号 + hello world（0.5h）**
  - 注册：https://wandb.ai/authorize
  - 装 SDK：`uv run --with wandb python -c "import wandb; wandb.init(project='guagua-hello'); wandb.log({'loss': 0.1}); wandb.finish()"`
  - **验收**：dashboard 能看到 `guagua-hello` project + 1 条 loss 曲线

- [ ] **[P0] W1-2 Fork apirrone 4 仓库到 zhuqingxun（0.5h）**
  - 用 `gh` CLI 批量 fork（已认证）：
    ```bash
    gh repo fork apirrone/Open_Duck_Mini --clone=false
    gh repo fork apirrone/Open_Duck_Mini_Runtime --clone=false
    gh repo fork apirrone/Open_Duck_Playground --clone=false
    gh repo fork apirrone/Open_Duck_reference_motion_generator --clone=false
    ```
  - **验收**：`gh repo list zhuqingxun --limit 10` 看到 4 个 fork
  - **不 add submodule**：PRD §5.2 锁 M2 决策门后才加

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

- [ ] WSL2 内 MuJoCo viewer 能跑（W1-5 ✅）
- [ ] W&B 个人 dashboard 有 hello world 曲线（W1-1 ✅）
- [ ] GitHub 个人主页有 4 个 apirrone fork（W1-2 ✅）
- [ ] Discord 已加入 + self-intro（W1-3 ✅）
- [ ] ncnynl 27 篇全通读 + 问题清单 ≥ 5（W1-6 ✅）
- [ ] Frank Fu + 子豪兄通读完（W1-7 + W1-8，P1 允许拖到 W2 上半周）

P0 全过 → todo 状态改 `completed`，进入 W2（`m0w2-deepread-and-mujoco.md`）
P0 未全过 → 本 todo 保持 `in-progress`，把缺项滚到 W2 同时记录原因

## 红线（W1 期间）

- ❌ 不下任何硬件订单（PRD §2.3 软件先行）
- ❌ 不 `git submodule add` 任何上游仓库（PRD §5.2 M2 决策门后才加；W1 想看上游代码用临时 clone 到 `~/code/upstream-readonly/`）
- ❌ 不在 `D:/CODE/guagua/` 下提交 venv / 大文件（沿用 .gitignore）
- ❌ 不预先优化目录结构（W2-1 才建 `sim/`，W1 不动仓库结构）

## 与 plan-m0 的对应

W1 任务 1:1 对应 `rpiv/plans/plan-m0.md` §4 W1-1 ~ W1-8。验收门以本文件为准（plan 里是计划，本文件是执行 + 勾选）。
