# ==========================================
# CONTRACT VERIFICATION: LM STUDIO API
# ==========================================
# Purpose: Verify upstream API behavior before touching application code.

param(
    [string]$BaseUrl = "http://localhost:1234",
    [string]$ModelID = "astral-4b-coder"
)

Write-Host "1. Testing Connection (GET /v1/models)..." -ForegroundColor Cyan
try {
    $models = Invoke-RestMethod -Method Get -Uri "$BaseUrl/v1/models" -ErrorAction Stop
    $count = if ($models -and $models.data) { $models.data.Count } else { 0 }
    Write-Host "   SUCCESS: Found $count models." -ForegroundColor Green
} catch {
    Write-Host "   FAIL: LM Studio not reachable at $BaseUrl" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Testing Load Contract (POST /v1/models/load)..." -ForegroundColor Cyan
try {
    $payload = @{
        model = $ModelID
        context_length = 8192
        gpu_offload_ratio = 1.0
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/models/load" -Body $payload -ContentType "application/json" -ErrorAction Stop
    if ($response.error) {
        Write-Host "   WARN: Model loaded but upstream returned error field: $($response.error)" -ForegroundColor Yellow
    } else {
        Write-Host "   SUCCESS: Model loaded." -ForegroundColor Green
    }
} catch {
    Write-Host "   FAIL: Load endpoint rejected request." -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n3. Testing Unload Contract (POST /v1/models/unload)..." -ForegroundColor Cyan
try {
    $payload = @{ model = $ModelID } | ConvertTo-Json
    $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/models/unload" -Body $payload -ContentType "application/json"

    if ($response -and $response.error -and $response.error -match "Unexpected endpoint") {
        Write-Host "   WARN: Upstream reports unload not supported: $($response.error)" -ForegroundColor Yellow
    } else {
        Write-Host "   SUCCESS: Model unloaded." -ForegroundColor Green
    }
} catch {
    Write-Host "   FAIL: Unload endpoint rejected request." -ForegroundColor Red
}
