"""
DVC Middleware Package
=====================

Purpose:
    Exports middleware components for DVC operations, providing reusable
    cross-cutting concerns like logging, error handling, and observability.

Available Middleware:
    - logging_middleware: Comprehensive operation logging and timing
    - error_handler_middleware: Exception handling and error transformation

Usage:
    Import middleware components for use in ModuLink chains:

    from scripts.dvc.middleware import logging_middleware, error_handler_middleware

    chain = chain([...]).with_middleware([
        logging_middleware,
        error_handler_middleware
    ])
"""

from .logging_middleware import logging_middleware
from .error_handler_middleware import error_handler_middleware
from .file_logging_middleware import (
    file_logging_middleware,
    file_logging_before_middleware,
    file_logging_after_middleware,
    setup_file_logger,
)

__all__ = [
    "logging_middleware",
    "error_handler_middleware",
    "file_logging_middleware",
    "file_logging_before_middleware",
    "file_logging_after_middleware",
    "setup_file_logger",
]
