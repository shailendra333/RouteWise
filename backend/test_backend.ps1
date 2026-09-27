# Backend Endpoint Tester
# Run this AFTER starting the backend to verify all endpoints are working

$baseUrl = "http://localhost:8000"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Backend Endpoint Tester" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$results = @()

function Test-Endpoint {
    param($name, $url)

    Write-Host "Testing: $name..." -NoNewline
    try {
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host " [OK]" -ForegroundColor Green
        return @{ Name = $name; Status = "OK"; Url = $url }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host " [FAIL] HTTP $statusCode" -ForegroundColor Red
        } else {
            Write-Host " [FAIL] Cannot connect" -ForegroundColor Red
        }
        return @{ Name = $name; Status = "FAIL"; Url = $url; Error = $_.Exception.Message }
    }
}

# Test endpoints
$results += Test-Endpoint "Health Check" "$baseUrl/api/health"
$results += Test-Endpoint "Database Stats" "$baseUrl/api/database-stats"
$results += Test-Endpoint "Traditional Agents Status" "$baseUrl/api/agents/status"
$results += Test-Endpoint "Traditional Agents Health" "$baseUrl/api/agents/health"
$results += Test-Endpoint "GenAI Agents Status" "$baseUrl/api/genai-agents/status"
$results += Test-Endpoint "GenAI Agents Health" "$baseUrl/api/genai-agents/health"
$results += Test-Endpoint "Agent Comparison" "$baseUrl/api/genai-agents/compare"
$results += Test-Endpoint "Performance Metrics" "$baseUrl/api/performance-metrics"
$results += Test-Endpoint "Analytics Data" "$baseUrl/api/analytics-data"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.Status -eq "OK" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$total = $results.Count

Write-Host ""
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failed -eq 0) {
    Write-Host "SUCCESS! All endpoints are working correctly." -ForegroundColor Green
    Write-Host "You can now use the frontend at http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "FAILED! Some endpoints are not responding." -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure backend is running in a separate terminal" -ForegroundColor Yellow
    Write-Host "2. Check: netstat -ano | findstr ':5000'" -ForegroundColor Yellow
    Write-Host "3. Look at backend terminal for errors" -ForegroundColor Yellow
    Write-Host "4. Try restarting the backend" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Failed endpoints:" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  - $($_.Name): $($_.Url)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

