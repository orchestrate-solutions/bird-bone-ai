"""
Security Middleware
==================

Middleware for handling security scanning, enforcement, and compliance checks.
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SecurityCheck:
    """Security check result."""

    name: str
    passed: bool
    message: str
    details: dict[str, Any]


class SecurityMiddleware:
    """Middleware for security operations."""

    def __init__(self):
        """Initialize security middleware."""
        self.checks_performed: list[SecurityCheck] = []

    def process(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Process security checks."""
        logger.info("Running security middleware...")

        try:
            # Run basic security checks
            self.check_dependencies_security(ctx)
            self.check_file_permissions(ctx)
            self.check_secrets_exposure(ctx)

            ctx["security_middleware_completed"] = True
            ctx["security_checks"] = [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                    "details": check.details,
                }
                for check in self.checks_performed
            ]

        except Exception as e:
            logger.error(f"Security middleware failed: {e}")
            ctx["security_middleware_error"] = str(e)

        return ctx

    def check_dependencies_security(self, ctx: dict[str, Any]) -> None:
        """Check for known security vulnerabilities in dependencies."""
        try:
            # Try to run safety check
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.checks_performed.append(
                    SecurityCheck(
                        name="dependency_security",
                        passed=True,
                        message="No known security vulnerabilities found in dependencies",
                        details={"output": result.stdout},
                    )
                )
            else:
                self.checks_performed.append(
                    SecurityCheck(
                        name="dependency_security",
                        passed=False,
                        message="Security vulnerabilities found in dependencies",
                        details={"output": result.stdout, "error": result.stderr},
                    )
                )

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.checks_performed.append(
                SecurityCheck(
                    name="dependency_security",
                    passed=False,
                    message=f"Could not run dependency security check: {e}",
                    details={"error": str(e)},
                )
            )

    def check_file_permissions(self, ctx: dict[str, Any]) -> None:
        """Check for proper file permissions."""
        try:
            project_root = Path.cwd()
            sensitive_files = [".env", ".env.local", "secrets.json", "private_key.pem"]

            issues = []
            for file_name in sensitive_files:
                file_path = project_root / file_name
                if file_path.exists():
                    stat = file_path.stat()
                    # Check if file is readable by others (octal 4)
                    if stat.st_mode & 0o004:
                        issues.append(f"{file_name} is readable by others")

            if not issues:
                self.checks_performed.append(
                    SecurityCheck(
                        name="file_permissions",
                        passed=True,
                        message="File permissions are secure",
                        details={"checked_files": sensitive_files},
                    )
                )
            else:
                self.checks_performed.append(
                    SecurityCheck(
                        name="file_permissions",
                        passed=False,
                        message="Insecure file permissions detected",
                        details={"issues": issues},
                    )
                )

        except Exception as e:
            self.checks_performed.append(
                SecurityCheck(
                    name="file_permissions",
                    passed=False,
                    message=f"Could not check file permissions: {e}",
                    details={"error": str(e)},
                )
            )

    def check_secrets_exposure(self, ctx: dict[str, Any]) -> None:
        """Check for exposed secrets in code."""
        try:
            # Simple pattern matching for common secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret_key\s*=\s*["\'][^"\']{20,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']',
            ]

            project_root = Path.cwd()
            python_files = list(project_root.rglob("*.py"))

            potential_secrets = []
            for file_path in python_files:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            import re

                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                potential_secrets.append(
                                    {
                                        "file": str(file_path),
                                        "line": content[: match.start()].count("\n")
                                        + 1,
                                        "pattern": pattern,
                                    }
                                )
                except Exception:
                    continue

            if not potential_secrets:
                self.checks_performed.append(
                    SecurityCheck(
                        name="secrets_exposure",
                        passed=True,
                        message="No potential secrets found in source code",
                        details={"files_checked": len(python_files)},
                    )
                )
            else:
                self.checks_performed.append(
                    SecurityCheck(
                        name="secrets_exposure",
                        passed=False,
                        message=f"Found {len(potential_secrets)} potential secrets in source code",
                        details={"potential_secrets": potential_secrets},
                    )
                )

        except Exception as e:
            self.checks_performed.append(
                SecurityCheck(
                    name="secrets_exposure",
                    passed=False,
                    message=f"Could not check for secrets exposure: {e}",
                    details={"error": str(e)},
                )
            )


__all__ = ["SecurityMiddleware", "SecurityCheck"]
