# akeyless-agentcore-runtime

Fetch [Akeyless](https://www.akeyless.io) secrets at **runtime** on [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/). Authenticate with **cloud identity** (AWS IAM) — no long-lived API keys in your agent deployment. Application secrets stay in Akeyless, not AWS Secrets Manager.

Built on the [Akeyless Python SDK](https://pypi.org/project/akeyless/) with AgentCore-specific auth, path conventions, caching, and optional MCP tools.

**Repository:** [github.com/akeyless-community/bedrock-agentcore-akeyless-runtime](https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime)

## Documentation

| Guide | Description |
|-------|-------------|
| **[Installation](docs/INSTALL.md)** | **pip install — no git clone required** |
| [Publishing to PyPI](docs/PYPI_PUBLISHING.md) | Trusted publishing setup for maintainers |
| [Akeyless setup](docs/AKEYLESS_SETUP.md) | Auth method, RBAC, secret paths — do this first |
| [Deployment patterns](docs/DEPLOYMENT.md) | In-agent fetch, hybrid, MCP server, Gateway Lambda |
| [Examples](examples/README.md) | Runnable sample agents |
| [Security](SECURITY.md) | Production checklist and reporting |
| [Maintainer guide](docs/MAINTAINER.md) | Branch protection, approvals, PyPI environment |
| [Contributing](CONTRIBUTING.md) | Development setup and PR guidelines |

## Why this integration?

| Concern | AWS default pattern | This integration |
|---------|--------------------|------------------|
| **Authentication to secrets platform** | IAM role → Secrets Manager | IAM role → Akeyless (AWS IAM auth method) |
| **Secret storage** | AWS Secrets Manager | Akeyless (static, dynamic, rotated) |
| **Bootstrap credentials** | None (IAM only) | Only `AKEYLESS_ACCESS_ID` (no secret key) |
| **Rotation & governance** | Secrets Manager policies | Akeyless RBAC, rotation, audit |

AgentCore Runtime provides an IAM execution role with ambient AWS credentials. This library uses those credentials to generate an Akeyless **cloud ID** and authenticate — the same pattern used by EKS, Lambda, and other Akeyless integrations.

## Install

**No git clone needed.** Add to your agent project and install with pip.

### From PyPI (recommended once published)

```bash
pip install akeyless-agentcore-runtime
```

See [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md) for maintainer setup. The package is not on PyPI yet — use GitHub install below until the first release is published.

### From GitHub (available now)

```bash
pip install "akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.3.0"
```

Add to your AgentCore `requirements.txt`:

```text
akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.3.0
bedrock-agentcore>=0.1.0
```

Full install guide (extras, MCP CLI, verification): **[docs/INSTALL.md](docs/INSTALL.md)**

Requires **Python 3.10+**.

## Quick start

### 1. Configure Akeyless

Follow **[docs/AKEYLESS_SETUP.md](docs/AKEYLESS_SETUP.md)** — create an AWS IAM Auth Method, RBAC, and store secrets under `/bedrock-agentcore/<agent>/<env>/`.

### 2. Set bootstrap env vars on AgentCore

Configure only auth + path prefix — **not** application secrets:

| Variable | Required | Example |
|----------|----------|---------|
| `AKEYLESS_ACCESS_ID` | Yes | `p-xxxxx` |
| `AKEYLESS_ACCESS_TYPE` | No (default: `aws_iam`) | `aws_iam` |
| `AKEYLESS_SECRET_PREFIX` | Recommended | `/bedrock-agentcore/my-agent/production` |
| `AKEYLESS_GATEWAY_URL` | No | `https://api.akeyless.io` |

### 3. Fetch a secret in your agent

```python
from akeyless_agentcore import get_secret

api_key = get_secret("OPENAI_API_KEY")
```

Works in both sync scripts and `async def` AgentCore handlers — it calls the Akeyless SDK directly (blocking HTTP, cached between invocations).

### 4. Deploy

```bash
agentcore deploy
```

See [examples/strands-agent/](examples/strands-agent/) for a complete agent.

## Two ways to retrieve secrets

| API | Who calls it | Purpose |
|-----|--------------|---------|
| **`get_secret()`** | Your Python code | Bootstrap secrets (e.g. model API key at startup) |
| **`get_akeyless_secret`** (tool) | The LLM agent | On-demand secrets via Strands / MCP / Gateway |

Both use the same Akeyless SDK under the hood (`auth` + `get_secret_value`). The tool adds a JSON response layer for agent frameworks.

```python
from akeyless_agentcore import get_secret
from akeyless_agentcore.tools.strands import create_strands_tools

api_key = get_secret("OPENAI_API_KEY")              # you call this
agent = Agent(model=model, tools=create_strands_tools())  # agent calls get_akeyless_secret
```

Recommended production pattern: **both** — see [examples/hybrid-agent/](examples/hybrid-agent/).

Full details: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

## API reference

### `get_secret(name)` — fetch a secret from your code

```python
from akeyless_agentcore import get_secret

api_key = get_secret("OPENAI_API_KEY")
```

### `AkeylessRuntimeClient` — full client

```python
from akeyless_agentcore import AkeylessRuntimeClient

client = AkeylessRuntimeClient(
    gateway_url="https://api.akeyless.io",
    secret_prefix="/bedrock-agentcore/my-agent/production",
    access_id="p-xxxxx",
    access_type="aws_iam",
)

client.get_secret("OPENAI_API_KEY")
client.get_secret_json("APP_CONFIG")
client.get_dynamic_secret("aws-creds")
client.get_rotated_secret("api-key")
client.list_secrets()
```

### Agent tools — `get_akeyless_secret` / `list_akeyless_secrets`

```python
from akeyless_agentcore.tools.strands import create_strands_tools
# or: pip install 'akeyless-agentcore-runtime[mcp]' for MCP server
```

## Authentication

| Method | `AKEYLESS_ACCESS_TYPE` | Additional env |
|--------|------------------------|----------------|
| **AWS IAM (recommended)** | `aws_iam` | `AKEYLESS_ACCESS_ID` |
| Access key | `access_key` | `AKEYLESS_ACCESS_ID`, `AKEYLESS_ACCESS_KEY` |
| API key | `api_key` | `AKEYLESS_ACCESS_ID`, `AKEYLESS_ACCESS_KEY` |
| Universal Identity | `universal_identity` | `AKEYLESS_UID_TOKEN` |
| JWT | `jwt` | `AKEYLESS_ACCESS_ID`, `AKEYLESS_JWT` |
| Pre-authenticated | — | `AKEYLESS_TOKEN` |

## Architecture

```mermaid
sequenceDiagram
    participant Agent as AgentCore Runtime
    participant Lib as akeyless-agentcore-runtime
    participant AWS as AWS STS/IAM
    participant AKL as Akeyless Gateway

    Agent->>Lib: get_secret("OPENAI_API_KEY")
    Lib->>AWS: Generate cloud ID (SigV4 GetCallerIdentity)
    AWS-->>Lib: Signed identity proof
    Lib->>AKL: POST /auth (access_id, aws_iam, cloud_id)
    AKL-->>Lib: Session token
    Lib->>AKL: GET /get-secret-value
    AKL-->>Lib: Secret value
    Lib-->>Agent: OPENAI_API_KEY
```

## Local development

```bash
export AKEYLESS_ACCESS_ID=p-xxxxx
export AKEYLESS_ACCESS_TYPE=access_key
export AKEYLESS_ACCESS_KEY=your-readonly-key
export AKEYLESS_SECRET_PREFIX=/bedrock-agentcore/my-agent/dev

python3 -c "from akeyless_agentcore import get_secret; print(get_secret('OPENAI_API_KEY')[:8] + '...')"
```

## Related community projects

- [netlify-akeyless-runtime](https://github.com/akeyless-community/netlify-runtime) — Netlify Functions
- [fly-akeyless-runtime](https://github.com/akeyless-community/fly-runtime) — Fly.io Machines
- [vercel-akeyless-runtime](https://github.com/akeyless-community/vercel-runtime) — Vercel serverless
- [heroku-akeyless-runtime](https://github.com/akeyless-community/heroku-runtime) — Heroku dynos

## License

Apache-2.0
