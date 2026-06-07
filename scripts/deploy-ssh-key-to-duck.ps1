# 把 Claude Code 用的公钥重新推到鸭子 authorized_keys
# 系统重置后鸭子端 authorized_keys 被清空, 需重新部署一次 (输一次密码 raspios)
# 用法: pwsh D:\CODE\guagua\scripts\deploy-ssh-key-to-duck.ps1

$ErrorActionPreference = 'Stop'
$pub = "$env:USERPROFILE\.ssh\id_ed25519_duck.pub"

Write-Host "==> 推送公钥到鸭子 (192.168.3.166), 接下来会提示输入密码: raspios" -ForegroundColor Cyan
Get-Content $pub | ssh -o StrictHostKeyChecking=accept-new raspios@192.168.3.166 "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"

Write-Host "==> 验证免密登录 (不应再提示密码):" -ForegroundColor Cyan
ssh duck 'echo SSH_KEY_OK; whoami; hostname'
