param(
  [ValidateSet('docker', 'local')]
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

$wr = Join-Path $PSScriptRoot 'infra\scripts\wr.ps1'

if (-not (Test-Path $wr)) {
  throw "Missing command wrapper at $wr"
}

if ($Help) {
  Write-Host 'Web Reader start wrapper (delegates to infra/scripts/wr.ps1)' -ForegroundColor Cyan
  Write-Host 'Examples:' -ForegroundColor Cyan
  Write-Host '  ./start.ps1                    -> wr up'
  Write-Host '  ./start.ps1 -Debug             -> wr debug up'
  Write-Host '  ./start.ps1 -InfraOnly         -> wr up --infra'
  Write-Host '  ./start.ps1 -Rebuild -Debug    -> wr debug up --build'
  exit 0
}

if ($Mode -eq 'local') {
  Write-Host 'Local mode is deprecated in start.ps1. Use frontend npm scripts directly for host-only UI dev.' -ForegroundColor Yellow
  exit 0
}

if ($Services -and $Services.Length -gt 0) {
  Write-Host 'Service selection is no longer supported by start.ps1. Use wr profiles (--infra/--app).' -ForegroundColor Yellow
}

$args = @()
if ($Debug) {
  $args += @('debug', 'up')
}
else {
  $args += 'up'
}

if ($InfraOnly) {
  $args += '--infra'
}

if ($Rebuild) {
  $args += '--build'
}

if ($Attach) {
  Write-Host 'Attach mode is deprecated in start.ps1. Use ./infra/scripts/wr.ps1 logs after startup.' -ForegroundColor Yellow
}

& $wr @args
