# Akeyless setup for AgentCore

Step-by-step guide to configure Akeyless before deploying an AgentCore agent with this library.

## Prerequisites

- An [Akeyless](https://www.akeyless.io) account (SaaS or self-hosted gateway)
- An AWS account with [Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) access
- Your AgentCore agent deployed (or planned) with an IAM execution role

## 1. Create an AWS IAM Auth Method

In the Akeyless console (or CLI), create an **AWS IAM** authentication method:

1. Go to **Auth Methods** → **New** → **AWS IAM**
2. Bind it to your AgentCore execution role ARN:
   ```
   arn:aws:iam::<account-id>:role/<agentcore-execution-role-name>
   ```
3. Copy the **Access ID** (format: `p-xxxxxxxxxxxx`)

> **Tip:** After your first `agentcore deploy`, find the execution role in the CloudFormation stack outputs or IAM console. You can update the auth method binding if the role name changes.

### CLI example

```bash
akeyless create-auth-method-aws-iam \
  --name agentcore-my-agent \
  --bound-iam-role-arn "arn:aws:iam::123456789012:role/AgentCoreExecutionRole"
```

## 2. Create a secret path and RBAC

Use a dedicated path per agent and environment:

```
/bedrock-agentcore/my-agent/production/
/bedrock-agentcore/my-agent/staging/
```

Create an Akeyless **role** with read-only access to that path:

| Permission | Scope |
|------------|-------|
| `read` | `/bedrock-agentcore/my-agent/production/*` |
| `list` | `/bedrock-agentcore/my-agent/production/*` |

Associate the AWS IAM auth method with this role.

## 3. Store secrets in Akeyless

Create static secrets under your prefix:

```
/bedrock-agentcore/my-agent/production/OPENAI_API_KEY
/bedrock-agentcore/my-agent/production/DATABASE_URL
/bedrock-agentcore/my-agent/production/APP_CONFIG   # JSON with multiple keys
```

**JSON secret example** (`APP_CONFIG`):

```json
{
  "DATABASE_URL": "postgresql://user:pass@host:5432/db",
  "STRIPE_KEY": "sk_live_..."
}
```

Use `get_secret_json("APP_CONFIG")` or `get_akeyless_secret(..., json_key="DATABASE_URL")` to read individual fields.

## 4. Configure AgentCore environment variables

Set **bootstrap** variables only — never application secrets:

```json
{
  "environment": {
    "AKEYLESS_ACCESS_ID": "p-xxxxxxxxxxxx",
    "AKEYLESS_ACCESS_TYPE": "aws_iam",
    "AKEYLESS_SECRET_PREFIX": "/bedrock-agentcore/my-agent/production",
    "AKEYLESS_GATEWAY_URL": "https://api.akeyless.io",
    "AGENTCORE_AGENT_NAME": "my-agent"
  }
}
```

For self-hosted gateways, set `AKEYLESS_GATEWAY_URL` to your gateway URL (e.g. `https://gateway.example.com`).

## 5. Verify locally (optional)

Before deploying to AgentCore, test with a read-only access key:

```bash
cp .env.example .env
# Edit .env with your test credentials

export AKEYLESS_ACCESS_TYPE=access_key
export AKEYLESS_ACCESS_KEY=your-readonly-key

python3 -c "
from akeyless_agentcore import get_secret
print('OK:', get_secret('OPENAI_API_KEY')[:6] + '...')
"
```

## 6. Verify on AgentCore

After deploy, check CloudWatch logs for authentication errors. Common issues:

| Error | Fix |
|-------|-----|
| `could not obtain cloud identity` | Execution role missing or not bound to auth method |
| `access denied` / `403` | RBAC role not associated with auth method |
| `not found` / `404` | Wrong `AKEYLESS_SECRET_PREFIX` or secret path |
| Gateway timeout | Security group / VPC egress blocking HTTPS to Akeyless |

## Dynamic and rotated secrets

For dynamic secrets (e.g. temporary AWS credentials):

```python
from akeyless_agentcore import AkeylessRuntimeClient

client = AkeylessRuntimeClient()
creds = client.get_dynamic_secret("aws-dynamic-secret")
```

Or via tool:

```python
get_akeyless_secret(name="aws-dynamic-secret", secret_type="dynamic")
```

For rotated secrets, use `secret_type="rotated"` or `client.get_rotated_secret(...)`.
