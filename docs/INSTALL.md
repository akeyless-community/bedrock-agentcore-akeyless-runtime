# Installation

You do **not** need to clone this repository to use the library. Add it as a dependency in your AgentCore agent project and install with `pip`.

## Option 1: PyPI (recommended)

Once published:

```bash
pip install akeyless-agentcore-runtime
```

With optional extras:

```bash
pip install 'akeyless-agentcore-runtime[strands]'
pip install 'akeyless-agentcore-runtime[mcp]'
pip install 'akeyless-agentcore-runtime[gateway]'
pip install 'akeyless-agentcore-runtime[all]'
```

In your agent's `requirements.txt`:

```text
akeyless-agentcore-runtime>=0.2.0
bedrock-agentcore>=0.1.0
```

> **Note:** PyPI publishing is in progress. Until the package is live, use Option 2 below.

## Option 2: Install directly from GitHub (no clone)

`pip` can install straight from the repository — no `git clone` required:

```bash
pip install "akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git"
```

Pin to a release tag for reproducible builds:

```bash
pip install "akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.2.0"
```

With extras:

```bash
pip install "akeyless-agentcore-runtime[strands] @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.2.0"
```

### AgentCore `requirements.txt` example

```text
# Akeyless runtime — cloud identity auth + secret fetch
akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.2.0

# AgentCore + agent framework
bedrock-agentcore>=0.1.0
strands-agents>=0.1.0
```

Then deploy as usual:

```bash
agentcore deploy
```

AgentCore packages your `requirements.txt` and installs dependencies in the runtime container automatically.

## Option 3: Copy the example agent (minimal)

If you only need a starting point, copy a single example file into your own AgentCore project:

1. Create an agent with `agentcore create --name MyAgent --defaults`
2. Copy [`examples/strands-agent/agent.py`](../examples/strands-agent/agent.py) into your project
3. Add the dependency from Option 1 or 2 to `requirements.txt`
4. Set bootstrap env vars (see [AKEYLESS_SETUP.md](AKEYLESS_SETUP.md))
5. `agentcore deploy`

You never need the full repository — just the pip dependency and your agent code.

## Option 4: MCP server CLI only

To run the MCP server without cloning:

```bash
pip install "akeyless-agentcore-runtime[mcp] @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.2.0"

export AKEYLESS_ACCESS_ID=p-xxxxx
export AKEYLESS_SECRET_PREFIX=/bedrock-agentcore/my-agent/production

akeyless-agentcore-mcp
```

## When you *do* need to clone

Clone the repo only if you are:

- Contributing code or opening a pull request
- Running the test suite locally
- Developing changes to the library itself

```bash
git clone https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git
cd bedrock-agentcore-akeyless-runtime
pip install -e ".[dev]"
pytest
```

## Verify installation

```bash
python3 -c "from akeyless_agentcore import __version__; print(__version__)"
```

Expected output: `0.2.0`
