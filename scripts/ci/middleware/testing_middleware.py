"""
Testing Middleware
=================

Middleware for test execution and reporting.
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test execution result."""

    name: str
    passed: bool
    message: str
    details: dict[str, Any]


class TestingMiddleware:
    """Middleware for testing operations."""

    def __init__(self):
        """Initialize testing middleware."""
        self.test_results: list[TestResult] = []

    def process(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Process testing operations."""
        logger.info("Running testing middleware...")

        try:
            # Run different types of tests
            self.run_unit_tests(ctx)
            self.check_test_coverage(ctx)
            self.run_linting(ctx)

            ctx["testing_middleware_completed"] = True
            ctx["test_results"] = [
                {
                    "name": result.name,
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details,
                }
                for result in self.test_results
            ]

        except Exception as e:
            logger.error(f"Testing middleware failed: {e}")
            ctx["testing_middleware_error"] = str(e)

        return ctx

    def run_unit_tests(self, ctx: dict[str, Any]) -> None:
        """Run unit tests."""
        try:
            project_root = Path.cwd()
            tests_dir = project_root / "tests"

            if not tests_dir.exists():
                self.test_results.append(
                    TestResult(
                        name="unit_tests",
                        passed=False,
                        message="No tests directory found",
                        details={"tests_dir": str(tests_dir)},
                    )
                )
                return

            # Try to run pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tests_dir), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.test_results.append(
                    TestResult(
                        name="unit_tests",
                        passed=True,
                        message="All unit tests passed",
                        details={"output": result.stdout, "tests_dir": str(tests_dir)},
                    )
                )
            else:
                self.test_results.append(
                    TestResult(
                        name="unit_tests",
                        passed=False,
                        message="Some unit tests failed",
                        details={
                            "output": result.stdout,
                            "error": result.stderr,
                            "tests_dir": str(tests_dir),
                        },
                    )
                )

        except subprocess.TimeoutExpired:
            self.test_results.append(
                TestResult(
                    name="unit_tests",
                    passed=False,
                    message="Unit tests timed out",
                    details={"timeout": 300},
                )
            )
        except FileNotFoundError:
            self.test_results.append(
                TestResult(
                    name="unit_tests",
                    passed=False,
                    message="pytest not available",
                    details={"error": "pytest module not found"},
                )
            )
        except Exception as e:
            self.test_results.append(
                TestResult(
                    name="unit_tests",
                    passed=False,
                    message=f"Could not run unit tests: {e}",
                    details={"error": str(e)},
                )
            )

    def check_test_coverage(self, ctx: dict[str, Any]) -> None:
        """Check test coverage."""
        try:
            project_root = Path.cwd()
            tests_dir = project_root / "tests"

            if not tests_dir.exists():
                self.test_results.append(
                    TestResult(
                        name="test_coverage",
                        passed=False,
                        message="No tests directory found for coverage check",
                        details={"tests_dir": str(tests_dir)},
                    )
                )
                return

            # Try to run coverage
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "coverage",
                    "run",
                    "-m",
                    "pytest",
                    str(tests_dir),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                # Get coverage report
                coverage_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if coverage_result.returncode == 0:
                    self.test_results.append(
                        TestResult(
                            name="test_coverage",
                            passed=True,
                            message="Test coverage calculated successfully",
                            details={
                                "coverage_report": coverage_result.stdout,
                                "tests_dir": str(tests_dir),
                            },
                        )
                    )
                else:
                    self.test_results.append(
                        TestResult(
                            name="test_coverage",
                            passed=False,
                            message="Could not generate coverage report",
                            details={"error": coverage_result.stderr},
                        )
                    )
            else:
                self.test_results.append(
                    TestResult(
                        name="test_coverage",
                        passed=False,
                        message="Coverage run failed",
                        details={"error": result.stderr},
                    )
                )

        except subprocess.TimeoutExpired:
            self.test_results.append(
                TestResult(
                    name="test_coverage",
                    passed=False,
                    message="Test coverage check timed out",
                    details={"timeout": 300},
                )
            )
        except FileNotFoundError:
            self.test_results.append(
                TestResult(
                    name="test_coverage",
                    passed=False,
                    message="coverage module not available",
                    details={"error": "coverage module not found"},
                )
            )
        except Exception as e:
            self.test_results.append(
                TestResult(
                    name="test_coverage",
                    passed=False,
                    message=f"Could not check test coverage: {e}",
                    details={"error": str(e)},
                )
            )

    def run_linting(self, ctx: dict[str, Any]) -> None:
        """Run code linting."""
        try:
            project_root = Path.cwd()
            python_files = list(project_root.rglob("*.py"))

            if not python_files:
                self.test_results.append(
                    TestResult(
                        name="linting",
                        passed=False,
                        message="No Python files found for linting",
                        details={"project_root": str(project_root)},
                    )
                )
                return

            # Try to run flake8
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    "--max-line-length=88",
                    str(project_root),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.test_results.append(
                    TestResult(
                        name="linting",
                        passed=True,
                        message="No linting issues found",
                        details={
                            "files_checked": len(python_files),
                            "project_root": str(project_root),
                        },
                    )
                )
            else:
                self.test_results.append(
                    TestResult(
                        name="linting",
                        passed=False,
                        message="Linting issues found",
                        details={
                            "output": result.stdout,
                            "files_checked": len(python_files),
                        },
                    )
                )

        except subprocess.TimeoutExpired:
            self.test_results.append(
                TestResult(
                    name="linting",
                    passed=False,
                    message="Linting check timed out",
                    details={"timeout": 60},
                )
            )
        except FileNotFoundError:
            self.test_results.append(
                TestResult(
                    name="linting",
                    passed=False,
                    message="flake8 not available, skipping linting",
                    details={"error": "flake8 module not found"},
                )
            )
        except Exception as e:
            self.test_results.append(
                TestResult(
                    name="linting",
                    passed=False,
                    message=f"Could not run linting: {e}",
                    details={"error": str(e)},
                )
            )


__all__ = ["TestingMiddleware", "TestResult"]
