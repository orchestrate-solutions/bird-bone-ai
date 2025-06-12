from typing import Dict, Any, Callable

# Import all middleware modules
from . import security_middleware
from . import validation_middleware
from . import testing_middleware
from . import deployment_middleware

Ctx = Dict[str, Any]
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
