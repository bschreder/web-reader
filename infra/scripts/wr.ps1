param(
  [Parameter(Mandatory = $true, Position = 0)]
  [ValidateSet('up', 'debug', 'down', 'logs', 'lint', 'test')]
  [string]$Command,

  [Parameter(Position = 1)]
  [string]$Subcommand,

  [switch]$Infra,
  [switch]$App,
  [switch]$Build,
  [switch]$UseDebug,
  [string]$Service,
  [ValidateSet('unit', 'integration', 'e2e', 'all')]
  [string]$Suite
)

$ErrorActionPreference = 'Stop'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ComposeBase = Join-Path $Root 'infra\compose\compose.yaml'
$ComposeDev = Join-Path $Root 'infra\compose\compose.dev.yaml'
$EnvFile = Join-Path $Root '.env'

if (-not (Test-Path $EnvFile)) {
  throw "Missing $EnvFile. Copy .env.example to .env first."
}

function Invoke-Compose {
  param(
    [string[]]$ComposeArgs,
    [switch]$UseDebug
  )

  $dockerComposeArgs = @('compose', '-f', $ComposeBase, '--env-file', $EnvFile)
  if ($UseDebug) {
    $dockerComposeArgs += @('-f', $ComposeDev)
  }
  $dockerComposeArgs += $ComposeArgs
  & docker @dockerComposeArgs
}

function Get-Profiles {
  if ($Infra -and -not $App) {
    return @('--profile', 'infra')
  }
  if ($App -and -not $Infra) {
    # App services depend on infra services in compose graph, so keep both profiles enabled
    # and scope startup to app services in the `up` command.
    return @('--profile', 'infra', '--profile', 'app')
  }
  return @('--profile', 'infra', '--profile', 'app')
}

function Invoke-TestSuite {
  param([string]$Level)

  switch ($Level) {
    'unit' {
      Push-Location (Join-Path $Root 'apps\fastmcp')
      uv run pytest tests/unit/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\langchain')
      uv run pytest tests/unit/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\backend')
      uv run pytest tests/unit/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\frontend')
      npm run test:unit
      Pop-Location
    }
    'integration' {
      Push-Location (Join-Path $Root 'apps\fastmcp')
      uv run pytest tests/integration/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\langchain')
      uv run pytest tests/integration/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\backend')
      uv run pytest tests/integration/ -v
      Pop-Location
    }
    'e2e' {
      Push-Location (Join-Path $Root 'apps\fastmcp')
      uv run pytest tests/e2e/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\langchain')
      uv run pytest tests/e2e/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\backend')
      uv run pytest tests/e2e/ -v
      Pop-Location
      Push-Location (Join-Path $Root 'apps\frontend')
      npm run test:e2e
      Pop-Location
    }
    'all' {
      Push-Location $Root
      ./scripts/test-all.sh all
      Pop-Location
    }
    default {
      throw "Unknown suite '$Level'. Use unit, integration, e2e, or all."
    }
  }
}

switch ($Command) {
  'up' {
    $profiles = Get-Profiles
    $composeCommandArgs = @()
    $composeCommandArgs += $profiles
    $composeCommandArgs += @('up', '-d')
    if ($Build) {
      $composeCommandArgs += '--build'
    }
    if ($App -and -not $Infra) {
      $composeCommandArgs += @('frontend', 'backend', 'langchain', 'fastmcp')
    }
    Invoke-Compose -ComposeArgs $composeCommandArgs -UseDebug:$UseDebug
  }
  'debug' {
    if ($Subcommand -ne 'up') {
      throw "Usage: ./infra/scripts/wr.ps1 debug up [--infra|--app] [--build]"
    }
    $profiles = Get-Profiles
    $composeCommandArgs = @()
    $composeCommandArgs += $profiles
    $composeCommandArgs += @('up', '-d')
    if ($Build) {
      $composeCommandArgs += '--build'
    }
    if ($App -and -not $Infra) {
      $composeCommandArgs += @('frontend', 'backend', 'langchain', 'fastmcp')
    }
    Invoke-Compose -ComposeArgs $composeCommandArgs -UseDebug
  }
  'down' {
    $profiles = Get-Profiles
    Invoke-Compose -ComposeArgs ($profiles + @('down'))
  }
  'logs' {
    if ($Service) {
      Invoke-Compose -ComposeArgs @('logs', '-f', $Service)
    }
    else {
      Invoke-Compose -ComposeArgs @('logs', '-f')
    }
  }
  'lint' {
    Push-Location (Join-Path $Root 'apps\frontend')
    npm run lint
    npm run typecheck
    Pop-Location
  }
  'test' {
    if (-not $Suite) {
      $Suite = $Subcommand
    }
    if (-not $Suite) {
      throw "Usage: ./infra/scripts/wr.ps1 test <unit|integration|e2e|all>"
    }
    Invoke-TestSuite -Level $Suite
  }
}
