---
title: "鸭子到 Gitee 的直连 SSH remote 未恢复"
type: todo
status: open
priority: low
created_at: 2026-07-01T23:15:00
updated_at: 2026-07-01T23:15:00
---

# 鸭子到 Gitee 的直连 SSH remote 未恢复

## 任务描述

2026-06-06/07 系统整盘重置后，鸭子上原本注册到 Gitee 账户(sean515)的出站 SSH key（`~/.ssh/id_ed25519_gitee`）连同私钥一起丢失。2026-07-01 部署 `guagua-customizations` 分支时，在鸭子上重新生成了一把新 key，但**没有注册到 Gitee 账户**——当时在 Bitwarden 里搜了 "gitee"/"gitee api"/"gitee token"/"gitee pat" 都只翻到网页登录凭据（含 2FA 恢复码），没有可用于 Gitee API v5 的 personal access token。

最终这次部署改用了 `git bundle` 临时方案（PC 端已有 Gitee 权限 → `git clone --bare` + `git bundle create --all` → `scp` 传到鸭子 → 鸭子本地 `git fetch <bundle文件>` 导入 refs），绕开了这个凭据缺口，效果上是可行的，但鸭子现在**没有自己直接 push 到 Gitee 的能力**。

如果以后要在鸭子上直接改代码、调试后想直接 `git push` 备份到 `gitee.com:sean515/guagua-duck-runtime-vendor.git`，就需要先补上这一步。

## 涉及文件

- 鸭子端：`~/.ssh/id_ed25519_gitee`（已存在，公钥待注册）+ `~/.ssh/config`（需加 `Host gitee.com IdentityFile ...`）
- Gitee 账户 SSH Keys 设置页，或 Gitee API v5 `POST /user/keys`（需要一个有效 PAT）

## 完成标准

- 在 Gitee 网页个人设置里手动生成一个新的 Personal Access Token（登录时用已有的账号密码 + 2FA 恢复码），存入 Bitwarden（命名清楚，比如 "Gitee API Token"，方便下次直接搜到）
- 用该 token 调 Gitee API v5 把鸭子新生成的公钥注册上去，或直接网页手动添加
- 鸭子端 `git remote add origin-gitee git@gitee.com:sean515/guagua-duck-runtime-vendor.git`，`git fetch origin-gitee` 验证连通
- 验证方式：鸭子上跑 `ssh -T git@gitee.com` 返回欢迎信息（不报 Permission denied）

## 备注

优先级低——当前部署/回退能力都不受影响（PC 端的 Gitee 访问权限本来就是主力，bundle 方式虽然多一道手工步骤但完全够用）。只有"鸭子端直接改代码后自助推送备份"这个具体场景需要它，遇到再补。
