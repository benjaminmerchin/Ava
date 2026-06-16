import os
from functools import lru_cache

try:  # optional — app must boot even without python-dotenv installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass


class Settings:
    def __init__(self) -> None:
        self.llm_base_url = os.getenv("AVA_LLM_BASE_URL", "").strip()
        self.llm_api_key = os.getenv("AVA_LLM_API_KEY", "").strip()
        self.llm_model = os.getenv("AVA_LLM_MODEL", "").strip()
        self.deep_mode = os.getenv("AVA_DEEP_MODE", "false").lower() in ("1", "true", "yes")
        self.allowed_origins = [
            o.strip() for o in os.getenv("AVA_ALLOWED_ORIGINS", "*").split(",") if o.strip()
        ]
        self.docs_root = os.getenv(
            "AVA_DOCS_ROOT",
            os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "docs")),
        )

    @property
    def has_llm(self) -> bool:
        """True once the TrueFoundry gateway is configured; otherwise mock mode."""
        return bool(self.llm_api_key and self.llm_model)


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
