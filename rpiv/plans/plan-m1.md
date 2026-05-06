---
description: "Plan: M1 参考动作 + 仿真加载 (W3+W4, 5/6 W3 已部分完成)"
status: in-progress
created_at: 2026-05-05T22:45:00
updated_at: 2026-05-06T00:15:00
archived_at: null
related_files:
  - rpiv/requirements/prd-stage-a.md
  - rpiv/plans/plan-m0.md
  - docs/m0-handoff-notes.md
---

# M1 Plan：参考动作 + 仿真加载（草稿）

> 对应 PRD §6 M1 章节（第 3-4 周 20 小时）。M0 已收尾，本 plan 是起步草稿，M1 第一周 session 接手时细化任务时序。

## 1. M1 总体目标

| 维度 | 目标 |
|------|------|
| 参考动作 | `Open_Duck_reference_motion_generator` 装好 + 生成 ≥ 1 条参考动作（站立/原地踏步/前进任选）|
| 仿真加载 | `Open_Duck_Playground` 装好 + MuJoCo 加载 OpenDuckMini V2 URDF |
| ONNX 部署侧验证 | **用上游预训练 ONNX 在 MuJoCo 中走一遍**（不自训）|
| 硬件 | 零投入（仍按 PRD §2.3 软件先行；硬件已 5/5 下单，M3 到货） |
| 交付 | 仿真录屏 1 段（机器人在 MuJoCo 里走路）+ 笔记 1 份"上游能跑的最小配置" |

## 2. 范围与边界

### 2.1 IN（M1 必做）
- `vendor/` 不加 submodule（PRD §5.2 锁 M2 决策门后才加）—— M1 期间用临时 clone 到 `~/code/upstream-readonly/` 只读阅读
- 上游 4 仓库官方 demo 在自己机器上跑通
- M1 不改 URDF（PRD §M1 明确"禁止改 URDF"）
- M1 不自训策略

### 2.2 OUT（留 M2+）
- ❌ PPO 训练（M2）
- ❌ 改 reward / 改网络结构（M2）
- ❌ ONNX 导出自训模型（M2）
- ❌ 真机部署（M3）

## 3. M1 任务表草稿（W3+W4 共 20h，M0 余 17h 备用 buffer）

> 实际任务时序 / 工时估算待 M1 第一周 session 细化。下表只是结构性骨架。

### W3（第 3 周，10h）：参考动作生成器

| # | 任务 | 工时 | P | 状态 |
|---|------|------|---|------|
| W3-1 | 临时 clone 4 个上游仓库到 `~/code/upstream-readonly/`（Mini/Runtime 默认分支 `v2`）| 0.5h | P0 | ✅ 5/6 完成 |
| W3-2 | `Open_Duck_reference_motion_generator` 装好（Placo IK 依赖）| 3h | P0 | ✅ 5/6 完成（实际 ~10 分钟，Placo 在 PyPI 有 wheel 不需本地编译；踩坑：git-lfs 必装否则 STL 全是 pointer）|
| W3-3 | 生成站立/原地踏步参考动作（脚本输出参考运动数据）| 2h | P0 | ✅ 5/6 完成（生成第一条 .json：500帧 × 0.02s = 10秒走路轨迹，640KB）|
| W3-4 | 笔记：参考运动生成的输入输出格式 / 与 ncnynl 教程对应章节交叉印证 | 1.5h | P2 按需 | ⏳ 按"文档不阻塞"延后 |
| buffer | 应对 Placo IK 装机问题（按 PRD §M1 风险表）| 3h | - | ⛔ 未触发，PRD 高估了风险 |

**W3 实际耗时**：约 30 分钟（vs 预算 10h），节省 9.5h 滚到 W4。

### W4（第 4 周，10h）：仿真加载 + ONNX 部署侧验证

| # | 任务 | 工时 | P |
|---|------|------|---|
| W4-1 | `Open_Duck_Playground` 装好（基于 Brax + JAX，确认 GPU/CPU 模式）| 2h | P0 |
| W4-2 | MuJoCo 加载 OpenDuckMini V2 URDF（用 `~/my_robot_2/robot.xml` 已有备份对照）| 2h | P0 |
| W4-3 | 用上游 `BEST_WALK_ONNX_2.onnx` 在 MuJoCo 中走一遍（部署侧 inference）| 3h | P0 |
| W4-4 | 录屏 1 段 + 写 `docs/m1-handoff-notes.md`：含"上游最小可跑配置"摘要 + M2 起步建议 | 2h | P0 |
| buffer | 应对 ONNX 在 MuJoCo 中行为异常 / Brax 装机问题 | 1h | - |

## 4. 关键依赖与已知信息

### 4.1 来自 M0 / share 文档
- 上游 ONNX 是 77 维 obs → 10 维 action（腿部）+ 4 维头部 command 直传
- imitation_phase 是 2 维（sin/cos 编码）
- 三段历史动作（last/last_last/last_last_last）共 30 维
- Asymmetric Actor-Critic：训练 Critic 用 privileged_state，部署只用 Actor
- 详见 `docs/openduckmini-knowledge-from-share-2026-05-04.md` §2

### 4.2 来自卖家聊天（爱折腾）
- 推理模型 = 官方原版 ONNX 默认配，每台只做参数微调（重心调整）
- 模型外观（STL）变化在 Pi 3B+ 整机版（头灯/主控位置/接线）—— M3 装机后再处理
- 详见 `docs/seller-chat-aizheteng.md`

### 4.3 关键风险
- **Placo IK 装机**：M1 最大可能卡点；若 > 2 周无解，触发 PRD §7.1 决策（求助 Discord/ncnynl 微信群/Issue）
- **MuJoCo 加载 V2 URDF 报错**：URDF/XML 格式兼容问题；可用 `~/my_robot_2/robot.xml` 4/28 已跑通的版本对照
- **上游 ONNX 在 MuJoCo 行为不正确**：可能是版本不匹配 / 输入归一化问题；先确认 MuJoCo 版本与上游 README 一致

## 5. M1 验收门（W4 末必过）

P0 阻塞门：
- [ ] 参考运动生成器至少生成 1 条参考动作
- [ ] MuJoCo 加载 V2 URDF 无报错
- [ ] 上游 ONNX 在 MuJoCo 中机器人能"走起来"（行为合理，不严格要求多稳）
- [ ] 仿真录屏 1 段 + `docs/m1-handoff-notes.md` 已 commit
- [ ] 累计 M0+M1 耗时 ≤ 50h（PRD 原 40h + 25% buffer）

任一 P0 不过 → 触发 PRD §7.1 决策门处理。

## 6. M1 → M2 衔接

M1 通过即进入 M2（自训 PPO + ONNX 导出 + M2 决策门）。M2 决策门是阶段 A 的硬件下单门——但 5/5 用户已先行下单，M2 决策门退化为"判断继续 sim2real vs 改用整机出厂栈"的判断点。

预计 M3（W7-W8）爱折腾整机已到货，M2 末（W6 末）可平行做 S0 出厂栈跑通验证（System 2 演进路径起点）。

## 7. 待 M1 第一周 session 细化的事

- [ ] W3-1 ~ W4-4 工时重估（M0 实际只用 3h，M1 估算可能也偏高）
- [ ] 是否合并 W3-3 + W4-2 到一个会话（参考动作 → URDF 加载 → ONNX walk 一气呵成）
- [ ] M1 期间是否提前装 Pi 3B+ 镜像（M3 提前准备，节省 M3 1-2h）
