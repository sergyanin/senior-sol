[CmdletBinding()]
param()

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
    $target = Join-Path $codexHome 'agents'

    $targetItem = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
    if ($null -ne $targetItem) {
        if ($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            throw "Refusing redirected agents directory: $target"
        }
        if (-not $targetItem.PSIsContainer) {
            throw "Agents target exists but is not a directory: $target"
        }
    }

    foreach ($name in $names) {
        $path = Join-Path $target $name
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            Remove-Item -LiteralPath $path
            Write-Output "removed: $name"
        }
        else {
            Write-Output "missing: $name"
        }
    }

    exit 0
}
catch {
    Write-Error $_
    exit 1
}
