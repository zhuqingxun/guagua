# 呱呱 Guagua

基于 [OpenDuck Mini](https://github.com/apirrone/Open_Duck_Mini) 的桌面级双足陪伴机器人。

原型来自 Antoine Pirrone (Pollen Robotics) 的开源 BDX 复刻项目，呱呱在其硬件基础上叠加自定义应用层（性格、交互、与用户的关系建模）。

## 项目结构

```
guagua/
├── docs/          # 持久化设计文档（硬件清单、软件架构、决策记录、卖家聊天 OCR、知识沉淀）
├── rpiv/          # 过程文件（PRD、计划、验证报告、待办）
├── sim/           # Python 仿真/训练子项目（uv 管理：mujoco + wandb）
└── vendor/        # 上游 OpenDuck submodule（M2 决策门后才加，目前用 ~/code/upstream-readonly/ 只读）
```

## 上游依赖

通过 git submodule 引入 [Antoine Pirrone](https://github.com/apirrone) 的 4 个 OpenDuck 项目仓库（Mini / Runtime / Playground / motion_generator）。M1 期间用 `~/code/upstream-readonly/` 临时只读阅读，M2 决策门通过后正式加 submodule。

## 状态

阶段 A 进行中：**M0 装工具看上游 ✅ 完成**，**M1 搬上游 demo 🚧 W3-1/2/3 完成**（2026-05-06），等爱折腾整机 5/8-10 到货后启动 M3。

## 开发流程

遵循 RPIV 四阶段：需求 → 计划 → 实施 → 验证。详见全局 `~/.claude/CLAUDE.md` + 本项目 `CLAUDE.md`。
