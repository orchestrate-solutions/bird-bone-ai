#!/usr/bin/env python3

"""
Bird-Bone AI Environment Validation Script
==========================================

Comprehensive validation script for Issue #2 requirements.
Validates the complete development environment setup including:
- Python version compatibility
- Required packages installation
- Git LFS functionality
- DVC configuration and connectivity
- Pre-commit hooks installation
- CUDA availability for GPU setups
- Environment health reporting

Usage:
    python scripts/validate_environment.py [--verbose] [--report-file PATH]
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Color codes for terminal output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.NC}")


def print_status(message: str) -> None:
    print_colored(f"[INFO] {message}", Colors.BLUE)


def print_success(message: str) -> None:
    print_colored(f"[SUCCESS] {message}", Colors.GREEN)


def print_warning(message: str) -> None:
    print_colored(f"[WARNING] {message}", Colors.YELLOW)


def print_error(message: str) -> None:
    print_colored(f"[ERROR] {message}", Colors.RED)


class EnvironmentValidator:
    """Comprehensive environment validation for bird-bone AI development."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "python_info": {},
            "package_validation": {},
            "gpu_info": {},
            "tools_validation": {},
            "overall_health": "unknown",
        }
        self.errors = []
        self.warnings = []

    def validate_python_version(self) -> bool:
        """Validate Python version compatibility (3.11+)."""
        print_status("Validating Python version...")

        version = sys.version_info
        self.results["python_info"] = {
            "version": f"{version.major}.{version.minor}.{version.micro}",
            "executable": sys.executable,
            "platform": platform.platform(),
        }

        if version.major == 3 and version.minor >= 11:
            print_success(
                f"Python {version.major}.{version.minor}.{version.micro} - Compatible ✓"
            )
            return True
        else:
            error_msg = f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False

    def validate_required_packages(self) -> dict[str, bool]:
        """Validate all required packages are installed and importable."""
        print_status("Validating required packages...")

        # Critical packages for bird-bone AI
        required_packages = [
            # Core ML Foundation
            ("torch", "PyTorch core framework"),
            ("transformers", "HuggingFace transformers"),
            ("accelerate", "Model acceleration"),
            ("safetensors", "Secure tensor serialization"),
            # Compression & Optimization
            ("bitsandbytes", "Advanced quantization"),
            ("peft", "Parameter-efficient fine-tuning"),
            # ModuLink Architecture
            ("modulink_py", "ModuLink framework"),
            # Pipeline & Workflow
            ("kedro", "ML pipeline orchestration"),
            ("dvc", "Data version control"),
            # Development & Testing
            ("pytest", "Testing framework"),
            ("black", "Code formatting"),
            ("ruff", "Fast linting"),
            # Monitoring & Visualization
            ("wandb", "Experiment tracking"),
            ("nbdime", "Notebook diffing"),
            ("jupyter", "Notebook environment"),
            # Data Processing
            ("numpy", "Numerical computing"),
            ("pandas", "Data manipulation"),
            ("matplotlib", "Plotting"),
        ]

        package_results = {}
        successful_imports = 0

        for package_name, description in required_packages:
            try:
                __import__(package_name)
                if self.verbose:
                    print_success(f"  ✓ {package_name} - {description}")
                package_results[package_name] = True
                successful_imports += 1
            except ImportError as e:
                error_msg = f"  ✗ {package_name} - FAILED: {str(e)}"
                print_error(error_msg)
                package_results[package_name] = False
                self.errors.append(f"Missing package: {package_name}")
            except Exception as e:
                error_msg = f"  ✗ {package_name} - ERROR: {str(e)}"
                print_error(error_msg)
                package_results[package_name] = False
                self.errors.append(f"Package error: {package_name} - {str(e)}")

        self.results["package_validation"] = package_results

        success_rate = successful_imports / len(required_packages) * 100
        print_status(
            f"Package validation: {successful_imports}/{len(required_packages)} ({success_rate:.1f}%)"
        )

        if success_rate >= 90:
            print_success("Package validation passed ✓")
        elif success_rate >= 70:
            print_warning("Package validation passed with warnings ⚠️")
        else:
            print_error("Package validation failed ✗")

        return package_results

    def validate_cuda_and_gpu(self) -> dict[str, any]:
        """Validate CUDA availability and GPU setup."""
        print_status("Validating GPU and CUDA setup...")

        gpu_info = {
            "cuda_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "gpu_devices": [],
            "optimal_setup": False,
        }

        try:
            import torch

            gpu_info["cuda_available"] = torch.cuda.is_available()

            if torch.cuda.is_available():
                gpu_info["cuda_version"] = torch.version.cuda
                gpu_info["gpu_count"] = torch.cuda.device_count()

                print_success(
                    f"CUDA {torch.version.cuda} available with {gpu_info['gpu_count']} GPU(s)"
                )

                # Get GPU details
                for i in range(torch.cuda.device_count()):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / (
                        1024**3
                    )

                    gpu_device = {
                        "id": i,
                        "name": gpu_name,
                        "memory_gb": round(gpu_memory, 1),
                    }
                    gpu_info["gpu_devices"].append(gpu_device)

                    if self.verbose:
                        print_status(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")

                    # Check for optimal GPUs (H100/A100)
                    if "H100" in gpu_name or "A100" in gpu_name:
                        gpu_info["optimal_setup"] = True
                        print_success(f"  ✓ Optimal GPU detected: {gpu_name}")

                # Test GPU functionality
                try:
                    x = torch.randn(1000, 1000, device="cuda:0")
                    y = torch.randn(1000, 1000, device="cuda:0")
                    torch.matmul(x, y)
                    print_success("GPU tensor operations test passed ✓")
                except Exception as e:
                    error_msg = f"GPU functionality test failed: {str(e)}"
                    print_error(error_msg)
                    self.errors.append(error_msg)

                if not gpu_info["optimal_setup"]:
                    warning_msg = (
                        "Consider using H100/A100 GPUs for optimal performance"
                    )
                    print_warning(warning_msg)
                    self.warnings.append(warning_msg)

            else:
                warning_msg = "CUDA not available - running in CPU-only mode"
                print_warning(warning_msg)
                self.warnings.append(warning_msg)

        except ImportError:
            error_msg = "PyTorch not available - cannot validate GPU setup"
            print_error(error_msg)
            self.errors.append(error_msg)
        except Exception as e:
            error_msg = f"GPU validation error: {str(e)}"
            print_error(error_msg)
            self.errors.append(error_msg)

        self.results["gpu_info"] = gpu_info
        return gpu_info

    def validate_git_lfs(self) -> bool:
        """Test Git LFS functionality."""
        print_status("Validating Git LFS setup...")

        try:
            # Check if git lfs is installed
            result = subprocess.run(
                ["git", "lfs", "version"], capture_output=True, text=True, check=True
            )

            if self.verbose:
                print_success(f"Git LFS version: {result.stdout.strip()}")

            # Check if git lfs is initialized in repo
            result = subprocess.run(
                ["git", "lfs", "env"], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                print_success("Git LFS functionality validated ✓")
                return True
            else:
                warning_msg = "Git LFS not initialized in repository"
                print_warning(warning_msg)
                self.warnings.append(warning_msg)
                return False

        except subprocess.CalledProcessError as e:
            error_msg = f"Git LFS validation failed: {str(e)}"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False
        except FileNotFoundError:
            error_msg = "Git LFS not installed"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False

    def validate_dvc_configuration(self) -> bool:
        """Validate DVC configuration and connectivity."""
        print_status("Validating DVC configuration...")

        try:
            # Check if DVC is installed and working
            result = subprocess.run(
                ["dvc", "version"], capture_output=True, text=True, check=True
            )

            if self.verbose:
                print_success(f"DVC version: {result.stdout.strip()}")

            # Check if DVC is initialized
            if Path(".dvc").exists():
                print_success("DVC initialized in repository ✓")

                # Check DVC config
                try:
                    result = subprocess.run(
                        ["dvc", "config", "--list"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    if self.verbose:
                        print_status("DVC configuration detected")
                except subprocess.CalledProcessError:
                    warning_msg = "DVC configuration issues detected"
                    print_warning(warning_msg)
                    self.warnings.append(warning_msg)

                return True
            else:
                warning_msg = "DVC not initialized in repository"
                print_warning(warning_msg)
                self.warnings.append(warning_msg)
                return False

        except subprocess.CalledProcessError as e:
            error_msg = f"DVC validation failed: {str(e)}"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False
        except FileNotFoundError:
            error_msg = "DVC not installed"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False

    def validate_precommit_hooks(self) -> bool:
        """Check pre-commit hooks installation."""
        print_status("Validating pre-commit hooks...")

        try:
            # Check if pre-commit is installed
            result = subprocess.run(
                ["pre-commit", "--version"], capture_output=True, text=True, check=True
            )

            if self.verbose:
                print_success(f"Pre-commit version: {result.stdout.strip()}")

            # Check if hooks are installed
            if Path(".pre-commit-config.yaml").exists():
                try:
                    result = subprocess.run(
                        ["pre-commit", "hook-impl", "--help"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    print_success("Pre-commit hooks configuration found ✓")
                    return True
                except subprocess.CalledProcessError:
                    warning_msg = (
                        "Pre-commit hooks not installed. Run: pre-commit install"
                    )
                    print_warning(warning_msg)
                    self.warnings.append(warning_msg)
                    return False
            else:
                warning_msg = "Pre-commit configuration file not found"
                print_warning(warning_msg)
                self.warnings.append(warning_msg)
                return False

        except subprocess.CalledProcessError as e:
            error_msg = f"Pre-commit validation failed: {str(e)}"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False
        except FileNotFoundError:
            error_msg = "Pre-commit not installed"
            print_error(error_msg)
            self.errors.append(error_msg)
            return False

    def generate_health_report(self) -> dict[str, any]:
        """Generate comprehensive environment health report."""
        print_status("Generating environment health report...")

        # Calculate overall health score
        total_checks = 0
        passed_checks = 0

        # Python version check
        total_checks += 1
        if self.results["python_info"].get("version", "").startswith(("3.11", "3.12")):
            passed_checks += 1

        # Package validation
        if self.results["package_validation"]:
            package_success_rate = sum(
                self.results["package_validation"].values()
            ) / len(self.results["package_validation"])
            total_checks += 1
            if package_success_rate >= 0.9:
                passed_checks += 1

        # GPU setup (optional but preferred)
        if self.results["gpu_info"].get("cuda_available", False):
            passed_checks += 0.5  # Bonus for GPU availability

        # Tools validation
        tools_score = 0
        if "git_lfs" in self.results["tools_validation"]:
            total_checks += 1
            if self.results["tools_validation"]["git_lfs"]:
                passed_checks += 1
                tools_score += 1

        if "dvc" in self.results["tools_validation"]:
            total_checks += 1
            if self.results["tools_validation"]["dvc"]:
                passed_checks += 1
                tools_score += 1

        if "precommit" in self.results["tools_validation"]:
            total_checks += 1
            if self.results["tools_validation"]["precommit"]:
                passed_checks += 1
                tools_score += 1

        # Calculate health score
        health_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        if health_score >= 90:
            self.results["overall_health"] = "excellent"
            health_status = "Excellent"
            health_color = Colors.GREEN
        elif health_score >= 75:
            self.results["overall_health"] = "good"
            health_status = "Good"
            health_color = Colors.YELLOW
        elif health_score >= 50:
            self.results["overall_health"] = "fair"
            health_status = "Fair"
            health_color = Colors.YELLOW
        else:
            self.results["overall_health"] = "poor"
            health_status = "Poor"
            health_color = Colors.RED

        self.results["health_score"] = round(health_score, 1)
        self.results["errors"] = self.errors
        self.results["warnings"] = self.warnings

        # Print summary
        print_colored("\nEnvironment Health Summary:", Colors.WHITE)
        print_colored(
            f"Overall Health: {health_status} ({health_score:.1f}%)", health_color
        )

        if self.errors:
            print_error(f"Errors: {len(self.errors)}")
            for error in self.errors[:3]:  # Show first 3 errors
                print_error(f"  • {error}")
            if len(self.errors) > 3:
                print_error(f"  ... and {len(self.errors) - 3} more errors")

        if self.warnings:
            print_warning(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings[:3]:  # Show first 3 warnings
                print_warning(f"  • {warning}")
            if len(self.warnings) > 3:
                print_warning(f"  ... and {len(self.warnings) - 3} more warnings")

        return self.results

    def run_full_validation(self) -> dict[str, any]:
        """Run complete environment validation."""
        print_colored("Bird-Bone AI Environment Validation", Colors.CYAN)
        print_colored("=" * 50, Colors.CYAN)

        # System info
        self.results["system_info"] = {
            "platform": platform.platform(),
            "python_executable": sys.executable,
            "working_directory": os.getcwd(),
        }

        # Run all validations
        self.validate_python_version()
        self.validate_required_packages()
        self.validate_cuda_and_gpu()

        # Tools validation
        tools_results = {}
        tools_results["git_lfs"] = self.validate_git_lfs()
        tools_results["dvc"] = self.validate_dvc_configuration()
        tools_results["precommit"] = self.validate_precommit_hooks()

        self.results["tools_validation"] = tools_results

        # Generate final report
        return self.generate_health_report()


def main():
    """Main function for environment validation."""
    parser = argparse.ArgumentParser(
        description="Validate bird-bone AI development environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_environment.py
  python scripts/validate_environment.py --verbose
  python scripts/validate_environment.py --report-file env_report.json
        """,
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--report-file", "-r", type=str, help="Save detailed report to JSON file"
    )

    args = parser.parse_args()

    # Run validation
    validator = EnvironmentValidator(verbose=args.verbose)
    results = validator.run_full_validation()

    # Save report if requested
    if args.report_file:
        try:
            with open(args.report_file, "w") as f:
                json.dump(results, f, indent=2)
            print_success(f"Detailed report saved to: {args.report_file}")
        except Exception as e:
            print_error(f"Failed to save report: {str(e)}")

    # Exit with appropriate code
    if results["overall_health"] in ["excellent", "good"]:
        print_success("\n✅ Environment validation completed successfully!")
        print_status("Your environment is ready for bird-bone AI development.")
        sys.exit(0)
    elif results["overall_health"] == "fair":
        print_warning("\n⚠️  Environment validation completed with warnings.")
        print_status("Address warnings for optimal development experience.")
        sys.exit(0)
    else:
        print_error("\n❌ Environment validation failed.")
        print_error("Please fix the errors before proceeding with development.")
        sys.exit(1)


if __name__ == "__main__":
    main()
