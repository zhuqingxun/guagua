# 鸭子系统重置/重刷卡后的一键恢复脚本 (PC 端运行)
# 重施本次会话 (2026-06-06) 的系统修复, 幂等可重复跑:
#   [1] WiFi fallback TIMEOUT 10->60 (延长连接窗口, fallback 逻辑保持出厂可靠路径不动)
#   [2] DNS 静态化: 电信 DNS 不通 -> 阿里 223.5.5.5 + 路由器 192.168.3.1, chattr +i 锁定
#   [3] NTP 阿里源: 默认 debian pool 国内不通 -> ntp.aliyun.com
#
# 前置条件 (按顺序):
#   a) 鸭子已 web 配好 WiFi (务必填 2.4G "1101", 不是 5G "1101_5G"! 5G channel 157 拦 SSH)
#   b) SSH key 已部署: pwsh scripts\deploy-ssh-key-to-duck.ps1
#
# 用法: pwsh D:\CODE\guagua\scripts\duck-post-reset-fix.ps1

$ErrorActionPreference = 'Stop'

Write-Host '==> [0] 检查 ssh duck 免密通道...' -ForegroundColor Cyan
$probe = ssh -n -o BatchMode=yes -o ConnectTimeout=8 duck 'echo OK' 2>$null
if ($probe -notmatch 'OK') {
    Write-Host '   ✗ ssh duck 不通。先确认: 鸭子已连家里网 + 已跑 deploy-ssh-key-to-duck.ps1' -ForegroundColor Red
    exit 1
}
Write-Host '   ✓ ssh duck 通' -ForegroundColor Green

# 鸭子端修复脚本 (here-string, 传前去 CRLF 防 bash \r 报错)
$fix = @'
#!/bin/bash
set -e
echo "=== 鸭子 post-reset 修复 ==="

# [1] WiFi fallback TIMEOUT 延长 (fallback 逻辑保持出厂: 连不上->清配置+起 openduckmini 热点)
WF=/home/raspios/tools/network/wifi_or_ap.sh
if [ -f "$WF" ]; then
  [ -f "${WF}.guagua-orig" ] || cp "$WF" "${WF}.guagua-orig"
  sed -i 's/^TIMEOUT=10\b/TIMEOUT=60/' "$WF"
  echo "[1] $(grep -m1 '^TIMEOUT=' $WF)"
else
  echo "[1] WARN: $WF 不存在, 跳过"
fi

# [2] DNS 静态化 + 锁定
sudo chattr -i /etc/resolv.conf 2>/dev/null || true
printf '# guagua static DNS (aliyun+router, 电信DNS不通)\nnameserver 223.5.5.5\nnameserver 192.168.3.1\n' | sudo tee /etc/resolv.conf >/dev/null
sudo chattr +i /etc/resolv.conf
NETF=/etc/systemd/network/10-wlan0.network
[ -f "$NETF" ] && sudo sed -i 's/^DNS=8.8.8.8/DNS=223.5.5.5 192.168.3.1/' "$NETF" || true
echo "[2] resolv.conf locked"

# [3] NTP 阿里源
TS=/etc/systemd/timesyncd.conf
sudo sed -i '/^#\?NTP=/d; /^#\?FallbackNTP=/d' "$TS"
sudo sed -i '/^\[Time\]/a NTP=ntp.aliyun.com cn.pool.ntp.org\nFallbackNTP=cn.pool.ntp.org time.cloudflare.com' "$TS"
sudo systemctl restart systemd-timesyncd
echo "[3] NTP set"

# verify
sleep 8
echo "=== VERIFY ==="
echo "TIMEOUT      : $(grep -m1 '^TIMEOUT=' $WF 2>/dev/null)"
echo "fallback出厂 : $(grep -c remote_current_wifi $WF 2>/dev/null) remote_current + $(grep -c 'create_ap --no-virt' $WF 2>/dev/null) create_ap (都应=1)"
echo "DNS resolve  : $(getent hosts baidu.com >/dev/null && echo OK || echo FAIL)"
echo "resolv lock  : $(lsattr /etc/resolv.conf)"
timedatectl | grep -iE 'synchron|local time'
echo "=== 完成 ==="
'@

$fix = $fix -replace "`r", ""
Write-Host '==> 通过 ssh duck 执行鸭子端修复...' -ForegroundColor Cyan
$fix | ssh duck 'bash -s'
