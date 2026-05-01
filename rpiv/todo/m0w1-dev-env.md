---
title: M0 第1周 开发环境与社区准入
type: todo
status: open
created_at: 2026-05-01
updated_at: 2026-05-01
milestone: M0-W1
time_estimate: 4 小时（约占第1周 10h 的 40%）
---

# M0 第1周 开发环境与社区

主控到货前可以做的"软件侧"备货。

## 待办

- [ ] **注册 Weights & Biases 账号**（个人版免费）
  - 用于阶段A 训练曲线追踪
- [ ] **Fork OpenDuck 上游 4 仓库到 zhuqingxun**
  - `apirrone/Open_Duck_Mini`
  - `apirrone/Open_Duck_Mini_Runtime`
  - `apirrone/Open_Duck_Playground`
  - `apirrone/Open_Duck_reference_motion_generator`
  - 备注：仅 fork 留档，本仓库通过 submodule 直接引上游 master
- [ ] **WSL2 Ubuntu 24.04 安装 MuJoCo 3.x**
  - 已安装 WSL2 → `pip install mujoco`（用 uv 管虚拟环境）
  - 验证：`python -c "import mujoco; mujoco.viewer.launch()"`
- [ ] **加入 Open Duck Mini Discord 社区**
  - https://discord.gg/UtJZsgfQGe
  - 用于卡 > 2 周时求助
- [ ] **通读 Frank Fu 中文博客**（约 2 小时）
  - https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
  - 重点：Python 环境陷阱章节

## 验收标准

- W&B 能跑通 hello world（dashboard 看到一条曲线）
- 4 个 fork 在 GitHub 个人主页可见
- WSL2 中 MuJoCo viewer 能弹窗显示默认场景
- Discord 已 onboarding（自我介绍发完）
- Frank Fu 博客读完一遍，记下 ≥3 个待验证问题
