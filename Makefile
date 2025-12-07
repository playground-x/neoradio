# Makefile for NeoRadio
# Note: On Windows, use Git Bash, WSL, or run npm scripts directly (npm run security)

.PHONY: help security security-fix security-python security-all test clean install

help:
	@echo "NeoRadio Security & Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Security Commands:"
	@echo "  make security          - Run npm audit for Node.js dependencies"
	@echo "  make security-fix      - Auto-fix npm vulnerabilities"
	@echo "  make security-python   - Check Python dependencies with pip check + safety"
	@echo "  make security-all      - Run all security scans (npm + Python)"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install           - Install all dependencies (Python + Node)"
	@echo "  make test              - Run all tests"
	@echo "  make clean             - Remove generated files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-dev        - Start development environment"
	@echo "  make docker-prod       - Start production environment"
	@echo "  make docker-down       - Stop all containers"
	@echo ""
	@echo "Windows Users: If make is not installed, use npm scripts:"
	@echo "  npm run security       - Same as 'make security'"
	@echo "  npm run security:all   - Same as 'make security-all'"

# Security targets
security:
	@echo "Running npm audit..."
	npm audit --audit-level=moderate

security-fix:
	@echo "Attempting to fix npm vulnerabilities..."
	npm audit fix

security-python:
	@echo "Checking Python dependencies..."
	python -m pip check
	@echo ""
	@echo "Running Python security scan..."
	python security_scan.py

security-all: security security-python
	@echo ""
	@echo "=== Security Scan Complete ==="

# Installation targets
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo ""
	@echo "Installing Node.js dependencies (if any)..."
	npm install

# Testing targets
test:
	@echo "Running Python tests..."
	python -m pytest -v
	@echo ""
	@echo "Running test coverage..."
	python -m pytest --cov=app --cov-report=term

# Docker targets
docker-dev:
	docker-compose up dev

docker-prod:
	docker-compose up -d postgres app nginx

docker-down:
	docker-compose down

# Cleanup targets
clean:
	@echo "Cleaning up generated files..."
	rm -f security-report.json
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -f .coverage
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete"
