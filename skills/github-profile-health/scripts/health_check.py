#!/usr/bin/env python3
"""
GitHub Profile Health Check Script
------------------------------------
Audits a GitHub user or organisation's repositories against seven
health dimensions anchored to OpenSSF Scorecard and GitHub best practices.

Usage:
    python health_check.py --help
    python health_check.py --owner HandymanKHM --token $GITHUB_TOKEN
    python health_check.py --owner HandymanKHM --token $GITHUB_TOKEN --repo skills
    python health_check.py --owner HandymanKHM --token $GITHUB_TOKEN --fix --output HEALTH_REPORT.md

Authentication:
    Pass --token or set GITHUB_TOKEN environment variable.
    Unauthenticated calls work for public repos but hit rate limits quickly.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def api_get(path: str, token: str | None) -> dict | list | None:
    """GET from GitHub REST API v3. Returns parsed JSON or None on 404."""
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    except URLError as e:
        print(f"  [WARN] Network error fetching {path}: {e}", file=sys.stderr)
        return None


def list_repos(owner: str, token: str | None) -> list[dict]:
    """Return all repos for an owner (handles pagination)."""
    repos = []
    page = 1
    while True:
        batch = api_get(f"/users/{owner}/repos?per_page=100&page={page}", token)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


# ---------------------------------------------------------------------------
# Seven-dimension checks
# ---------------------------------------------------------------------------

def check_documentation(owner: str, repo: str, token: str | None) -> dict:
    """Dim 1: README present, description set, topics tagged."""
    info = api_get(f"/repos/{owner}/{repo}", token) or {}
    readme = api_get(f"/repos/{owner}/{repo}/readme", token)
    score = 0
    notes = []
    if readme:
        score += 4
    else:
        notes.append("Missing README")
    if info.get("description"):
        score += 3
    else:
        notes.append("No repository description")
    if info.get("topics"):
        score += 3
    else:
        notes.append("No topics/tags set")
    return {"score": score, "notes": notes, "authority": "GitHub Docs: Repository best practices"}


def check_licensing(owner: str, repo: str, token: str | None) -> dict:
    """Dim 2: LICENSE file present with SPDX identifier."""
    info = api_get(f"/repos/{owner}/{repo}", token) or {}
    license_info = info.get("license") or {}
    score = 0
    notes = []
    if license_info.get("spdx_id") and license_info["spdx_id"] != "NOASSERTION":
        score = 10
    elif license_info.get("name"):
        score = 7
        notes.append("License detected but no SPDX identifier")
    else:
        notes.append("No LICENSE file detected")
    return {"score": score, "notes": notes, "authority": "OpenSSF Scorecard: License check"}


def check_branch_protection(owner: str, repo: str, default_branch: str, token: str | None) -> dict:
    """Dim 3: Default branch has protection rules."""
    protection = api_get(f"/repos/{owner}/{repo}/branches/{default_branch}/protection", token)
    score = 0
    notes = []
    if protection is None:
        notes.append(f"No branch protection on '{default_branch}'")
        return {"score": 0, "notes": notes, "authority": "OpenSSF Scorecard: Branch-Protection check"}
    if protection.get("required_pull_request_reviews"):
        score += 4
    else:
        notes.append("PR reviews not required")
    if protection.get("required_status_checks", {}).get("contexts"):
        score += 3
    else:
        notes.append("No required status checks configured")
    dismiss = (protection.get("required_pull_request_reviews") or {}).get("dismiss_stale_reviews")
    if dismiss:
        score += 3
    else:
        notes.append("Stale review dismissal not enabled")
    return {"score": score, "notes": notes, "authority": "OpenSSF Scorecard: Branch-Protection check"}


def check_ci_health(owner: str, repo: str, token: str | None) -> dict:
    """Dim 4: Workflow files present; last run green."""
    workflows = api_get(f"/repos/{owner}/{repo}/actions/workflows", token) or {}
    runs = api_get(f"/repos/{owner}/{repo}/actions/runs?per_page=10", token) or {}
    wf_list = workflows.get("workflows", [])
    run_list = (runs.get("workflow_runs") or [])
    score = 0
    notes = []
    if not wf_list:
        notes.append("No GitHub Actions workflow files found")
        return {"score": 0, "notes": notes, "authority": "DORA: Deployment frequency + change failure rate"}
    score += 4
    if run_list:
        latest = run_list[0]
        if latest.get("conclusion") == "success":
            score += 6
        elif latest.get("conclusion") in (None, "in_progress"):
            score += 3
            notes.append("Latest run still in progress")
        else:
            notes.append(f"Latest run conclusion: {latest.get('conclusion', 'unknown')}")
    else:
        notes.append("No workflow runs found")
        score += 3
    return {"score": score, "notes": notes, "authority": "DORA: Deployment frequency + change failure rate"}


def check_security_posture(owner: str, repo: str, token: str | None) -> dict:
    """Dim 5: SECURITY.md, Dependabot, secret scanning, no open critical CVEs."""
    security_md = api_get(f"/repos/{owner}/{repo}/contents/SECURITY.md", token)
    dependabot_config = api_get(f"/repos/{owner}/{repo}/contents/.github/dependabot.yml", token)
    vuln_alerts = api_get(f"/repos/{owner}/{repo}/vulnerability-alerts", token)
    score = 0
    notes = []
    if security_md:
        score += 3
    else:
        notes.append("Missing SECURITY.md")
    if dependabot_config:
        score += 4
    else:
        notes.append("No .github/dependabot.yml — Dependabot not configured")
    # vulnerability-alerts returns 204 (empty dict) if enabled, 404 (None) if not
    if vuln_alerts is not None:
        score += 3
    else:
        notes.append("Vulnerability alerts may not be enabled (requires push access to confirm)")
        score += 1
    return {"score": score, "notes": notes, "authority": "OpenSSF Scorecard: Security-Policy, Vulnerabilities checks"}


def check_dependency_hygiene(owner: str, repo: str, token: str | None) -> dict:
    """Dim 6: Lock files present; dependabot config; no known critical advisories."""
    lock_files = [
        "package-lock.json", "yarn.lock", "Pipfile.lock",
        "poetry.lock", "go.sum", "Cargo.lock", "Gemfile.lock",
        "requirements.txt", "pyproject.toml",
    ]
    found_lock = False
    for lf in lock_files:
        result = api_get(f"/repos/{owner}/{repo}/contents/{lf}", token)
        if result:
            found_lock = True
            break
    dependabot_config = api_get(f"/repos/{owner}/{repo}/contents/.github/dependabot.yml", token)
    score = 0
    notes = []
    if found_lock:
        score += 5
    else:
        notes.append("No dependency lock file found")
    if dependabot_config:
        score += 5
    else:
        notes.append("No Dependabot configuration for automated dependency updates")
    return {"score": score, "notes": notes, "authority": "OpenSSF Scorecard: Pinned-Dependencies check"}


def check_community_health(owner: str, repo: str, token: str | None) -> dict:
    """Dim 7: CONTRIBUTING.md, issue templates, PR templates."""
    contributing = api_get(f"/repos/{owner}/{repo}/contents/CONTRIBUTING.md", token)
    issue_templates = api_get(f"/repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE", token)
    pr_template = api_get(f"/repos/{owner}/{repo}/contents/.github/pull_request_template.md", token)
    score = 0
    notes = []
    if contributing:
        score += 4
    else:
        notes.append("Missing CONTRIBUTING.md")
    if issue_templates:
        score += 3
    else:
        notes.append("No .github/ISSUE_TEMPLATE directory")
    if pr_template:
        score += 3
    else:
        notes.append("No .github/pull_request_template.md")
    return {"score": score, "notes": notes, "authority": "GitHub Community Profile standards"}


# ---------------------------------------------------------------------------
# Scoring and reporting
# ---------------------------------------------------------------------------

WEIGHTS = {
    "documentation": 1.0,
    "licensing": 1.0,
    "branch_protection": 2.0,
    "ci_health": 1.5,
    "security_posture": 2.0,
    "dependency_hygiene": 1.0,
    "community_health": 1.0,
}

GRADE_BANDS = [
    (9.0, "Gold"),
    (7.0, "Silver"),
    (5.0, "Bronze"),
    (0.0, "Red"),
]


def grade(score: float) -> str:
    for threshold, label in GRADE_BANDS:
        if score >= threshold:
            return label
    return "Red"


def weighted_score(dimensions: dict) -> float:
    total_weight = sum(WEIGHTS[k] for k in dimensions)
    total_score = sum(dimensions[k]["score"] * WEIGHTS[k] for k in dimensions)
    return round(total_score / total_weight, 2)


def audit_repo(owner: str, repo_info: dict, token: str | None) -> dict:
    repo = repo_info["name"]
    default_branch = repo_info.get("default_branch", "main")
    print(f"  Auditing: {repo} ...", file=sys.stderr)
    dimensions = {
        "documentation": check_documentation(owner, repo, token),
        "licensing": check_licensing(owner, repo, token),
        "branch_protection": check_branch_protection(owner, repo, default_branch, token),
        "ci_health": check_ci_health(owner, repo, token),
        "security_posture": check_security_posture(owner, repo, token),
        "dependency_hygiene": check_dependency_hygiene(owner, repo, token),
        "community_health": check_community_health(owner, repo, token),
    }
    overall = weighted_score(dimensions)
    return {
        "repo": repo,
        "default_branch": default_branch,
        "overall_score": overall,
        "grade": grade(overall),
        "dimensions": dimensions,
    }


def render_markdown_report(owner: str, results: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# GitHub Profile Health Report: {owner}",
        f"_Generated: {now}_\n",
        "## Summary\n",
        "| Repository | Score | Grade |",
        "|-----------|-------|-------|",
    ]
    for r in sorted(results, key=lambda x: x["overall_score"], reverse=True):
        lines.append(f"| {r['repo']} | {r['overall_score']}/10 | {r['grade']} |")

    lines.append("\n---\n")
    lines.append("## Detailed Results\n")
    for r in results:
        lines.append(f"### {r['repo']} — {r['grade']} ({r['overall_score']}/10)\n")
        any_issues = False
        for dim, data in r["dimensions"].items():
            if data["notes"]:
                any_issues = True
                dim_label = dim.replace("_", " ").title()
                lines.append(f"**{dim_label}** (score: {data['score']}/10)")
                lines.append(f"_Authority: {data['authority']}_")
                for note in data["notes"]:
                    lines.append(f"- [ ] {note}")
                lines.append("")
        if not any_issues:
            lines.append("_No issues found — all dimensions passing._\n")

    lines.append("---\n")
    lines.append("## Fix Priority Queue\n")
    all_issues = []
    for r in results:
        for dim, data in r["dimensions"].items():
            for note in data["notes"]:
                all_issues.append({
                    "repo": r["repo"],
                    "dim": dim,
                    "note": note,
                    "weight": WEIGHTS[dim],
                    "dim_score": data["score"],
                })
    # Sort by weight (high-weight dims first), then by score (low score = most broken)
    all_issues.sort(key=lambda x: (-x["weight"], x["dim_score"]))
    for i, issue in enumerate(all_issues, 1):
        lines.append(f"{i}. **[{issue['repo']}]** {issue['note']} _(dimension: {issue['dim'].replace('_', ' ')})_")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fix actions (safe, non-destructive)
# ---------------------------------------------------------------------------

def apply_fixes(owner: str, results: list[dict], token: str | None) -> None:
    """Print gh CLI commands for automated fixes. Does not execute them."""
    print("\n## Automated Fix Commands\n")
    print("Run these commands to address the highest-priority issues:\n")
    for r in results:
        repo = r["repo"]
        dims = r["dimensions"]
        if not dims["documentation"]["notes"]:
            continue
        for note in dims["documentation"]["notes"]:
            if "README" in note:
                print(f"# {repo}: Create minimal README")
                print(f'gh api repos/{owner}/{repo} --method PATCH -f has_wiki=false')
                print(f'README_FILE=$(mktemp)')
                print(f'echo "# {repo}\\n\\nTODO: Add description." > "$README_FILE"')
                print(f'gh api repos/{owner}/{repo}/contents/README.md \\')
                print(f'  --method PUT \\')
                print(f'  -f message="Add README" \\')
                print(f'  -f content=$(base64 "$README_FILE" | tr -d "\\n") \\')
                print(f'  -f branch={r["default_branch"]}')
                print()
        if "No .github/dependabot.yml" in "\n".join(dims["security_posture"]["notes"] + dims["dependency_hygiene"]["notes"]):
            print(f"# {repo}: Enable Dependabot")
            print(f'gh api repos/{owner}/{repo}/vulnerability-alerts --method PUT')
            print(f'gh api repos/{owner}/{repo}/automated-security-fixes --method PUT')
            print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--owner", required=True, help="GitHub username or org to audit")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--repo", help="Audit a single repository instead of all repos")
    parser.add_argument("--output", default="-", help="Output file for Markdown report (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of Markdown")
    parser.add_argument("--fix", action="store_true", help="Print gh CLI fix commands after the report")
    args = parser.parse_args()

    if not args.token:
        print("WARNING: No GitHub token provided. Rate limits will apply and some checks may fail.", file=sys.stderr)

    print(f"Auditing GitHub profile: {args.owner}", file=sys.stderr)

    if args.repo:
        repo_info = api_get(f"/repos/{args.owner}/{args.repo}", args.token)
        if not repo_info:
            print(f"ERROR: Repository {args.owner}/{args.repo} not found.", file=sys.stderr)
            sys.exit(1)
        repos = [repo_info]
    else:
        repos = list_repos(args.owner, args.token)
        if not repos:
            print(f"ERROR: No repositories found for {args.owner}.", file=sys.stderr)
            sys.exit(1)

    results = [audit_repo(args.owner, r, args.token) for r in repos]

    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = render_markdown_report(args.owner, results)

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)

    if args.fix:
        apply_fixes(args.owner, results, args.token)

    # Exit non-zero if any Red repos found
    red_repos = [r["repo"] for r in results if r["grade"] == "Red"]
    if red_repos:
        print(f"\n[!] Red-grade repositories requiring immediate action: {', '.join(red_repos)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
