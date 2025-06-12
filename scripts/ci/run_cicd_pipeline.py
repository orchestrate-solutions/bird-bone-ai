#!/usr/bin/env python3
"""
Comprehensive CI/CD Pipeline Integration
========================================

This script provides a unified interface for running the complete CI/CD pipeline
including security checks, environment validation, testing, and deployment readiness.
"""
import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Add the scripts directory to Python path for imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Import our CI/CD modules
import configure_security_settings
import setup_environment_validation
import setup_testing_pipeline
import validate_ci_cd_operations
from middleware import (
    deployment_middleware,
    security_middleware,
    testing_middleware,
    validation_middleware,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """CI/CD pipeline stages."""

    VALIDATION = "validation"
    SECURITY = "security"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    INTEGRATION = "integration"


@dataclass
class PipelineResult:
    """Result of a pipeline stage."""

    stage: PipelineStage
    success: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0


class CICDPipeline:
    """Comprehensive CI/CD pipeline orchestrator."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the CI/CD pipeline."""
        self.project_root = project_root or Path.cwd()
        self.results: list[PipelineResult] = []
        self.context: dict[str, Any] = {
            "project_root": str(self.project_root),
            "timestamp": time.time(),
        }

        # Initialize middleware components
        self.middlewares = {
            "security": security_middleware.SecurityMiddleware(),
            "validation": validation_middleware.ValidationMiddleware(),
            "testing": testing_middleware.TestingMiddleware(),
            "deployment": deployment_middleware.DeploymentMiddleware(),
        }

    def add_result(
        self,
        stage: PipelineStage,
        success: bool,
        message: str,
        details: dict[str, Any] | None = None,
        duration: float = 0.0,
    ):
        """Add a pipeline result."""
        result = PipelineResult(
            stage=stage,
            success=success,
            message=message,
            details=details or {},
            duration=duration,
        )
        self.results.append(result)

        # Log the result
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"{stage.value}: {message} (duration: {duration:.2f}s)")

    def run_validation_stage(self) -> bool:
        """Run environment validation stage."""
        logger.info("Running validation stage...")
        start_time = time.time()

        try:
            # Run environment validation
            validation_ctx = setup_environment_validation.setup_environment_validation(
                self.context.copy()
            )

            # Run validation middleware
            middleware_ctx = self.middlewares["validation"].process(self.context.copy())

            success = validation_ctx.get("environment_validated", False)
            duration = time.time() - start_time

            self.add_result(
                PipelineStage.VALIDATION,
                success,
                (
                    "Environment validation completed"
                    if success
                    else "Environment validation failed"
                ),
                {
                    "validation_context": validation_ctx,
                    "middleware_results": middleware_ctx,
                },
                duration,
            )

            # Update main context
            self.context.update(validation_ctx)
            self.context.update(middleware_ctx)

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                PipelineStage.VALIDATION,
                False,
                f"Validation stage failed: {e}",
                {"error": str(e)},
                duration,
            )
            return False

    def run_security_stage(self) -> bool:
        """Run security checks stage."""
        logger.info("Running security stage...")
        start_time = time.time()

        try:
            # Run security configuration
            security_ctx = configure_security_settings.configure_security_settings(
                self.context.copy()
            )

            # Run security middleware
            middleware_ctx = self.middlewares["security"].process(self.context.copy())

            # Check security results
            security_checks = middleware_ctx.get("security_checks", [])
            critical_failures = [
                check
                for check in security_checks
                if not check["passed"] and check["name"] in ["dependency_security"]
            ]

            success = len(critical_failures) == 0
            duration = time.time() - start_time

            self.add_result(
                PipelineStage.SECURITY,
                success,
                (
                    "Security checks completed"
                    if success
                    else f"Security issues found: {len(critical_failures)} critical"
                ),
                {
                    "security_context": security_ctx,
                    "middleware_results": middleware_ctx,
                    "critical_failures": critical_failures,
                },
                duration,
            )

            # Update main context
            self.context.update(security_ctx)
            self.context.update(middleware_ctx)

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                PipelineStage.SECURITY,
                False,
                f"Security stage failed: {e}",
                {"error": str(e)},
                duration,
            )
            return False

    def run_testing_stage(self) -> bool:
        """Run testing stage."""
        logger.info("Running testing stage...")
        start_time = time.time()

        try:
            # Run testing pipeline setup
            testing_ctx = setup_testing_pipeline.setup_testing_pipeline(
                self.context.copy()
            )

            # Run testing middleware
            middleware_ctx = self.middlewares["testing"].process(self.context.copy())

            # Check test results
            test_results = middleware_ctx.get("test_results", [])
            critical_test_failures = [
                result
                for result in test_results
                if not result["passed"] and result["name"] == "unit_tests"
            ]

            success = len(critical_test_failures) == 0
            duration = time.time() - start_time

            self.add_result(
                PipelineStage.TESTING,
                success,
                (
                    "Testing stage completed"
                    if success
                    else f"Critical test failures: {len(critical_test_failures)}"
                ),
                {
                    "testing_context": testing_ctx,
                    "middleware_results": middleware_ctx,
                    "test_failures": critical_test_failures,
                },
                duration,
            )

            # Update main context
            self.context.update(testing_ctx)
            self.context.update(middleware_ctx)

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                PipelineStage.TESTING,
                False,
                f"Testing stage failed: {e}",
                {"error": str(e)},
                duration,
            )
            return False

    def run_deployment_stage(self) -> bool:
        """Run deployment readiness stage."""
        logger.info("Running deployment stage...")
        start_time = time.time()

        try:
            # Run deployment middleware
            middleware_ctx = self.middlewares["deployment"].process(self.context.copy())

            # Check deployment readiness
            deployment_checks = middleware_ctx.get("deployment_checks", [])
            deployment_failures = [
                check for check in deployment_checks if not check["passed"]
            ]

            success = len(deployment_failures) == 0
            duration = time.time() - start_time

            self.add_result(
                PipelineStage.DEPLOYMENT,
                success,
                (
                    "Deployment readiness confirmed"
                    if success
                    else f"Deployment issues: {len(deployment_failures)}"
                ),
                {
                    "middleware_results": middleware_ctx,
                    "deployment_failures": deployment_failures,
                },
                duration,
            )

            # Update main context
            self.context.update(middleware_ctx)

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                PipelineStage.DEPLOYMENT,
                False,
                f"Deployment stage failed: {e}",
                {"error": str(e)},
                duration,
            )
            return False

    def run_integration_validation(self) -> bool:
        """Run final integration validation."""
        logger.info("Running integration validation...")
        start_time = time.time()

        try:
            # Run comprehensive CI/CD validation
            validator = validate_ci_cd_operations.CICDValidator(self.project_root)
            validation_report = validator.run_comprehensive_validation()

            success = validation_report["overall_status"] in ["passed", "warning"]
            duration = time.time() - start_time

            self.add_result(
                PipelineStage.INTEGRATION,
                success,
                f"Integration validation: {validation_report['overall_status']}",
                {"validation_report": validation_report},
                duration,
            )

            # Update main context
            self.context["integration_validation"] = validation_report

            return success

        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                PipelineStage.INTEGRATION,
                False,
                f"Integration validation failed: {e}",
                {"error": str(e)},
                duration,
            )
            return False

    def run_full_pipeline(
        self, stages: list[PipelineStage] | None = None
    ) -> dict[str, Any]:
        """Run the complete CI/CD pipeline."""
        if stages is None:
            stages = list(PipelineStage)

        logger.info(f"Starting CI/CD pipeline with stages: {[s.value for s in stages]}")
        pipeline_start = time.time()

        stage_methods = {
            PipelineStage.VALIDATION: self.run_validation_stage,
            PipelineStage.SECURITY: self.run_security_stage,
            PipelineStage.TESTING: self.run_testing_stage,
            PipelineStage.DEPLOYMENT: self.run_deployment_stage,
            PipelineStage.INTEGRATION: self.run_integration_validation,
        }

        overall_success = True
        for stage in stages:
            if stage in stage_methods:
                stage_success = stage_methods[stage]()
                if not stage_success:
                    overall_success = False
                    # Continue with non-critical stages
                    if stage in [PipelineStage.VALIDATION, PipelineStage.TESTING]:
                        logger.warning(
                            f"Critical stage {stage.value} failed, but continuing pipeline"
                        )

        total_duration = time.time() - pipeline_start

        # Generate final report
        report = self.generate_pipeline_report(overall_success, total_duration)

        # Save report
        report_file = self.project_root / "ci_cd_pipeline_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Pipeline report saved to {report_file}")

        return report

    def generate_pipeline_report(
        self, overall_success: bool, total_duration: float
    ) -> dict[str, Any]:
        """Generate comprehensive pipeline report."""
        successful_stages = len([r for r in self.results if r.success])
        failed_stages = len([r for r in self.results if not r.success])

        report = {
            "pipeline_run": {
                "timestamp": time.time(),
                "overall_success": overall_success,
                "total_duration": total_duration,
                "stages_run": len(self.results),
                "successful_stages": successful_stages,
                "failed_stages": failed_stages,
            },
            "stage_results": [
                {
                    "stage": result.stage.value,
                    "success": result.success,
                    "message": result.message,
                    "duration": result.duration,
                    "timestamp": result.timestamp,
                    "details": result.details,
                }
                for result in self.results
            ],
            "context": self.context,
        }

        # Print summary
        print("\n" + "=" * 80)
        print("CI/CD PIPELINE EXECUTION REPORT")
        print("=" * 80)
        print(f"Overall Status: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Stages Executed: {len(self.results)}")
        print(f"Successful: {successful_stages}")
        print(f"Failed: {failed_stages}")
        print("=" * 80)

        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            print(
                f"{status_icon} {result.stage.value.upper()}: {result.message} ({result.duration:.2f}s)"
            )

        print("=" * 80)

        return report


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Run CI/CD pipeline")
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=[stage.value for stage in PipelineStage],
        help="Stages to run (default: all)",
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Convert stage names to enums
    stages = None
    if args.stages:
        stages = [PipelineStage(stage) for stage in args.stages]

    # Initialize and run pipeline
    pipeline = CICDPipeline(args.project_root)
    report = pipeline.run_full_pipeline(stages)

    # Exit with appropriate code
    if report["pipeline_run"]["overall_success"]:
        print("\n🎉 CI/CD Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ CI/CD Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
