"""
Validate CI/CD Operations
========================

Comprehensive validation of CI/CD pipeline operations including:
- Pipeline health checks
- Security configuration validation
- Environment setup verification
- Testing pipeline validation
- Deployment readiness assessment
"""

import json
import logging

# Import our CI/CD modules
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Union

# Add the scripts directory to Python path for imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import configure_security_settings
import setup_environment_validation
import setup_testing_pipeline
from middleware import (
    deployment_middleware,
    security_middleware,
    testing_middleware,
    validation_middleware,
)

Ctx = dict[str, Any]

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status levels."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    component: str
    check: str
    status: ValidationStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class CICDValidator:
    """Comprehensive CI/CD pipeline validator."""

    def __init__(self, project_root: Union[Path, None] = None):
        """Initialize the validator."""
        self.project_root = project_root or Path.cwd()
        self.results: list[ValidationResult] = []

        # Initialize middleware components
        self.security_middleware = security_middleware.SecurityMiddleware()
        self.validation_middleware = validation_middleware.ValidationMiddleware()
        self.testing_middleware = testing_middleware.TestingMiddleware()
        self.deployment_middleware = deployment_middleware.DeploymentMiddleware()

    def add_result(
        self,
        component: str,
        check: str,
        status: ValidationStatus,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """Add a validation result."""
        result = ValidationResult(
            component=component,
            check=check,
            status=status,
            message=message,
            details=details or {},
        )
        self.results.append(result)

        # Log the result
        level = (
            logging.INFO
            if status == ValidationStatus.PASSED
            else (
                logging.WARNING if status == ValidationStatus.WARNING else logging.ERROR
            )
        )
        logger.log(level, f"{component}.{check}: {message}")

    def validate_project_structure(self) -> None:
        """Validate basic project structure."""
        logger.info("Validating project structure...")

        required_files = [
            "pyproject.toml",
            "requirements.txt",
            ".github/workflows",
            "tests",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.add_result(
                    "project_structure",
                    f"file_{file_path.replace('/', '_')}",
                    ValidationStatus.PASSED,
                    f"Found {file_path}",
                )
            else:
                self.add_result(
                    "project_structure",
                    f"file_{file_path.replace('/', '_')}",
                    ValidationStatus.WARNING,
                    f"Missing {file_path}",
                )

    def validate_ci_cd_scripts(self) -> None:
        """Validate CI/CD scripts exist and are importable."""
        logger.info("Validating CI/CD scripts...")

        scripts_dir = self.project_root / "scripts" / "ci"
        required_scripts = [
            "configure_security_settings.py",
            "setup_environment_validation.py",
            "setup_testing_pipeline.py",
            "validate_ci_cd_operations.py",
        ]

        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                try:
                    # Test if the script is syntactically valid
                    with open(script_path) as f:
                        compile(f.read(), script_path, "exec")
                    self.add_result(
                        "ci_cd_scripts",
                        script.replace(".py", ""),
                        ValidationStatus.PASSED,
                        f"Script {script} is valid",
                    )
                except SyntaxError as e:
                    self.add_result(
                        "ci_cd_scripts",
                        script.replace(".py", ""),
                        ValidationStatus.FAILED,
                        f"Syntax error in {script}: {e}",
                    )
            else:
                self.add_result(
                    "ci_cd_scripts",
                    script.replace(".py", ""),
                    ValidationStatus.FAILED,
                    f"Missing script: {script}",
                )

    def validate_middleware_components(self) -> None:
        """Validate middleware components."""
        logger.info("Validating middleware components...")

        middlewares = [
            ("security", self.security_middleware),
            ("validation", self.validation_middleware),
            ("testing", self.testing_middleware),
            ("deployment", self.deployment_middleware),
        ]

        for name, middleware in middlewares:
            try:
                # Test middleware initialization
                if hasattr(middleware, "process"):
                    self.add_result(
                        "middleware",
                        name,
                        ValidationStatus.PASSED,
                        f"{name} middleware initialized successfully",
                    )
                else:
                    self.add_result(
                        "middleware",
                        name,
                        ValidationStatus.WARNING,
                        f"{name} middleware missing process method",
                    )
            except Exception as e:
                self.add_result(
                    "middleware",
                    name,
                    ValidationStatus.FAILED,
                    f"{name} middleware failed: {e}",
                )

    def validate_environment_setup(self) -> None:
        """Validate environment setup using our validation module."""
        logger.info("Validating environment setup...")

        try:
            ctx = {}
            validated_ctx = setup_environment_validation.setup_environment_validation(
                ctx
            )

            if validated_ctx.get("environment_validated"):
                self.add_result(
                    "environment",
                    "validation",
                    ValidationStatus.PASSED,
                    "Environment validation passed",
                    validated_ctx,
                )
            else:
                self.add_result(
                    "environment",
                    "validation",
                    ValidationStatus.WARNING,
                    "Environment validation had issues",
                    validated_ctx,
                )
        except Exception as e:
            self.add_result(
                "environment",
                "validation",
                ValidationStatus.FAILED,
                f"Environment validation failed: {e}",
            )

    def validate_security_configuration(self) -> None:
        """Validate security configuration."""
        logger.info("Validating security configuration...")

        try:
            ctx = {}
            secured_ctx = configure_security_settings.configure_security_settings(ctx)

            if secured_ctx.get("security_configured"):
                self.add_result(
                    "security",
                    "configuration",
                    ValidationStatus.PASSED,
                    "Security configuration completed",
                    secured_ctx,
                )
            else:
                self.add_result(
                    "security",
                    "configuration",
                    ValidationStatus.WARNING,
                    "Security configuration incomplete",
                    secured_ctx,
                )
        except Exception as e:
            self.add_result(
                "security",
                "configuration",
                ValidationStatus.FAILED,
                f"Security configuration failed: {e}",
            )

    def validate_testing_pipeline(self) -> None:
        """Validate testing pipeline setup."""
        logger.info("Validating testing pipeline...")

        try:
            ctx = {}
            tested_ctx = setup_testing_pipeline.setup_testing_pipeline(ctx)

            if tested_ctx.get("testing_pipeline_setup"):
                self.add_result(
                    "testing",
                    "pipeline_setup",
                    ValidationStatus.PASSED,
                    "Testing pipeline setup completed",
                    tested_ctx,
                )
            else:
                self.add_result(
                    "testing",
                    "pipeline_setup",
                    ValidationStatus.WARNING,
                    "Testing pipeline setup incomplete",
                    tested_ctx,
                )
        except Exception as e:
            self.add_result(
                "testing",
                "pipeline_setup",
                ValidationStatus.FAILED,
                f"Testing pipeline setup failed: {e}",
            )

    def validate_github_workflows(self) -> None:
        """Validate GitHub Actions workflows."""
        logger.info("Validating GitHub workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.add_result(
                "github",
                "workflows_dir",
                ValidationStatus.WARNING,
                "No .github/workflows directory found",
            )
            return

        workflow_files = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )

        if not workflow_files:
            self.add_result(
                "github",
                "workflow_files",
                ValidationStatus.WARNING,
                "No GitHub workflow files found",
            )
            return

        for workflow_file in workflow_files:
            try:
                import yaml

                with open(workflow_file) as f:
                    workflow_data = yaml.safe_load(f)

                # Basic validation
                if "on" in workflow_data and "jobs" in workflow_data:
                    self.add_result(
                        "github",
                        f"workflow_{workflow_file.stem}",
                        ValidationStatus.PASSED,
                        f"Workflow {workflow_file.name} is valid",
                    )
                else:
                    self.add_result(
                        "github",
                        f"workflow_{workflow_file.stem}",
                        ValidationStatus.WARNING,
                        f"Workflow {workflow_file.name} missing required sections",
                    )
            except Exception as e:
                self.add_result(
                    "github",
                    f"workflow_{workflow_file.stem}",
                    ValidationStatus.FAILED,
                    f"Invalid workflow {workflow_file.name}: {e}",
                )

    def validate_dependencies(self) -> None:
        """Validate project dependencies."""
        logger.info("Validating dependencies...")

        # Check requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file) as f:
                    requirements = f.read().strip()
                if requirements:
                    self.add_result(
                        "dependencies",
                        "requirements_txt",
                        ValidationStatus.PASSED,
                        "requirements.txt exists and has content",
                    )
                else:
                    self.add_result(
                        "dependencies",
                        "requirements_txt",
                        ValidationStatus.WARNING,
                        "requirements.txt is empty",
                    )
            except Exception as e:
                self.add_result(
                    "dependencies",
                    "requirements_txt",
                    ValidationStatus.FAILED,
                    f"Error reading requirements.txt: {e}",
                )
        else:
            self.add_result(
                "dependencies",
                "requirements_txt",
                ValidationStatus.WARNING,
                "No requirements.txt found",
            )

        # Check pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import tomli

                with open(pyproject_file, "rb") as f:
                    pyproject_data = tomli.load(f)

                if "project" in pyproject_data or "tool" in pyproject_data:
                    self.add_result(
                        "dependencies",
                        "pyproject_toml",
                        ValidationStatus.PASSED,
                        "pyproject.toml is valid",
                    )
                else:
                    self.add_result(
                        "dependencies",
                        "pyproject_toml",
                        ValidationStatus.WARNING,
                        "pyproject.toml exists but may be incomplete",
                    )
            except ImportError:
                self.add_result(
                    "dependencies",
                    "pyproject_toml",
                    ValidationStatus.WARNING,
                    "Cannot validate pyproject.toml (tomli not installed)",
                )
            except Exception as e:
                self.add_result(
                    "dependencies",
                    "pyproject_toml",
                    ValidationStatus.FAILED,
                    f"Error reading pyproject.toml: {e}",
                )
        else:
            self.add_result(
                "dependencies",
                "pyproject_toml",
                ValidationStatus.WARNING,
                "No pyproject.toml found",
            )

    def validate_project_shell_scripts(self) -> None:
        """Validate project shell scripts for known problematic commands."""
        logger.info("Validating project shell scripts for deprecated ruff arguments...")
        scripts_dir = self.project_root / "scripts"

        if not scripts_dir.is_dir():
            self.add_result(
                "shell_scripts",
                "scripts_directory_check",
                ValidationStatus.SKIPPED,
                "Scripts directory not found, skipping shell script validation.",
                {"path": str(scripts_dir)},
            )
            return

        sh_files = list(scripts_dir.rglob("*.sh"))

        if not sh_files:
            self.add_result(
                "shell_scripts",
                "deprecated_ruff_arg_check",
                ValidationStatus.PASSED,
                "No .sh files found in scripts directory; deprecated ruff argument check passed.",
                {"path": str(scripts_dir)},
            )
            return

        deprecated_arg_found_in_any_script = False
        any_read_errors = False

        for sh_file in sh_files:
            try:
                with open(sh_file, encoding="utf-8") as f:  # Added encoding
                    for line_num, line in enumerate(f, 1):
                        if "ruff --show-files" in line:
                            self.add_result(
                                "shell_scripts",
                                f"deprecated_ruff_arg_in_{sh_file.name.replace('.', '_')}",
                                ValidationStatus.WARNING,
                                f"Found deprecated 'ruff --show-source' in {sh_file.name} at line {line_num}. Consider using '--show-files'.",
                                {"file": str(sh_file), "line": line_num},
                            )
                            deprecated_arg_found_in_any_script = True
            except Exception as e:
                self.add_result(
                    "shell_scripts",
                    f"read_error_{sh_file.name.replace('.', '_')}",
                    ValidationStatus.FAILED,
                    f"Error reading shell script {sh_file.name}: {e}",
                    {"file": str(sh_file)},
                )
                any_read_errors = True

        if not deprecated_arg_found_in_any_script and not any_read_errors:
            self.add_result(
                "shell_scripts",
                "deprecated_ruff_arg_check",
                ValidationStatus.PASSED,
                "All found .sh files checked; no deprecated 'ruff --show-files' arguments found.",
            )
        # If deprecated_arg_found_in_any_script is True, specific warnings have already been added.
        # If any_read_errors is True, specific failures have already been added.

    def run_comprehensive_validation(self) -> dict[str, Any]:
        """Run all validation checks."""
        logger.info("Starting comprehensive CI/CD validation...")

        validation_checks = [
            self.validate_project_structure,
            self.validate_ci_cd_scripts,
            self.validate_middleware_components,
            self.validate_environment_setup,
            self.validate_security_configuration,
            self.validate_testing_pipeline,
            self.validate_github_workflows,
            self.validate_dependencies,
            self.validate_project_shell_scripts,  # Added new validation
        ]

        for check in validation_checks:
            try:
                check()
            except Exception as e:
                logger.error(f"Validation check {check.__name__} failed: {e}")
                self.add_result(
                    "validation",
                    check.__name__,
                    ValidationStatus.FAILED,
                    f"Check failed: {e}",
                )

        return self.generate_report()

    def generate_report(self) -> dict[str, Any]:
        """Generate a comprehensive validation report."""
        total_checks = len(self.results)
        passed = len([r for r in self.results if r.status == ValidationStatus.PASSED])
        warnings = len(
            [r for r in self.results if r.status == ValidationStatus.WARNING]
        )
        failed = len([r for r in self.results if r.status == ValidationStatus.FAILED])
        skipped = len([r for r in self.results if r.status == ValidationStatus.SKIPPED])

        # Calculate overall status
        if failed > 0:
            overall_status = ValidationStatus.FAILED
        elif warnings > 0:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASSED

        report = {
            "timestamp": time.time(),
            "overall_status": overall_status.value,
            "summary": {
                "total_checks": total_checks,
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "skipped": skipped,
            },
            "results": [
                {
                    "component": r.component,
                    "check": r.check,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
        }

        # Print summary
        print("\n" + "=" * 60)
        print("CI/CD PIPELINE VALIDATION REPORT")
        print("=" * 60)
        print(f"Overall Status: {overall_status.value.upper()}")
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print("=" * 60)

        # Print detailed results
        for result in self.results:
            status_icon = {
                ValidationStatus.PASSED: "✅",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.FAILED: "❌",
                ValidationStatus.SKIPPED: "⏭️",
            }[result.status]

            print(f"{status_icon} {result.component}.{result.check}: {result.message}")

        print("=" * 60)

        return report


def validate_ci_cd_operations(ctx: Ctx) -> Ctx:
    """
    Main function for validating CI/CD operations.
    """
    logger.info("Starting CI/CD operations validation...")

    try:
        validator = CICDValidator()
        report = validator.run_comprehensive_validation()

        ctx["ci_cd_validation_report"] = report
        ctx["ci_cd_operations_validated"] = report["overall_status"] in [
            "passed",
            "warning",
        ]

        # Save report to file
        report_file = Path("ci_cd_validation_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Validation report saved to {report_file}")

        return ctx

    except Exception as e:
        logger.error(f"CI/CD operations validation failed: {e}")
        ctx["ci_cd_operations_validated"] = False
        ctx["validation_error"] = str(e)
        return ctx


def main():
    """Main entry point for direct execution."""
    ctx = {}
    result_ctx = validate_ci_cd_operations(ctx)

    if result_ctx.get("ci_cd_operations_validated"):
        print("\n🎉 CI/CD pipeline validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ CI/CD pipeline validation failed!")
        if "validation_error" in result_ctx:
            print(f"Error: {result_ctx['validation_error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

__all__ = [
    "validate_ci_cd_operations",
    "CICDValidator",
    "ValidationStatus",
    "ValidationResult",
]
