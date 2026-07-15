[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

try {
    $names = @(
        'senior-sol-luna-low.toml'
        'senior-sol-luna-medium.toml'
        'senior-sol-terra-high.toml'
        'senior-sol-terra-low.toml'
        'senior-sol-terra-medium.toml'
    )
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    $source = Join-Path (Split-Path -Parent $PSScriptRoot) 'agents'
    $target = Join-Path $codexHome 'agents'
    $hadConflict = $false

    New-Item -ItemType Directory -Path $target -Force | Out-Null

    foreach ($name in $names) {
        $origin = Join-Path $source $name
        $destination = Join-Path $target $name

        if (-not (Test-Path -LiteralPath $destination)) {
            Copy-Item -LiteralPath $origin -Destination $destination
            Write-Output "created: $name"
        }
        elseif ((Get-FileHash -LiteralPath $origin).Hash -eq (Get-FileHash -LiteralPath $destination).Hash) {
            Write-Output "unchanged: $name"
        }
        elseif ($Force) {
            Copy-Item -LiteralPath $origin -Destination $destination -Force
            Write-Output "replaced: $name"
        }
        else {
            Write-Output "conflict: $name"
            $hadConflict = $true
        }
    }

    if ($hadConflict) {
        exit 1
    }
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
