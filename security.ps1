# PowerShell Security Scanner for NeoRadio (Windows-native alternative to Makefile)
# Usage: .\security.ps1 [command]
# Commands: security, security-fix, security-python, security-all, help

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "`nNeoRadio Security & Development Commands (PowerShell)" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan

    Write-Host "Security Commands:" -ForegroundColor Yellow
    Write-Host "  .\security.ps1 security          - Run npm audit for Node.js dependencies"
    Write-Host "  .\security.ps1 security-fix      - Auto-fix npm vulnerabilities"
    Write-Host "  .\security.ps1 security-python   - Check Python dependencies"
    Write-Host "  .\security.ps1 security-all      - Run all security scans (npm + Python)`n"

    Write-Host "Alternative - Use npm scripts directly:" -ForegroundColor Yellow
    Write-Host "  npm run security                 - Same as 'security' command"
    Write-Host "  npm run security:all             - Same as 'security-all' command`n"
}

function Run-Security {
    Write-Host "`nRunning npm audit..." -ForegroundColor Green
    npm audit --audit-level=moderate
}

function Run-SecurityFix {
    Write-Host "`nAttempting to fix npm vulnerabilities..." -ForegroundColor Green
    npm audit fix
}

function Run-SecurityPython {
    Write-Host "`nChecking Python dependencies..." -ForegroundColor Green
    python -m pip check
    Write-Host "`nRunning Python security scan..." -ForegroundColor Green
    python security_scan.py
}

function Run-SecurityAll {
    Write-Host "`n=== Running All Security Scans ===" -ForegroundColor Cyan
    Run-Security
    Run-SecurityPython
    Write-Host "`n=== Security Scan Complete ===" -ForegroundColor Cyan
}

# Main command router
switch ($Command.ToLower()) {
    "security" {
        Run-Security
    }
    "security-fix" {
        Run-SecurityFix
    }
    "security-python" {
        Run-SecurityPython
    }
    "security-all" {
        Run-SecurityAll
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
}
