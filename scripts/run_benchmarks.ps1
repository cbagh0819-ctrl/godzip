# PowerShell script to execute the 14-category GODZIP benchmark suite
Write-Host "Running GODZIP 14-Category Benchmark Suite..." -ForegroundColor Cyan
python -m benchmark.benchmark
Write-Host "`nBenchmark finished. Reports are available in benchmark\reports\" -ForegroundColor Green
