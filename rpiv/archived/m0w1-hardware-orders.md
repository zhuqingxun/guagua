---
title: M0 第1周 硬件采购三件套
type: todo
status: archived
created_at: 2026-05-01
updated_at: 2026-05-02T00:18:00
archived_at: 2026-05-02T00:18:00
superseded_by: rpiv/requirements/prd-stage-a.md
milestone: M0-W1
---

# 已被 prd-stage-a.md 取代

原计划在 M0 第 1 周下单三件套（Orin Nano + Bambu A1 + STS3215×16，~¥7100），现按 PRD「软件先行」原则推迟到 M2 决策门后，且选型整体改为爱折腾整机/散件（~¥3900-¥4199）。

具体执行 todo 见 `rpiv/todo/m2-purchase-decision.md`。

---

## 历史记录（仅供追溯，不再执行）

阶段A 关键件下单，交付周期长的优先：
- Jetson Orin Nano 8GB 开发板 ×1 ≈ 3500 元 → 推迟到阶段 B（M7+）
- Bambu Lab A1 3D 打印机 ×1 ≈ 2000 元 → 取消（爱折腾整机含全套 3D 打印件）
- Feetech STS3215 串行总线舵机 ×16 ≈ 1600 元 → 取消（爱折腾整机含 14× 12V 升级舵机）

## Why superseded

调研后发现：
1. 上游 apirrone Open_Duck_Mini_Runtime **只支持 Pi Zero 2W**，Orin Nano 阶段 A 没有现成路径，需要 1-3 周自己摸适配（详见 PRD §11）
2. 国内整机渠道（爱折腾、feisuo、灵犀）全部基于树莓派系，**ncnynl 27 篇深度教程**就是爱折腾自家
3. 软件先行原则：M0-M2 用 6 周验证软件链路能学下来，再下单避免预算+心理双重沉没
4. 爱折腾整机含全套 3D 打印件、舵机、电池、IMU、相机，无需自购打印机（节省 ¥2000）
