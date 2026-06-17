import os
from functools import lru_cache

try:  # optional — app must boot even without python-dotenv installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass


class Settings:
    def __init__(self) -> None:
        # TrueFoundry AI Gateway (OpenAI-compatible). Same vars as lyvica-resilient-agent.
        self.tfy_base_url = os.getenv("TFY_BASE_URL", "").strip()
        self.tfy_api_key = os.getenv("TFY_API_KEY", "").strip()
        self.model_primary = os.getenv("MODEL_PRIMARY", "").strip()
        self.model_fallbacks = [
            m.strip()
            for m in (os.getenv("MODEL_FALLBACK_1", ""), os.getenv("MODEL_FALLBACK_2", ""))
            if m.strip()
        ]

        self.deep_mode = os.getenv("AVA_DEEP_MODE", "false").lower() in ("1", "true", "yes")
        self.allowed_origins = [
            o.strip() for o in os.getenv("AVA_ALLOWED_ORIGINS", "*").split(",") if o.strip()
        ]
        self.docs_root = os.getenv(
            "AVA_DOCS_ROOT",
            os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "docs")),
        )

        # ElevenLabs TTS (direct — the TF gateway has no audio)
        self.eleven_api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
        self.eleven_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL").strip()
        self.eleven_model = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2_5").strip()

    @property
    def model_chain(self) -> list[str]:
        """Primary first, then fallbacks."""
        return [self.model_primary, *self.model_fallbacks] if self.model_primary else []

    @property
    def has_llm(self) -> bool:
        """True once the TrueFoundry gateway is configured; otherwise mock mode."""
        return bool(self.tfy_api_key and self.tfy_base_url and self.model_primary)

    @property
    def has_tts(self) -> bool:
        return bool(self.eleven_api_key)


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
