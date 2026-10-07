param([ValidateSet('api','web','test','migrate')][string]$Service = 'api')
# Explicit foreground service: run API and web in separate terminals.
& (Join-Path $PSScriptRoot 'scripts/dev.ps1') -Service $Service
exit $LASTEXITCODE
