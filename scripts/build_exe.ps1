# Standalone Windows Distribution Packager for GODZIP
# Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  GODZIP Standalone Windows Packager" -ForegroundColor Cyan
Write-Host "  Author: Chandan Bagh (@cbagh0819-ctrl)" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

$PythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Error "Python 3 is required but not found in PATH."
    exit 1
}

# Ensure PyInstaller is installed
& "$PythonExe" -m pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    & "$PythonExe" -m pip install pyinstaller
}

Write-Host "Building standalone GODZIP.exe with PyInstaller..." -ForegroundColor Cyan

& "$PythonExe" -m PyInstaller `
    --clean `
    --noconfirm `
    --onefile `
    --name "GODZIP" `
    --add-data "godzip/assets;godzip/assets" `
    --hidden-import "PySide6.QtCore" `
    --hidden-import "PySide6.QtGui" `
    --hidden-import "PySide6.QtWidgets" `
    --hidden-import "cryptography" `
    --hidden-import "zstandard" `
    --hidden-import "lz4" `
    --hidden-import "brotli" `
    --hidden-import "py7zr" `
    --hidden-import "blake3" `
    godzip/main.py

if ($LASTEXITCODE -eq 0) {
    $ExePath = Join-Path (Get-Location) "dist\GODZIP.exe"
    if (Test-Path $ExePath) {
        $SizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
        Write-Host "==========================================================" -ForegroundColor Green
        Write-Host "  [SUCCESS] Standalone Executable Created!" -ForegroundColor Green
        Write-Host "  Path: $ExePath ($SizeMB MB)" -ForegroundColor Green
        Write-Host "  Ready for redistribution with zero dependencies." -ForegroundColor Gray
        Write-Host "==========================================================" -ForegroundColor Green
    }
} else {
    Write-Error "PyInstaller build failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}
