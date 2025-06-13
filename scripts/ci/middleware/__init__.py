from collections.abc import Callable
from typing import Any

# Import all middleware modules
from . import (deployment_middleware, security_middleware, testing_middleware,
               validation_middleware)

Ctx = dict[str, Any]
Middleware = Callable[[Ctx, Callable[[Ctx], Ctx]], Ctx]

# Make modules available at package level
__all__ = [
    "security_middleware",
    "validation_middleware",
    "testing_middleware",
    "deployment_middleware",
    "Ctx",
    "Middleware",
]
