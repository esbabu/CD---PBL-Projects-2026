import asyncio
from typing import Dict

class CancellationToken:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

class CancellationManager:
    def __init__(self):
        self._tokens: Dict[str, CancellationToken] = {}

    def get_token(self, run_id: str) -> CancellationToken:
        if run_id not in self._tokens:
            self._tokens[run_id] = CancellationToken(run_id)
        return self._tokens[run_id]

    def cancel(self, run_id: str) -> bool:
        token = self._tokens.get(run_id)
        if token:
            token.cancel()
            return True
        return False

    def remove(self, run_id: str) -> None:
        self._tokens.pop(run_id, None)

cancellation_manager = CancellationManager()
