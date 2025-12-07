# Security Scanning Guide

This document explains how to run security scans for NeoRadio on Windows and other platforms.

## Overview

NeoRadio includes multiple security scanning tools:
- **npm audit** - Scans Node.js dependencies for known vulnerabilities
- **Python security scanner** - Checks Python dependencies with pip check and optional Safety package
- **Makefile** - For Linux/Mac/WSL users
- **PowerShell script** - Native Windows solution
- **npm scripts** - Cross-platform solution (recommended for Windows)

## Quick Start (Windows Users - Recommended)

### Using npm scripts (easiest):
```bash
# Run npm security audit
npm run security

# Run all security scans (npm + Python)
npm run security:all

# Fix npm vulnerabilities automatically
npm run security:fix

# Run Python security scan only
npm run security:python
```

### Using PowerShell:
```powershell
# Run npm security audit
.\security.ps1 security

# Run all security scans
.\security.ps1 security-all

# Fix npm vulnerabilities
.\security.ps1 security-fix

# Run Python security scan only
.\security.ps1 security-python
```

## For Linux/Mac/WSL/Git Bash Users

### Using Make:
```bash
# Show all available commands
make help

# Run npm security audit
make security

# Run all security scans
make security-all

# Fix npm vulnerabilities
make security-fix

# Run Python security scan only
make security-python
```

## Security Scanning Components

### 1. npm audit

Scans Node.js dependencies for known vulnerabilities using the npm registry database.

**What it checks:**
- Direct dependencies listed in package.json
- Transitive dependencies (dependencies of dependencies)
- Known CVEs and security advisories

**Output:**
- Vulnerability severity (low, moderate, high, critical)
- Affected packages and versions
- Recommendations for fixes

**Note:** Currently, NeoRadio has no npm dependencies, so npm audit will report "found 0 vulnerabilities" until frontend dependencies are added.

### 2. Python Security Scanner

Custom Python script that checks Python dependencies.

**What it checks:**
- Dependency conflicts (via `pip check`)
- Outdated packages
- Known vulnerabilities (via Safety package, if installed)
- Version pinning in requirements.txt

**Installing Safety (Optional but Recommended):**
```bash
pip install safety
```

Safety maintains a database of known security vulnerabilities in Python packages.

### 3. Output Example

```
╔══════════════════════════════════════════════════════════╗
║            NeoRadio Security Scanner                     ║
╚══════════════════════════════════════════════════════════╝

============================================================
Running pip check for dependency conflicts...
============================================================
✓ No dependency conflicts found

============================================================
Checking for outdated packages...
============================================================
✗ Found 2 outdated package(s):

Package              Current         Latest          Type
------------------------------------------------------------
flask                3.1.0           3.1.2           wheel
requests             2.31.0          2.32.5          wheel

============================================================
Checking for known vulnerabilities (using safety if available)...
============================================================
✓ No known vulnerabilities found

============================================================
Checking requirements.txt for version pinning...
============================================================
✓ All dependencies are pinned

============================================================
SECURITY SCAN SUMMARY
============================================================
✓ All security checks passed

⚠ Note: 2 package(s) have updates available
```

## Current Dependencies

### Python (requirements.txt)
- `flask==3.1.2` - Web framework
- `requests==2.32.5` - HTTP library
- `gunicorn==21.2.0` - WSGI server (production)
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `pytest==8.3.4` - Testing framework
- `pytest-cov==6.0.0` - Code coverage

### Node.js (package.json)
- Currently no runtime dependencies
- Only npm audit infrastructure

## Integration with CI/CD

### GitHub Actions (Automated)

NeoRadio includes **two automated GitHub Actions workflows** that run security scans:

#### 1. CI Workflow (`.github/workflows/ci.yml`)
Runs on every push and pull request:
- ✅ Unit tests with pytest
- ✅ npm audit for Node.js dependencies
- ✅ Python security scanner
- ✅ Code quality checks (flake8, black, isort)
- ✅ Docker build validation

**Status:** [![CI - Tests and Security](https://github.com/playground-x/neoradio/actions/workflows/ci.yml/badge.svg)](https://github.com/playground-x/neoradio/actions/workflows/ci.yml)

#### 2. Security Scan Workflow (`.github/workflows/security-scan.yml`)
Runs weekly (Monday 9 AM UTC) and on dependency changes:
- ✅ Comprehensive Python security (Safety + Bandit)
- ✅ npm audit with detailed reports
- ✅ CodeQL semantic analysis
- ✅ Dependency review (for PRs)
- 📊 Artifact reports (90-day retention)

**Status:** [![Security Scan](https://github.com/playground-x/neoradio/actions/workflows/security-scan.yml/badge.svg)](https://github.com/playground-x/neoradio/actions/workflows/security-scan.yml)

#### Viewing Results
1. Go to repository → **Actions** tab
2. Select workflow run
3. Download security reports from **Artifacts** section
4. View CodeQL results in **Security** → **Code scanning**

See [.github/workflows/README.md](.github/workflows/README.md) for complete CI/CD documentation.

### Manual CI/CD Integration Example

For other CI/CD platforms (GitLab CI, Jenkins, etc.):

```yaml
security-scan:
  script:
    - pip install -r requirements.txt
    - npm install
    - npm run security
    - python security_scan.py
```

## Troubleshooting

### "make: command not found" on Windows
- **Solution 1:** Use npm scripts instead: `npm run security`
- **Solution 2:** Use PowerShell script: `.\security.ps1 security`
- **Solution 3:** Install Git Bash and use make from there
- **Solution 4:** Install WSL (Windows Subsystem for Linux)

### "npm audit" shows no vulnerabilities but I have dependencies
This is normal if you don't have npm dependencies yet. The package.json is configured for security scanning infrastructure.

### "Safety package not installed"
This is optional. Install with:
```bash
pip install safety
```

### PowerShell script execution policy error
If you get an error about execution policy:
```powershell
# View current policy
Get-ExecutionPolicy

# Allow script execution for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Best Practices

1. **Run security scans regularly** - Before commits, before deployments
2. **Pin dependency versions** - Use `==` in requirements.txt, not `>=`
3. **Keep dependencies updated** - Balance security with stability
4. **Review audit reports** - Don't just auto-fix without understanding
5. **Use Safety for Python** - Install and run for vulnerability database checks
6. **Integrate with CI/CD** - Automate security scans in your pipeline

## Security Scanning Schedule

**Recommended:**
- Before every commit: `npm run security`
- Weekly: `npm run security:all`
- Before deployment: `npm run security:all`
- After updating dependencies: `npm run security:all`

## Additional Tools

For more comprehensive security scanning, consider:
- **Bandit** - Python code security linter (`pip install bandit`)
- **OWASP Dependency-Check** - Multi-language dependency scanner
- **Snyk** - Commercial security scanning platform (free tier available)
- **Dependabot** - GitHub's automated dependency updates

## Reporting Security Issues

If you discover a security vulnerability in NeoRadio:
1. Do NOT open a public issue
2. Email the maintainers directly
3. Provide details and steps to reproduce
4. Allow time for a fix before public disclosure
