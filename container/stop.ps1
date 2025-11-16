$ErrorActionPreference = 'Stop'

Write-Host "Stopping docker-compose services..." -ForegroundColor Cyan

$composeDir = Join-Path $PSScriptRoot '.'
$envFile = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '.env'

Push-Location $composeDir
try {
  docker compose --env-file $envFile down
} finally {
  Pop-Location
}

Write-Host "Compose stopped." -ForegroundColor Green
