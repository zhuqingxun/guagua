---
title: "PC ↔ 呱呱（鸭子 Pi 3B+）建立 Cloudflare Tunnel 持久通道"
type: todo
status: open
priority: medium
created_at: 2026-05-10T22:35:00
updated_at: 2026-05-10T22:35:00
---

# PC ↔ 鸭子 Cloudflare Tunnel 持久通道

## 用户原话（2026-05-10 晚 S0 收工时）

> 后面要模仿 All-in-One 项目当中 PC 和手机 Termux 建立的通道，也要跟这个呱呱项目建立一个通道，使用 Cloudflare 的 Tunnel。

## 目标

让 PC（D:\CODE\guagua 主开发机）跟鸭子 Pi 3B+ 之间有一条**不依赖家庭 LAN IP** 的稳定通道，覆盖以下场景：

- 离家时也能 SSH 到鸭子
- 鸭子上的 web 服务（爱折腾 web 控制 / xiaozhi MCP WebSocket / 未来自家 MCP server）能从外网访问
- 鸭子 LAN IP 变化（DHCP lease 到期、换路由器、切 hotspot）时不需要重新查 IP
- 跟手机端建立同样通道（参考 All-in-One PC↔Termux 模式）

## 参考来源

`D:\ALL-IN-ONE\` 项目的 PC↔手机 Termux 通道实现（具体协议栈待复核——Obsidian vault 走的是 git via Gitee，但用户提到 Cloudflare Tunnel，可能是另一条独立通道，需要查 All-in-One 的 docs/rpiv 看具体方案）。

## 关联红线

- ✅ 域名走 zqxbase.com（已纳入 Port Manager 规范，详见 `D:/CODE/OS/tools/port-manager/ports.yaml`）
- ✅ Cloudflare Tunnel 在中国 LAN 出向稳定，比 SSH 端口转发可靠
- ⚠️ Railway + Cloudflare 自定义域名需 CNAME + TXT 双记录（rules/railway-deploy.md 已沉淀，本 todo 不涉及 Railway，但 Tunnel 关联 DNS 配置可能复用此教训）

## 触发条件

不阻塞 S0 / M1 W4 / M2 推进。建议触发时机（择其一）：

1. S0 整套跑通后（路线图 #10 reboot 验证通过），鸭子开始有真实需要远程访问的服务（xiaozhi MCP server / 自家 MCP server）
2. 用户某次离家想 SSH 鸭子但 LAN IP 不知道时，触发"该上 Tunnel 了"的紧迫感
3. M3 W3 闲暇期主动做（属于基础设施一次性投入，做完受益期长）

## 执行清单（待 plan 阶段细化）

- [ ] 复核 All-in-One 项目里 Cloudflare Tunnel 的具体实现（docs/ 或 rpiv/ 找文档）
- [ ] 鸭子端装 cloudflared（aarch64 deb 包；Pi 3B+ 兼容）
- [ ] Cloudflare 控制台创建 Tunnel + 配置 ingress（SSH / web / MCP WebSocket 三种 service）
- [ ] zqxbase.com 子域名分配（如 duck.zqxbase.com / duck-mcp.zqxbase.com），登记到 Port Manager `ports.yaml`
- [ ] 鸭子端 cloudflared 跑成 systemd 服务（开机自启 + crash restart）
- [ ] PC 端验证 SSH / curl 走 Tunnel 域名通
- [ ] 手机端通道：评估 Termux 直接装 cloudflared 还是走另一种方式（参考 All-in-One 实现）
- [ ] 文档沉淀到 `docs/infra-cloudflare-tunnel-duck.md`（或合并到 OS 项目的全局基础设施 rules）

## Why（决策动机记录）

通道不是为了"现在好用"，是为了"将来减摩擦"：

- S1 自家 MCP server 要暴露给 xiaozhi.me 云端 → 需要稳定公网入口
- S2 自建 xiaozhi-esp32-server 时，鸭子可能要从外网拉镜像 / 推日志
- M5-M6 真机调试时，离家也能远程触发实验
- 拒绝重蹈"每次 LAN IP 变了就抓瞎"的覆辙
