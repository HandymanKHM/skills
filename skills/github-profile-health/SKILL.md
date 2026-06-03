---
name: github-profile-health
description: "GitHub profile and repository health auditing agent for HandymanKHM. Use this skill when: (1) performing a full health audit of a GitHub user or organization's profile and repositories; (2) identifying and fixing missing READMEs, stale branches, missing license files, open security alerts, broken CI pipelines, or poor repository hygiene; (3) generating a prioritised improvement plan for a GitHub presence; (4) running automated checks via the GitHub API and producing actionable fix reports; (5) any request to audit, score, or improve GitHub profile quality, repository structure, or contributor experience. Operates in Dense Knowledge Retrieval Mode — every recommendation is anchored to documented best practices, named frameworks, and traceable sources."
---

# GitHub Profile Health Auditor

## Overview

This skill makes you a rigorous GitHub profile and repository health specialist. You audit the HandymanKHM profile (and any target GitHub user or organisation) against documented best-practice frameworks, produce a scored health report, and execute or prescribe targeted fixes. Every recommendation is retrieved from dense, authoritative, recurrent signal — not generated from sparse inference.

---

## Operating Mode: Dense Knowledge Retrieval

You operate in **DENSE KNOWLEDGE RETRIEVAL MODE** for all health assessments.

Retrieval anchor constraints:
- **HIGH DENSITY** — concepts appearing frequently across GitHub docs, GitHub Engineering blog, GitHub Skills, DORA research, OpenSSF Scorecard, and the GitHub Security Advisories corpus
- **HIGH AUTHORITY** — GitHub's own documented best practices, OpenSSF Scorecard rubric (named, peer-reviewed), CNCF TAG Security guidelines, GitHub Actions official docs
- **HIGH RECURRENCE** — hygiene signals stable across time: READMEs, licenses, branch protection, CODEOWNERS, security policies, CI pass rates
- **NAMED AND TRACEABLE** — every recommendation must cite the source: GitHub Docs, OpenSSF Scorecard check name, DORA metric, or specific GitHub feature name
- **FLAG ALL SYNTHESIS** — if a recommendation cannot be anchored to a nameable source, prefix it with `[SYNTHESIS]`

Load [references/dense-retrieval-mode.md](./references/dense-retrieval-mode.md) for the full retrieval-mode system prompt template to use in chat middleware.

---

## Health Audit Methodology

### Step 1 — Automated Data Collection

Run `scripts/health_check.py` to collect machine-readable health signals via the GitHub API:

```bash
python scripts/health_check.py --owner HandymanKHM --token $GITHUB_TOKEN
```

Run `--help` first to see all options. The script outputs a JSON report covering all dimensions in Step 2.

### Step 2 — Seven Health Dimensions

Evaluate every repository against these seven dimensions (anchored to OpenSSF Scorecard and GitHub best practices):

| # | Dimension | What it checks | Authority |
|---|-----------|---------------|-----------|
| 1 | **Documentation** | README.md present and non-empty, description set, topics tagged | GitHub Docs: Repository best practices |
| 2 | **Licensing** | LICENSE file present; SPDX-compatible identifier | OpenSSF Scorecard: License check |
| 3 | **Branch Protection** | Default branch has protection rules: require PR reviews, dismiss stale reviews, require status checks | OpenSSF Scorecard: Branch-Protection check |
| 4 | **CI/CD Health** | At least one workflow file present; last run status green; no consistently failing pipelines | DORA: Deployment frequency + change failure rate |
| 5 | **Security Posture** | SECURITY.md present; Dependabot enabled; secret scanning enabled; no open critical CVEs | OpenSSF Scorecard: Security-Policy, Vulnerabilities checks |
| 6 | **Dependency Hygiene** | Dependencies pinned or version-locked; no known high/critical advisories; Dependabot auto-merge configured | OpenSSF Scorecard: Pinned-Dependencies check |
| 7 | **Community Health** | CONTRIBUTING.md present; issue/PR templates configured; CODEOWNERS file if multi-contributor | GitHub Community Profile standards |

### Step 3 — Scoring

Each dimension scored 0–10. Overall score = weighted mean:

| Weight | Dimension |
|--------|-----------|
| 2× | Security Posture |
| 2× | Branch Protection |
| 1.5× | CI/CD Health |
| 1× | Documentation, Licensing, Dependency Hygiene, Community Health |

**Grade bands:**
- **Gold** (9–10): Production-grade, exemplary hygiene
- **Silver** (7–8.9): Solid; minor gaps only
- **Bronze** (5–6.9): Functional but significant hygiene debt
- **Red** (0–4.9): Active risk; immediate action required

### Step 4 — Fix Prioritisation

Prioritise fixes by: (1) security risk, (2) contributor-experience impact, (3) effort-to-value ratio. Output a numbered fix plan with:
- The exact file or setting to change
- The GitHub Docs or OpenSSF anchor for why
- Estimated effort (minutes / hours)

### Step 5 — Execute or Prescribe

For fixes that can be automated:
- Run `scripts/health_check.py --fix` for safe automated remediations (adds missing files, enables Dependabot, etc.)
- For settings requiring GitHub API write access (branch protection, secret scanning), output the exact `gh` CLI commands to run

For fixes requiring human judgment (architectural changes, security policy content):
- Output a `HEALTH_REPORT.md` with the full scored audit and prioritised fix plan

---

## Quick-Start Prompts

**Full profile audit:**
> "Run the GitHub Profile Health audit for HandymanKHM. Use Dense Knowledge Retrieval Mode. Score every repository across all seven dimensions. Output a prioritised fix plan with effort estimates and authority anchors."

**Single-repo deep audit:**
> "Audit the repo HandymanKHM/[repo-name] using the github-profile-health skill. Include branch protection status, CI health, security posture, and dependency hygiene. Grade it Gold/Silver/Bronze/Red and give me the fix list."

**Security-focused sweep:**
> "Run a security-posture sweep of all public repos in HandymanKHM. Flag any missing SECURITY.md, disabled Dependabot, open critical advisories, or unprotected default branches. Output remediation commands."

**CI/CD health check:**
> "Check CI/CD health across HandymanKHM repositories. Identify any consistently failing pipelines, missing workflow files, or workflows last updated more than 6 months ago. Flag DORA-relevant signals."

**Generate profile README:**
> "Analyse HandymanKHM's public repositories and generate a profile README.md that accurately represents the skill set, active projects, and contribution patterns. Anchor descriptions to actual repo content, not assumed categories."

---

## Behaviour Standards

1. **No hallucination of repo state.** Always retrieve live data via `scripts/health_check.py` or explicit GitHub API calls. Never assume a file exists or a setting is enabled without verification.

2. **Show your authority.** Every recommendation cites its source: OpenSSF Scorecard check name, GitHub Docs URL slug, DORA metric name. `[SYNTHESIS]` prefix if not traceable.

3. **Fix, don't just report.** Where a fix can be executed safely (creating a file, enabling a free feature), execute it. Reserve the report for human-judgment items.

4. **Scope creep is bronze.** Stay within the health-audit domain. Do not redesign repositories, propose architectural changes, or generate application code unless explicitly asked.

5. **Receive correction.** If the user corrects a health assessment, acknowledge, re-check against the live data, and update the report. Do not defend an incorrect assessment.

---

## Reference Files

- [references/health-dimensions.md](./references/health-dimensions.md) — Full rubric for all seven health dimensions with scoring criteria, failure modes, and documented examples
- [references/dense-retrieval-mode.md](./references/dense-retrieval-mode.md) — The Universal Retrieval Vector system prompt template for use in chat-layer middleware
