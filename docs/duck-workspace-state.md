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
| `origin` | github.com/apirrone/Open_Duck_Mini_Runtime | upstream (爱折腾 fork 自此, **不动**) |
| ~~`origin-github`~~ | git@github.com:zhuqingxun/guagua-duck-runtime-vendor.git | **🚧 deferred** (本会话只做本地, push 走 GitHub, 见 rpiv todo `[deferred] 配 GitHub remote`) |

### Branches

| 分支 | HEAD 标识 | 含义 |
|---|---|---|
| `v2` | upstream tracking (`34c60ef antennas test`) | 别用,留作 upstream sync 参考 |
| `vendor-baseline-2026-05-23` | `0671b96` snapshot: 爱折腾出厂态 (2026-05-23) | 永久 baseline,**禁止改**。81 files 一次性 commit (含全部 53 dirty + 28 untracked)。任何回归测试以此为对照 |
| `guagua-customizations` (HEAD) | `1e5f7e5` fix: consume A.triggered after paused toggle | **生产用此分支**,start_duck_mcp.sh / systemd unit 跑的是这个 checkout |

### Patch 列表 (guagua-customizations 分支上, 按 git log 顺序倒序)

| Commit | 日期 | 作用 | Diff 副本 |
|---|---|---|---|
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
