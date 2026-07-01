# Publishing to PyPI

Step-by-step guide to publish `akeyless-agentcore-runtime` to PyPI using [trusted publishing](https://docs.pypi.org/trusted-publishers/) (no API tokens in GitHub Secrets).

## Do you need a public GitHub repo?

| Goal | Public repo required? |
|------|----------------------|
| **Publish to PyPI** via trusted publishing | **No** — private repos work |
| **`pip install akeyless-agentcore-runtime`** from PyPI | **No** — PyPI is public; users don't need GitHub access |
| **`pip install` from GitHub URL** (no clone) | **Yes** — private repos require a GitHub token |
| **Community contributors / issues / docs on GitHub** | **Yes** — recommended for `akeyless-community` packages |

**Recommendation:** Make the repository **public** before the first release. PyPI publishing works either way, but a public repo matches how other [akeyless-community](https://github.com/akeyless-community) packages work and lets users install from GitHub without credentials.

### Make the repo public (one-time)

GitHub → **Settings** → **General** → **Danger Zone** → **Change repository visibility** → **Public**

Or via CLI (org admin required):

```bash
gh repo edit akeyless-community/bedrock-agentcore-akeyless-runtime --visibility public
```

---

## Prerequisites

- Admin access to the `akeyless-community` GitHub org (or repo maintainer)
- A [PyPI](https://pypi.org) account
- The package name `akeyless-agentcore-runtime` available on PyPI (first publisher claims it)

---

## Step 1: Register the PyPI project with a trusted publisher

You can do this **before** the first upload.

1. Log in to [pypi.org](https://pypi.org)
2. Go to **Account settings** → **Publishing** → **Add a new pending publisher**
3. Fill in:

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `akeyless-agentcore-runtime` |
| **Publisher** | GitHub |
| **Owner** | `akeyless-community` |
| **Repository name** | `bedrock-agentcore-akeyless-runtime` |
| **Workflow name** | `publish.yml` |
| **Environment name** | *(leave blank unless using Step 4)* |

4. Click **Add**

This creates a **pending** PyPI project. The first successful publish from the trusted workflow completes registration.

> **First-time only:** If the name is taken, choose a variant (e.g. `akeyless-bedrock-agentcore`) and update `name` in `pyproject.toml`.

---

## Step 2: Verify the GitHub Actions workflow

The repo already includes `.github/workflows/publish.yml`:

- Triggers on **GitHub Release published**
- Builds wheel + sdist with `python -m build`
- Uploads via `pypa/gh-action-pypi-publish` (OIDC — no `PYPI_API_TOKEN` secret)

For **private** repositories, the workflow sets:

```yaml
permissions:
  id-token: write   # OIDC for PyPI
  contents: read    # checkout access
```

No changes needed unless you add a `pypi` environment (Step 4).

---

## Step 3: Create a GitHub Release

Publishing is triggered by publishing a release (not just pushing a tag).

### Option A: GitHub UI

1. Go to [Releases](https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime/releases)
2. **Draft a new release**
3. Choose tag `v0.2.0` (or create a new tag matching `version` in `pyproject.toml`)
4. Title: `v0.2.0`
5. **Publish release**

### Option B: CLI

```bash
gh release create v0.2.0 \
  --repo akeyless-community/bedrock-agentcore-akeyless-runtime \
  --title "v0.2.0" \
  --notes "Initial PyPI release"
```

### Version checklist before release

1. Bump `version` in `pyproject.toml` (currently `0.2.0`)
2. Commit and push to `main`
3. Create tag matching the version: `v0.2.0`
4. Publish the release

---

## Step 4 (optional): Require manual approval

Add a GitHub **environment** for extra safety:

1. Repo **Settings** → **Environments** → **New environment** → name it `pypi`
2. Enable **Required reviewers** (pick maintainers)
3. In PyPI pending publisher config, set **Environment name** to `pypi`
4. Uncomment in `publish.yml`:

```yaml
jobs:
  publish:
    environment: pypi
```

Releases will wait for approval before uploading to PyPI.

---

## Step 5: Confirm the publish

1. Open **Actions** → **Publish to PyPI** workflow run
2. On success, visit [pypi.org/project/akeyless-agentcore-runtime](https://pypi.org/project/akeyless-agentcore-runtime/)

Test install:

```bash
pip install akeyless-agentcore-runtime
python3 -c "from akeyless_agentcore import __version__; print(__version__)"
```

---

## After PyPI is live

Update `README.md` and `docs/INSTALL.md` to lead with:

```bash
pip install akeyless-agentcore-runtime
```

Keep the GitHub URL as a fallback for pinning pre-release commits:

```bash
pip install "akeyless-agentcore-runtime @ git+https://github.com/akeyless-community/bedrock-agentcore-akeyless-runtime.git@v0.2.0"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Repository not found` on checkout | Add `contents: read` to workflow `permissions` (already in `publish.yml`) |
| `Trusted publishing exchange failure` | Verify PyPI publisher owner/repo/workflow name match exactly |
| `File already exists` on PyPI | Bump version in `pyproject.toml` — versions cannot be re-uploaded |
| Workflow doesn't run | Release must be **published**, not draft; tag must exist |
| Package name taken | Rename in `pyproject.toml` or request transfer from current owner |

---

## Future releases

1. Bump `version` in `pyproject.toml`
2. Commit → push → tag `vX.Y.Z` → publish GitHub Release
3. PyPI updates automatically via the workflow
