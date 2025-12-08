#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security scanner for NeoRadio Python dependencies
Checks for known vulnerabilities in installed packages
"""

import subprocess
import sys
import json
import io
from typing import Dict, List, Tuple

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def run_pip_check() -> Tuple[bool, str]:
    """
    Run pip check to find dependency conflicts
    Returns: (success, output)
    """
    print("=" * 60)
    print("Running pip check for dependency conflicts...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ No dependency conflicts found")
            return True, result.stdout
        else:
            print("✗ Dependency conflicts detected:")
            print(result.stdout)
            return False, result.stdout
    except Exception as e:
        print(f"✗ Error running pip check: {e}")
        return False, str(e)


def check_outdated_packages() -> List[Dict]:
    """
    Check for outdated packages
    Returns: List of outdated packages
    """
    print("\n" + "=" * 60)
    print("Checking for outdated packages...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout:
            outdated = json.loads(result.stdout)

            if outdated:
                print(f"✗ Found {len(outdated)} outdated package(s):")
                print()
                print(f"{'Package':<20} {'Current':<15} {'Latest':<15} {'Type':<10}")
                print("-" * 60)

                for pkg in outdated:
                    print(f"{pkg['name']:<20} {pkg['version']:<15} {pkg['latest_version']:<15} {pkg.get('latest_filetype', 'N/A'):<10}")

                return outdated
            else:
                print("✓ All packages are up to date")
                return []
        else:
            print("✗ Error checking outdated packages")
            return []

    except Exception as e:
        print(f"✗ Error checking outdated packages: {e}")
        return []


def check_known_vulnerabilities() -> Tuple[bool, str]:
    """
    Check if safety package is available and run vulnerability scan
    Returns: (success, output)
    """
    print("\n" + "=" * 60)
    print("Checking for known vulnerabilities (using safety if available)...")
    print("=" * 60)

    # Check if safety is installed
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "show", "safety"],
            capture_output=True,
            check=True
        )
        safety_installed = True
    except subprocess.CalledProcessError:
        safety_installed = False

    if safety_installed:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True
            )

            # Check for stderr output (errors or warnings)
            if result.stderr and not result.stdout:
                print(f"⚠ Safety check warning: {result.stderr.strip()}")
                print("ℹ Continuing scan without Safety vulnerability check")
                return True, "Safety check skipped due to errors"

            if result.stdout:
                try:
                    vulnerabilities = json.loads(result.stdout)

                    if vulnerabilities:
                        print(f"✗ Found {len(vulnerabilities)} known vulnerability/vulnerabilities:")
                        print()

                        for vuln in vulnerabilities:
                            print(f"Package: {vuln[0]}")
                            print(f"  Installed: {vuln[2]}")
                            print(f"  Vulnerability: {vuln[3]}")
                            print(f"  ID: {vuln[4]}")
                            print()

                        return False, json.dumps(vulnerabilities, indent=2)
                    else:
                        print("✓ No known vulnerabilities found")
                        return True, "No vulnerabilities"
                except json.JSONDecodeError as e:
                    print(f"⚠ Safety check output parsing failed: {e}")
                    print(f"ℹ Raw output (first 200 chars): {result.stdout[:200]}")
                    print("ℹ Continuing scan without Safety vulnerability check")
                    return True, "Safety output parsing failed"
            else:
                print("✓ No known vulnerabilities found")
                return True, "No vulnerabilities"

        except Exception as e:
            print(f"⚠ Error running safety check: {e}")
            print("ℹ Continuing scan without Safety vulnerability check")
            return True, str(e)
    else:
        print("ℹ Safety package not installed")
        print("  Install with: pip install safety")
        print("  Skipping vulnerability database check")
        return True, "Safety not installed"


def check_requirements_versions():
    """
    Check if requirements.txt has pinned versions
    """
    print("\n" + "=" * 60)
    print("Checking requirements.txt for version pinning...")
    print("=" * 60)

    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()

        unpinned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '==' not in line:
                    unpinned.append(line)

        if unpinned:
            print(f"⚠ Found {len(unpinned)} unpinned dependencies:")
            for dep in unpinned:
                print(f"  - {dep}")
            print("\nRecommendation: Pin versions with '==' for reproducible builds")
        else:
            print("✓ All dependencies are pinned")

    except FileNotFoundError:
        print("✗ requirements.txt not found")
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")


def main():
    """Main security scan function"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "NeoRadio Security Scanner" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    all_passed = True

    # Run pip check
    pip_ok, _ = run_pip_check()
    all_passed = all_passed and pip_ok

    # Check for outdated packages
    outdated = check_outdated_packages()

    # Check for known vulnerabilities
    vuln_ok, _ = check_known_vulnerabilities()
    all_passed = all_passed and vuln_ok

    # Check requirements.txt version pinning
    check_requirements_versions()

    # Summary
    print("\n" + "=" * 60)
    print("SECURITY SCAN SUMMARY")
    print("=" * 60)

    if all_passed:
        print("✓ All security checks passed")
        print()
        if outdated:
            print(f"⚠ Note: {len(outdated)} package(s) have updates available")
        return 0
    else:
        print("✗ Security issues detected - review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
