# Contributing

Thanks for contributing to `akeyless-agentcore-runtime`.

## Development setup

Requires Python 3.10+.

```bash
git clone https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git
cd bedrock-agentcore-akeyless-runtime
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Optional extras

```bash
pip install -e ".[mcp]"       # MCP server tools
pip install -e ".[strands]"   # Strands in-process tools
pip install -e ".[gateway]"   # AgentCore Gateway Lambda setup
pip install -e ".[all]"       # everything
```

## Pull requests

1. Fork and create a feature branch from `main`.
2. Add or update tests for behavior changes.
3. Run `pytest` before opening the PR.
4. Do not commit real credentials, `.env` files, or gateway tokens.
5. Keep changes focused — this package should stay small and dependency-light.

## Publishing (maintainers)

### PyPI (recommended for end users)

See **[docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md)** for the full trusted-publishing walkthrough.

Summary:

1. Add a **pending publisher** on PyPI (`akeyless-community` / `bedrock-agentcore-akeyless-runtime` / `publish.yml`)
2. *(Recommended)* Make the repo **public** — not required for PyPI, but required for `pip install` from GitHub without credentials
3. Publish a **GitHub Release** (e.g. `v0.2.0`) — the workflow uploads automatically

Manual fallback:

```bash
pip install build twine
python -m build
twine upload dist/*
```
