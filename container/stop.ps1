$ErrorActionPreference = 'Stop'

Write-Host "Deprecated entrypoint: delegating to infra/scripts/wr.ps1 down --infra" -ForegroundColor Yellow

$wr = Join-Path $PSScriptRoot '..\infra\scripts\wr.ps1'
& $wr down --infra
