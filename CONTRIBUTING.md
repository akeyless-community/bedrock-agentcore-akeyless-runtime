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

**All changes to `main` require review and approval from `@akeyless-community/cs-admin`.**

External contributors (outside the Akeyless org):

1. **Fork** the repository — do not request write access unless you are a maintainer.
2. Create a feature branch from `main`.
3. Add or update tests for behavior changes.
4. Run `pytest` before opening the PR.
5. Open a pull request using the provided template.
6. Wait for **CI** (`ci-success`) and a **maintainer approval** before merge.

Maintainers merge after approval. Direct pushes to `main` are not allowed.

See [docs/MAINTAINER.md](docs/MAINTAINER.md) for branch protection and org settings.

## Publishing (maintainers)

### PyPI (recommended for end users)

See **[docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md)** for the full trusted-publishing walkthrough.

Summary:

1. Add a **pending publisher** on PyPI (`akeyless-community` / `bedrock-agentcore-akeyless-runtime` / `publish.yml`)
2. *(Recommended)* Make the repo **public** — not required for PyPI, but required for `pip install` from GitHub without credentials
3. Publish a **GitHub Release** (e.g. `v0.3.0`) — the workflow uploads automatically

Manual fallback:

```bash
pip install build twine
python -m build
twine upload dist/*
```
