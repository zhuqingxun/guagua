---
title: M0-W2 sim/ 骨架 + 教程深读 + M0 交付文档（5/5 完成）
type: todo
status: completed
priority: high
created_at: 2026-05-05T18:00:00
updated_at: 2026-05-05T22:50:00
milestone: M0-W2
time_estimate: 10h（实际 ~2h，应用「文档不阻塞」+ W2-4 deferred 后剩 P0 = W2-1/W2-5/W2-6 三项）
related_files:
  - rpiv/plans/plan-m0.md
  - rpiv/plans/plan-m1.md
  - rpiv/todo/m0w1-dev-env.md
  - docs/m0-handoff-notes.md
---

# M0-W2：sim/ 骨架 + 深读 + 交付（10h）

> 对应 `rpiv/plans/plan-m0.md` §5 W2 任务表。前置：W1 P0 全部完成。
>
> W2 末是 M0 验收门，过门后进入 M1（参考动作 + 仿真加载）。

## 任务清单（按依赖排序）

### 先做：项目骨架（2h）— W2-1（其余任务依赖）

- [x] **[P0] W2-1 `sim/` 子目录 + uv 项目骨架 ✅ 5/5 已完成**
  - 实际：5/5 迁移自 ~/openduck-warmup（5 文件 cp + 改名 guagua-sim + uv sync 通过 + verify_mujoco.py 通过）
  - 详见 `sim/README.md`

### 教程类（5/5 改非阻塞，按 memory `feedback_doc_reading_not_blocker`）

- [x] **[P2 按需] W2-2 ncnynl 重点章节 ✅ 已基本完成**
  - 用户告知 W1 阶段主要文件已读
  - **不阻塞 M0 过门**；M2 训练 / M3 部署 / M4 sim2real 遇到具体卡点时回查相应章节即可
  - 重点章节备查：「系统安装 / Pi OS」「仿真环境 MuJoCo + Playground」「训练 PPO / reward」「sim2real / 标定」

- [x] **[P2 按需] W2-3 Frank Fu reward 设计 + RL 算法 ✅ 5/5 用户已读完**
  - 用户原话："W2-3 Frank Fu 我已经读完了"
  - **遇到 reward 不收敛 / RL 算法选型问题时回查**
  - 与 `docs/openduckmini-knowledge-from-share-2026-05-04.md` §2.5 imitation_phase 段交叉对照（如需）

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

## W2 验收门（5/5 修订，应用「文档不阻塞」原则 = M0 验收门）

参考 `rpiv/plans/plan-m0.md` §6：

**P0 阻塞门**：
- [x] WSL2 + MuJoCo 模块 OK（W1-5 ✅，viewer GUI 5min 手动验证即可）
- [x] 上游 4 仓库 fork 完成（W1-2 ✅）
- [ ] W&B 至少 1 条曲线（W1-1 hello ✅ + W2-4 真训练）
- [x] `sim/` 子目录已建 + `uv run` 可启动（W2-1 ✅）
- [ ] `docs/m0-handoff-notes.md` 已 commit（W2-5；问题清单不设硬指标，按需收）
- [ ] 累计 M0 耗时 ≤ 25h（20h 预算 + 25% buffer）

**P2 不卡阻塞**（按 memory `feedback_doc_reading_not_blocker`）：
- [x] ncnynl 已基本读 + Frank Fu 已读完（W1-6 + W1-7 ✅）
- [ ] 子豪兄随时看（W1-8）
- [ ] M0 复盘 + plan-m1.md 草稿（W2-6）

**已废除**：
- ⛔ Discord onboarding 硬指标（W1-3，5/5 用户放弃）
- ⛔ "ncnynl 27 篇全通读 + Frank Fu + 子豪兄全过" 硬指标（5/5 改非阻塞）

P0 全过 + W2-4/W2-5/W2-6 完成 → 本 todo 状态改 `completed`，PRD frontmatter `status` 维持 `in-progress` 等待 M1 推进；起 `m1w1-*.md` todo
任一 P0 不过 → 触发 PRD §7.1 M0 决策门处理

## 红线（W2 期间）

- ❌ 不 add submodule（M2 决策门后才加）
- ❌ 不写自己的 RL 训练代码（M2 任务）
- ❌ 不下硬件订单
- ❌ M0 验收门未过禁止跳级到 M1

## 与 plan-m0 的对应

W2 任务 1:1 对应 plan-m0.md §5 W2-1 ~ W2-6。
