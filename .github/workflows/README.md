# GitHub Actions Workflows

This directory contains the CI/CD workflows for NeoRadio.

## Workflows

### 1. CI - Tests and Security (`ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `feature-*` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs:**

#### Test Job
- Runs on Python 3.11 and 3.12 (matrix)
- Executes pytest with coverage reporting
- Uploads coverage to Codecov
- **Required for PR merge**

#### Security Jobs
- **Python Security**: Runs pip check and custom security scanner
- **npm Security**: Runs npm audit and generates reports
- Both jobs continue on error to not block PRs

#### Code Quality (Lint)
- Runs flake8, black, and isort
- Checks code formatting and style
- Continues on error (advisory only)

#### Docker Build
- Tests both development and production Docker images
- Uses GitHub Actions cache for faster builds
- Ensures Docker configurations are valid

#### CI Summary
- Aggregates results from all jobs
- Creates GitHub Actions summary

**Estimated Runtime:** 3-5 minutes

---

### 2. Security Scan (Scheduled) (`security-scan.yml`)

**Triggers:**
- Scheduled: Every Monday at 9:00 AM UTC
- Push to `main` when dependency files change
- Manual dispatch

**Jobs:**

#### Dependency Review
- Runs on pull requests only
- Checks for vulnerabilities in dependency changes
- Fails on moderate or higher severity

#### Python Security Analysis
- Runs pip check
- Custom security scanner
- **Safety**: Checks Python vulnerability database
- **Bandit**: Static code analysis for security issues
- Uploads reports as artifacts (90-day retention)

#### npm Security Analysis
- Runs npm audit at low threshold
- Generates detailed JSON reports
- Uploads reports as artifacts (90-day retention)

#### CodeQL Analysis
- GitHub's semantic code analysis
- Scans Python and JavaScript code
- Detects security vulnerabilities and code quality issues
- Results appear in Security tab

#### Security Summary
- Aggregates security scan results
- Lists available reports

**Estimated Runtime:** 5-8 minutes

---

## Artifacts

Workflows generate the following artifacts:

| Artifact | Workflow | Description | Retention |
|----------|----------|-------------|-----------|
| npm-audit-report | CI, Security Scan | npm vulnerability report (JSON) | 30/90 days |
| safety-report | Security Scan | Python vulnerability report (JSON) | 90 days |
| bandit-report | Security Scan | Python security analysis (JSON) | 90 days |
| coverage.xml | CI | Test coverage report | N/A (uploaded to Codecov) |

## Viewing Results

### GitHub Actions UI
1. Go to repository → Actions tab
2. Select workflow run
3. View job results and logs
4. Download artifacts from summary page

### Security Alerts
- CodeQL results: Repository → Security → Code scanning
- Dependabot alerts: Repository → Security → Dependabot

### Codecov
- Coverage reports: https://codecov.io/gh/playground-x/neoradio
- PR comments show coverage changes

## Workflow Status Badges

Add these badges to README.md:

```markdown
[![CI - Tests and Security](https://github.com/playground-x/neoradio/actions/workflows/ci.yml/badge.svg)](https://github.com/playground-x/neoradio/actions/workflows/ci.yml)
[![Security Scan](https://github.com/playground-x/neoradio/actions/workflows/security-scan.yml/badge.svg)](https://github.com/playground-x/neoradio/actions/workflows/security-scan.yml)
```

## Required Secrets

No secrets are currently required. Optional secrets:

| Secret | Purpose | Required |
|--------|---------|----------|
| CODECOV_TOKEN | Upload coverage to Codecov | No (works without for public repos) |

## Permissions

Workflows use these permissions:

- **CI**: Default (read repository, write checks)
- **Security Scan**:
  - `security-events: write` (for CodeQL)
  - `actions: read`
  - `contents: read`

## Troubleshooting

### CI Workflow Failing

**Tests failing:**
- Check pytest output in Test job logs
- Verify Python version compatibility
- Run tests locally: `pytest -v`

**Security scans blocking:**
- Security jobs set to `continue-on-error: true`
- Should not block PRs
- Check job configuration if blocking

**Docker build failing:**
- Check Dockerfile syntax
- Verify base image availability
- Test locally: `docker build -f Dockerfile .`

### Security Scan Workflow Issues

**CodeQL not running:**
- Requires `security-events: write` permission
- Check repository settings → Actions → General → Workflow permissions
- Enable "Read and write permissions"

**Safety/Bandit not installed:**
- Check pip install step in workflow
- Verify requirements.txt doesn't conflict

**Scheduled workflow not running:**
- GitHub may disable scheduled workflows on inactive repos
- Re-enable in Actions tab
- Trigger manually via workflow_dispatch

### Artifact Upload Failures

**Artifact not found:**
- Ensure file is generated before upload step
- Check file path is correct
- Use `if: always()` to upload even on failure

**Size limit exceeded:**
- GitHub Actions artifacts limited to 10GB total
- Individual file limit varies by plan
- Compress large reports

## Manual Workflow Triggers

All workflows support manual triggering:

1. Go to Actions tab
2. Select workflow (left sidebar)
3. Click "Run workflow" button
4. Select branch
5. Click "Run workflow"

## Local Testing

Test workflows locally with [act](https://github.com/nektos/act):

```bash
# Install act
# Windows (Chocolatey): choco install act-cli
# macOS: brew install act
# Linux: See GitHub releases

# Run CI workflow
act -W .github/workflows/ci.yml

# Run specific job
act -W .github/workflows/ci.yml -j test

# Run with secrets
act -W .github/workflows/ci.yml --secret-file .secrets
```

## Optimization Tips

1. **Cache Dependencies**
   - Python: Uses `cache: 'pip'` in setup-python
   - npm: Uses `cache: 'npm'` in setup-node
   - Docker: Uses GitHub Actions cache

2. **Matrix Testing**
   - Currently tests Python 3.11 and 3.12
   - Add more versions if needed in strategy.matrix

3. **Parallel Jobs**
   - All jobs run in parallel (no dependencies except summary)
   - Reduces total workflow time

4. **Conditional Execution**
   - Use `if` conditions to skip unnecessary jobs
   - Example: `if: github.event_name == 'pull_request'`

## Adding New Workflows

1. Create `.github/workflows/your-workflow.yml`
2. Follow existing workflow patterns
3. Test with manual trigger
4. Add status badge to README
5. Document in this file

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
