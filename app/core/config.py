from pathlib import Path

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, extra="allow", env_file=".env"
    )

    app_title: str = Field(default="RAG System")
    app_host: str = Field(default="0.0.0.0")
    app_port: str = Field(default="8001")
    docs_path: Path = Field(default="data/docs")
    debug: bool = Field(default=True)
    azure_docs_loader_key: str = Field(default=...)
    azure_docs_loader_endpoint: str = Field(default=...)
    azure_openai_endpoint: AnyHttpUrl = Field(default=...)
    azure_openai_api_key: str = Field(default=...)
    azure_openai_api_version: str = Field(default="2024-08-01-preview")
    ollama_base_url: AnyHttpUrl = Field(default="http://192.168.31.192:11434")

    @field_validator("docs_path", mode="before")
    def validate_and_create_directory(cls, value):  # noqa:N805
        resolved_path = Path(value).resolve()
        if not resolved_path.exists():
            resolved_path.mkdir(parents=True, exist_ok=True)
        if not resolved_path.is_dir():
            msg = f"Path {resolved_path} not a directory."
            raise ValueError(msg)
        return resolved_path


settings = AppSettings()
