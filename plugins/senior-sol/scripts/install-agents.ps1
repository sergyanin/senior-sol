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

    $targetItem = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
    if ($null -ne $targetItem) {
        if ($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw "Refusing redirected agents directory: $target"
        }
        if (-not $targetItem.PSIsContainer) {
            throw "Agents target exists but is not a directory: $target"
        }
    }
    else {
        New-Item -ItemType Directory -Path $target | Out-Null
        $targetItem = Get-Item -LiteralPath $target -Force
        if (($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or -not $targetItem.PSIsContainer) {
            throw "Agents target is not a real directory: $target"
        }
    }

    foreach ($name in $names) {
        $origin = Join-Path $source $name
        $destination = Join-Path $target $name

        $destinationItem = Get-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
        if ($null -ne $destinationItem -and (
            $destinationItem.PSIsContainer -or
            ($destinationItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
        )) {
            throw "Refusing non-file or redirected managed destination: $destination"
        }

        if ($null -eq $destinationItem) {
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
