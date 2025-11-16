param(
  [ValidateSet('docker','local')]
  [string]$Mode = 'docker',
  [string[]]$Services,
  [switch]$All,
  [switch]$Prune,
  [Alias('H')]
  [switch]$Help
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

function Show-Help() {
  @"
Web Reader - stop.ps1

Usage:
  ./stop.ps1 [-Mode docker|local] [-Services svc1,svc2] [-All] [-Prune] [-Help]

Options:
  -Mode     docker (default) to stop Docker services, or local to stop local dev processes.
  -Services Comma-separated list to stop only selected services (frontend, backend, langchain, fastmcp). Docker mode only.
  -All      Stop all application services (default if -Services not provided).
  -Prune    Run docker system prune and volume prune after stopping.
  -Help/-H  Show this help.
"@ | Write-Host
}

function Ensure-Command($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Required command '$name' not found on PATH."
  }
}

function Stop-App([string[]]$Svc, [switch]$AllFlag) {
  $appDir = Join-Path $PSScriptRoot 'docker'
  $composeFile = Join-Path $appDir 'docker-compose.yml'
  if (-not (Test-Path $composeFile)) { throw "Compose file not found at $composeFile" }
  $envFile = Join-Path $PSScriptRoot '.env'

  Push-Location $appDir
  try {
    if ($AllFlag -or -not $Svc -or $Svc.Length -eq 0) {
      Write-Info 'Stopping all application services...'
      & docker compose --env-file $envFile down
    } else {
      Write-Info "Stopping selected services: $($Svc -join ', ')"
      & docker compose --env-file $envFile stop $Svc
    }
  } finally { Pop-Location }
  Write-Ok 'Application services stopped.'
}

function Stop-Infra() {
  $infraDir = Join-Path $PSScriptRoot 'container'
  $infraStop = Join-Path $infraDir 'stop.ps1'
  if (Test-Path $infraStop) {
    Write-Info 'Stopping external infrastructure (Playwright, Ollama)...'
    & $infraStop
    Write-Ok 'External infrastructure stopped.'
  } else {
    Write-Warn 'No infra stop script found. Skipping.'
  }
}

function Prune-Docker() {
  Write-Warn 'Pruning unused Docker resources (volumes, networks, images, build cache)...'
  & docker system prune -f
  & docker volume prune -f
  Write-Ok 'Docker prune complete.'
}

function Stop-Local() {
  Write-Info 'Attempting to stop local frontend (manual process termination may be required).'
  Get-Process | Where-Object { $_.ProcessName -like 'node' } | Stop-Process -Force -ErrorAction SilentlyContinue
  Write-Ok 'Requested local frontend stop.'
}

# ------------------ Main ------------------
if ($Help) { Show-Help; exit 0 }

Ensure-Command 'docker'

if ($Mode -eq 'docker') {
  Stop-App -Svc:$Services -AllFlag:$All
  Stop-Infra
  if ($Prune) { Prune-Docker }
}
elseif ($Mode -eq 'local') {
  Stop-Local
} else {
  throw "Unknown mode: $Mode"
}

Write-Ok 'Stop sequence complete.'
