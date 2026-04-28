# Windows AI Assistant - Test Runner Script
# Runs all tests and generates a report

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Windows AI Assistant - Test Runner" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
Write-Host "Checking pytest installation..." -ForegroundColor Yellow
try {
    $pytestVersion = pytest --version 2>&1
    Write-Host "✓ pytest found: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pytest not found. Installing..." -ForegroundColor Yellow
    python -m pip install pytest pytest-cov
    Write-Host "✓ pytest installed" -ForegroundColor Green
}

# Run tests with coverage
Write-Host ""
Write-Host "Running tests with coverage..." -ForegroundColor Yellow
python -m pytest tests/ -v --tb=short --cov=src/windows_ai --cov-report=term-missing --cov-report=html

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for details" -ForegroundColor Yellow
}

# Generate summary
Write-Host ""
Write-Host "Test Summary:" -ForegroundColor Cyan
Write-Host "-" * 60 -ForegroundColor Cyan

# Count test files
$testFiles = Get-ChildItem -Path tests -Filter test_*.py
Write-Host "Test files: $($testFiles.Count)" -ForegroundColor White

# Count test functions
$testCount = 0
foreach ($file in $testFiles) {
    $content = Get-Content $file.FullName -Raw
    $testMatches = [regex]::Matches($content, 'def test_\w+\(')
    $testCount += $testMatches.Count
}
Write-Host "Test functions: $testCount" -ForegroundColor White

Write-Host ""
Write-Host "Done." -ForegroundColor Green
