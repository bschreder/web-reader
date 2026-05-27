param(
  [ValidateSet('docker', 'local')]
  [string]$Mode = 'docker',
  [string[]]$Services,
  [switch]$All,
  [switch]$Prune,
  [Alias('H')]
  [switch]$Help
)

$ErrorActionPreference = 'Stop'

$wr = Join-Path $PSScriptRoot 'infra\scripts\wr.ps1'

if (-not (Test-Path $wr)) {
  throw "Missing command wrapper at $wr"
}

if ($Help) {
  Write-Host 'Web Reader stop wrapper (delegates to infra/scripts/wr.ps1)' -ForegroundColor Cyan
  Write-Host 'Examples:' -ForegroundColor Cyan
  Write-Host '  ./stop.ps1              -> wr down'
  Write-Host '  ./stop.ps1 -Prune       -> wr down + docker prune'
  exit 0
}

if ($Mode -eq 'local') {
  Write-Host 'Local mode is deprecated in stop.ps1. Stop host processes directly.' -ForegroundColor Yellow
  exit 0
}

if ($Services -and $Services.Length -gt 0) {
  Write-Host 'Service selection is no longer supported by stop.ps1. Use ./infra/scripts/wr.ps1 down for profile-driven shutdown.' -ForegroundColor Yellow
}

if ($All) {
  Write-Host '-All is now the default behavior for stop.ps1.' -ForegroundColor Yellow
}

& $wr down

if ($Prune) {
  docker system prune -f
  docker volume prune -f
}
