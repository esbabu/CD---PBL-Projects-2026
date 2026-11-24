from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve repository root: backend/app/core/config.py -> parents[3] == CompilerAI/
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_agent_dir(explicit_path: Optional[str], relative_candidates: List[str], fallback_candidates: List[str]) -> str:
    if explicit_path:
        p = Path(explicit_path)
        if p.is_dir():
            return str(p.resolve())
    for rel in relative_candidates:
        p = PROJECT_ROOT / rel
        if p.is_dir():
            return str(p.resolve())
    for fb in fallback_candidates:
        p = Path(fb)
        if p.is_dir():
            return str(p.resolve())
    return explicit_path or str(PROJECT_ROOT / relative_candidates[0])


class Settings(BaseSettings):
    app_name: str = "CompilerAI Run Service"
    app_version: str = "0.2.0"
    api_prefix: str = "/api"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    demo_mode: bool = False

    # Optional explicit overrides via .env; auto-discovers workspace-local folders first
    algo_agent_path_override: Optional[str] = None
    security_agent_path_override: Optional[str] = None

    use_real_optimization: bool = True
    use_real_security: bool = True
    llm_connected: bool = False

    @property
    def algo_agent_path(self) -> str:
        return _resolve_agent_dir(
            self.algo_agent_path_override,
            relative_candidates=[
                "algo_agent_groq",
                "algo_agent/algo_agent",
                "algo_agent",
            ],
            fallback_candidates=[
                r"c:\Users\user\Desktop\algo_agent_groq",
                r"c:\Users\user\Desktop\algo_agent\algo_agent",
            ],
        )

    @property
    def security_agent_path(self) -> str:
        return _resolve_agent_dir(
            self.security_agent_path_override,
            relative_candidates=[
                "security_related_files (2)/security_related_files",
                "security_related_files/security_related_files",
                "security_related_files",
            ],
            fallback_candidates=[
                r"c:\Users\user\Desktop\security_related_files (2)\security_related_files",
            ],
        )

    @property
    def optimization_adapter_mode(self) -> str:
        if self.use_real_optimization and Path(self.algo_agent_path).is_dir():
            return "real"
        return "mock"

    @property
    def security_adapter_mode(self) -> str:
        if self.use_real_security and Path(self.security_agent_path).is_dir():
            return "real"
        return "mock"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
