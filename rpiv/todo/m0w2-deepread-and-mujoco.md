---
title: M0-W2 sim/ 骨架 + 教程深读 + M0 交付文档（10h）
type: todo
status: open
priority: high
created_at: 2026-05-05T18:00:00
updated_at: 2026-05-05T18:00:00
milestone: M0-W2
time_estimate: 10h
related_files:
  - rpiv/plans/plan-m0.md
  - rpiv/todo/m0w1-dev-env.md
---

# M0-W2：sim/ 骨架 + 深读 + 交付（10h）

> 对应 `rpiv/plans/plan-m0.md` §5 W2 任务表。前置：W1 P0 全部完成。
>
> W2 末是 M0 验收门，过门后进入 M1（参考动作 + 仿真加载）。

## 任务清单（按依赖排序）

### 先做：项目骨架（2h）— W2-1（其余任务依赖）

- [ ] **[P0] W2-1 创建 `sim/` 子目录 + uv 项目骨架（1.5h）**
  - 目录结构：
    ```
    sim/
    ├── pyproject.toml       # uv 项目，依赖 mujoco / wandb / hydra-core / numpy
    ├── README.md            # sim/ 用途 + 如何启动
    ├── .python-version      # 3.11 (上游 Open_Duck_Playground 推荐)
    ├── scripts/
    │   └── verify_mujoco.py # M0 验收用：装好后跑这个，输出 mujoco/numpy 版本
    └── .gitignore           # 忽略 .venv/ wandb/ outputs/ checkpoints/
    ```
  - `cd /mnt/d/CODE/guagua/sim && uv init && uv add mujoco wandb hydra-core numpy`
  - 写 `scripts/verify_mujoco.py`（5-10 行：import + 加载默认 humanoid model + 打印基本信息）
  - **验收**：`cd sim && uv run scripts/verify_mujoco.py` 输出 mujoco 版本 + humanoid nq/nv 维度

- [ ] **[P0] 把 sim/ 和 .gitignore 关系处理好（顺手 0.5h）**
  - 检查根 `.gitignore` 已含 `**/.venv/` `**/__pycache__/` `**/wandb/` `**/outputs/`
  - sim/ 自己加 `sim/.gitignore` 处理 hydra `outputs/` `multirun/` 默认目录
  - **验收**：`git status` 在 sim/ 内只看到代码文件，无 venv/缓存

### 并行段（5h）— W2-2 + W2-3（教程深读）

> W2-2 和 W2-3 不互相依赖，建议在不同晚上分别推进（保持注意力）

- [ ] **[P0] W2-2 ncnynl 重点章节深读（3h）**
  - 重点 4 章（W1 通读后筛选）：
    - 「系统安装 / Pi OS」
    - 「仿真环境 MuJoCo + Playground」
    - 「训练 PPO / reward」
    - 「sim2real / 标定」
  - 每章节深读 + 笔记入 `docs/m0-handoff-notes.md`（W2-5 写）
  - **验收**：4 章节笔记草稿就绪（可先散记，W2-5 再整合）

- [ ] **[P0] W2-3 Frank Fu reward 设计 + RL 算法章节深读（2h）**
  - 重点：reward 函数公式（imitation reward / linear velocity reward / orientation reward / smoothness penalty）
  - 与 `docs/openduckmini-knowledge-from-share-2026-05-04.md` §2.5 imitation_phase 段做交叉对照
  - 笔记入 `docs/m0-handoff-notes.md`
  - **验收**：reward 公式抄 1 遍 + 与 share 文档的相互印证关系笔记好

### 验证段（1h）— W2-4

- [ ] **[P1] W2-4 W&B 跑 1 次完整 hello world 训练曲线（1h）**
  - 在 `sim/` 项目下用 PyTorch 跑 MNIST mini（5 epoch），W&B log loss + acc
  - 目的：验证 sim/ 项目下 wandb 集成路径无误，为 M2 真实训练打基础
  - **验收**：W&B `guagua-sim-hello` project 能看到 5 epoch 的两条曲线

### 收尾段（2.5h）— W2-5 + W2-6

- [ ] **[P0] W2-5 写 `docs/m0-handoff-notes.md`（2h）**
  - 结构：
    1. M0 概览（实际工时 vs 预算 / 完成项 / 跳过项）
    2. 待验证问题表（≥ 10 条，分类：硬件 / 仿真 / 训练 / sim2real / 部署）
    3. 上游"最小可跑配置"摘要（apirrone 4 仓库各自的 README 关键命令汇总）
    4. 教程要点（ncnynl 4 章节 + Frank Fu reward 章节）
    5. M1 起步建议（基于 M0 学到的，给 M1 plan 提供输入）
  - **验收**：文件 commit 入 git；问题清单 ≥ 10 条

- [ ] **[P0] W2-6 M0 复盘 + plan-m1.md 草稿（0.5h）**
  - 在 `rpiv/plans/plan-m0.md` §10 追加复盘段：
    - 实际工时 vs 20h 预算
    - 最大坑（环境/教程/账号 哪一类最耗）
    - 给 M1 的节奏调整建议
  - 起 `rpiv/plans/plan-m1.md` 草稿（frontmatter + §1 目标，不要求完整 plan，让 M1 第一周 session 接手细化）
  - **验收**：复盘段已写；plan-m1.md 已 commit（status: pending）

## W2 验收门（周日晚 = M0 验收门）

参考 `rpiv/plans/plan-m0.md` §6：

- [ ] WSL2 + MuJoCo viewer 通过（W1 已过则继承）
- [ ] 上游 4 仓库 fork 完成（W1）
- [ ] W&B 至少 1 条曲线（W1 hello + W2-4 训练）
- [ ] Discord onboarding 完成（W1）
- [ ] ncnynl 27 篇全通读 + Frank Fu + 子豪兄全过（W1）
- [ ] `docs/m0-handoff-notes.md` 含 ≥ 10 条问题（W2-5）
- [ ] `sim/` 子目录已建 + `uv run` 可启动（W2-1）
- [ ] 累计 M0 耗时 ≤ 25h（20h 预算 + 25% buffer）

8 项全过 → 本 todo 状态改 `completed`，PRD frontmatter `status` 维持 `in-progress` 等待 M1 推进；起 `m1w1-*.md` todo
任一项不过 → 触发 PRD §7.1 M0 决策门处理

## 红线（W2 期间）

- ❌ 不 add submodule（M2 决策门后才加）
- ❌ 不写自己的 RL 训练代码（M2 任务）
- ❌ 不下硬件订单
- ❌ M0 验收门未过禁止跳级到 M1

## 与 plan-m0 的对应

W2 任务 1:1 对应 plan-m0.md §5 W2-1 ~ W2-6。
