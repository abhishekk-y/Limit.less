param([ValidateSet('api','web','test','migrate')][string]$Service = 'api')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
if ($env:PYTHON_EXECUTABLE) { $pythonPath = $env:PYTHON_EXECUTABLE }
if (Test-Path -LiteralPath (Join-Path $projectRoot '.local/runtime-deps')) {
  $runtimePaths = @((Join-Path $projectRoot '.local/runtime-deps'), $projectRoot, (Join-Path $projectRoot 'apps/api'))
  if ($env:PYTHONPATH) { $runtimePaths += $env:PYTHONPATH }
  $env:PYTHONPATH = $runtimePaths -join [IO.Path]::PathSeparator
}
switch ($Service) {
  'api' {
    if (-not $env:LOCAL_AUTO_APPLY_ENABLED) { $env:LOCAL_AUTO_APPLY_ENABLED = 'true' }
    & $pythonPath -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
  }
  'web' { npm --prefix apps/web run dev }
  'test' { & $pythonPath -m pytest tests -q }
  'migrate' { Set-Location -LiteralPath (Join-Path $projectRoot 'apps/api'); & $pythonPath -m alembic upgrade head }
}
exit $LASTEXITCODE
