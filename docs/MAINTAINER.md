# Maintainer guide: repository access controls

Settings applied to restrict changes so **people outside the Akeyless org must be reviewed and approved** before code lands on `main` or ships to PyPI.

## What is enforced

| Control | Effect |
|---------|--------|
| **Branch protection on `main`** | No direct pushes; changes only via pull request |
| **Push restrictions** | Only `@akeyless-community/cs-admin` can push or merge to `main` |
| **CODEOWNERS** (`@akeyless-community/cs-admin`) | PRs require approval from a `cs-admin` team member |
| **CI required** | `ci-success` must pass before merge |
| **Stale review dismissal** | New commits invalidate prior approvals |
| **Last-push approval** | Re-approval required after new commits |
| **`pypi` environment** | PyPI publish requires approval from a maintainer |

> **Note:** For *private* repositories, team-based push restrictions require a **GitHub Team** plan. This repo is **public**, so push restrictions are available on **GitHub Free for organizations** and limit merge/push to `main` to `cs-admin`. Required PR + CODEOWNERS approval is an independent second layer — external fork contributors are blocked by PR review regardless of push restrictions.

## Files in this repo

- [`.github/CODEOWNERS`](../.github/CODEOWNERS) — routes all paths to `@akeyless-community/cs-admin`
- [`.github/pull_request_template.md`](../.github/pull_request_template.md) — reminds external contributors about review
- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — `ci-success` gate for branch protection
- [`.github/workflows/publish.yml`](../.github/workflows/publish.yml) — uses protected `pypi` environment

## Org settings (verify in GitHub UI)

These are **organization-level** and cannot be stored in the repo. An org admin should confirm:

### 1. Base permissions

**Organization settings** → **Member privileges** → **Base permissions**

- Recommended: **Read** for org members who are not maintainers
- Outside collaborators: grant access **per repository** only when needed

### 2. Fork PR workflows (important for external contributors)

**Organization settings** → **Actions** → **General** → **Fork pull request workflows**

- Enable: **Require approval for all outside collaborators**  
  (or at minimum: first-time contributors)

This prevents fork PRs from running Actions with secrets until a maintainer approves the workflow run.

### 3. Add maintainers to the team

**Organization** → **Teams** → **cs-admin** → add Akeyless reviewers who can approve PRs and PyPI releases.

## Re-applying branch protection

If settings are lost (e.g. repo transfer), an org admin can re-apply:

```bash
gh api \
  --method PUT \
  repos/akeyless-community/bedrock-agentcore-akeyless-runtime/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      { "context": "ci-success" }
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "require_last_push_approval": true
  },
  "restrictions": {
    "users": [],
    "teams": ["cs-admin"],
    "apps": []
  },
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

If the API returns an error applying `restrictions`, or succeeds but `restrictions.teams` is still empty when you verify with:

```bash
gh api repos/akeyless-community/bedrock-agentcore-akeyless-runtime/branches/main/protection/restrictions/teams
```

set **Restrict who can push to matching branches** to `@akeyless-community/cs-admin` in **Settings → Branches → `main` → Edit** instead of silently omitting the layer.

## PyPI environment

The `pypi` environment requires approval from maintainers before packages upload to PyPI.

**Repository** → **Settings** → **Environments** → **pypi** → **Required reviewers**

Configure reviewers from `@akeyless-community/cs-admin`. Verify the current list in the environment settings UI — do not rely on a hardcoded name list in this doc.

Publishing a GitHub Release starts the workflow; an configured reviewer must approve the `pypi` environment deployment.

## External contributor flow

1. Fork the public repo (read access is open)
2. Open a PR from their fork
3. CI runs after maintainer approves workflow (if fork, per org setting)
4. A `cs-admin` member reviews and approves
5. A `cs-admin` member merges

Direct push to `main` and unapproved PyPI releases are blocked.
