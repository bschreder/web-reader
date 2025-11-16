param(
  [switch]$Build
)

$ErrorActionPreference = 'Stop'

Write-Host "Starting docker-compose services..." -ForegroundColor Cyan

$composeDir = Join-Path $PSScriptRoot '.'
$envFile = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '.env'

Push-Location $composeDir
try {
  if ($Build) {
    docker compose --env-file $envFile up -d --build
  } else {
    docker compose --env-file $envFile up -d
  }
} finally {
  Pop-Location
}

Write-Host "Compose started." -ForegroundColor Green
