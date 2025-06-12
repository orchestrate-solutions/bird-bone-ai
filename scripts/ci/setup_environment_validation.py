"""
Setup Environment Validation Link
=================================

Environment validation logic for CI/CD pipeline.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

Ctx = dict[str, Any]


def setup_environment_validation(ctx: Ctx) -> Ctx:
    """
    Set up and run environment validation.
    """
    try:
        project_root = Path(ctx.get("project_root", Path.cwd()))

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ctx["python_version"] = python_version

        # Check if requirements.txt exists
        requirements_file = project_root / "requirements.txt"
        ctx["requirements_exists"] = requirements_file.exists()

        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=project_root,
            )
            ctx["git_repository"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            ctx["git_repository"] = False

        # Check if essential directories exist
        essential_dirs = ["scripts", "tests"]
        ctx["essential_dirs_exist"] = all(
            (project_root / dir_name).exists() for dir_name in essential_dirs
        )

        # Overall validation status
        validation_success = (
            sys.version_info >= (3, 8)  # Python 3.8+
            and ctx["requirements_exists"]
            and ctx["git_repository"]
            and ctx["essential_dirs_exist"]
        )

        ctx["environment_validated"] = validation_success
        ctx["environment_validation_setup"] = True

        if validation_success:
            print(f"Environment validation passed (Python {python_version})")
        else:
            print("Environment validation failed - check requirements")

    except Exception as e:
        print(f"Environment validation error: {e}")
        ctx["environment_validated"] = False
        ctx["environment_validation_error"] = str(e)

    return ctx


__all__ = ["setup_environment_validation"]
