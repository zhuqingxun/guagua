# 鸭子 SD 卡整盘镜像备份 + 恢复说明

**制作日期**: 2026-06-07
**镜像内容**: 商家初始化(出厂) + 2026-06-07 本会话系统修复后的**完整可运行环境**快照
**用途**: 将来鸭子出任何问题(系统损坏/误操作/SD 卡坏), 把镜像写回新 SD 卡即可**完全恢复**到这个正常运行的状态

---

## 为什么用整盘镜像, 不用 Gitee/git

用户曾问"是不是通过 Gitee 上传备份"。**整个可运行环境不能用 git 备份**:

- git 适合文本配置/代码(如 Runtime 仓库已备份到 Gitee), 但备份"整个能启动的系统"不行
- 系统环境 = OS(Debian 12) + 全部 `/etc` 配置 + `venv_duck` Python 环境 + apt 系统包 + 二进制库 + 权限/符号链接/特殊文件, git 无法还原成可启动系统, 且仓库会撑到几 GB
- 正确做法 = **SD 卡整盘镜像**(本文档), 写回卡即一模一样恢复

---

## 镜像信息

| 项 | 值 |
|---|---|
| 文件 | `D:\duck-backup\duck-env-initial-2026-06-07.img.zst` |
| 源盘 | 鸭子 `/dev/mmcblk0` 整盘 14.6GB(boot 512MB vfat + 根分区 14.1GB ext4) |
| 压缩 | zstd(`.zst`), 解压后是裸 `.img`(14.6GB) |
| 制作方式 | 远程 `ssh duck 'sudo dd if=/dev/mmcblk0 bs=4M \| zstd' > PC文件`(在线备份, dd 前已 sync) |
| 一致性 | **在线备份**(系统运行中 dd 根分区), 恢复后首次 boot 内核会自动 fsck 修小不一致。OpenDuck 运行时写盘少, 风险低 |

---

## 恢复步骤(将来有了 SD 卡)

### 准备
- 一张 **≥16GB** SD 卡(源盘 14.6GB, 16GB 卡通常实际 ≥14.6GB 可容纳; 保险用 32GB)
- 读卡器
- 写卡工具(任选): **Raspberry Pi Imager** / **balenaEtcher** / **Win32DiskImager** / Linux `dd`

### 方式 A: Raspberry Pi Imager(最简单, 推荐)
1. 先解压: 用 7-Zip 或命令 `zstd -d D:\duck-backup\duck-env-initial-2026-06-07.img.zst`(得到 `.img`)
   - 或装了 zstd 的话直接 `zstd -d 文件.zst -o duck.img`
2. 打开 Raspberry Pi Imager → "Use custom" 选解压出的 `.img` → 选 SD 卡 → 写入
3. 写完插回鸭子, 上电

### 方式 B: balenaEtcher
1. balenaEtcher **可直接选 `.zst`? 不一定**, 保险先解压成 `.img`
2. Flash from file → 选 `.img` → 选 SD 卡 → Flash

### 方式 C: 命令行(Windows, 无需解压中间文件)
```
# 需要装 zstd for windows; <PHYSICALDRIVE> 用 diskpart/Get-Disk 确认是 SD 卡, 别选错盘!
zstd -dc D:\duck-backup\duck-env-initial-2026-06-07.img.zst | dd of=\\.\PhysicalDriveN bs=4M
```
> ⚠️ Windows 上 dd 写物理盘需要管理员 + 确认盘号(`Get-Disk` 看), **选错盘会清空你的硬盘**, 务必核对容量是 SD 卡。

### 验证恢复
1. SD 卡插回鸭子, 上电, 等 1-2 分钟
2. 鸭子开机自动连家里 WiFi 1101(本镜像已含修复) → PC `ssh duck 'hostname; uptime'` 应通
3. 首次 boot 可能因 fsck 多花 30-60 秒, 属正常

---

## 备份文件管理建议

- **不要放 git 仓库**(`D:\CODE\guagua\`)——镜像几 GB 会撑爆 repo。当前放 `D:\duck-backup\`(仓库外)
- **多备一份**: 复制到移动硬盘 / 华为云盘, 防 PC 硬盘坏(单点)
- **定期更新**: 以后 S0 定制(PS4/小智/reboot 自启)做好了, 重新跑一次备份, 文件名带新日期, 这样镜像里也含那些定制

## 重新制作备份(以后环境有重大更新时)
```
ssh -n duck 'sync; sync'
cmd /c 'ssh -n duck "sudo dd if=/dev/mmcblk0 bs=4M 2>/dev/null | zstd -T0 -3" > D:\duck-backup\duck-env-<日期>.img.zst'
```
> ⚠️ PowerShell 的 `>` 会破坏二进制流, **必须用 `cmd /c` 重定向**(cmd 的 `>` 二进制安全)。`ssh -n` 防后台 stdin hang。

---

## 相关
- `docs/duck-post-reset-recovery.md` — 另一种恢复方式(重置后手动重配网+重施修复, 不依赖镜像)
- 两者关系: 整盘镜像 = 一键完全还原(最省事, 但需 SD 卡+读卡器); post-reset-fix = 无镜像时的手动重建路径
