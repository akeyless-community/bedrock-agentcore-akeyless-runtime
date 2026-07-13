"""Example Bedrock AgentCore agent that fetches secrets from Akeyless at runtime.

Deploy with the AgentCore CLI:
  agentcore deploy

Bootstrap env vars (set in agentcore/aws-targets.json or AgentCore console):
  AKEYLESS_ACCESS_ID=p-xxxxx
  AKEYLESS_ACCESS_TYPE=aws_iam
  AKEYLESS_SECRET_PREFIX=/bedrock-agentcore/my-agent/production
  AGENTCORE_AGENT_NAME=my-agent

Store application secrets in Akeyless (not in AWS Secrets Manager):
  /bedrock-agentcore/my-agent/production/OPENAI_API_KEY
"""

from __future__ import annotations

import json
import os

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.openai import OpenAIModel

from akeyless_agentcore import get_secret

app = BedrockAgentCoreApp()


def _load_openai_api_key() -> str:
    """Fetch the OpenAI API key from Akeyless using the runtime's AWS IAM role."""
    raw = get_secret("OPENAI_API_KEY")
    # Support plain string or JSON {"OPENAI_API_KEY": "sk-..."}
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("OPENAI_API_KEY"):
            return str(data["OPENAI_API_KEY"]).strip()
    except json.JSONDecodeError:
        pass
    return raw.strip()


@app.entrypoint
async def handler(request):
    api_key = _load_openai_api_key()
    model = OpenAIModel(
        client_args={"api_key": api_key},
        model_id=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    )
    agent = Agent(model=model, system_prompt="You are a helpful assistant.")

    prompt = request.get("prompt", "")
    async for event in agent.stream_async(prompt):
        yield event


if __name__ == "__main__":
    app.run()
