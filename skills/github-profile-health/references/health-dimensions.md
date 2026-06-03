# GitHub Repository Health Dimensions

Reference for all seven health dimensions used by the GitHub Profile Health Auditor.
Each dimension is anchored to a named, traceable authority.

---

## Dimension 1 — Documentation

**Authority:** [GitHub Docs: Repository best practices](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)

**What healthy looks like:**
- `README.md` present at repository root; non-empty; includes: project purpose, installation, usage, and contribution note
- Repository **description** field populated (appears in search results and profile)
- At least three **topics** tagged (enables discoverability via `github.com/topics/...`)

**What the theatre version looks like:**
- README exists but contains only the auto-generated scaffold ("# project-name — *Add a description*")
- Description field blank
- No topics set — invisible to GitHub Explore and search

**Scoring:** README (4pt) + description (3pt) + topics (3pt) = 10

---

## Dimension 2 — Licensing

**Authority:** [OpenSSF Scorecard: License check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#license); [SPDX License List](https://spdx.org/licenses/)

**What healthy looks like:**
- `LICENSE` or `LICENSE.md` or `LICENSE.txt` at repository root
- License uses a valid SPDX identifier (e.g., `MIT`, `Apache-2.0`, `GPL-3.0-only`)
- GitHub auto-detects and displays the license badge on the repo page

**What the theatre version looks like:**
- No license file — defaults to "All rights reserved" which blocks any reuse
- Custom license text with no SPDX identifier — tooling cannot parse it

**Common safe choices for personal/OSS projects:**
- `MIT` — permissive, attribution required, no patent grant
- `Apache-2.0` — permissive, attribution + patent grant
- `GPL-3.0-only` — copyleft, derivatives must be open source

**Scoring:** SPDX-identified license (10pt); license detected without SPDX (7pt); no license (0pt)

---

## Dimension 3 — Branch Protection

**Authority:** [OpenSSF Scorecard: Branch-Protection check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#branch-protection); [GitHub Docs: Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

**What healthy looks like:**
- Default branch (`main` or `master`) has a branch protection rule enabled
- **Require pull request reviews before merging** — at least 1 approving review required
- **Dismiss stale pull request approvals when new commits are pushed** — prevents approval bypass
- **Require status checks to pass before merging** — CI must be green before merge is allowed

**What the theatre version looks like:**
- Branch protection rule exists but has zero required checks — all settings are empty checkboxes
- "Allow force pushes" enabled — history can be rewritten, audit trail broken
- No status checks configured — CI runs but doesn't gate merges

**Fix:** Settings → Branches → Add branch protection rule → select all three options above.

**Scoring:** PR reviews required (4pt) + required status checks (3pt) + dismiss stale reviews (3pt) = 10

---

## Dimension 4 — CI/CD Health

**Authority:** [DORA Research: Four Key Metrics](https://dora.dev/guides/dora-metrics-four-keys/) (Deployment Frequency, Change Failure Rate); [GitHub Actions docs](https://docs.github.com/en/actions)

**What healthy looks like:**
- At least one `.github/workflows/*.yml` workflow file present
- Most recent workflow run has conclusion `success`
- No workflow with >20% failure rate over the last 30 days (Change Failure Rate signal)
- Workflows last updated within the past 6 months (not abandoned)

**What the theatre version looks like:**
- Workflow files present but all runs are failing or skipped
- Workflow checks out code and runs no actual tests (`steps: - run: echo "ok"`)
- Workflow last updated 2+ years ago with pinned-to-ancient dependency versions

**DORA metric anchors:**
- *Deployment frequency* — how often the pipeline successfully deploys; healthy = daily or on-demand
- *Change failure rate* — % of deployments causing a failure; healthy = <15%
- *Mean time to recovery* — how quickly failures are fixed; healthy = <1 hour for critical

**Scoring:** Workflows present (4pt) + last run green (6pt) = 10

---

## Dimension 5 — Security Posture

**Authority:** [OpenSSF Scorecard: Security-Policy check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#security-policy); [OpenSSF Scorecard: Vulnerabilities check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#vulnerabilities); [GitHub Security features overview](https://docs.github.com/en/code-security/getting-started/github-security-features)

**What healthy looks like:**
- `SECURITY.md` at repository root (or in `.github/`) — documents how to report vulnerabilities
- Dependabot alerts enabled — GitHub notifies when dependencies have known CVEs
- Secret scanning enabled (free for public repos) — detects committed credentials
- No open critical or high severity Dependabot alerts

**SECURITY.md minimum content:**
```markdown
## Reporting a Vulnerability

Please report security issues to security@example.com
(replace with your actual security contact address or link to a private disclosure form).
Do not file a public GitHub issue for security vulnerabilities.

We aim to respond within 72 hours and will coordinate a fix and disclosure timeline with you.
```

**What the theatre version looks like:**
- `SECURITY.md` exists but contains only "contact us" with no actual disclosure process
- Dependabot alerts enabled but ignored — 50+ open alerts, last acknowledged 6 months ago
- Secret scanning enabled but `.github/secret_scanning.yml` excludes all pattern types

**Scoring:** SECURITY.md (3pt) + Dependabot configured (4pt) + vulnerability alerts active (3pt) = 10

---

## Dimension 6 — Dependency Hygiene

**Authority:** [OpenSSF Scorecard: Pinned-Dependencies check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies); [GitHub Docs: Dependabot version updates](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates)

**What healthy looks like:**
- Dependency lock file committed (`package-lock.json`, `yarn.lock`, `poetry.lock`, `go.sum`, `Cargo.lock`, etc.)
- `.github/dependabot.yml` configured to open automated PRs for dependency updates
- GitHub Actions workflows pin action versions to full SHA hashes (not `@v3` tags which can be moved)
- No known high/critical CVEs in direct dependencies

**What the theatre version looks like:**
- No lock file committed — `npm install` produces non-deterministic builds
- `dependabot.yml` exists but `open-pull-requests-limit: 0` (effectively disabled)
- Workflow uses `actions/checkout@main` — vulnerable to supply-chain attacks if `main` is compromised

**Minimal `.github/dependabot.yml` for npm + GitHub Actions:**
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Scoring:** Lock file present (5pt) + Dependabot config (5pt) = 10

---

## Dimension 7 — Community Health

**Authority:** [GitHub Community Profile standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories); [GitHub Docs: Issue and pull request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

**What healthy looks like:**
- `CONTRIBUTING.md` — tells contributors how to set up locally, coding standards, PR process
- `.github/ISSUE_TEMPLATE/` directory — at least a bug report and feature request template
- `.github/pull_request_template.md` — prompts contributors to fill in context, testing notes, issue link

**What the theatre version looks like:**
- CONTRIBUTING.md says "please read our docs" with no actual contributing instructions
- Single issue template that just says "Describe the issue" with no structured fields
- No PR template — contributors submit PRs with "fixed stuff" as the description

**Minimum CONTRIBUTING.md sections:**
1. Prerequisites (tools, accounts, access needed)
2. Local development setup (step-by-step commands)
3. Running tests
4. Submitting a pull request (branch naming, PR size, review expectations)
5. Code of conduct reference

**Scoring:** CONTRIBUTING.md (4pt) + issue templates (3pt) + PR template (3pt) = 10

---

## Grade Bands and Remediation Priority

| Grade | Score Range | Meaning | Remediation SLA |
|-------|------------|---------|----------------|
| **Gold** | 9.0–10 | Exemplary hygiene, production-grade | Maintain; review quarterly |
| **Silver** | 7.0–8.9 | Solid; minor gaps | Address within 30 days |
| **Bronze** | 5.0–6.9 | Significant hygiene debt | Address within 14 days |
| **Red** | 0–4.9 | Active risk | Address immediately |

**Weight multipliers in overall score:**
- Security Posture: 2× (OpenSSF mandated as highest-priority signal)
- Branch Protection: 2× (prevents history tampering and unsafe merges)
- CI/CD Health: 1.5× (DORA identifies as core delivery health signal)
- All others: 1×
