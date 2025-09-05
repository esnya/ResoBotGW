"""Typed configuration (Pydantic Settings) for ResoBotGW.

Non-null by default; validates required environment values and supports `.env`.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Runtime configuration values (validated, non-null).

    Add fields as the gateway grows. All values must be non-null.
    """

    # Use alias to map from environment variable name
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    # MCP (stdio) optional settings — absence means MCP disabled
    mcp_stdio_command: str | None = Field(default=None, alias="MCP_STDIO_COMMAND")
    mcp_stdio_args: str | None = Field(default=None, alias="MCP_STDIO_ARGS")

    # Settings behaviour
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("openai_api_key")
    @classmethod
    def _validate_openai_api_key(cls, v: str) -> str:
        vv = v.strip()
        if not vv:
            raise ValueError("OPENAI_API_KEY is required and must be non-empty")
        return vv

    @field_validator("mcp_stdio_command")
    @classmethod
    def _validate_mcp_stdio_command(cls, v: str | None) -> str | None:
        if v is None:
            return None
        vv = v.strip()
        if not vv:
            raise ValueError("MCP_STDIO_COMMAND, if set, must be non-empty")
        return vv

    @staticmethod
    def from_env(env: dict[str, str] | None = None) -> Config:
        """Load configuration from the given mapping or OS environment.

        Preserves previous behaviour of raising ValueError on invalid input.
        """
        if env is None:
            try:
                return Config()
            except ValidationError as e:  # keep previous exception surface
                raise ValueError(str(e)) from e

        # Validate from an explicit mapping (no implicit OS read)
        data: dict[str, Any] = {
            "openai_api_key": env.get("OPENAI_API_KEY"),
            "mcp_stdio_command": env.get("MCP_STDIO_COMMAND"),
            "mcp_stdio_args": env.get("MCP_STDIO_ARGS"),
        }
        try:
            return Config.model_validate(data)
        except ValidationError as e:  # keep previous exception surface
            raise ValueError(str(e)) from e
