# 呱呱项目启动期交接文档

> 日期: 2026-05-01
> 用途: 项目从 `D:/CODE/OS` 会话切换到 `D:/CODE/guagua` 工作空间前的状态快照
> 受众: 接续工作的新 Claude Code 会话 (冷启动后请先读完本文件)

---

## 一、项目身份 (一句话)

**呱呱 (guagua)** 是基于 [OpenDuck Mini](https://github.com/apirrone/Open_Duck_Mini) 硬件的桌面级双足陪伴机器人, 在开源 BDX Droid 复刻硬件之上叠加自定义应用层 (性格 / 交互 / 关系建模)。

| 字段 | 值 |
|------|---|
| 中文名 | 呱呱 |
| 项目代号 / 目录名 | `guagua` |
| 项目根目录 | `D:/CODE/guagua/` |
| 启动日期 | 2026-05-01 |
| 当前阶段 | 硬件预研 / 仓库初始化前夜 |

**命名理由备查**: 中文叠字带"小、亲昵"语义场 (类比 团团/豆豆/毛毛); 拼音 `guagua` 作为目录名避免 Unicode 路径在 Windows / Docker / git remote 中的兼容隐患; 不撞 R2/D2 系列梗 (那是另一个项目 OpenClaw 的命名空间)。

---

## 二、上游硬件原型 (OpenDuck Mini 生态)

由 Antoine Pirrone (Pollen Robotics R&D 工程师) 主导的开源项目, **不是单一仓库, 是 multi-repo 生态**, 拆成 4 个活跃仓库:

| 仓库 | 角色 | 最近更新 | 重要度 |
|------|------|----------|--------|
| [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini) | 硬件设计 (机械 / 电子 / BOM) | 2026-04-30 | 主仓库, 必装 |
| [`apirrone/Open_Duck_Mini_Runtime`](https://github.com/apirrone/Open_Duck_Mini_Runtime) | 实机控制运行时 (电机 / 传感器) | 2026-04-30 | 想动起来必装 |
| [`apirrone/Open_Duck_Playground`](https://github.com/apirrone/Open_Duck_Playground) | Mujoco RL 仿真训练环境 | 2026-04-22 | 训练自定义策略才需要 |
| [`apirrone/Open_Duck_reference_motion_generator`](https://github.com/apirrone/Open_Duck_reference_motion_generator) | 参考动作生成器 | 2026-04-16 | 自定义动作才需要 |
| `apirrone/duck_gym` | 旧 RL 环境 | 2024-09 (停更) | 跳过 |

**关于 v1 vs v2**: GitHub 上**没有独立的 v2 仓库**, V2 是主仓库 `Open_Duck_Mini` 内的迭代。无需选择版本, 用主仓库即可拿到最新进展。

---

## 三、本仓库的定位

`guagua/` 是**应用层**, 不重写硬件设计、不重写底层运动控制。在上游硬件 + Runtime 之上叠加:
- 呱呱的"性格" / 交互风格 (拟人化设定)
- 与用户的关系建模 (从陌生到熟悉的演化)
- 对话 / 视觉 / 动作的高层调度
- 与用户其他工具链的整合 (NeuroMem / aixue 等)

上游通过 `git submodule` 引入到 `vendor/`, 跟随上游升级独立, 避免 fork 同步痛苦。

---

## 四、已做出的决策 (新会话不要再问)

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 项目位置 | `D:/CODE/guagua/` | 与既有项目同层, `sync-gitee.ps1` 会自动扫描 |
| 起步方式 | 全新空仓库 + 上游作 git submodule | 保持升级独立性, 避免 fork 同步成本 |
| 主推流 | GitHub `origin` | 用户日常工作主战场 |
| Gitee 镜像 | 仅 `git remote add gitee`, **不直接 push** | 由 `D:/CODE/OS/tools/sync-gitee.ps1` 每日 13:30 自动镜像 |
| 项目治理 | RPIV 四阶段流程 (需求 → 计划 → 实施 → 验证) | 与全局 `~/.claude/CLAUDE.md` 对齐 |
| 文档分类 | `docs/` 持久化 / `rpiv/` 过程文件 | 与既有项目惯例一致 |

---

## 五、未决问题 (新会话需要先决策)

### 5.1 submodule 范围 (优先级最高)

| 选项 | 内容 | 适用场景 |
|------|------|---------|
| **推荐** | Mini + Runtime | 让呱呱物理动起来的最小集合 |
| 完整 | Mini + Runtime + Playground + motion_generator | 计划训练自定义 RL 策略 |
| 极简 | 仅 Mini | 自己重写控制代码, 不依赖上游 Runtime |
| 延后 | 先空仓库启动 | 暂时不确定深度, 先 commit 基础文件 |

用户在前一会话中**未做最终选择**, 切到 guagua 目录后请先用 `AskUserQuestion` 确认。

### 5.2 GitHub 仓库可见性

public 还是 private? 用户既有项目混合存在 (zqxbase 是 public, evo-neo 是 private)。需问。

### 5.3 Web 端机器人思考交接

用户在 claude.ai 网页端有"关于做机器人的思考"对话, 计划:
1. 在 web 端让 Claude 输出"交接 Markdown" (压缩对话精华)
2. 复制粘贴或导出, 落到 `D:/CODE/guagua/docs/robot-thinking-handoff.md`
3. 在新会话中读取后开始 PRD / plan

**当前状态**: 未导入。新会话可主动询问用户是否准备好导入。

---

## 六、当前文件状态 (磁盘上的实际内容)

```
D:/CODE/guagua/
├── README.md                                    ✅ 中文, 简介 + 项目结构
├── .gitignore                                   ✅ Python + 嵌入式 + ML 通用模板
├── docs/
│   └── handoff-2026-05-01-kickoff.md           ✅ 本文件
└── rpiv/
    ├── requirements/                            (空)
    ├── plans/                                   (空)
    ├── todo/                                    (空)
    ├── validation/                              (空)
    └── archived/                                (空)
```

**待生成**:
- [ ] `CLAUDE.md` (项目本地指引, 建议在切到 guagua 目录后基于实际代码结构再写, 避免空写)
- [ ] `.git/` (git 仓库初始化)
- [ ] `vendor/` 子目录 (待 submodule 范围决策后创建)

---

## 七、新会话启动指引

### 7.1 切换到 guagua 目录的具体动作

1. 打开新的终端窗口, `cd D:/CODE/guagua/`
2. 启动 Claude Code: `claude` (或用 `D:/CODE/OS/tools/start-claude.ps1`)
3. 在新会话中第一条 prompt 推荐:

   ```
   读 docs/handoff-2026-05-01-kickoff.md 了解项目上下文。
   我现在准备做: [具体动作, 例如 "git init + 加 submodule" / "导入 claude.ai 的机器人思考" / "写 CLAUDE.md"]
   ```

### 7.2 新会话需要立刻做的健康检查

- `git status` 确认 `.git/` 是否已存在 (初次切过去时应不存在)
- `ls vendor/` 确认 submodule 是否已初始化
- 读 `docs/handoff-2026-05-01-kickoff.md` 的"五、未决问题"

### 7.3 新会话的红线 (必须遵守)

1. **远端只 push GitHub**: 违反会触发用户纠正 (前一会话已踩过)
2. **不要 `git submodule add` 任何 URL 未经确认**: submodule 范围还没定
3. **不要凭记忆给 OpenDuck 仓库 URL**: 用 `gh search repos --owner=apirrone duck` 重新核对, 上游可能改名 / 迁移
4. **写代码前先走 RPIV**: PRD → plan → execute → validate, 不跳阶段
5. **遵守全局 CLAUDE.md**: Python 用 `uv run`, PowerShell 写 .ps1 文件, 中文回复, 等等

---

## 八、关键命令速查

```bash
# 切到项目根
cd D:/CODE/guagua/

# 初始化 git (确认未做之后再跑)
git init -b master

# 加 GitHub 远端 (用户名 zhuqingxun, SSH 已配)
git remote add origin git@github.com:zhuqingxun/guagua.git

# 加 Gitee 镜像远端 (仅注册, 不主动 push, 用户名 sean515)
git remote add gitee git@gitee.com:sean515/guagua.git

# submodule 添加示例 (待用户确认范围后执行)
mkdir -p vendor
git submodule add https://github.com/apirrone/Open_Duck_Mini vendor/Open_Duck_Mini
git submodule add https://github.com/apirrone/Open_Duck_Mini_Runtime vendor/Open_Duck_Mini_Runtime

# 查看上游最近活跃度
gh search repos --owner=apirrone duck --limit 20 --json name,description,url,updatedAt
```

---

## 九、参考资料

- 上游主仓库: https://github.com/apirrone/Open_Duck_Mini
- 上游作者: [Antoine Pirrone](https://github.com/apirrone) (Pollen Robotics R&D)
- 用户全局规范: `~/.claude/CLAUDE.md`
- Gitee 自动同步脚本: `D:/CODE/OS/tools/sync-gitee.ps1` (每日 13:30 计划任务)
- RPIV 工作流文档: `D:/CODE/OS/docs/development-workflow.md`

---

> **写给未来的我**: 这是呱呱出生的那一天。先把名字、定位、上游生态、远端策略钉死, 剩下的按 RPIV 一步步来。不急。
