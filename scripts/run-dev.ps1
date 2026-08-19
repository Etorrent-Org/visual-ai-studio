$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Environnement absent. Exécutez : python -m venv .venv puis .\.venv\Scripts\python.exe -m pip install -e '.[dev]'"
}
& $Python -m visual_ai_studio.main
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

