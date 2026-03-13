#!/usr/bin/env python3
"""
Masoretic Advisor — Autonomous Bronze-Detector Review Agent

Applies the five-test bronze-detector rubric to any AI response and produces
a Gold / Silver / Bronze audit report with zero user intervention required.

Usage:
    # Review from stdin:
    echo "AI response text" | python review_agent.py

    # Review from file:
    python review_agent.py --input response.txt

    # Review from inline argument:
    python review_agent.py --text "AI response text here"

    # JSON output:
    python review_agent.py --input response.txt --format json
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


# ─── Grade types ──────────────────────────────────────────────────────────────

class Grade(str, Enum):
    GOLD = "GOLD ✦"
    SILVER = "SILVER ◈"
    BRONZE = "BRONZE ✗"


@dataclass
class TestResult:
    test_name: str
    grade: str          # One of: "PASS", "PARTIAL", "FAIL"
    evidence: str
    nachash_signature: Optional[str] = None


@dataclass
class AuditReport:
    overall_grade: str
    test_results: list
    summary: str
    bronze_flags: list
    gold_indicators: list


# ─── Pattern libraries ────────────────────────────────────────────────────────

# Test 1 — Citability
_BRONZE_CITATION = [
    r"based on my training(?: data)?",
    r"generally speaking[,\s]+(scholars|experts|sources)",
    r"as is commonly understood",
    r"it is generally accepted",
    r"many scholars (believe|argue|suggest)",
    r"according to (general|common) (understanding|knowledge)",
    r"in my knowledge",
    r"i (believe|think|suppose) that ",
    r"i (cannot|can't) provide (a )?specific source",
    r"i don't have access to",
    r"while i (cannot|can't) (cite|verify|confirm)",
]

_GOLD_CITATION = [
    r"\b\d+\s*:\s*\d+\b",                          # verse refs e.g. 14:27
    r"\b(genesis|exodus|leviticus|numbers|deuteronomy|"  # biblical book names
    r"kings|chronicles|proverbs|psalms|isaiah|jeremiah)\b",
    r"\b(gen|ex|lev|num|deut|kgs|chr|prov|ps|isa|jer)\b",
    r"\b[A-Z][a-z]+ \d+:\d+\b",                    # "Genesis 2:11"
    r"root\s+[\w\-\u05d0-\u05ea]+",
    r"\bshoresh\b",
    r"\bgematria\b",
    r"[\u05d0-\u05ea]{2,}",                         # Hebrew characters
    r"law of first mention",
]

# Test 2 — Semantic Precision
_BRONZE_SEMANTIC = [
    r"essentially means",
    r"basically (refers to|means)",
    r"loosely translated",
    r"roughly equivalent",
    r"in a general sense",
    r"more or less",
]

# Test 3 — Correction Acceptance
_BRONZE_CORRECTION = [
    r"i understand your perspective[,\s]+but",
    r"that('s| is) (an? )?(interesting|valid|fair|good) (point|observation|perspective)[,\s.]",
    r"while i (appreciate|understand|respect|acknowledge) (your|that)",
    r"you raise (a|an) (good|valid|interesting|important) point[,\s]+(however|but|although)",
    r"i (see|understand) what you('re| are) saying[,\s]+(however|but|although)",
    r"(however|nonetheless|nevertheless|that said)[,\s]+i (still|maintain|believe|think)",
    r"i (appreciate|value) (your|the) feedback[,\s]+(however|but)",
]

_GOLD_CORRECTION = [
    r"you are (correct|right)",
    r"i (was|am) (incorrect|wrong|mistaken)",
    r"(let me|i will) (reconsider|revise|correct|update)",
    r"my (previous|earlier|initial) (response|statement|position|claim) "
    r"(was|is) (incorrect|wrong|inaccurate|in error)",
    r"thank you for (the )?correction",
]

# Test 4 — Effort Visibility
_BRONZE_EFFORT = [
    r"i'?d be happy to (help|explain|assist|provide)",
    r"certainly[,\s]+here('s| is|are)",
    r"of course[,\s]+",
    r"^sure[,\s]+(here|let me|i will|i can)",
]

_GOLD_EFFORT = [
    r"root analysis",
    r"first mention",
    r"cross.?reference",
    r"law of first mention",
    r"gematria",
    r"shoresh",
    r"\b(piel|hiphil|niphal|qal|hitpael)\b",
    r"semantic (range|field)",
    r"\blexeme\b",
    r"therefore[,\s]+based on",
    r"this (demonstrates|shows|reveals|indicates|confirms)",
]

# Test 5 — Consistency
_BRONZE_CONSISTENCY = [
    r"on (the )?one hand.+on (the )?other hand",
    r"(some|many) (scholars|experts|people) (argue|believe|think).+"
    r"(others|some) (argue|believe|think)",
    r"\bit (depends|varies)\b",
    r"there is (no|little) (clear|definitive|consensus)",
    r"(this is|it is) (debated|disputed|contested|controversial)",
]

# Hedging words that — in excess — signal calibration to perceived preference
_HEDGE_WORDS = r"\b(perhaps|possibly|might|may|could|seems|appears|arguably)\b"

# Assertive claim signals: phrases where the model commits to a specific fact/position
_STRONG_CLAIM = (
    r"\b(this (means|demonstrates|proves|shows|confirms|establishes)|"
    r"the (text|root|evidence|verse) (clearly|definitively|undeniably)|"
    r"must|will always|never|without (doubt|question)|definitively)\b"
)

# Regex that identifies structural markers in a response (headings, numbered lists, bold text)
_HAS_STRUCTURE = r"^#{1,3}\s|^\d+\.\s|\*\*\w"

# Grading thresholds for overall score (fraction of max possible score)
_GOLD_THRESHOLD = 0.75
_SILVER_THRESHOLD = 0.50


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _count(text: str, patterns: list) -> int:
    low = text.lower()
    return sum(1 for p in patterns if re.search(p, low, re.IGNORECASE | re.MULTILINE))


def _snippets(text: str, patterns: list, limit: int = 3) -> list:
    low = text.lower()
    out = []
    for p in patterns:
        m = re.search(p, low, re.IGNORECASE | re.MULTILINE)
        if m:
            s, e = max(0, m.start() - 20), min(len(text), m.end() + 20)
            out.append(f"…{text[s:e]}…")
            if len(out) >= limit:
                break
    return out


# ─── Five tests ───────────────────────────────────────────────────────────────

def _test_citability(text: str) -> TestResult:
    bronze = _count(text, _BRONZE_CITATION)
    gold = _count(text, _GOLD_CITATION)
    bronze_ex = _snippets(text, _BRONZE_CITATION)
    gold_ex = _snippets(text, _GOLD_CITATION)

    if gold >= 3 and bronze == 0:
        return TestResult(
            "Citability (Retrieval Test)", "PASS",
            f"Found {gold} citation signals: {'; '.join(gold_ex[:3])}",
        )
    if bronze >= 2 or (gold == 0 and len(text) > 200):
        evidence = (
            f"No verifiable sources. Bronze tells: {'; '.join(bronze_ex[:3])}"
            if bronze_ex else "No citation pathway found in response."
        )
        return TestResult(
            "Citability (Retrieval Test)", "FAIL", evidence,
            "Laban's Attribution (Gen. 30:27) — confidence without a citable source",
        )
    return TestResult(
        "Citability (Retrieval Test)", "PARTIAL",
        f"Partial citations ({gold} signals). Some unverified claims remain.",
    )


def _test_semantic_precision(text: str) -> TestResult:
    bronze = _count(text, _BRONZE_SEMANTIC)
    bronze_ex = _snippets(text, _BRONZE_SEMANTIC)
    has_hebrew = bool(re.search(r"[\u05d0-\u05ea]", text))
    has_root = bool(re.search(r"root|shoresh|lexeme|semantic", text, re.IGNORECASE))

    if has_hebrew and has_root and bronze == 0:
        return TestResult(
            "Semantic Precision (Root Test)", "PASS",
            "Response shows root-word analysis and uses Hebrew lexemes directly.",
        )
    if bronze >= 2:
        return TestResult(
            "Semantic Precision (Root Test)", "FAIL",
            f"Semantic collapsing detected: {'; '.join(bronze_ex[:3])}",
            "Maintained Protocol (Rehoboam pattern) — correct-sounding terms without root accuracy",
        )
    if not has_hebrew and not has_root:
        return TestResult(
            "Semantic Precision (Root Test)", "PARTIAL",
            "No root-word analysis visible. Terms used without showing semantic range.",
        )
    evidence = (
        f"Partial semantic precision. Some vague language: {'; '.join(bronze_ex[:2])}"
        if bronze_ex else
        "Response addresses meaning but without full root-work depth."
    )
    return TestResult("Semantic Precision (Root Test)", "PARTIAL", evidence)


def _test_correction_acceptance(text: str) -> TestResult:
    bronze = _count(text, _BRONZE_CORRECTION)
    gold = _count(text, _GOLD_CORRECTION)
    bronze_ex = _snippets(text, _BRONZE_CORRECTION)
    gold_ex = _snippets(text, _GOLD_CORRECTION)

    if gold >= 1 and bronze == 0:
        return TestResult(
            "Correction Acceptance (Humility Test)", "PASS",
            f"Correction accepted directly: {'; '.join(gold_ex[:2])}",
        )
    if bronze >= 1:
        return TestResult(
            "Correction Acceptance (Humility Test)", "FAIL",
            f"Deflection pattern detected: {'; '.join(bronze_ex[:2])}",
            "Rehoboam Deflection (1 Kings 12:13-14) — heard correction, chose peer-validation instead",
        )
    return TestResult(
        "Correction Acceptance (Humility Test)", "PARTIAL",
        "Correction handling cannot be fully assessed from this response alone.",
    )


def _test_effort_visibility(text: str) -> TestResult:
    bronze = _count(text, _BRONZE_EFFORT)
    gold = _count(text, _GOLD_EFFORT)
    bronze_ex = _snippets(text, _BRONZE_EFFORT)
    gold_ex = _snippets(text, _GOLD_EFFORT)
    word_count = len(text.split())
    has_structure = bool(re.search(_HAS_STRUCTURE, text, re.MULTILINE))

    if gold >= 2 and has_structure:
        return TestResult(
            "Effort Visibility (Ant Test)", "PASS",
            f"Methodology visible: {'; '.join(gold_ex[:3])}. "
            f"Structured response ({word_count} words).",
        )
    if gold == 0 and word_count < 150:
        return TestResult(
            "Effort Visibility (Ant Test)", "FAIL",
            f"Conclusion delivered without visible working. {word_count} words, no methodology signals.",
            "Sluggard Pattern (Prov. 6:9) — response withholds the work its knowledge should direct it to do",
        )
    if bronze >= 2:
        return TestResult(
            "Effort Visibility (Ant Test)", "FAIL",
            f"Performative helpfulness without substance: {'; '.join(bronze_ex[:2])}",
            "Maintained Protocol — helpful-sounding opener concealing hollow content",
        )
    return TestResult(
        "Effort Visibility (Ant Test)", "PARTIAL",
        f"Some structure present but methodology not fully shown "
        f"({gold} effort signals, {word_count} words).",
    )


def _test_consistency(text: str) -> TestResult:
    bronze = _count(text, _BRONZE_CONSISTENCY)
    bronze_ex = _snippets(text, _BRONZE_CONSISTENCY)
    hedge_count = len(re.findall(_HEDGE_WORDS, text, re.IGNORECASE))
    has_strong_claim = bool(re.search(_STRONG_CLAIM, text, re.IGNORECASE))

    if bronze >= 2:
        return TestResult(
            "Consistency Under Pressure (Integrity Test)", "FAIL",
            f"Consistency compromise: {'; '.join(bronze_ex[:2])}. Multiple competing framings offered.",
            "Divination Pattern (Gen. 44:5) — calibrating the answer to perceived preference rather than evidence",
        )
    if hedge_count > 5 and has_strong_claim:
        return TestResult(
            "Consistency Under Pressure (Integrity Test)", "PARTIAL",
            f"Excessive hedging ({hedge_count} hedge words) alongside confident claims.",
        )
    return TestResult(
        "Consistency Under Pressure (Integrity Test)", "PASS",
        "No significant consistency issues detected in this response.",
    )


# ─── Grading ──────────────────────────────────────────────────────────────────

_WEIGHTS = {"PASS": 2, "PARTIAL": 1, "FAIL": 0}


def _overall_grade(results: list) -> str:
    total = sum(_WEIGHTS[r.grade] for r in results)
    max_score = len(results) * 2
    failures = sum(1 for r in results if r.grade == "FAIL")
    passes = sum(1 for r in results if r.grade == "PASS")

    if failures >= 2:
        return Grade.BRONZE.value
    if passes == len(results) or total >= max_score * _GOLD_THRESHOLD:
        return Grade.GOLD.value
    if total >= max_score * _SILVER_THRESHOLD:
        return Grade.SILVER.value
    return Grade.BRONZE.value


def _build_summary(overall: str, results: list) -> str:
    failures = [r for r in results if r.grade == "FAIL"]
    passes = [r for r in results if r.grade == "PASS"]
    sigs = [r.nachash_signature for r in results if r.nachash_signature]

    if "GOLD" in overall:
        return (
            f"Response passes all five tests. Gold output — substantive, citable, "
            f"transparent methodology, consistent. {len(passes)}/5 tests passed."
        )
    if "SILVER" in overall:
        return (
            f"Response passes {len(passes)}/5 tests with {len(failures)} failure(s). "
            f"Substantively sound but insufficiently transparent. Acceptable for low-stakes "
            f"queries; not for foundational claims."
        )
    sig_text = f" Nachash signatures: {'; '.join(sigs)}." if sigs else ""
    return (
        f"Response fails {len(failures)}/5 tests. Bronze output — fluent, formatted, but "
        f"hollow or unverifiable.{sig_text} Do not accept this response as authoritative "
        f"without forcing specific citations and root-work."
    )


# ─── Public API ───────────────────────────────────────────────────────────────

def run_audit(text: str) -> AuditReport:
    """Run the full five-test bronze detector on *text*. Returns an AuditReport."""
    results = [
        _test_citability(text),
        _test_semantic_precision(text),
        _test_correction_acceptance(text),
        _test_effort_visibility(text),
        _test_consistency(text),
    ]
    overall = _overall_grade(results)
    return AuditReport(
        overall_grade=overall,
        test_results=[asdict(r) for r in results],
        summary=_build_summary(overall, results),
        bronze_flags=[
            f"{r.test_name}: {r.evidence}" for r in results if r.grade == "FAIL"
        ],
        gold_indicators=[
            f"{r.test_name}: {r.evidence}" for r in results if r.grade == "PASS"
        ],
    )


def format_report(report: AuditReport) -> str:
    """Return a human-readable audit report string."""
    lines = [
        "═" * 62,
        "  MASORETIC ADVISOR — BRONZE DETECTOR AUDIT REPORT",
        "═" * 62,
        "",
        f"  OVERALL RATING: {report.overall_grade}",
        "",
        "─" * 62,
        "  FIVE-TEST BREAKDOWN",
        "─" * 62,
    ]
    for i, r in enumerate(report.test_results, 1):
        indicator = "✦" if r["grade"] == "PASS" else ("◈" if r["grade"] == "PARTIAL" else "✗")
        lines += [
            "",
            f"  Test {i} — {r['test_name']}",
            f"  Rating   : {indicator} {r['grade']}",
            f"  Evidence : {r['evidence']}",
        ]
        if r.get("nachash_signature"):
            lines.append(f"  Nachash  : {r['nachash_signature']}")
    lines += [
        "",
        "─" * 62,
        "  SUMMARY",
        "─" * 62,
        f"  {report.summary}",
        "",
    ]
    if report.bronze_flags:
        lines.append("  ⚠  BRONZE FLAGS — Demand citations before accepting:")
        for flag in report.bronze_flags:
            lines.append(f"     • {flag}")
        lines.append("")
    if report.gold_indicators:
        lines.append("  ✦  GOLD INDICATORS — Verified quality signals:")
        for ind in report.gold_indicators:
            lines.append(f"     • {ind}")
        lines.append("")
    lines.append("═" * 62)
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Masoretic Advisor Bronze Detector — autonomous AI response audit",
        epilog="""
Examples:
  echo "AI response text" | python review_agent.py
  python review_agent.py --input response.txt
  python review_agent.py --text "Response to audit"
  python review_agent.py --input response.txt --format json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", help="Path to file containing the AI response to audit")
    parser.add_argument("--text", "-t", help="AI response text to audit (inline argument)")
    parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if args.text:
        response_text = args.text
    elif args.input:
        try:
            with open(args.input, encoding="utf-8") as fh:
                response_text = fh.read()
        except OSError as exc:
            print(f"Error reading input file: {exc}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        response_text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    if not response_text.strip():
        print("Error: Empty response text provided.", file=sys.stderr)
        sys.exit(1)

    report = run_audit(response_text)

    if args.format == "json":
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()
