#!/bin/bash
# Boot-time 自动诊断：station 模式下抓 tcpdump+journal+周期快照
# 输出: /var/log/duck-debug/<ts>/  + symlink latest
TS=$(date +%Y%m%d-%H%M%S)
DIR=/var/log/duck-debug/$TS
mkdir -p "$DIR"
ln -sfn "$DIR" /var/log/duck-debug/latest

# 等 wifi_or_ap.service / network 稳定
sleep 8

# === baseline 快照（无论模式都拍） ===
{
  echo "=== baseline @ $(date) ==="
  echo "## ip -br a";          ip -br a
  echo "## ip route";          ip route
  echo "## iw dev wlan0 info"; iw dev wlan0 info 2>&1 | head -20
  echo "## iw dev wlan0 link"; iw dev wlan0 link 2>&1 | head -10
  echo "## iptables filter -S";iptables -S
  echo "## iptables nat -S";   iptables -t nat -S
  echo "## iptables mangle -S";iptables -t mangle -S
  echo "## ss -tlnp";          ss -tlnp
  echo "## sysctl key";        sysctl net.ipv4.tcp_timestamps net.ipv4.conf.all.rp_filter net.ipv4.conf.wlan0.rp_filter net.ipv4.tcp_syncookies net.ipv4.tcp_max_syn_backlog net.ipv4.icmp_echo_ignore_all net.ipv4.conf.all.accept_redirects 2>&1
  echo "## timedatectl";       timedatectl
  echo "## conntrack count";   cat /proc/sys/net/netfilter/nf_conntrack_count 2>/dev/null
  echo "## sshd_config effective"; sshd -T 2>&1 | grep -iE "loglevel|usedns|maxstartups|tcpkeepalive"
} > "$DIR/baseline.txt" 2>&1

WLAN_IP=$(ip -4 a show wlan0 2>/dev/null | grep -oP 'inet \K[0-9.]+')
MODE=$([[ "$WLAN_IP" =~ ^192\.168\.3\. ]] && echo station || echo ap)
echo "MODE=$MODE WLAN_IP=$WLAN_IP" >> "$DIR/baseline.txt"

if [[ "$MODE" != "station" ]]; then
  echo "Not station mode, skip deep capture" >> "$DIR/baseline.txt"
  exit 0
fi

# === station 模式深度采集 ===

# tcpdump: TCP 22 + ICMP + ARP，rotate 60s 最多 10 个文件 (60MB 上限)
nohup tcpdump -i wlan0 -s 0 -U -G 60 -W 10 -w "$DIR/wlan0-%H%M%S.pcap" \
  '(tcp port 22) or icmp or arp' > "$DIR/tcpdump.log" 2>&1 &
echo $! > "$DIR/tcpdump.pid"

# journal follow（含 sshd DEBUG3）
nohup bash -c "journalctl -f --no-pager > '$DIR/journal-follow.log' 2>&1" &
echo $! > "$DIR/journal.pid"

# 周期快照: 每 20s 一次, 共 15 次 (5 分钟覆盖窗口)
(
  for i in $(seq 1 15); do
    {
      echo "===== iter $i @ $(date) ====="
      echo "## ss tcp 22"; ss -tnan '( sport = :22 or dport = :22 )'
      echo "## sshd procs";  pgrep -a sshd
      echo "## conntrack 22"; grep -E "(dport|sport)=22" /proc/net/nf_conntrack 2>/dev/null | head -10
      echo "## TCP listen drops"; awk '/^TcpExt:/{h=$0;next}/TcpExt/{for(i=1;i<=NF;i++)if(h~/ListenOverflows|ListenDrops|EmbryonicRsts|TCPAbortOnClose|TCPAbortOnData|TCPAbortFailed|TCPRcvCoalesce/)printf "%s=%s ",$i,$(i);print ""}' /proc/net/netstat 2>/dev/null | head
      echo "## nstat (if exists)"; command -v nstat >/dev/null && nstat -azs 2>/dev/null | grep -iE "Listen|Rst|Abort" | head
    } >> "$DIR/periodic.log" 2>&1
    sleep 20
  done
  # 5 分钟后清理后台进程
  for f in "$DIR"/tcpdump.pid "$DIR"/journal.pid; do
    [ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null
  done
  echo "Captures stopped @ $(date)" >> "$DIR/periodic.log"
) &
echo $! > "$DIR/periodic.pid"

echo "Capture started, will run 5 min" >> "$DIR/baseline.txt"
