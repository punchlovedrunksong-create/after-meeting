import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _split_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    frontend_origins: tuple[str, ...] = tuple(
        _split_origins(
            os.getenv(
                "FRONTEND_ORIGIN",
                "http://127.0.0.1:5173,http://localhost:5173",
            )
        )
    )
    ai_base_url: str = os.getenv("AI_BASE_URL", "").strip()
    ai_model: str = os.getenv("AI_MODEL", "")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_timeout_seconds: float = float(os.getenv("AI_TIMEOUT_SECONDS", "45"))


settings = Settings()

