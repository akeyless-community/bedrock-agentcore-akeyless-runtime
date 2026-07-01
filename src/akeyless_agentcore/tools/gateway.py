"""AgentCore Gateway Lambda handler and tool schema for Akeyless secrets."""

from __future__ import annotations

import json
from typing import Any

from akeyless_agentcore.tools.service import SecretToolService, SecretType

GATEWAY_TOOL_SCHEMA: dict[str, Any] = {
    "inlinePayload": [
        {
            "name": "list_akeyless_secrets",
            "description": (
                "List Akeyless secret names under a path prefix. "
                "Returns names only, never secret values."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "Optional Akeyless path prefix (defaults to AKEYLESS_SECRET_PREFIX)",
                    }
                },
            },
        },
        {
            "name": "get_akeyless_secret",
            "description": (
                "Fetch a secret value from Akeyless using cloud identity authentication. "
                "Use json_key to return a single field from JSON secrets."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Secret name or full path starting with /",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional full Akeyless path overriding prefix + name",
                    },
                    "secret_type": {
                        "type": "string",
                        "enum": ["static", "dynamic", "rotated"],
                        "description": "Secret type (default: static)",
                    },
                    "json_key": {
                        "type": "string",
                        "description": "Return only this key from a JSON secret",
                    },
                    "ignore_cache": {
                        "type": "boolean",
                        "description": "Bypass in-memory secret cache",
                    },
                },
                "required": ["name"],
            },
        },
    ]
}


def gateway_lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entrypoint for AgentCore Gateway MCP tool invocations."""
    service = SecretToolService()
    tool_name = "unknown"
    if context and getattr(context, "client_context", None):
        custom = getattr(context.client_context, "custom", None) or {}
        tool_name = custom.get("bedrockAgentCoreToolName", "unknown")

    try:
        if "list_akeyless_secrets" in tool_name:
            result = service.list_secrets(prefix=event.get("prefix"))
        elif "get_akeyless_secret" in tool_name:
            secret_type = event.get("secret_type", "static")
            if secret_type not in ("static", "dynamic", "rotated"):
                secret_type = "static"
            result = service.get_secret(
                event["name"],
                path=event.get("path"),
                secret_type=secret_type,  # type: ignore[arg-type]
                json_key=event.get("json_key"),
                ignore_cache=bool(event.get("ignore_cache", False)),
            )
        else:
            result = service.get_secret(event.get("name", "")) if event.get("name") else None
            if result is None:
                return _lambda_response({"ok": False, "error": f"Unknown tool: {tool_name}"}, status=400)

        status = 200 if result.ok else 400
        body = json.loads(result.to_json())
        return _lambda_response(body, status=status)
    except KeyError as exc:
        return _lambda_response({"ok": False, "error": f"Missing required field: {exc}"}, status=400)
    except Exception as exc:
        return _lambda_response({"ok": False, "error": str(exc)}, status=500)


def _lambda_response(body: dict[str, Any], status: int = 200) -> dict[str, Any]:
    return {"statusCode": status, "body": json.dumps(body)}
