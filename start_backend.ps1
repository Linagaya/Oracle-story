#!/usr/bin/env powershell
# 启动后端服务
Write-Host "正在检查必要目录..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dirs = @(
    "$scriptDir\data\training\train",
    "$scriptDir\data\training\val",
    "$scriptDir\data\test",
    "$scriptDir\backend\model"
)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "目录检查完成。`n" -ForegroundColor Green

Write-Host "正在启动甲骨文AI识别后端服务..." -ForegroundColor Green
Set-Location backend
pip install -r requirements.txt
Write-Host "`n启动FastAPI服务器..." -ForegroundColor Green
python main.py