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

```bash
python -m build
twine upload dist/*
```
