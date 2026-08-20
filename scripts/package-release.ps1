param(
    [string]$Version = "0.1.1"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$InstallerCompiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
$ReleaseDir = Join-Path $Root "release"
$InstallerOutput = Join-Path $Root "installer\output"
$SetupName = "Visual-AI-Studio-Setup-$Version.exe"
$SetupPath = Join-Path $InstallerOutput $SetupName
$AgentPath = Join-Path $Root "agent\studio-visuel-agent.zip"

if (-not (Test-Path -LiteralPath $InstallerCompiler)) {
    throw "Inno Setup 6 introuvable : $InstallerCompiler"
}
if (-not (Test-Path -LiteralPath $AgentPath)) {
    throw "Package Studio Visuel introuvable : $AgentPath"
}

Push-Location $Root
try {
    & "$PSScriptRoot\quality.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & "$PSScriptRoot\build.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $InstallerCompiler "installer\visual-ai-studio.iss"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if (-not (Test-Path -LiteralPath $SetupPath)) {
        throw "Installateur attendu introuvable : $SetupPath"
    }

    Remove-Item -LiteralPath $ReleaseDir -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $ReleaseDir | Out-Null

    Copy-Item -LiteralPath $SetupPath -Destination (Join-Path $ReleaseDir $SetupName)
    Copy-Item -LiteralPath $AgentPath -Destination (Join-Path $ReleaseDir "studio-visuel-agent.zip")

    $Files = @(
        Join-Path $ReleaseDir $SetupName
        Join-Path $ReleaseDir "studio-visuel-agent.zip"
    )

    $ChecksumLines = foreach ($File in $Files) {
        $Hash = Get-FileHash -LiteralPath $File -Algorithm SHA256
        "{0}  {1}" -f $Hash.Hash.ToLowerInvariant(), (Split-Path -Leaf $File)
    }
    $ChecksumLines | Set-Content -LiteralPath (Join-Path $ReleaseDir "SHA256SUMS.txt") -Encoding ascii

    Write-Host "Release prête dans : $ReleaseDir"
    Get-ChildItem -LiteralPath $ReleaseDir | Select-Object Name, Length
} finally {
    Pop-Location
}
