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

    foreach ($name in $names) {
        $path = Join-Path $target $name
        if (Test-Path -LiteralPath $path) {
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
