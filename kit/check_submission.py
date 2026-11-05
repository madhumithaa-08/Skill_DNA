"""
SKILL DNA — Submission artifact completeness check (strands-ship pattern: ss check).

Verifies every artifact the bench → video → article pipeline produces is present
and non-empty, prints a clear PASS/FAIL table, and runs an advisory secret scan.
Returns 0 only if zero required FAILs; otherwise 1.

Usage:
    python kit/check_submission.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "kit" / "results"
DEMO = ROOT / "demo"

# Secret patterns (adapted from strands-ship submit.py) — advisory only.
SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"aws_secret_access_key\s*="
)


def _nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def _valid_json(path: Path, *required_keys) -> bool:
    if not _nonempty(path):
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return isinstance(data, dict) and all(k in data for k in required_keys)
    except Exception:
        return False


def _video_path() -> tuple[Path | None, str]:
    mp4 = RESULTS / "demo.mp4"
    webm = RESULTS / "demo.webm"
    if _nonempty(mp4):
        return mp4, "demo.mp4"
    if _nonempty(webm):
        return webm, "demo.webm"
    return None, ""


def _cases_signed() -> tuple[bool, str]:
    cases = ROOT / "kit" / "cases" / "cases.jsonl"
    if not cases.exists():
        return False, "kit/cases/cases.jsonl missing"
    lines = [l for l in cases.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        return False, "kit/cases/cases.jsonl is empty"
    unsigned = 0
    for l in lines:
        try:
            if not json.loads(l).get("signed_by"):
                unsigned += 1
        except Exception:
            return False, "kit/cases/cases.jsonl has a malformed line"
    if unsigned:
        return False, f"{unsigned} case(s) missing signed_by"
    return True, f"{len(lines)} signed cases"


def _secrets() -> list[str]:
    """Advisory scan of tracked files for committed secrets. Skips vendored dirs."""
    hits: list[str] = []
    try:
        files = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            capture_output=True, text=True, cwd=ROOT,
        ).stdout.split()
    except Exception:
        files = []
    if not files:
        files = [str(p) for p in ROOT.rglob("*") if p.is_file()]
    skip_parts = {"kit", "strands-ship", ".venv", "__pycache__", "node_modules", ".git", "results", "_raw"}
    for f in files:
        p = ROOT / f
        try:
            parts = set(p.parts)
        except Exception:
            continue
        if not skip_parts.isdisjoint(parts) and "kit" in parts:
            continue
        if any(seg in parts for seg in (".venv", "__pycache__", "node_modules", ".git", "strands-ship")):
            continue
        if not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        if p.name == ".env":
            continue  # presence is checked separately; contents never read
        try:
            if SECRET.search(p.read_text(errors="ignore")):
                hits.append(f)
        except OSError:
            pass
    return hits


def main(argv=None) -> int:
    print("\n📋 SKILL DNA — Submission Artifact Check\n")
    rows: list[tuple[str, str, str]] = []
    add = lambda status, what, note="": rows.append((status, what, note))

    # --- Required artifacts ---
    vid, vname = _video_path()
    add("PASS" if vid else "FAIL", "Demo video recorded (mp4 or webm)",
        vname if vid else "run `python kit/ss.py video --target local`")
    add("PASS" if _valid_json(RESULTS / "video_run.json", "scenes", "under_3_min") else "FAIL",
        "video_run.json present & valid", "kit/results/video_run.json")
    add("PASS" if _valid_json(RESULTS / "results.json", "rows", "overall_pass_rate") else "FAIL",
        "results.json present & valid", "kit/results/results.json")
    add("PASS" if _nonempty(RESULTS / "MEASURE.md") else "FAIL",
        "MEASURE.md generated", "kit/results/MEASURE.md")
    add("PASS" if _nonempty(DEMO / "ARTICLE_GENERATED.md") else "FAIL",
        "Generated article present", "demo/ARTICLE_GENERATED.md")
    ok_cases, cases_note = _cases_signed()
    add("PASS" if ok_cases else "FAIL", "Signed benchmark cases", cases_note)
    add("PASS" if _nonempty(ROOT / "README.md") else "FAIL", "README.md present", "README.md")
    add("PASS" if _nonempty(ROOT / ".env") else "FAIL", ".env present (contents not shown)", ".env")

    # --- Advisory only ---
    add("INFO" if _nonempty(DEMO / "BUILDER_CENTER_ARTICLE.md") else "ADVISORY",
        "Human article draft (advisory)", "demo/BUILDER_CENTER_ARTICLE.md")

    print(f"{'Status':8}{'Artifact':48}{'Note'}")
    print("-" * 100)
    for status, what, note in rows:
        mark = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "ADVISORY": "⚠️"}.get(status, " ")
        print(f"{mark} {status:6}{what:48}{note}")

    fails = sum(1 for s, _, _ in rows if s == "FAIL")
    advisory = sum(1 for s, _, _ in rows if s in ("ADVISORY",))

    # Secret scan
    print("\n🔐 Secret scan (advisory):")
    sec_hits = _secrets()
    if sec_hits:
        print("   ⚠️  possible secrets in:")
        for h in sec_hits:
            print(f"      - {h}")
    else:
        print("   ✅ no AWS keys or private keys found in tracked files (.env contents not read)")

    print(f"\n  {fails} FAIL, {advisory} advisory" + (". Fix every FAIL, then run `python kit/ss.py check` again." if fails else ". All required artifacts present."))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
