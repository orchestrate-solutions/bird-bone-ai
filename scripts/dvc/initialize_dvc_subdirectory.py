"""
DVC Subdirectory Initialization Link
===================================

Purpose:
    Initializes DVC in the /models subdirectory, creating the necessary DVC
    configuration and directory structure for model versioning.

Input Context Requirements:
    - models_dir: str - Path to models directory
    - project_root: str - Project root directory path
    - dvc_available: bool - Must be True to proceed

Output Context Additions:
    - dvc_initialized: bool - Whether DVC was successfully initialized
    - dvc_dir: str - Path to .dvc directory within models
    - dvc_config_path: str - Path to DVC config file
    - dvc_init_output: str - Output from DVC init command
    - operation: str - Set to 'initialize_dvc_subdirectory'

Context Modifications:
    - models_exists: bool - Updated to True if directory was created

Error Conditions:
    - Previous errors exist -> skips processing and returns context unchanged
    - DVC not available -> handled by previous link
    - DVC init command fails -> raises CalledProcessError (handled by middleware)
    - Permission errors -> raises PermissionError (handled by middleware)

Dependencies:
    - subprocess: For running DVC commands
    - pathlib.Path: For directory handling

Side Effects:
    - Creates models directory if it doesn't exist
    - Initializes DVC repository in models subdirectory
    - Creates .dvc directory and configuration files

Example Context Flow:
    Input:  {
        'models_dir': '/project/models',
        'project_root': '/project',
        'dvc_available': True,
        'models_exists': False
    }
    Output: {
        'models_dir': '/project/models',
        'project_root': '/project',
        'dvc_available': True,
        'models_exists': True,
        'operation': 'initialize_dvc_subdirectory',
        'dvc_initialized': True,
        'dvc_dir': '/project/models/.dvc',
        'dvc_config_path': '/project/models/.dvc/config',
        'dvc_init_output': 'Initialized DVC repository...'
    }
"""

import subprocess
from pathlib import Path

from modulink import Ctx


async def initialize_dvc_subdirectory_link(ctx: Ctx) -> Ctx:
    """Initialize DVC in the /models subdirectory"""
    # Skip if there are previous errors
    if ctx.get("errors"):
        return ctx

    models_dir = Path(ctx["models_dir"])

    # Create models directory if it doesn't exist
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)

    # Check if DVC is already initialized
    dvc_dir = models_dir / ".dvc"
    if dvc_dir.exists():
        dvc_config_path = dvc_dir / "config"
        return {
            **ctx,
            "operation": "initialize_dvc_subdirectory",
            "dvc_initialized": True,
            "dvc_dir": str(dvc_dir),
            "dvc_config_path": str(dvc_config_path),
            "dvc_init_output": "DVC already initialized",
            "models_exists": True,
        }

    # Initialize DVC in subdirectory (must run from within the subdirectory)
    result = subprocess.run(
        ["dvc", "init", "--subdir"], capture_output=True, text=True, cwd=str(models_dir)
    )

    if result.returncode != 0:
        return {
            **ctx,
            "operation": "initialize_dvc_subdirectory",
            "dvc_initialized": False,
            "error": f"DVC init failed: {result.stderr}",
            "errors": ctx.get("errors", []) + [f"DVC init failed: {result.stderr}"],
        }

    dvc_dir = models_dir / ".dvc"
    dvc_config_path = dvc_dir / "config"

    return {
        **ctx,
        "operation": "initialize_dvc_subdirectory",
        "dvc_initialized": True,
        "dvc_dir": str(dvc_dir),
        "dvc_config_path": str(dvc_config_path),
        "dvc_init_output": result.stdout.strip(),
        "models_exists": True,
    }
