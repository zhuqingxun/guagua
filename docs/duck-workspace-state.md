# Duck Workspace 状态索引

> **作用**: 鸭子 (Pi 3B+, `192.168.3.166`) 上 `~/open_duck_mini_ws/` 三个 sub-repos 的 git 状态 manifest。跨会话/机器恢复时**只读此文件**就能拿到所有 baseline / customization branch / remote / patch 列表。
>
> **维护规则**: 每次对鸭子上任何 sub-repo 做了影响 git history 的操作 (新 commit / 新分支 / 新 remote / 新 patch),回到 PC 后必须 Edit 此文件同步。
>
> **创建于**: 2026-05-23 (S0 通关后,#10 reboot 自启准备阶段)

---

## 三个 Sub-Repos 总览

| 路径 | 上游 | 当前默认分支 | 状态 | guagua 自定义状态 |
|---|---|---|---|---|
| `~/open_duck_mini_ws/mcp-openduck/` | gitee.com/ncnynl/mcp-openduck | `master` (HEAD `3fa9fd5`) | clean | 无 patch (mcp_point.sh 被 .gitignore 排除) |
| `~/open_duck_mini_ws/Open_Duck_Mini/` | github.com/apirrone/Open_Duck_Mini | `v2` (HEAD `cc4a2d4`) | clean | 无 patch |
| `~/open_duck_mini_ws/Open_Duck_Mini_Runtime/` | github.com/apirrone/Open_Duck_Mini_Runtime | `v2` (HEAD `34c60ef`) | **5/23 baseline 化** | 见下方 §1 |

---

## §1. Open_Duck_Mini_Runtime (主要 customization 入口)

### Remotes

| 名 | URL | 用途 |
|---|---|---|
| `origin` | https://github.com/apirrone/Open_Duck_Mini_Runtime | upstream (爱折腾 fork 自此, **只 fetch**, 不 push) |
| `origin-gitee` | git@gitee.com:sean515/guagua-duck-runtime-vendor.git | **✅ 备份 push 目标** (2026-05-23 19:55 部署). 私有仓库, 两个分支 (`vendor-baseline-2026-05-23` + `guagua-customizations`) 均已 push. 鸭子端 `~/.ssh/id_ed25519_gitee` ed25519 SSH key 已加到 Gitee 账户 (sean515) |

### Branches

| 分支 | HEAD 标识 | 含义 |
|---|---|---|
| `v2` | upstream tracking (`34c60ef antennas test`) | 别用,留作 upstream sync 参考 |
| `vendor-baseline-2026-05-23` | `0671b96` snapshot: 爱折腾出厂态 (2026-05-23) | 永久 baseline,**禁止改**。81 files 一次性 commit (含全部 53 dirty + 28 untracked)。任何回归测试以此为对照 |
| `guagua-customizations` (HEAD) | `26c4cc6` fix(ps4_controller): PS4Controller 修两个 hotplug v1 残留 bug (vendor 第 5+6 bug) | **生产用此分支**,start_duck_mcp.sh / systemd unit 跑的是这个 checkout |

### Patch 列表 (guagua-customizations 分支上, 按 git log 顺序倒序)

| Commit | 日期 | 作用 | Diff 副本 |
|---|---|---|---|
| `26c4cc6` fix(ps4_controller): 两 hotplug v1 残留 bug | 2026-05-26 | **修 vendor 第 5+6 bug, 完整闭合 hotplug v2**: (1) 第 5 bug `obs dim concat → ONNX InvalidArgument crash`: `PS4Controller.__init__` `self.last_commands = [0.0] * 7` Python list, attach 后第一帧 cmd_queue 空 + silent except 不改 self.last_commands → 仍 list; MCPController.get_last_command return `self.commands[:]` 也 list; merge_commands `m_last + p_last` = **list concat 14 维** (不是 element-wise add); np.clip → ndarray[14] → obs 108 维 → ONNX expect 101 维 → systemd restart loop. 改 line 34: `[0.0]*7` → `np.zeros(7, dtype=np.float32)` 从源头杜绝 list type 漂移. (2) 第 6 bug `JOYDEVICEREMOVED 永不触发 detach`: 20916cb 注释错误 - `pygame.event.get()` 是 destructive read, commands_worker 跑 ≥20Hz 抢先 drain SDL queue, main loop 每 25 帧 ~2Hz pump 永远拿不到 REMOVED. 修复: `get_commands()` event loop 第一个 if 处理 REMOVED 自调 `self.detach()` + raise pygame.error 让 commands_worker except 同步处理 (idempotent). **验证 2026-05-26 20:30-20:43**: 完整 hotplug 4 场景闭环 (Attached + Detached×2 双保险 + re-Attached + InvalidArgument=0 + svc 始终 active) | [patches/obs-dim-detach-fix-2026-05-26.diff](./patches/obs-dim-detach-fix-2026-05-26.diff) |
| `20916cb` feat: PS4 手柄运行时热插拔 | 2026-05-24 | **替代 `6f93be8`+`fbb17b7` 双 stub patch, 实现真正的运行时热插拔**: vendor `PS4Controller.__init__` 直接 `pygame.joystick.Joystick(0)` 硬依赖手柄, systemd 启动时若手柄不在线 → 抛异常 → fallback 到 _StubPS4, 手柄中途按 PS 键唤醒后 RLWalk 不会重探必须 systemctl restart. 改 2 文件: (1) `mini_bdx_runtime/ps4_controller.py` 改 lazy init + 加 `try_attach()` / `detach()` + `_attached` flag, `get_last_command()` 在 not attached 时返 stub 4-tuple (替代 _StubPS4), `commands_worker()` 在 not attached 时跳过 read joystick 不污染 queue, 中途 pygame.error 自动 detach; (2) `scripts/v2_rl_walk_mujoco_mcp.py` 删除 line 124-138 的 _StubPS4 try/except block (PS4Controller 自身已 self-stub), 主循环每 25 帧 (~0.5s @ 50Hz) `pygame.event.get()` 处理 JOYDEVICEADDED → try_attach() / JOYDEVICEREMOVED → detach(). 复用 `i` 帧计数器, 顶部加 `import pygame`. **预验证**: pygame 2.6.0 + SDL 2.28.4 JOYDEVICEADDED/REMOVED 事件机制已用 `scripts/verify_pygame_hotplug.py` v3+v7 双向 verify | [patches/hotplug-2026-05-24.diff](./patches/hotplug-2026-05-24.diff) |
| `b7d1529` chore: 注释耳朵随机动 | 2026-05-24 | **禁用耳朵 SG90 在 walk 主循环里的 PS4 trigger 驱动**: 用户反馈耳朵"随机动太频繁声音太大", 根因是 PS4 trigger idle 时仍以 50Hz 写 PWM 到 SG90, trigger 噪声/漂移导致持续微调 → buzz + 微抖动. 注释 `scripts/v2_rl_walk_mujoco_mcp.py` 第 460-466 行整个 `if self.duck_config.antennas:` 块, `antennas.py` 实现保留以备 LLM 模式恢复. 顺带发现上游 `debug_antennas_twitch` 分支佐证这是已知问题 | [patches/antennas-disable-random-2026-05-24.diff](./patches/antennas-disable-random-2026-05-24.diff) |
| `1e5f7e5` fix: consume A.triggered after paused toggle to prevent storm | 2026-05-23 | **修 vendor LLM 模式无法稳定 unpause 的 bug**: vendor 物理按键脉冲语义设计 A.triggered,但 LLM 模式下 `duck.start()` 让 `self.A_pressed=True` 持续多帧 (没复位机制),broadcast 100ms 周期 + RLWalk 50Hz 主循环,`update_if_changed` 在 is_pressed 不变时不替换 self.buttons → `self.buttons.A.triggered` 持续 True → RLWalk **每帧 toggle paused** = 翻烧饼,最终落点不定。修复 1 行: line 475 加 `self.buttons.A.triggered = False` 处理完立刻 consume → 单次 toggle,paused 稳定。保留 vendor Arm/Disarm 设计 (启动锁定 + 主动解锁 = 安全语义)。**验证**: ssh duck + python ws client 发 duck_start → grep PAUSE/UNPAUSE 只 1 次 UNPAUSE (修复前 50Hz 翻烧饼无数次); 鸭子能动 (S0 #10 喊"前进"实测通过) | [patches/paused-trigger-consume-2026-05-23.diff](./patches/paused-trigger-consume-2026-05-23.diff) |
| `fbb17b7` fix: _StubPS4 return 4-tuple match PS4Controller | 2026-05-23 | **修 6f93be8 的 regression**: 旧 stub 返 `[0.0]*7` 单 list,但 `v2_rl_walk_mujoco_mcp.py:300` 的 `merge_commands()` 用 4 元解包 `p_last, p_buttons, p_left, p_right = ps4_values`, 报 `ValueError too many values to unpack`,systemd restart loop。新 stub 返 `(np.zeros(7,float32), Buttons(), 0.0, 0.0)` 匹配真实 PS4Controller.get_last_command() (`mini_bdx_runtime/ps4_controller.py:186-191`) | [patches/ps4-stub-fix-2026-05-23.diff](./patches/ps4-stub-fix-2026-05-23.diff) |
| `6f93be8` patch: PS4Controller fallback to stub | 2026-05-23 | v2_rl_walk_mujoco_mcp.py:125 try/except 包 PS4Controller(), 失败 fallback `_StubPS4`。**注**: 此 commit stub 实现错误,被 `fbb17b7` 修正。保留此 commit 作追溯锚点,不 amend | [patches/ps4-controller-fallback-2026-05-23.diff](./patches/ps4-controller-fallback-2026-05-23.diff) |
| `9ad727e` chore: gitignore + rm cached log/jpg | 2026-05-23 | 排除 `commands_*log.txt` (4 个) + `test.jpg` 防运行时副产物污染 customization history; **保留** `imu_calib_data.pkl` / `polynomial_coefficients.pkl` (硬件有效配置) | — |
| `0671b96` snapshot: 爱折腾出厂态 (baseline 锚) | 2026-05-23 | 仅在 baseline 分支, customization 第一个 commit 是 `9ad727e` | — |

### 备份验证 (每次重大变更后跑)

```bash
ssh duck 'cd /home/raspios/open_duck_mini_ws/Open_Duck_Mini_Runtime && git log --oneline --all | head -10 && echo --- && git branch && echo --- && git status --short'
```

期望: 三个分支 `v2` + `vendor-baseline-2026-05-23` + `guagua-customizations` 都在,working tree 干净 (no output)。

未来配 GitHub remote 后追加:
```bash
ssh duck 'cd .../Runtime && git ls-remote origin-github | head'  # 期望列到两分支
```

---

## §2. mcp-openduck (S0 阶段不动)

S0 红线明确禁止改 mcp-openduck (爱折腾自家 MCP 流程,S1 才换)。本会话不做 baseline,只记录现状:

- HEAD: `3fa9fd5 update README.md. 去掉 --mcp参数,默认不需要了`
- 唯一关键自配文件: `mcp_point.sh` (含 wss URL token,被 `.gitignore` 排除,**不进 git**)
- 替代追溯方式: token rotate 历史记到 docs/ (例 `s0-handoff-passed-2026-05-22.md`)

---

## §3. Open_Duck_Mini (硬件/URDF/onnx 权重源)

爱折腾原封 fork,我们不改:

- HEAD: `cc4a2d4 Merge branch 'v2' of github.com:apirrone/mini_BDX into v2`
- 关键文件: `BEST_WALK_ONNX_2.onnx` (50Hz 控制循环用的 RL policy 权重,红线禁止改)

---

## §4. 鸭子访问通道

| 项 | 值 |
|---|---|
| SSH 别名 | `ssh duck` (PC 端 `~/.ssh/config` 已配, 5/19 完成 todo) |
| 真实地址 | `raspios@192.168.3.166` |
| WiFi | 2.4G `1101` (5GHz 已禁用,5/10 channel 157 LAN 拦截 bug) |
| 鸭子 SSH key (出向) | `~/.ssh/id_ed25519_gitee` (5/23 生, 文件名遗留 Gitee 字样, 可改名也可不改; 公钥 `AAAAC3NzaC1lZDI1NTE5AAAAIKb3JvsC9a7hUzWUjek+5DOh0dtWhPF2JjzIy/9Qr5LD openduckmini-v108@guagua-vendor-2026-05-23`) |
| 鸭子 ssh config | `~/.ssh/config` 含 `Host gitee.com IdentityFile ~/.ssh/id_ed25519_gitee` (deferred 重命名为 github.com) |

---

## §5. 灾难恢复 SOP

**鸭子 SD 卡损坏 / 换机后从零恢复 Runtime 仓库 customization**:

```bash
# 0. 新 Pi 装好系统 + venv_duck + 通网 + ncnynl 教程基础环境就绪
# 1. 进 ws 目录, 删掉爱折腾原版 Runtime (或先备份):
cd ~/open_duck_mini_ws/
mv Open_Duck_Mini_Runtime Open_Duck_Mini_Runtime.aizheteng-original

# 2. 从 Gitee 拉 guagua-customizations 分支 (含 baseline + 所有 patch):
git clone -b guagua-customizations git@gitee.com:sean515/guagua-duck-runtime-vendor.git Open_Duck_Mini_Runtime

# 3. 验证关键 patch 都在:
cd Open_Duck_Mini_Runtime
git log --oneline | head -5
grep -q "_StubPS4" scripts/v2_rl_walk_mujoco_mcp.py && echo "OK PS4 patch present" || echo "FAIL PS4 patch missing"

# 4. 重新装 SSH key 走 git push (如果新 Pi 也要后续 push):
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_gitee -N "" -q -C "<new-host>@guagua-vendor"
# 把 pub key 加到 Gitee SSH Keys
# 鸭子 ~/.ssh/config 加 Host gitee.com IdentityFile ~/.ssh/id_ed25519_gitee
```

**误改 baseline 紧急回滚** (vendor-baseline 是 immutable, 任何 push 到 baseline 分支的 commit 都需 revert):

```bash
ssh duck 'cd ~/open_duck_mini_ws/Open_Duck_Mini_Runtime && git reflog show vendor-baseline-2026-05-23 | head'
# 找到误改前的 commit hash → git reset --hard <hash>
# 然后 git push --force-with-lease origin-gitee vendor-baseline-2026-05-23 (谨慎!)
```

---

## §6. 修订记录

- 2026-05-23 - 朱庆勋 - 首版, S0 通关后建立 vendor baseline 工程纪律, Runtime 仓库 baseline + customization 双分支化 + Gitee 私有备份
- 2026-05-23 - 朱庆勋 - 增 `fbb17b7` fix commit 入 Patch 列表 (修 6f93be8 regression). 经验: vendor patch 必须 grep 调用方下游消费方式, 不能只看构造函数;否则会引入 stub 数据结构不匹配 regression
- 2026-05-23 - 朱庆勋 - 增 `1e5f7e5` fix commit (paused trigger consume); systemd unit 加 `PYTHONUNBUFFERED=1`. S0 #10 LLM-MCP 模式喊"前进"实测鸭子动. **重要发现**: vendor LLM 模式从未真正端到端测试过——PS4 模式按 X(=A) 是物理按键脉冲,LLM 调 duck_start 是状态持续,二者语义不等价导致 paused storm。卖家 demo 应该全程 PS4 手柄,未触达此 bug。**经验**: 接手 vendor 代码时,**新模式 (LLM/voice) 必须端到端验证至物理动作**,不能只看 mcp tool 调用响应。本会话 4 个独立 bug 串联(PS4 crash → PYTHONUNBUFFERED → paused storm → duck_pause vendor bug 未修),靠 advisor + 用户 domain knowledge ("X 键解锁") 才定位
- 2026-05-23 19:55 - 朱庆勋 - **Runtime 备份 Gitee 已部署** (从 5/23 早 handoff v1 "deferred GitHub" 改成 Gitee). 两个分支 `vendor-baseline-2026-05-23` (0671b96) + `guagua-customizations` (1e5f7e5) push 到 `gitee.com:sean515/guagua-duck-runtime-vendor` 私有仓库. Gitee API v5 自动化路径 (Bitwarden PAT → 加 SSH key → 创建仓库) 5/1 已沉淀模板, 本次复用. 鸭子端 SSH key id_ed25519_gitee 已加 Gitee (id=5799928). SD 卡损坏现可走 §5 灾难恢复 SOP 从 Gitee 恢复
- 2026-05-24 - 朱庆勋 - 增 `b7d1529` chore commit (注释耳朵随机动). **未推 Gitee** (主会话控制 push 时机). 任务理解修正: 用户描述"随机动"实际不是 `random_move()` 函数, 而是 PS4 trigger idle 噪声 + 50Hz PWM 写入 SG90 导致的 buzz/微抖动症状. 上游 `debug_antennas_twitch` 分支存在佐证这是已知问题. 注释整个 `if self.duck_config.antennas:` 块 (而非单行) 以彻底消除 50Hz 写 PWM. antennas.py 实现保留, LLM 模式恢复时只需删注释
- 2026-05-24 - 朱庆勋 - 增 `20916cb` feat commit (PS4 手柄运行时热插拔). **未推 Gitee** (主会话控制 push 时机). 替代 `6f93be8`+`fbb17b7` 早期 stub 方案: 那两 commit 只解决"启动时无手柄不崩溃", 但 RLWalk 进程内手柄热插拔仍需 `systemctl restart`. 本 patch 用 pygame `JOYDEVICEADDED/REMOVED` event 实现真正运行时热插拔. **设计要点**: (1) `PS4Controller.__init__` 不再 raise, lazy init + `_attached` flag 全程管理 (2) `commands_worker` daemon thread 永远跑 (保留 vendor 设计), `_attached=False` 时跳过 read joystick 不污染 queue (3) 主循环每 25 帧 (~0.5s @ 50Hz) pump 一次 event, 远小于人感知阈值 (4) 复用 vendor 已有 `i` 帧计数器, 顶部新加 `import pygame` (vendor 原文件没显式导入). **预验证**: 今天会话用 `scripts/verify_pygame_hotplug.py` v3+v7 双向 verify pygame 2.6.0 + SDL 2.28.4 hotplug 机制工作, 任何时候按 PS 键唤醒 DS4 蓝牙手柄 1-2 秒内事件触发. **DS4 蓝牙限制**: paired MAC `A0:5A:5F:0A:0F:2C`, host 主动 `bluetoothctl connect` 失败 (DS4 固件不允许), 必须设备端按 PS 键发起. 用户场景: 开机不带手柄, 中途按 PS 键唤醒, 现在不再需要 manual restart.
