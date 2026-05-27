param(
  [switch]$Build
)

$ErrorActionPreference = 'Stop'

Write-Host "Deprecated entrypoint: delegating to infra/scripts/wr.ps1 up --infra" -ForegroundColor Yellow

$wr = Join-Path $PSScriptRoot '..\infra\scripts\wr.ps1'
$args = @('up', '--infra')
if ($Build) {
  $args += '--build'
}

& $wr @args
