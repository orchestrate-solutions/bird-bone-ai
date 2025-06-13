"""
DVC Operations Testing Link
==========================

Purpose:
    Tests basic DVC operations to ensure the initialization was successful and
    all components are working correctly before completing the setup process.

Input Context Requirements:
    - models_dir: str - Path to models directory

Output Context Additions:
    - test_results: list - List of test results with success/failure status
    - all_tests_passed: bool - Whether all tests passed successfully
    - operation: str - Set to 'test_dvc_operations'

Error Conditions:
    - Previous errors exist -> skips processing and returns context unchanged
    - DVC command failures -> captured in test_results, not raised
    - Individual test failures -> captured but don't stop other tests

Dependencies:
    - subprocess: For running DVC commands
    - pathlib.Path: For directory handling

Side Effects:
    - None (read-only testing operations)

Example Context Flow:
    Input:  {
        'models_dir': '/project/models'
    }
    Output: {
        'models_dir': '/project/models',
        'operation': 'test_dvc_operations',
        'test_results': [
            {'test': 'dvc_status', 'success': True, 'output': '...'},
            {'test': 'dvc_config_list', 'success': True, 'output': '...'}
        ],
        'all_tests_passed': True
    }
"""

import subprocess
from pathlib import Path

from modulink import Ctx


async def test_dvc_operations_link(ctx: Ctx) -> Ctx:
    """Test basic DVC operations to ensure everything is working"""
    # Skip if there are previous errors
    if ctx.get("errors"):
        return ctx

    models_dir = Path(ctx["models_dir"])
    test_results = []

    # Test 1: DVC status
    try:
        result = subprocess.run(
            ["dvc", "status"],
            capture_output=True,
            text=True,
            cwd=models_dir,
            check=True,
        )
        test_results.append(
            {
                "test": "dvc_status",
                "success": True,
                "output": result.stdout.strip(),
                "description": "DVC status command execution",
            }
        )
    except subprocess.CalledProcessError as e:
        test_results.append(
            {
                "test": "dvc_status",
                "success": False,
                "error": str(e),
                "stderr": e.stderr.decode() if e.stderr else None,
                "description": "DVC status command execution",
            }
        )

    # Test 2: DVC config list
    try:
        result = subprocess.run(
            ["dvc", "config", "--list"],
            capture_output=True,
            text=True,
            cwd=models_dir,
            check=True,
        )
        test_results.append(
            {
                "test": "dvc_config_list",
                "success": True,
                "output": result.stdout.strip(),
                "description": "DVC configuration listing",
            }
        )
    except subprocess.CalledProcessError as e:
        test_results.append(
            {
                "test": "dvc_config_list",
                "success": False,
                "error": str(e),
                "stderr": e.stderr.decode() if e.stderr else None,
                "description": "DVC configuration listing",
            }
        )

    # Test 3: DVC version (should work if DVC is properly installed)
    try:
        result = subprocess.run(
            ["dvc", "--version"],
            capture_output=True,
            text=True,
            cwd=models_dir,
            check=True,
        )
        test_results.append(
            {
                "test": "dvc_version",
                "success": True,
                "output": result.stdout.strip(),
                "description": "DVC version check",
            }
        )
    except subprocess.CalledProcessError as e:
        test_results.append(
            {
                "test": "dvc_version",
                "success": False,
                "error": str(e),
                "stderr": e.stderr.decode() if e.stderr else None,
                "description": "DVC version check",
            }
        )

    # Test 4: Check if DVC files exist
    dvc_dir = models_dir / ".dvc"
    dvc_config = dvc_dir / "config"

    files_test = {
        "test": "dvc_files_exist",
        "success": True,
        "description": "DVC directory and files existence check",
        "details": {},
    }

    files_test["details"]["dvc_dir_exists"] = dvc_dir.exists()
    files_test["details"]["dvc_config_exists"] = dvc_config.exists()
    files_test["details"]["dvcignore_exists"] = (models_dir / ".dvcignore").exists()
    files_test["details"]["dvc_yaml_exists"] = (models_dir / "dvc.yaml").exists()

    # Test fails if any critical files are missing
    if not all(
        [
            files_test["details"]["dvc_dir_exists"],
            files_test["details"]["dvc_config_exists"],
        ]
    ):
        files_test["success"] = False
        files_test["error"] = "Critical DVC files missing"

    test_results.append(files_test)

    # Determine if all tests passed
    all_tests_passed = all(test["success"] for test in test_results)

    return {
        **ctx,
        "operation": "test_dvc_operations",
        "test_results": test_results,
        "all_tests_passed": all_tests_passed,
    }
