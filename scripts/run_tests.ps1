# PowerShell script to execute the full GODZIP automated test suite
Write-Host "Running GODZIP Automated Test Suite..." -ForegroundColor Cyan
python -m pytest tests -v
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll GODZIP tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nTest failures detected." -ForegroundColor Red
}
exit $LASTEXITCODE
