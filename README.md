# 呱呱 Guagua

基于 [OpenDuck Mini](https://github.com/apirrone/Open_Duck_Mini) 的桌面级双足陪伴机器人。

原型来自 Antoine Pirrone (Pollen Robotics) 的开源 BDX 复刻项目，呱呱在其硬件基础上叠加自定义应用层（性格、交互、与用户的关系建模）。

## 项目结构

```
guagua/
├── docs/          # 持久化设计文档（硬件清单、软件架构、决策记录）
├── rpiv/          # 过程文件（PRD、计划、验证报告、待办）
└── vendor/        # 上游 OpenDuck Mini 子模块（git submodule，待初始化）
```

## 上游依赖

通过 git submodule 引入 [Antoine Pirrone](https://github.com/apirrone) 的 OpenDuck 项目仓库。具体子模块范围在仓库初始化时确定，参见 `docs/upstream-strategy.md`。

## 状态

项目刚启动（2026-05-01），处于硬件预研阶段。

## 开发流程

遵循 RPIV 四阶段：需求 → 计划 → 实施 → 验证。详见全局 `~/.claude/CLAUDE.md`。
