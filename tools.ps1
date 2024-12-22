param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "`nAvailable commands:" -ForegroundColor Cyan
    Write-Host "help    - Show this help message"
    Write-Host "install - Install dependencies"
    Write-Host "dev     - Start development environment"
    Write-Host "prod    - Start production environment"
    Write-Host "test    - Run tests"
    Write-Host "lint    - Check code style"
    Write-Host "clean   - Clean temporary files"
    Write-Host "db      - Database migration`n"
}

switch ($Command) {
    "install" {
        Write-Host "Installing dependencies..." -ForegroundColor Green
        pip install -r backend/requirements.txt
        pip install -r backend/requirements-dev.txt
        Set-Location frontend
        npm install
        Set-Location ..
    }
    "dev" {
        Write-Host "Starting development environment..." -ForegroundColor Green
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    }
    "prod" {
        Write-Host "Starting production environment..." -ForegroundColor Green
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    }
    "test" {
        Write-Host "Running tests..." -ForegroundColor Green
        pytest backend/tests
    }
    "lint" {
        Write-Host "Checking code style..." -ForegroundColor Green
        flake8 backend
        black backend --check
        mypy backend
    }
    "clean" {
        Write-Host "Cleaning temporary files..." -ForegroundColor Green
        Get-ChildItem -Path . -Include "__pycache__" -Recurse | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Include "*.pyc", "*.pyo", "*.pyd" -Recurse | Remove-Item -Force
    }
    "db" {
        Write-Host "Running database migration..." -ForegroundColor Green
        Set-Location backend
        alembic upgrade head
        Set-Location ..
    }
    default {
        Show-Help
    }
} 