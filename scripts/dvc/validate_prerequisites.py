"""
DVC Prerequisites Validation Link
================================

Purpose:
    Validates that all prerequisites for DVC initialization are met including
    DVC installation, Git availability, and directory structure.

Input Context Requirements:
    - No specific requirements (typically first link in chain)

Output Context Additions:
    - dvc_version: str - Version of DVC installed (e.g., "dvc version 3.51.2")
    - dvc_available: bool - Whether DVC command is accessible
    - git_available: bool - Whether Git is available and working
    - models_dir: str - Absolute path to models directory
    - models_exists: bool - Whether models directory exists
    - project_root: str - Project root directory path
    - operation: str - Set to 'validate_prerequisites'

Error Conditions:
    - DVC not installed/accessible -> adds 'dvc_not_available' error to context
    - Git not available -> continues but sets git_available=False
    - FileSystem errors -> handled by error middleware

Dependencies:
    - subprocess: For running DVC and Git commands
    - pathlib.Path: For directory handling

Side Effects:
    - None (read-only validation)

Example Context Flow:
    Input:  {'errors': []}
    Output: {
        'errors': [],
        'operation': 'validate_prerequisites',
        'dvc_version': 'dvc version 3.51.2',
        'dvc_available': True,
        'git_available': True,
        'models_dir': '/project/models',
        'models_exists': True,
        'project_root': '/project'
    }
"""

import subprocess
from pathlib import Path
from modulink import Ctx


async def validate_prerequisites_link(ctx: Ctx) -> Ctx:
    """Validate that all prerequisites for DVC initialization are met"""
    project_root = Path.cwd()
    models_dir = project_root / "models"

    # Check if DVC is available
    try:
        result = subprocess.run(
            ["dvc", "--version"], capture_output=True, text=True, check=True
        )
        dvc_version = result.stdout.strip()
        dvc_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            **ctx,
            "errors": ctx.get("errors", [])
            + [
                {
                    "type": "dvc_not_available",
                    "details": "DVC command not found or not accessible",
                }
            ],
        }

    # Check Git status
    try:
        subprocess.run(
            ["git", "status"], capture_output=True, check=True, cwd=project_root
        )
        git_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_available = False

    # Check if models directory exists
    models_exists = models_dir.exists()

    return {
        **ctx,
        "operation": "validate_prerequisites",
        "dvc_version": dvc_version,
        "dvc_available": dvc_available,
        "git_available": git_available,
        "models_dir": str(models_dir),
        "models_exists": models_exists,
        "project_root": str(project_root),
    }
