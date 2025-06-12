"""
CI Logging Middleware
=====================

Purpose:
    Provides comprehensive logging functionality for CI operations, tracking
    operation progress, timing, and context flow through the chain.

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

Side Effects:
    - Writes log messages to configured logger
    - Measures and optionally stores operation timing

Example Usage:
    Applied as middleware to any ModuLink chain to provide automatic logging
    of all operations with detailed context information.
"""

import logging
import time

from . import Ctx  # Adjusted import for CI context

# Configure logger for CI operations
logger = logging.getLogger("ci_operations")


def ci_logging_middleware(ctx: Ctx, next_func) -> Ctx:
    """Log all CI operations with detailed context and timing"""
    operation = ctx.get("operation", "unknown_operation")
    start_time = time.time()

    # Log operation start
    logger.info(f"🚀 Starting CI operation: {operation}")

    # Log relevant context information (excluding sensitive data)
    context_info = {
        k: v
        for k, v in ctx.items()
        if k not in ["errors", "test_results"] and not k.startswith("_")
    }

    if context_info:
        logger.debug(f"📋 Context for {operation}: {context_info}")

    try:
        # Execute the next function in the chain
        result = next_func(ctx)

        # Calculate duration
        duration = time.time() - start_time

        # Log successful completion
        logger.info(f"✅ Successfully completed: {operation} in {duration:.2f}s")

        # Log any new context additions
        new_keys = set(result.keys()) - set(ctx.keys())
        if new_keys:
            logger.debug(f"📤 New context keys from {operation}: {list(new_keys)}")

        # Optionally add timing to context
        if ctx.get("track_timing", False):
            result = {**result, f"{operation}_duration": duration}

        return result

    except Exception as e:
        # Calculate duration even for failures
        duration = time.time() - start_time

        # Log error with details
        logger.error(
            f"❌ Failed operation: {operation} after {duration:.2f}s - {str(e)}"
        )
        logger.exception(f"💥 Exception details for {operation}:")

        # Re-raise the exception to let error middleware handle it
        raise


__all__ = ["ci_logging_middleware"]
