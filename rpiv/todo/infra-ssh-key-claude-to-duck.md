---
title: "配 SSH key 让 Claude Code 直接 SSH 鸭子（不再复制粘贴中转）"
type: todo
status: open
priority: high
created_at: 2026-05-10T22:45:00
updated_at: 2026-05-10T22:45:00
---

# 配 SSH key 让 Claude Code 直接操作鸭子

## 背景（2026-05-10 晚 S0 收工时用户问起）

> 当前我从这个 Claude Code 上面不能直接通过 SSH 去操作我的呱呱吗？

**现状回答**：不能。Claude Code 的 Bash 工具**无 stdin**——`ssh raspios@192.168.3.166` 弹密码提示时无人输入，命令挂起直到超时。所以整个 5/10 S0 调试会话里，每一条鸭子端命令都靠"PC 复制单行 → 用户切到鸭子 SSH 终端粘贴 → 输出回贴对话"中转，至少 50% 会话时间被这个摩擦消耗。

## 目标

配 SSH key 实现 PC（含 Claude Code）→ 鸭子无密码 SSH，让 Claude Bash 工具能直接：

```
ssh raspios@192.168.3.166 'cat /etc/resolv.conf'
ssh raspios@192.168.3.166 'systemctl status systemd-networkd'
```

—— 拿到输出立即处理，对话流不再需要复制粘贴。

## 工作量

**一次性 5 分钟**，分 3 步：

1. **PC 端检查/生成 key**（如果 `~/.ssh/id_ed25519.pub` 已存在，跳过）
   ```
   ssh-keygen -t ed25519 -C "claude-code-pc-to-duck" -f ~/.ssh/id_ed25519
   ```
2. **复制 pub key 到鸭子的 authorized_keys**（这一步**仍需要用户输入一次密码 raspios**，因为第一次登录才能写）
   - PowerShell 没有原生 ssh-copy-id，可以用：
     ```
     Get-Content ~/.ssh/id_ed25519.pub | ssh raspios@192.168.3.166 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
     ```
3. **PC 端验证无密码 SSH**：
   ```
   ssh raspios@192.168.3.166 'echo OK; hostname'
   ```
   返回 `OK / OPENDUCKMINI-V108` 即成功

## 收益

| 场景 | 配 key 前 | 配 key 后 |
|------|----------|----------|
| S0 路线图 #5-#10（剩余 6 步，每步多条命令） | 每条命令复制粘贴中转 | Claude 直接执行 + 解析 |
| M3+ 调试 / M4 sim2real / 真机日志读取 | 同上 | 同上 |
| S1 自家 MCP 开发期 | 高频代码部署 + 服务重启 | rsync + ssh remote restart 一气呵成 |
| 紧急排查（如鸭子卡死） | 用户得切终端跑诊断 | Claude 直接拉 journal |

**对今天剩余 S0 工作的影响最大**——拆 ESP32 + xiaozhi.me 注册 + ESP32 配网期间，Claude 可以并行做鸭子端的 mcp_point.sh 配置 / start_mcp 启动 / 实时日志监控等，而不是等用户回贴输出。

## 触发时机

**强烈推荐：下次会话开头先做这个再继续 S0**。S0 路线图剩余 #5-#10 步全部受益。

不要拖到 S0 收尾——拖了等于把红利浪费在最不需要的阶段（调试已经收尾时）。

## 跟其它 todo 的关系

- **`infra-cloudflare-tunnel-pc-duck.md`**：Cloudflare Tunnel 解决"远程可达性"（LAN IP 漂移 / 离家访问），SSH key 解决"操作无摩擦"。**SSH key 是 Tunnel 的前置**——Tunnel 拉起后还是要 ssh，没 key 一样卡密码。**先做 SSH key，后做 Tunnel**。

## 注意事项

- key 文件不要 push 到 git（`~/.ssh/id_ed25519` 是私钥，永远本地）
- 鸭子端 `~/.ssh/authorized_keys` 权限必须 600，目录 700，否则 sshd 拒绝认证
- 鸭子 LAN IP 192.168.3.166 是 DHCP，万一漂移到新 IP，key 仍有效（key 绑用户不绑 IP），只需用新 IP ssh
- 配置完毕后**可选**禁用密码登录（`/etc/ssh/sshd_config` 设 `PasswordAuthentication no`），但**强烈建议留密码登录**作为兜底（SSH key 文件丢了就完蛋）
