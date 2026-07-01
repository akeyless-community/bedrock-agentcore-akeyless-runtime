"""Deployable MCP server exposing Akeyless secrets as AgentCore Runtime tools.

Deploy with AgentCore CLI:
  agentcore configure -e server.py --protocol MCP
  agentcore deploy

Or run locally:
  AKEYLESS_ACCESS_ID=p-xxxxx AKEYLESS_ACCESS_TYPE=access_key AKEYLESS_ACCESS_KEY=... \\
    python server.py
"""

from akeyless_agentcore.tools.mcp import run_mcp_server

if __name__ == "__main__":
    run_mcp_server()
