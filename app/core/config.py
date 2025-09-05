import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields to be ignored
    )

    app_env: str = "dev"
    api_keys: str | list[str] = []
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "genai_bench"

    # LLM API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Judge settings
    default_judge_model: str = "gpt-4o-mini"
    judge_prompt_version: str = "v2"

    # Security
    secret_key: str = "dev-secret-key"

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v

    def get_pricing(self) -> dict[str, dict[str, float]]:
        """Get pricing configuration from environment variables"""
        pricing = {}
        for key, value in os.environ.items():
            if key.startswith("PRICE_INPUT."):
                model = key.replace("PRICE_INPUT.", "")
                if model not in pricing:
                    pricing[model] = {}
                pricing[model]["input"] = float(value)
            elif key.startswith("PRICE_OUTPUT."):
                model = key.replace("PRICE_OUTPUT.", "")
                if model not in pricing:
                    pricing[model] = {}
                pricing[model]["output"] = float(value)
        return pricing


settings = Settings()
