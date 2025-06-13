"""
File-Based Logging Middleware
============================

Purpose:
    Provides comprehensive file-based logging functionality for DVC operations,
    storing detailed operation logs in persistent files for debugging and auditing.

Input Context Requirements:
    - Any context (works with all contexts)

Output Context Modifications:
    - Adds timing information to context if enabled
    - No destructive modifications to context

Error Conditions:
    - Logging failures are suppressed to avoid breaking the chain

Dependencies:
    - logging: Standard Python logging module
    - time: For operation timing
    - pathlib: For log file path management

Side Effects:
    - Writes detailed log messages to files in logs/ directory
    - Creates log files with rotation and timestamping

Example Usage:
    Applied as middleware to any ModuLink chain to provide automatic file logging
    of all operations with detailed context information and persistence.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

from modulink import Ctx


def setup_file_logger(log_name: str = "dvc_operations") -> logging.Logger:
    """Set up file-based logger with proper formatting and rotation"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create file handler with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{log_name}_{timestamp}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create detailed formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create the file logger instance
file_logger = setup_file_logger("dvc_operations")


def file_logging_middleware(ctx: Ctx) -> Ctx:
    """File-based logging middleware with detailed context tracking"""
    operation = ctx.get("operation", "unknown_operation")
    start_time = time.time()

    # Log operation start with emoji indicators
    file_logger.info(f"🚀 Starting DVC operation: {operation}")

    # Log relevant context information (excluding sensitive data)
    context_info = {
        k: v
        for k, v in ctx.items()
        if k not in ["errors", "test_results"] and not k.startswith("_")
    }

    if context_info:
        # Pretty print context for file logging
        context_json = json.dumps(context_info, indent=2, default=str)
        file_logger.info(f"📋 Context for {operation}:\n{context_json}")

    try:
        # The middleware doesn't execute the next function directly in ModuLink
        # Instead, it logs the current state and returns the context

        # Calculate duration (this is just for the middleware processing time)
        duration = time.time() - start_time

        # Log middleware completion
        file_logger.info(f"✅ Middleware processed: {operation} in {duration:.4f}s")

        # Log any new context additions
        if "started_at" not in ctx:
            ctx = {**ctx, "started_at": datetime.now().isoformat()}

        # Optionally add timing to context
        if ctx.get("track_timing", False):
            ctx = {**ctx, f"{operation}_middleware_duration": duration}

        return ctx

    except Exception as e:
        # Calculate duration even for failures
        duration = time.time() - start_time

        # Log error with details
        file_logger.error(
            f"❌ Middleware failed for: {operation} after {duration:.4f}s - {str(e)}"
        )
        file_logger.exception(f"💥 Exception details for {operation}:")

        # Add error to context but don't break the chain
        errors = ctx.get("errors", [])
        errors.append(f"Middleware error in {operation}: {str(e)}")

        return {**ctx, "errors": errors}


def file_logging_before_middleware(ctx: Ctx) -> Ctx:
    """Before middleware - logs operation start with detailed context"""
    operation = ctx.get("operation", "unknown_operation")

    file_logger.info(f"🎯 BEFORE: {operation}")

    # Filter and log relevant context values (excluding sensitive/large data)
    context_to_log = {}
    for k, v in ctx.items():
        if k.startswith("_"):
            continue  # Skip private keys
        elif k in ["errors", "test_results"] and v:
            context_to_log[k] = (
                f"[{len(v)} items]" if isinstance(v, list) else "[present]"
            )
        elif k == "sample_pipeline" and isinstance(v, dict):
            context_to_log[k] = f"[dict with {len(v)} keys]"
        elif isinstance(v, str | int | float | bool) or v is None:
            context_to_log[k] = v
        elif isinstance(v, list | dict):
            if len(str(v)) > 200:  # Large objects
                context_to_log[k] = f"[{type(v).__name__} - {len(v)} items]"
            else:
                context_to_log[k] = v
        else:
            context_to_log[k] = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)

    if context_to_log:
        context_json = json.dumps(context_to_log, indent=2, default=str)
        file_logger.info(f"📥 Input Context:\n{context_json}")

    return ctx


def file_logging_after_middleware(ctx: Ctx) -> Ctx:
    """After middleware - logs operation completion with detailed context"""
    operation = ctx.get("operation", "unknown_operation")

    file_logger.info(f"🏁 AFTER: {operation}")

    # Filter and log relevant context values (excluding sensitive/large data)
    context_to_log = {}
    for k, v in ctx.items():
        if k.startswith("_"):
            continue  # Skip private keys
        elif k in ["errors", "test_results"] and v:
            context_to_log[k] = (
                f"[{len(v)} items]" if isinstance(v, list) else "[present]"
            )
        elif k == "sample_pipeline" and isinstance(v, dict):
            context_to_log[k] = f"[dict with {len(v)} keys]"
        elif isinstance(v, str | int | float | bool) or v is None:
            context_to_log[k] = v
        elif isinstance(v, list | dict):
            if len(str(v)) > 200:  # Large objects
                context_to_log[k] = f"[{type(v).__name__} - {len(v)} items]"
            else:
                context_to_log[k] = v
        else:
            context_to_log[k] = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)

    if context_to_log:
        context_json = json.dumps(context_to_log, indent=2, default=str)
        file_logger.info(f"📤 Output Context:\n{context_json}")

    # Log any errors that occurred
    if ctx.get("errors"):
        file_logger.warning(f"⚠️ Errors in {operation}: {ctx['errors']}")

    return ctx
