# Quick Test Script for Tic-Tac-Toe Multiplayer
# This script tests the frontend-backend connectivity

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  TIC-TAC-TOE CONNECTIVITY TEST" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if Docker containers are running
Write-Host "[1/6] Checking Docker containers..." -ForegroundColor Yellow
$containers = docker compose ps --format json | ConvertFrom-Json
$backendRunning = $false
$frontendRunning = $false

foreach ($container in $containers) {
    if ($container.Service -eq "backend" -and $container.State -eq "running") {
        $backendRunning = $true
        Write-Host "  ✓ Backend container is running" -ForegroundColor Green
    }
    if ($container.Service -eq "frontend" -and $container.State -eq "running") {
        $frontendRunning = $true
        Write-Host "  ✓ Frontend container is running" -ForegroundColor Green
    }
}

if (-not $backendRunning) {
    Write-Host "  ✗ Backend container is NOT running" -ForegroundColor Red
    Write-Host "  Run: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

if (-not $frontendRunning) {
    Write-Host "  ✗ Frontend container is NOT running" -ForegroundColor Red
    Write-Host "  Run: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Backend Health Check
Write-Host "[2/6] Testing backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Host "  ✓ Backend is healthy" -ForegroundColor Green
        Write-Host "    Status: $($health.status)" -ForegroundColor Gray
        Write-Host "    Timestamp: $($health.timestamp)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Backend health check failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Cannot connect to backend" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Frontend Accessibility
Write-Host "[3/6] Testing frontend accessibility..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/public/index.html" -Method Get -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend is accessible" -ForegroundColor Green
        Write-Host "    Status Code: $($response.StatusCode)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Frontend returned status $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Cannot connect to frontend" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 4: User Registration
Write-Host "[4/6] Testing user registration..." -ForegroundColor Yellow
$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$testUser = "test$timestamp"
$testPass = "password123"
try {
    $regBody = @{
        username = $testUser
        password = $testPass
    } | ConvertTo-Json

    $regResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/register" -Method Post -Body $regBody -ContentType "application/json" -TimeoutSec 5
    
    if ($regResponse.access_token) {
        Write-Host "  ✓ User registration successful" -ForegroundColor Green
        Write-Host "    Username: $($regResponse.username)" -ForegroundColor Gray
        Write-Host "    User ID: $($regResponse.user_id)" -ForegroundColor Gray
        $token = $regResponse.access_token
    } else {
        Write-Host "  ✗ Registration failed - no token received" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Registration failed" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 5: User Login
Write-Host "[5/6] Testing user login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = $testUser
        password = $testPass
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/login" -Method Post -Body $loginBody -ContentType "application/json" -TimeoutSec 5
    
    if ($loginResponse.access_token) {
        Write-Host "  ✓ User login successful" -ForegroundColor Green
        Write-Host "    Token received" -ForegroundColor Gray
        $token = $loginResponse.access_token
    } else {
        Write-Host "  ✗ Login failed - no token received" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Login failed" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 6: Get User Profile
Write-Host "[6/6] Testing user profile retrieval..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }

    $profile = Invoke-RestMethod -Uri "http://localhost:8000/api/users/me" -Method Get -Headers $headers -TimeoutSec 5
    
    if ($profile.username) {
        Write-Host "  ✓ Profile retrieved successfully" -ForegroundColor Green
        Write-Host "    Username: $($profile.username)" -ForegroundColor Gray
        Write-Host "    Total Games: $($profile.total_games)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Profile retrieval failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Profile retrieval failed" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  ✓ ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend-Backend connectivity is working correctly!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8080/public/index.html to test the UI" -ForegroundColor White
Write-Host "  2. Open http://localhost:8080/test_frontend_backend.html for interactive tests" -ForegroundColor White
Write-Host "  3. Check TESTING_GUIDE.md for complete testing instructions" -ForegroundColor White
Write-Host ""
