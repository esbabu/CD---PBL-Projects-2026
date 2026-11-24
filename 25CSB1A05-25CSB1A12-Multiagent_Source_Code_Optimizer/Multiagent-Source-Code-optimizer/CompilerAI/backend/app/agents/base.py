from typing import Protocol, Callable, Awaitable
from app.contracts.requests import RunMode, InferenceMode
from app.contracts.optimization import OptimizationRequest, OptimizationResult
from app.contracts.security import SecurityRequest, SecurityResult
from app.contracts.events import RunEvent

# Port protocols defining stable adapter boundaries
class OptimizationAgentPort(Protocol):
    async def run(
        self,
        request: OptimizationRequest,
        emit: Callable[[RunEvent], Awaitable[None]],
    ) -> OptimizationResult:
        """Execute optimization on source code and emit progress events."""
        ...

class SecurityAgentPort(Protocol):
    async def run(
        self,
        request: SecurityRequest,
        emit: Callable[[RunEvent], Awaitable[None]],
    ) -> SecurityResult:
        """Execute security assessment on source code and emit progress events."""
        ...
