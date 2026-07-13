# Secure AI Agent Secrets on Amazon Bedrock AgentCore with Akeyless

**Suggested subtitle:** Use cloud identity for authentication and Akeyless for secrets — no long-lived credentials in your agent runtime.

**Meta description (≤160 chars):** Fetch secrets at runtime on Amazon Bedrock AgentCore using AWS IAM cloud identity and Akeyless — no API keys in your deployment.

**Target audience:** Platform engineers, security architects, and developers deploying production AI agents on Amazon Bedrock AgentCore.

**Integration repo:** [github.com/akeyless-community/bedrock-agentcore-akeyless-runtime](https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime)

---

## Introduction

AI agents are moving from prototypes to production. With [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), teams can deploy agents on managed, session-isolated compute — with built-in support for identity, observability, tools, and MCP-based integrations.

But production agents still need secrets: model API keys, database credentials, OAuth client secrets, and third-party service tokens. The security question is not *whether* agents need secrets — it is *how* those secrets are stored, accessed, and governed at runtime.

Today we are introducing an open-source integration — **`akeyless-agentcore-runtime`** — that lets AgentCore agents retrieve secrets from [Akeyless](https://www.akeyless.io) at runtime, authenticated by **AWS IAM cloud identity**. No long-lived Akeyless API keys need to be baked into your agent deployment. Application secrets stay in Akeyless; AgentCore provides the identity.

This article explains the problem, the architecture, how the integration works with AgentCore Runtime and AgentCore Gateway, and how to get started in minutes.

---

## The challenge: secrets in agent runtimes

When you deploy an agent to AgentCore Runtime, AWS provisions an **IAM execution role** for your workload. That role is the cryptographic identity of your agent — the same pattern used across AWS for Lambda, EKS, and ECS.

For secrets, many teams default to one of two approaches:

1. **Environment variables** — simple, but secrets are duplicated across deployments, visible in configuration, and hard to rotate centrally.
2. **AWS Secrets Manager** — native and well integrated, but organizations with existing secrets platforms (or multi-cloud requirements) may already govern secrets elsewhere.

Neither approach fully leverages what AgentCore already gives you: a **strong cloud identity at runtime**. If your enterprise secrets platform can trust that identity, agents can authenticate without static credentials — and secrets never need to leave your governed vault.

That is the model this integration enables.

---

## The solution: cloud identity in, secrets out

The integration follows a simple split of responsibilities:

| Layer | Responsibility |
|-------|----------------|
| **Amazon Bedrock AgentCore** | Workload identity (IAM execution role), runtime compute, Gateway MCP, observability |
| **AWS IAM** | Proves *who* the agent is (SigV4-signed identity) |
| **Akeyless** | Stores, rotates, and governs *what* the agent can access |
| **`akeyless-agentcore-runtime`** | Connects the two at runtime — authenticate with cloud identity, fetch secrets on demand |

```
┌──────────────────────────────────────────────────────────────────┐
│              Amazon Bedrock AgentCore Runtime                     │
│                                                                   │
│   Your agent (Strands, LangGraph, custom)                          │
│        │                                                          │
│        ▼                                                          │
│   akeyless-agentcore-runtime                                     │
│        │                                                          │
│        ├──▶ AWS STS / IAM  (generate cloud identity proof)         │
│        └──▶ Akeyless Gateway  (auth + get-secret-value)          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Bootstrap configuration** on the agent is minimal — only non-secret values such as an Akeyless Access ID and a secret path prefix. Application secrets (API keys, DB URLs, tokens) live in Akeyless and are pulled at runtime.

---

## How authentication works

AgentCore Runtime workloads run with ambient AWS credentials from their execution role. The integration uses the same **AWS IAM authentication method** already supported by Akeyless across Lambda, EKS, Jenkins, and other platforms:

1. The library generates an Akeyless **cloud ID** — a SigV4-signed `sts:GetCallerIdentity` proof from the agent's IAM role.
2. It calls the Akeyless `/auth` API with `access_type=aws_iam`, the configured Access ID, and the cloud ID.
3. Akeyless validates the cloud ID against an **AWS IAM Auth Method** bound to the AgentCore execution role ARN.
4. Akeyless returns a short-lived session token.
5. The library uses that token to fetch secrets via `get-secret-value`, `get-dynamic-secret-value`, or `get-rotated-secret-value`.

No Akeyless access key is stored in the AgentCore deployment. If the execution role is compromised, you revoke or rotate at the IAM layer; if a secret is compromised, you rotate in Akeyless — without redeploying the agent.

This aligns with AgentCore's security model: **identity from AWS, least-privilege access to external resources.**

---

## Deployment patterns

The integration supports three production patterns, which can be used independently or together.

### 1. In-agent fetch (bootstrap secrets)

For secrets needed on every invocation — such as a model API key — fetch directly in agent code:

```python
from akeyless_agentcore import get_secret

api_key = get_secret("OPENAI_API_KEY")
```

This is fast, deterministic, and avoids LLM tool-call overhead. Warm AgentCore invocations benefit from in-memory caching of auth tokens and secret values.

### 2. AgentCore tools (on-demand secrets)

For secrets the agent should retrieve dynamically — database credentials, per-tenant config, rotated API keys — expose Akeyless as **MCP tools** compatible with AgentCore Gateway and in-process frameworks like Strands:

| Tool | Returns values? | Purpose |
|------|----------------|---------|
| `list_akeyless_secrets` | No (names only) | Discover secrets under a path prefix |
| `get_akeyless_secret` | Yes | Fetch static, dynamic, or rotated secrets |

Tools authenticate with the same AWS IAM cloud identity — no separate credential path.

### 3. Hybrid (recommended for production)

Combine both: bootstrap what you always need, tool-call what you need on demand.

```python
from akeyless_agentcore import get_secret
from akeyless_agentcore.tools.strands import create_strands_tools

api_key = get_secret("OPENAI_API_KEY")   # every invocation
tools = create_strands_tools()                 # agent-driven secrets
```

You can also deploy a **dedicated MCP server** on AgentCore Runtime or register a **Gateway Lambda target** so multiple agents share one secrets tool endpoint.

---

## Integration with AgentCore services

### AgentCore Runtime

Add the library to your agent's `requirements.txt` and deploy with the AgentCore CLI:

```text
akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.3.0
bedrock-agentcore>=0.1.0
```

Set bootstrap environment variables in your AgentCore deployment config:

| Variable | Example |
|----------|---------|
| `AKEYLESS_ACCESS_ID` | `p-xxxxxxxxxxxx` |
| `AKEYLESS_ACCESS_TYPE` | `aws_iam` |
| `AKEYLESS_SECRET_PREFIX` | `/bedrock-agentcore/my-agent/production` |

### AgentCore Gateway

For organizations centralizing tools behind [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), the integration provides a Lambda handler and MCP tool schema. Agents discover `list_akeyless_secrets` and `get_akeyless_secret` alongside your other tools — with Gateway handling ingress authentication and tool routing.

### AgentCore Identity

AgentCore Identity manages OAuth tokens and credentials for user-delegated and machine-to-machine flows to third-party services. This integration complements that layer: **AgentCore Identity for OAuth and token vault use cases; Akeyless for centralized secrets management, dynamic credentials, and cross-platform governance** — especially when secrets already live in Akeyless or must be shared across AWS and non-AWS workloads.

---

## Security benefits

**No long-lived secrets in the deployment.** Only the Akeyless Access ID and path prefix are configured on the agent. The Access ID is not a secret — it is an identifier bound to IAM role validation.

**Least privilege by path.** Scope each agent to `/bedrock-agentcore/<agent-name>/<environment>/*` with read-only RBAC in Akeyless.

**Audit trail.** Every secret access is logged in Akeyless with the authenticated identity — supporting compliance and incident response.

**Dynamic and rotated secrets.** Beyond static secrets, agents can fetch short-lived database credentials, cloud API keys, and rotated tokens — reducing blast radius compared to static environment variables.

**No secret sprawl across environments.** Production, staging, and development secrets are separated by path prefix — aligned with AgentCore deployment contexts.

---

## Getting started

### Prerequisites

- An AWS account with Amazon Bedrock AgentCore access
- Python 3.10+ and the [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html)
- An Akeyless account (SaaS or self-hosted gateway)

### Step 1: Configure Akeyless

1. Create an **AWS IAM Auth Method** bound to your AgentCore execution role ARN.
2. Create a read-only Akeyless role scoped to `/bedrock-agentcore/my-agent/production/*`.
3. Store secrets in Akeyless:

   ```
   /bedrock-agentcore/my-agent/production/OPENAI_API_KEY
   /bedrock-agentcore/my-agent/production/DATABASE_URL
   ```

### Step 2: Add the library to your agent

```python
from bedrock_agentcore import BedrockAgentCoreApp
from akeyless_agentcore import get_secret

app = BedrockAgentCoreApp()

@app.entrypoint
async def handler(request):
    api_key = get_secret("OPENAI_API_KEY")
    # ... initialize your agent with api_key ...
    yield {"status": "ready"}
```

### Step 3: Deploy

```bash
agentcore deploy
```

Full setup guides, examples, and deployment patterns are in the [integration repository](https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime).

---

## Example: Strands agent on AgentCore

A complete example agent using [Strands Agents](https://github.com/strands-agents/sdk-python) is available in the repository. It loads an OpenAI API key from Akeyless at invocation time — no secrets in `agentcore/aws-targets.json` or CloudFormation templates.

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models.openai import OpenAIModel
from akeyless_agentcore import get_secret

app = BedrockAgentCoreApp()

@app.entrypoint
async def handler(request):
    api_key = get_secret("OPENAI_API_KEY")
    model = OpenAIModel(client_args={"api_key": api_key}, model_id="gpt-4o-mini")
    agent = Agent(model=model)

    async for event in agent.stream_async(request.get("prompt", "")):
        yield event
```

---

## When to use Akeyless vs. AWS Secrets Manager on AgentCore

Both are valid on AgentCore. Choose based on your organization's needs:

| Consideration | AWS Secrets Manager | Akeyless + this integration |
|---------------|--------------------|-----------------------------|
| Native AWS integration | Built-in, minimal setup | Requires Akeyless auth method binding |
| Multi-cloud / hybrid secrets | AWS-scoped | Centralized across clouds and platforms |
| Dynamic & rotated credentials | Supported | Core Akeyless capability |
| Existing secrets investment | Best if already on AWS SM | Best if already on Akeyless |
| Agent identity | IAM role → Secrets Manager policy | IAM role → Akeyless cloud ID auth |

For teams already on Akeyless, this integration lets AgentCore agents participate in the same secrets governance model as the rest of the estate — without migrating secrets into a second vault.

---

## What's next

The integration is open source under Apache 2.0, maintained by the [Akeyless community](https://github.com/akeyless-community), with examples for:

- In-agent fetch (`examples/strands-agent/`)
- Hybrid bootstrap + tools (`examples/hybrid-agent/`)
- MCP server on AgentCore Runtime (`examples/mcp-server/`)
- AgentCore Gateway Lambda target (`examples/gateway-lambda/`)

We welcome feedback, issues, and contributions from the AgentCore community.

**Resources:**

- Integration repository: [github.com/akeyless-community/bedrock-agentcore-akeyless-runtime](https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime)
- Amazon Bedrock AgentCore: [aws.amazon.com/bedrock/agentcore](https://aws.amazon.com/bedrock/agentcore/)
- AgentCore documentation: [docs.aws.amazon.com/bedrock-agentcore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- Akeyless documentation: [docs.akeyless.io](https://docs.akeyless.io)

---

## About the authors

*[Placeholder — add author names, titles, and affiliations for Akeyless and AWS co-authors as appropriate for publication.]*

---

## Publication notes (remove before publishing)

### Suggested title alternatives for AWS review

1. **Secure AI Agent Secrets on Amazon Bedrock AgentCore with Akeyless** *(recommended)*
2. Bringing Enterprise Secrets Management to Amazon Bedrock AgentCore
3. Zero-Standing-Access Secrets for AgentCore: Cloud Identity Meets Akeyless

### Suggested AWS blog category

- AWS Marketplace / Partner Network showcase, or
- AWS Security Blog (AI agents + secrets management angle), or
- Amazon Bedrock / Machine Learning blog

### Assets to prepare for co-publish

- [ ] Architecture diagram (high-res PNG/SVG) — adapt the mermaid flow above
- [ ] Screenshot of Akeyless AWS IAM Auth Method configuration
- [ ] Screenshot of AgentCore deploy with env vars (redacted)
- [ ] 60-second demo video: deploy agent → fetch secret → invoke

### AWS legal / review checklist

- [ ] Confirm "Amazon Bedrock AgentCore" first-use naming per AWS trademark guidelines
- [ ] Confirm no unsupported claims about AWS partnership unless formally approved
- [ ] AWS reviewer validates AgentCore service descriptions and links
- [ ] Redact any customer-specific paths or account IDs in code samples

### Short social post (LinkedIn / X)

> Production AI agents on Amazon Bedrock AgentCore need secrets — but they shouldn't carry long-lived API keys.
>
> We built an open-source integration that uses your agent's **AWS IAM execution role** to authenticate to **Akeyless** and fetch secrets at runtime.
>
> ✅ Cloud identity auth — no static credentials in the deployment
> ✅ Static, dynamic, and rotated secrets
> ✅ Works with AgentCore Runtime, Gateway MCP tools, and Strands agents
>
> Get started: [link to repo]

### Estimated read time

~8 minutes (≈1,600 words)
