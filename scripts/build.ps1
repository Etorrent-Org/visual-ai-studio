$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Environnement .venv absent." }
Push-Location $Root
try {
    & $Python -m PyInstaller --noconfirm --clean --windowed --name "Visual AI Studio" `
        --collect-all keyring --collect-all visual_ai_studio `
        --add-data "src\visual_ai_studio\resources;visual_ai_studio\resources" `
        "src\visual_ai_studio\main.py"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
