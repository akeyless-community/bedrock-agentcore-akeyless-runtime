"""Hybrid agent: in-agent fetch for bootstrap secrets + tools for on-demand secrets.

Pattern:
- OPENAI_API_KEY loaded directly at startup (fast, deterministic, no tool-call tokens)
- DATABASE_URL fetched via tool when the agent needs it (agent-driven, auditable)

Deploy:
  agentcore deploy
"""

from __future__ import annotations

import json
import os

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.openai import OpenAIModel

from akeyless_agentcore import get_secret
from akeyless_agentcore.tools.strands import create_strands_tools

app = BedrockAgentCoreApp()


def _bootstrap_openai_key() -> str:
    """In-agent fetch: model credentials loaded once at cold start."""
    raw = get_secret("OPENAI_API_KEY")
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("OPENAI_API_KEY"):
            return str(data["OPENAI_API_KEY"]).strip()
    except json.JSONDecodeError:
        pass
    return raw.strip()


@app.entrypoint
async def handler(request):
    api_key = _bootstrap_openai_key()
    model = OpenAIModel(
        client_args={"api_key": api_key},
        model_id=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    )

    # Tool-based fetch: agent decides when to retrieve other secrets
    akeyless_tools = create_strands_tools()
    agent = Agent(
        model=model,
        tools=akeyless_tools,
        system_prompt=(
            "You are a helpful assistant. "
            "Use list_akeyless_secrets to discover available secrets. "
            "Use get_akeyless_secret to fetch values when needed. "
            "Never echo secret values back to the user unless explicitly asked."
        ),
    )

    prompt = request.get("prompt", "")
    async for event in agent.stream_async(prompt):
        yield event


if __name__ == "__main__":
    app.run()
