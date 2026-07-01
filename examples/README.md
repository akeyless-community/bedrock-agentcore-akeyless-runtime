# Examples

| Example | Pattern | Description |
|---------|---------|-------------|
| [`strands-agent/`](strands-agent/) | In-agent fetch | Minimal Strands agent; loads OpenAI key from Akeyless at startup |
| [`hybrid-agent/`](hybrid-agent/) | Hybrid | Bootstrap fetch + Strands tools for on-demand secrets |
| [`mcp-server/`](mcp-server/) | MCP server | Standalone MCP endpoint deployable to AgentCore Runtime |
| [`gateway-lambda/`](gateway-lambda/) | Gateway Lambda | Lambda handler + setup script for AgentCore Gateway |

## Quick start

1. Complete [Akeyless setup](../docs/AKEYLESS_SETUP.md)
2. Copy `.env.example` to `.env` for local testing (never commit `.env`)
3. Pick an example and follow its `requirements.txt`

```bash
# Local test (access_key auth)
export AKEYLESS_ACCESS_ID=p-xxxxx
export AKEYLESS_ACCESS_TYPE=access_key
export AKEYLESS_ACCESS_KEY=your-readonly-key
export AKEYLESS_SECRET_PREFIX=/bedrock-agentcore/my-agent/dev

cd examples/strands-agent
pip install -r requirements.txt
python agent.py   # or: agentcore deploy
```
