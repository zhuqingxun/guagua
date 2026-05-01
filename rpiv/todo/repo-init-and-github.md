---
title: Git 初始化 + GitHub Public 仓库创建 + Gitee 镜像 remote
type: todo
status: open
created_at: 2026-05-01
updated_at: 2026-05-01
priority: high
blocking: 后续所有 commit / PR / submodule 操作
---

# 仓库初始化

## 待办

- [ ] `cd D:/CODE/guagua && git init -b master`
- [ ] 首次 commit（README + .gitignore + docs + rpiv 骨架 + CLAUDE.md + memory 链接）
- [ ] `gh repo create zhuqingxun/guagua --public --source=. --description="桌面级双足陪伴机器人"`（需用户授权）
- [ ] `git remote add origin git@github.com:zhuqingxun/guagua.git`
- [ ] `git remote add gitee git@gitee.com:sean515/guagua.git`（仅 add，不 push）
- [ ] `git push -u origin master`
- [ ] 在 sync-gitee.ps1 配置中确认 guagua 已纳入扫描

## 红线

- ❌ 禁止 `git push gitee`，由 `D:/CODE/OS/tools/sync-gitee.ps1` 每日 13:30 自动镜像
- ❌ submodule 暂不添加（用户已决定空仓启动）

## 验收

- GitHub 上 `zhuqingxun/guagua` 仓库可访问，public 可见性
- `git remote -v` 同时显示 origin 和 gitee
- sync-gitee.ps1 下次运行（13:30）后 Gitee 端能看到 commit
