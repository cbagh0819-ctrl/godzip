# PowerShell script to unregister GODZIP Windows Explorer Context Menu
# Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)

Write-Host "Unregistering GODZIP Windows Explorer Context Menu..." -ForegroundColor Yellow

$PythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Error "Python 3 is not found in PATH."
    exit 1
}

& "$PythonExe" -m godzip.cli shell unregister

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] GODZIP Context Menu unregistered successfully." -ForegroundColor Green
} else {
    Write-Error "Unregistration failed with code $LASTEXITCODE."
}
