# Start Docker Desktop Service and Test
# Run this script as Administrator

Write-Host "=== Starting Docker Desktop Service ===" -ForegroundColor Cyan

# Start Docker Desktop Service
try {
    Start-Service -Name "com.docker.service"
    Write-Host "✓ Docker Desktop Service started successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to start Docker Desktop Service: $_" -ForegroundColor Red
    Write-Host "Try starting Docker Desktop from Start Menu instead" -ForegroundColor Yellow
}

# Wait for Docker to be ready
Write-Host "`nWaiting for Docker daemon to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test Docker
Write-Host "`n=== Testing Docker Installation ===" -ForegroundColor Cyan

Write-Host "`n1. Docker Version:" -ForegroundColor Yellow
docker --version

Write-Host "`n2. Docker Compose Version:" -ForegroundColor Yellow
docker compose version

Write-Host "`n3. Docker Info:" -ForegroundColor Yellow
docker info

Write-Host "`n=== Docker is ready for testing! ===" -ForegroundColor Green
