$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Sense Atlas: http://127.0.0.1:8785'
python -m http.server 8785 --bind 127.0.0.1 --directory dist
