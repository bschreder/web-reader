param(
  [ValidateSet('docker','local')]
  [string]$Mode = 'docker',
  [switch]$Rebuild,
  [switch]$Attach,
  [string[]]$Services,
  [switch]$InfraOnly,
  [switch]$Debug,
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
Web Reader - start.ps1

Usage:
  ./start.ps1 [-Mode docker|local] [-Rebuild] [-Attach] [-Services svc1,svc2] [-InfraOnly] [-Debug] [-Help]

Options:
  -Mode       docker (default) to run with Docker Compose, or local to start only the frontend locally.
  -Rebuild    Forces image rebuild for Docker services.
  -Attach     Runs docker compose up attached (shows logs). Default is detached (-d).
  -Services   Comma-separated list to start only specified services (frontend, backend, langchain, fastmcp).
  -InfraOnly  Start only external infrastructure (Ollama + Playwright) without app services.
  -Debug      Start application services in debug mode with open debug ports for VS Code attach.
  -Help/-H    Show this help.

Debug ports:
  backend  (debugpy): 5671
  langchain(debugpy): 5672
  fastmcp  (debugpy): 5673
  frontend (node inspect): 9229 (optional)

See README.DEBUG.md for full debugging instructions and VS Code launch configs.
"@ | Write-Host
}

function Ensure-Command($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Required command '$name' not found on PATH."
  }
}

function Ensure-Network($networkName) {
  $exists = & docker network ls --format '{{.Name}}' | Select-String -SimpleMatch $networkName
  if (-not $exists) {
    Write-Info "Creating external Docker network '$networkName'..."
    & docker network create $networkName | Out-Null
    Write-Ok "Created network '$networkName'"
  } else {
    Write-Info "Network '$networkName' already exists"
  }
}

function Start-Infra([switch]$RebuildFlag) {
  $infraDir = Join-Path $PSScriptRoot 'container'
  $infraStart = Join-Path $infraDir 'start.ps1'
  if (-not (Test-Path $infraStart)) {
    throw "Infra start script not found at $infraStart"
  }
  Write-Info 'Starting external infrastructure (Playwright, Ollama)...'
  & $infraStart @{
    Build = $RebuildFlag
  }
  Write-Ok 'External infrastructure started.'
}

function Connect-Infra-To-Network($networkName) {
  $targets = @(
    @{ Name = 'ws-ollama'; Alias = 'ollama' },
    @{ Name = 'ws-playwright'; Alias = 'playwright' }
  )

  foreach ($t in $targets) {
    try {
      # If already connected, this will error; ignore
      & docker network connect --alias $($t.Alias) $networkName $($t.Name) 2>$null
      Write-Info "Connected $($t.Name) to '$networkName' as '$($t.Alias)'"
    } catch {
      Write-Info "Skipping network connect for $($t.Name) (maybe already connected)."
    }
  }
}

function Start-App([switch]$RebuildFlag, [switch]$AttachFlag, [string[]]$Svc) {
  $appDir = Join-Path $PSScriptRoot 'docker'
  $composeFile = Join-Path $appDir 'docker-compose.yml'
  if (-not (Test-Path $composeFile)) {
    throw "Application compose file not found at $composeFile"
  }
  $envFile = Join-Path $PSScriptRoot '.env'

  # Use static override file if -Debug specified
  $overrideArgs = @()
  if ($Debug) {
    $overrideFile = Join-Path $appDir 'docker-compose.override.yml'
    if (-not (Test-Path $overrideFile)) {
      Write-Warn "Debug override requested but docker-compose.override.yml not found. Create it under docker/."
    } else {
      $overrideArgs += @('-f', 'docker-compose.yml', '-f', 'docker-compose.override.yml')
      Write-Info "Debug override enabled via docker-compose.override.yml"
    }
  }

  Push-Location $appDir
  try {
  $args = @('compose')
  if ($overrideArgs.Length -gt 0) { $args += $overrideArgs } else { $args += @('-f','docker-compose.yml') }
    if (Test-Path $envFile) { $args += @('--env-file', $envFile) }
    $args += @('up')
    if (-not $AttachFlag) { $args += '-d' }
    if ($RebuildFlag) { $args += '--build' }
    if ($Svc -and $Svc.Length -gt 0) { $args += $Svc }

    Write-Info "Starting application services: docker $($args -join ' ')"
    & docker @args
  } finally {
    Pop-Location
  }

  Write-Ok 'Application services started.'
}

function Start-Frontend-Local() {
  $feDir = Join-Path $PSScriptRoot 'frontend'
  if (-not (Test-Path (Join-Path $feDir 'package.json'))) {
    throw "Frontend not found at $feDir"
  }
  Write-Info 'Installing frontend dependencies...'
  & npm --prefix $feDir ci
  Write-Info 'Building frontend...'
  & npm --prefix $feDir run build
  Write-Info 'Starting frontend dev server in a new window...'
  Start-Process powershell -ArgumentList @('-NoExit', '-Command', "npm --prefix `"$feDir`" run dev") | Out-Null
  Write-Ok 'Frontend dev server started.'
}

# --------------------------- Main ---------------------------
if ($Help) { Show-Help; exit 0 }

Ensure-Command 'docker'

if ($Mode -eq 'docker') {
  $externalNet = 'external-services-network'
  Ensure-Network $externalNet
  Start-Infra -RebuildFlag:$Rebuild
  Connect-Infra-To-Network $externalNet

  if (-not $InfraOnly) {
    Start-App -RebuildFlag:$Rebuild -AttachFlag:$Attach -Svc:$Services
    Write-Host ''
    Write-Ok 'Stack is up!'
    Write-Host 'Frontend: http://localhost:3000' -ForegroundColor Gray
    Write-Host 'Backend:  http://localhost:8000' -ForegroundColor Gray
    Write-Host 'LangChain: (internal, port 8001)' -ForegroundColor Gray
    Write-Host 'FastMCP:   (internal, port 3000)' -ForegroundColor Gray
    Write-Host 'Ollama:    http://localhost:11434 (API)' -ForegroundColor Gray
    Write-Host 'Playwright: ws://localhost:3002 (server)' -ForegroundColor Gray
    if ($Debug) {
      Write-Host ''
      Write-Warn 'Debug mode enabled. Attach with VS Code:'
      Write-Host ' - backend (debugpy):   localhost:5671' -ForegroundColor Gray
      Write-Host ' - langchain (debugpy): localhost:5672' -ForegroundColor Gray
      Write-Host ' - fastmcp (debugpy):   localhost:5673' -ForegroundColor Gray
      Write-Host ' - frontend (node):     localhost:9229 (optional)' -ForegroundColor Gray
    }
  } else {
    Write-Ok 'Infrastructure only mode complete.'
  }
}
elseif ($Mode -eq 'local') {
  Write-Warn 'Local mode: starting only frontend locally. Backends should run via Docker (recommended).'
  Start-Frontend-Local
} else {
  throw "Unknown mode: $Mode"
}
