# Windows AI Assistant - One-Click Installation Script
# Run as Administrator for best results

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Windows AI Assistant - Installation" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check if Python version is 3.11+
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        Write-Host "✗ Python 3.11+ required. Current version: $pythonVersion" -ForegroundColor Red
        exit 1
    }
}

# Install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check Ollama
Write-Host ""
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Ollama not found. Installing..." -ForegroundColor Yellow
    Write-Host "Visit https://ollama.ai/ to install Ollama" -ForegroundColor Cyan
    Write-Host "After installation, run: ollama serve && ollama pull gemma3:4b" -ForegroundColor Cyan
}

# Create logs directory
Write-Host ""
Write-Host "Creating logs directory..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✓ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "✓ Logs directory already exists" -ForegroundColor Green
}

# Copy example config if not exists
Write-Host ""
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path "src/windows_ai/config.yaml")) {
    if (Test-Path "examples/config_example.yaml") {
        Copy-Item "examples/config_example.yaml" "src/windows_ai/config.yaml"
        Write-Host "✓ Configuration file created from example" -ForegroundColor Green
        Write-Host "  Edit src/windows_ai/config.yaml to customize settings" -ForegroundColor Cyan
    }
} else {
    Write-Host "✓ Configuration file already exists" -ForegroundColor Green
}

# Run tests
Write-Host ""
Write-Host "Running tests..." -ForegroundColor Yellow
try {
    python -m pytest tests/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All tests passed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Some tests failed. Check output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not run tests (pytest may not be installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "2. Pull model: ollama pull gemma3:4b" -ForegroundColor White
Write-Host "3. Run quick start: python examples/quick_start.py" -ForegroundColor White
Write-Host "4. Read README.md for full documentation" -ForegroundColor White
Write-Host ""
