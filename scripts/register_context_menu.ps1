# PowerShell script to register GODZIP Windows Explorer Context Menu and File Associations
# Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)

Write-Host "Registering GODZIP Windows Explorer Context Menu..." -ForegroundColor Cyan

$PythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Error "Python 3 is not found in PATH. Please ensure Python is installed and in PATH."
    exit 1
}

& "$PythonExe" -m godzip.cli shell register

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] GODZIP Context Menu registered successfully!" -ForegroundColor Green
    Write-Host "You can now right-click any file/folder to compress, or right-click any .god file to extract or inspect." -ForegroundColor Gray
} else {
    Write-Error "Registration failed with code $LASTEXITCODE."
}
