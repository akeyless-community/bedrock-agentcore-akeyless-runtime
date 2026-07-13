"""Tests for the shared secret tool service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from akeyless_agentcore.tools.service import SecretToolService


class FakeClient:
    def __init__(self) -> None:
        self.config = MagicMock(secret_prefix="/bedrock-agentcore/demo/production")

    def resolve_path(self, name: str) -> str:
        return f"/bedrock-agentcore/demo/production/{name}"

    def list_secrets(self, prefix: str | None = None) -> list[str]:
        base = prefix or self.config.secret_prefix
        return [f"{base}/OPENAI_API_KEY", f"{base}/DATABASE_URL"]

    def get_secret(self, name: str, options=None) -> str:
        return f"static-value-for-{name}"

    def get_dynamic_secret(self, name: str, options=None) -> str:
        return f"dynamic-value-for-{name}"

    def get_rotated_secret(self, name: str, options=None) -> str:
        return f"rotated-value-for-{name}"


class TestSecretToolService:
    def test_list_secrets_returns_names_only(self):
        service = SecretToolService(client=FakeClient())  # type: ignore[arg-type]
        result = service.list_secrets()
        assert result.ok is True
        assert result.data["count"] == 2
        assert "OPENAI_API_KEY" in result.data["secrets"][0]

    def test_get_static_secret(self):
        service = SecretToolService(client=FakeClient())  # type: ignore[arg-type]
        result = service.get_secret("DATABASE_URL")
        assert result.ok is True
        assert result.data["value"] == "static-value-for-DATABASE_URL"

    def test_get_dynamic_secret(self):
        service = SecretToolService(client=FakeClient())  # type: ignore[arg-type]
        result = service.get_secret("aws-creds", secret_type="dynamic")
        assert result.ok is True
        assert "dynamic-value" in result.data["value"]

    def test_get_json_key(self):
        client = FakeClient()

        def get_secret(name: str, options=None) -> str:
            return '{"OPENAI_API_KEY": "sk-test", "ORG": "acme"}'

        client.get_secret = get_secret  # type: ignore[method-assign]
        service = SecretToolService(client=client)  # type: ignore[arg-type]
        result = service.get_secret("OPENAI_API_KEY", json_key="OPENAI_API_KEY")
        assert result.ok is True
        assert result.data["value"] == "sk-test"

    def test_missing_json_key(self):
        client = FakeClient()
        client.get_secret = lambda name, options=None: '{"other": "x"}'  # type: ignore[method-assign]
        service = SecretToolService(client=client)  # type: ignore[arg-type]
        result = service.get_secret("cfg", json_key="missing")
        assert result.ok is False
        assert "not found" in (result.error or "").lower()
