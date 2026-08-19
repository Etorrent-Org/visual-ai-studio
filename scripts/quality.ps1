$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Environnement .venv absent." }
& $Python -m ruff check "$Root\src" "$Root\tests"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m mypy "$Root\src"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

