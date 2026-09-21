from __future__ import annotations

import contextlib
import os
from pathlib import Path

import keyring
from platformdirs import (
    user_config_dir,
    user_data_dir,
)
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)

SERVICE_NAME = "Visual AI Studio"
SECRET_ACCOUNT = "webhook-secret"
DEFAULT_AUTH_HEADER = "X-Visual-AI-Token"


class AppSettings(BaseModel):
    webhook_url: HttpUrl | None = None
    auth_header_name: str = DEFAULT_AUTH_HEADER

    timeout_seconds: float = Field(
        default=300.0,
        ge=1.0,
        le=300.0,
    )

    projects_dir: Path = Field(
        default_factory=lambda: (
            Path(
                user_data_dir(
                    "Visual AI Studio",
                    "Visual AI Studio",
                )
            )
            / "projects"
        )
    )

    agent_url: HttpUrl | None = None

    max_file_size_mb: int = Field(
        default=50,
        ge=1,
        le=500,
    )


class SettingsStore:
    def __init__(
        self,
        path: Path | None = None,
    ) -> None:
        self.path = path or (
            Path(
                user_config_dir(
                    "Visual AI Studio",
                    "Visual AI Studio",
                )
            )
            / "settings.json"
        )

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()

        return AppSettings.model_validate_json(self.path.read_text(encoding="utf-8"))

    def save(
        self,
        settings: AppSettings,
    ) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            settings.model_dump_json(indent=2),
            encoding="utf-8",
        )

    @property
    def secret_path(self) -> Path:
        """Fallback secret file used when the container has no keyring."""
        return self.path.with_name(".webhook-secret")

    def get_secret(self) -> str:
        try:
            secret = keyring.get_password(SERVICE_NAME, SECRET_ACCOUNT) or ""
        except Exception:
            secret = ""
        if secret:
            return secret

        try:
            return self.secret_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            return ""

    def set_secret(self, secret: str) -> None:
        secret = secret.strip()
        if secret:
            self.secret_path.parent.mkdir(parents=True, exist_ok=True)
            self.secret_path.write_text(secret, encoding="utf-8")
            with contextlib.suppress(OSError):
                os.chmod(self.secret_path, 0o600)
            with contextlib.suppress(Exception):
                keyring.set_password(SERVICE_NAME, SECRET_ACCOUNT, secret)
            return

        with contextlib.suppress(Exception):
            keyring.delete_password(SERVICE_NAME, SECRET_ACCOUNT)
        with contextlib.suppress(FileNotFoundError):
            self.secret_path.unlink()
