"""In-process Strands tools for agents that call Akeyless without Gateway."""

from __future__ import annotations

from typing import Any

from akeyless_agentcore.tools.service import SecretToolService, SecretType

try:
    from strands import tool
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError(
        "Strands tools require strands-agents. Install with: "
        "pip install 'akeyless-agentcore-runtime[strands]'"
    ) from exc


def create_strands_tools(service: SecretToolService | None = None) -> list[Any]:
    """Return Strands tool callables backed by the shared SecretToolService."""
    tool_service = service or SecretToolService()

    @tool
    def list_akeyless_secrets(prefix: str | None = None) -> str:
        """List Akeyless secret names under a path prefix. Returns names only, never values."""
        return tool_service.list_secrets(prefix=prefix).to_json()

    @tool
    def get_akeyless_secret(
        name: str,
        path: str | None = None,
        secret_type: SecretType = "static",
        json_key: str | None = None,
        ignore_cache: bool = False,
    ) -> str:
        """Fetch a secret from Akeyless. Use json_key for a single field from JSON secrets."""
        return tool_service.get_secret(
            name,
            path=path,
            secret_type=secret_type,
            json_key=json_key,
            ignore_cache=ignore_cache,
        ).to_json()

    return [list_akeyless_secrets, get_akeyless_secret]
