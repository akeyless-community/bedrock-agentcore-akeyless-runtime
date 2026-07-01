"""AgentCore tool integrations for Akeyless secrets."""

from akeyless_agentcore.tools.service import SecretToolService

__all__ = [
    "GATEWAY_TOOL_SCHEMA",
    "SecretToolService",
    "create_mcp_server",
    "create_strands_tools",
    "gateway_lambda_handler",
    "run_mcp_server",
]


def __getattr__(name: str):
    if name in ("create_mcp_server", "run_mcp_server"):
        from akeyless_agentcore.tools.mcp import create_mcp_server, run_mcp_server

        return {"create_mcp_server": create_mcp_server, "run_mcp_server": run_mcp_server}[name]
    if name == "create_strands_tools":
        from akeyless_agentcore.tools.strands import create_strands_tools

        return create_strands_tools
    if name in ("gateway_lambda_handler", "GATEWAY_TOOL_SCHEMA"):
        from akeyless_agentcore.tools.gateway import GATEWAY_TOOL_SCHEMA, gateway_lambda_handler

        return {
            "gateway_lambda_handler": gateway_lambda_handler,
            "GATEWAY_TOOL_SCHEMA": GATEWAY_TOOL_SCHEMA,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
