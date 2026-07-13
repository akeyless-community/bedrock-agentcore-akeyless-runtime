# Deployment patterns

This guide covers the three ways to use `akeyless-agentcore-runtime` on AWS Bedrock AgentCore.

## Pattern overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AgentCore Runtime                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Your agent (Strands / LangGraph / custom)               │   │
│  │                                                          │   │
│  │  ┌─────────────────┐    ┌──────────────────────────┐  │   │
│  │  │ In-agent fetch  │    │ Strands tools (optional) │  │   │
│  │  │ get_secret      │    │ create_strands_tools()   │  │   │
│  │  └────────┬────────┘    └────────────┬─────────────┘  │   │
│  │           │                          │                 │   │
│  │           └──────────┬───────────────┘                 │   │
│  │                      ▼                                 │   │
│  │           akeyless-agentcore-runtime                   │   │
│  │           (AWS IAM cloud identity → Akeyless)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Akeyless Gateway │
                    └──────────────────┘

Optional: AgentCore Gateway (shared tools across agents)
┌──────────────┐     MCP      ┌─────────────────────┐
│  Agent A     │─────────────▶│  AgentCore Gateway  │
│  Agent B     │─────────────▶│  └─ Lambda: Akeyless│
└──────────────┘              └─────────────────────┘
```

## Pattern 1: In-agent fetch only

**Best for:** agents that need the same secrets on every invocation (model API keys, fixed config).

See [`examples/strands-agent/agent.py`](../examples/strands-agent/agent.py).

```bash
cd examples/strands-agent
pip install -r requirements.txt
agentcore create --name my-agent --defaults   # if new project
agentcore deploy
```

Add to `requirements.txt`:

```
akeyless-agentcore-runtime>=0.3.0
bedrock-agentcore>=0.1.0
```

## Pattern 2: Hybrid (recommended)

**Best for:** bootstrap secrets in code + agent-driven secret retrieval.

See [`examples/hybrid-agent/agent.py`](../examples/hybrid-agent/agent.py).

```bash
cd examples/hybrid-agent
pip install -r requirements.txt
agentcore deploy
```

- `OPENAI_API_KEY` loaded via `get_secret()` at startup
- Other secrets available via `list_akeyless_secrets` / `get_akeyless_secret` tools

## Pattern 3: MCP server on AgentCore Runtime

**Best for:** a dedicated secrets MCP endpoint consumed by multiple agents or MCP clients.

See [`examples/mcp-server/server.py`](../examples/mcp-server/server.py).

```bash
pip install 'akeyless-agentcore-runtime[mcp]'
cd examples/mcp-server
agentcore configure -e server.py --protocol MCP
agentcore deploy
```

Agents connect via MCP and discover:
- `list_akeyless_secrets`
- `get_akeyless_secret`

Run locally for development:

```bash
export AKEYLESS_ACCESS_ID=p-xxxxx
export AKEYLESS_ACCESS_TYPE=access_key
export AKEYLESS_ACCESS_KEY=your-key
export AKEYLESS_SECRET_PREFIX=/bedrock-agentcore/my-agent/dev

akeyless-agentcore-mcp
# Server listens on http://0.0.0.0:8000/mcp
```

## Pattern 4: AgentCore Gateway Lambda

**Best for:** centralized secret tools shared across many agents via AgentCore Gateway.

1. Package and deploy [`examples/gateway-lambda/handler.py`](../examples/gateway-lambda/handler.py) as a Lambda
2. Ensure the Lambda execution role can reach Akeyless (HTTPS egress) and has the same AWS IAM auth binding
3. Register with Gateway:

```bash
pip install 'akeyless-agentcore-runtime[gateway]'
python examples/gateway-lambda/setup_gateway_target.py \
  --lambda-arn arn:aws:lambda:us-east-1:123456789012:function:akeyless-secrets \
  --config gateway_config.json
```

4. Connect your agent to the Gateway MCP endpoint (see [AgentCore Gateway quickstart](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-quick-start.html))

## Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AKEYLESS_ACCESS_ID` | Yes* | — | Akeyless auth method Access ID |
| `AKEYLESS_ACCESS_TYPE` | No | `aws_iam` | Auth method type |
| `AKEYLESS_SECRET_PREFIX` | Recommended | derived | Path prefix for short secret names |
| `AKEYLESS_GATEWAY_URL` | No | `https://api.akeyless.io` | Akeyless API / gateway URL |
| `AGENTCORE_AGENT_NAME` | No | — | Used to derive secret prefix |
| `AKEYLESS_ENV` | No | `production` | Environment segment in derived prefix |
| `AKEYLESS_SECRET_CACHE_TTL_SECONDS` | No | `300` | In-memory secret cache TTL |
| `AKEYLESS_TOKEN_EXPIRY_MARGIN_SECONDS` | No | `60` | Token refresh margin |

\* Not required if `AKEYLESS_TOKEN` is set (pre-authenticated session).

## Choosing a pattern

| Requirement | Pattern |
|-------------|---------|
| Simple agent, one API key | In-agent fetch |
| Agent picks secrets dynamically | Hybrid or tools only |
| Multiple agents, one secrets service | Gateway Lambda or MCP server |
| Secrets must not pass through LLM context | In-agent fetch only |
| Audit tool invocations per secret access | Tools (Gateway or Strands) |
