"""
DVC Error Handler Middleware
===========================

Purpose:
    Handles and transforms exceptions that occur during DVC operations into
    structured error information stored in context, enabling graceful error
    recovery and detailed error reporting.

Input Context Requirements:
    - Any context (works with all contexts)

Output Context Modifications:
    - Adds 'errors' list to context when exceptions occur
    - Preserves original context data

Error Conditions:
    - All exceptions are caught and transformed into context errors
    - Does not re-raise exceptions (absorbs them into context)

Dependencies:
    - subprocess: For handling subprocess errors
    - json: For JSON parsing errors
    - yaml: For YAML parsing errors

Side Effects:
    - Converts exceptions into structured error data
    - Prevents exception propagation up the chain

Example Usage:
    Applied as middleware to DVC chains to ensure that any operation failures
    are captured as structured data rather than causing chain termination.
"""

import subprocess
import json
from modulink import Middleware, Ctx


def error_handler_middleware(ctx: Ctx, next_func) -> Ctx:
    """Handle DVC-specific errors and emit them as context"""
    try:
        return next_func(ctx)

    except subprocess.CalledProcessError as e:
        """Handle DVC command execution errors"""
        error_info = {
            "type": "dvc_command_error",
            "operation": ctx.get("operation", "unknown"),
            "command": " ".join(e.cmd) if isinstance(e.cmd, list) else str(e.cmd),
            "returncode": e.returncode,
            "stdout": e.stdout.decode("utf-8") if e.stdout else None,
            "stderr": e.stderr.decode("utf-8") if e.stderr else None,
            "timestamp": ctx.get("operation", "unknown"),
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}

    except FileNotFoundError as e:
        """Handle missing file/directory errors"""
        error_info = {
            "type": "file_not_found_error",
            "operation": ctx.get("operation", "unknown"),
            "details": str(e),
            "filename": (
                str(e.filename) if hasattr(e, "filename") and e.filename else None
            ),
            "errno": e.errno if hasattr(e, "errno") else None,
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}

    except PermissionError as e:
        """Handle permission-related errors"""
        error_info = {
            "type": "permission_error",
            "operation": ctx.get("operation", "unknown"),
            "details": str(e),
            "filename": (
                str(e.filename) if hasattr(e, "filename") and e.filename else None
            ),
            "errno": e.errno if hasattr(e, "errno") else None,
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}

    except (json.JSONDecodeError, ValueError) as e:
        """Handle JSON/YAML parsing errors"""
        error_info = {
            "type": "parsing_error",
            "operation": ctx.get("operation", "unknown"),
            "details": str(e),
            "error_type": type(e).__name__,
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}

    except OSError as e:
        """Handle general OS-level errors"""
        error_info = {
            "type": "os_error",
            "operation": ctx.get("operation", "unknown"),
            "details": str(e),
            "errno": e.errno if hasattr(e, "errno") else None,
            "filename": (
                str(e.filename) if hasattr(e, "filename") and e.filename else None
            ),
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}

    except Exception as e:
        """Handle any other unexpected errors"""
        error_info = {
            "type": "general_error",
            "operation": ctx.get("operation", "unknown"),
            "details": str(e),
            "exception_type": type(e).__name__,
            "exception_module": type(e).__module__,
        }

        return {**ctx, "errors": ctx.get("errors", []) + [error_info]}
