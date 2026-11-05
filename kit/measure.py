"""
SKILL DNA — Measurement script (strands-ship pattern: ss measure / ss bench).

Scores the SKILL DNA agents against the signed cases in kit/cases/cases.jsonl,
dispatching each case by its ``label`` to the matching agent and scoring the
result against the case's ``expected_*`` field:

  observer            -> ObserverAgent.analyze()        vs expected_gaps
  interviewer         -> InterviewerAgent.generate_questions() vs expected_questions
  knowledge_architect -> KnowledgeArchitectAgent.build_fingerprint() vs expected_fingerprint_keys
  curriculum_quiz     -> CurriculumAgent.create_lesson() vs expected_answer (in quiz answers)

A one-prompt baseline (no agents, no tools, no feedback loop) is also run on the
observer/interviewer cases for the honest comparison that goes in MEASURE.md.

Writes:
  kit/results/results.json  — machine-readable, per-case pass/fail + metrics
  kit/results/MEASURE.md    — human-readable report (same numbers)

Per-case crashes are caught and recorded as a failed row (passed:false,
detail = the error) — never hidden, matching the strands-ship pattern.

Usage:
    python kit/measure.py
    python kit/measure.py --limit 4
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from strands import Agent
from strands.models import BedrockModel

CASES_FILE  = ROOT / "kit" / "cases" / "cases.jsonl"
RESULTS_DIR = ROOT / "kit" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
REGION   = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def model() -> BedrockModel:
    return BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.2)


# ---------------------------------------------------------------------------
# Synonyms for matching expected concepts against free-text agent output.
# Shared by the gap scorer (observer) and the question scorer (interviewer).
# ---------------------------------------------------------------------------
_SYNONYMS: dict[str, list[str]] = {
    # observer gaps
    "knot tension":    ["tension", "tight", "tightness", "resist", "secure", "firm", "grip", "feel", "fingertip"],
    "dye temperature": ["temperature", "heat", "hot", "warm", "boiling", "bath", "degree", "thermal"],
    "timing":          ["duration", "time", "long", "minutes", "hours", "when", "period", "ready"],
    "wheel speed":     ["speed", "spin", "rpm", "rotation", "wheel"],
    "hand pressure":   ["pressure", "press", "force", "push", "palm", "hand"],
    "water frequency": ["water", "wet", "moisture", "damp", "frequency"],
    "thread tension":  ["tension", "tight", "warp", "thread"],
    "beater force":    ["beater", "force", "press", "beat"],
    "pattern planning":["pattern", "plan", "design", "motif", "spacing", "distance"],
    # interviewer expected-question concepts
    "tactile tension": ["tension", "tight", "tightness", "resist", "resistance", "firm", "grip", "feel", "fingertip"],
    "feel when correct":["feel", "correct", "right", "know when", "ready", "sense", "tell", "judge", "recognise", "recognize"],
    "test method":     ["test", "method", "check", "verify", "way to", "determine", "how to tell", "how do you know"],
}


def _match_concepts(haystack: str, expected: list[str]) -> tuple[list[str], list[str]]:
    """Return (matched, missed) for ``expected`` concepts found in ``haystack``.

    A concept matches if it (or any of its synonyms) appears as a substring in
    the lower-cased haystack text.
    """
    if not expected:
        return [], []
    ht = haystack.lower()
    matched, missed = [], []
    for exp in expected:
        el = exp.lower()
        if el in ht:
            matched.append(exp)
            continue
        syns = _SYNONYMS.get(el, el.split())
        if any(s and s in ht for s in syns):
            matched.append(exp)
        else:
            missed.append(exp)
    return matched, missed


def _score(matched: list, expected: list, has_output: bool) -> float:
    """Fraction of expected items matched (1.0 if no expectation and output exists)."""
    if not expected:
        return 1.0 if has_output else 0.0
    return round(len(matched) / len(expected), 2)


# ---------------------------------------------------------------------------
# Baseline: one prompt, no agents, no tools, no feedback loop
# ---------------------------------------------------------------------------
BASELINE_PROMPT = """You are a craft knowledge assistant.
Given an artisan's description, in one JSON reply list:
- visible_steps (list of strings)
- knowledge_gaps (list of things NOT visible/unclear)
- questions (2-3 interview questions)
Output only valid JSON."""


def run_baseline(text: str) -> dict:
    agent = Agent(model=model(), system_prompt=BASELINE_PROMPT, callback_handler=None)
    t0 = time.time()
    raw = str(agent(text))
    ms = int((time.time() - t0) * 1000)
    m = re.search(r"\{[\s\S]*\}", raw)
    try:
        result = json.loads(m.group()) if m else {}
    except Exception:
        result = {}
    return {"result": result, "latency_ms": ms}


# ---------------------------------------------------------------------------
# SKILL DNA agent runners (one stage each)
# ---------------------------------------------------------------------------
def run_observer(text: str) -> tuple[dict, int, str | None]:
    t0 = time.time()
    try:
        from agents.observer_agent import ObserverAgent
        obs = ObserverAgent().analyze(text)
        return obs, int((time.time() - t0) * 1000), None
    except Exception as exc:  # a crash is a result too — counted, never hidden
        return {}, int((time.time() - t0) * 1000), f"{type(exc).__name__}: {exc}"[:200]


def run_interviewer(gaps: list, craft: str) -> tuple[list, int, str | None]:
    t0 = time.time()
    try:
        from agents.interviewer_agent import InterviewerAgent
        qs = InterviewerAgent().generate_questions(gaps, craft)
        return qs, int((time.time() - t0) * 1000), None
    except Exception as exc:
        return [], int((time.time() - t0) * 1000), f"{type(exc).__name__}: {exc}"[:200]


def _minimal_observation(text: str) -> dict:
    """Build a minimal structured observation from raw case text for the architect."""
    steps = [s.strip() for s in re.split(r"[.;\n]+", text) if s.strip()]
    return {
        "visible_steps": steps or [text],
        "tools_identified": [],
        "materials_identified": [],
        "knowledge_gaps": [],
    }


def run_architect(text: str, craft: str) -> tuple[dict, int, str | None]:
    t0 = time.time()
    try:
        from agents.knowledge_architect import KnowledgeArchitectAgent
        fp_dir = ROOT / "data" / "skill_fingerprints"
        before = set(p.name for p in fp_dir.glob("*.json")) if fp_dir.exists() else set()
        obs = _minimal_observation(text)
        result = KnowledgeArchitectAgent().build_fingerprint(obs, {}, craft, "Artisan")
        fp = result.get("fingerprint", result) if isinstance(result, dict) else {}
        if not isinstance(fp, dict):
            fp = {}
        # The architect's tool saves the real fingerprint to disk; if the agent's
        # text response wasn't JSON, score the actual artifact it produced instead.
        if not fp or not any(fp.get(k) for k in ("materials", "techniques", "decisions")):
            if fp_dir.exists():
                new_files = [p for p in fp_dir.glob("*.json") if p.name not in before]
                if new_files:
                    newest = max(new_files, key=lambda p: p.stat().st_mtime)
                    try:
                        fp = json.loads(newest.read_text(encoding="utf-8"))
                    except Exception:
                        pass
        return fp, int((time.time() - t0) * 1000), None
    except Exception as exc:
        return {}, int((time.time() - t0) * 1000), f"{type(exc).__name__}: {exc}"[:200]


def run_curriculum(fingerprint: dict) -> tuple[dict, int, str | None]:
    t0 = time.time()
    try:
        from agents.curriculum_agent import CurriculumAgent
        lesson = CurriculumAgent().create_lesson(fingerprint)
        return lesson if isinstance(lesson, dict) else {}, int((time.time() - t0) * 1000), None
    except Exception as exc:
        return {}, int((time.time() - t0) * 1000), f"{type(exc).__name__}: {exc}"[:200]


def _quiz_correct_answers(lesson: dict) -> list[str]:
    """Extract every correct-answer string from a generated lesson quiz."""
    out: list[str] = []
    for q in lesson.get("quiz", []) if isinstance(lesson.get("quiz"), list) else []:
        if not isinstance(q, dict):
            continue
        for key in ("correct_answer", "correctAnswer", "answer", "correct", "correct_option"):
            val = q.get(key)
            if isinstance(val, str) and val.strip():
                out.append(val)
                break
            if isinstance(val, (int, float)):
                out.append(str(val))
                break
    return out


# ---------------------------------------------------------------------------
# Per-label scoring
# ---------------------------------------------------------------------------
def score_observer(case: dict) -> dict:
    text = case.get("text", "")
    obs, ms, err = run_observer(text)
    if err:
        return _failed_row(case, "observer", ms, err, case.get("expected_gaps", []))
    gaps = obs.get("knowledge_gaps", [])
    haystack = " ".join(str(g) for g in gaps)
    expected = case.get("expected_gaps", [])
    matched, missed = _match_concepts(haystack, expected)
    score = _score(matched, expected, bool(gaps))
    return {
        "id": case["id"], "label": "observer", "craft": case.get("craft", ""),
        "agent": "observer", "passed": score == 1.0, "score": score,
        "expected": expected, "matched": matched, "missed": missed,
        "latency_ms": ms, "detail": f"{len(gaps)} gaps found; {len(matched)}/{len(expected)} expected matched",
    }


def score_interviewer(case: dict) -> dict:
    text = case.get("text", "")
    craft = case.get("craft", "Traditional Craft")
    qs, ms, err = run_interviewer([text], craft)
    if err:
        return _failed_row(case, "interviewer", ms, err, case.get("expected_questions", []))
    haystack = " ".join(str(q) for q in qs)
    expected = case.get("expected_questions", [])
    matched, missed = _match_concepts(haystack, expected)
    score = _score(matched, expected, bool(qs))
    return {
        "id": case["id"], "label": "interviewer", "craft": craft,
        "agent": "interviewer", "passed": score == 1.0, "score": score,
        "expected": expected, "matched": matched, "missed": missed,
        "latency_ms": ms, "detail": f"{len(qs)} questions generated; {len(matched)}/{len(expected)} expected concepts matched",
    }


def score_knowledge_architect(case: dict) -> dict:
    text = case.get("text", "")
    craft = case.get("craft", "Traditional Craft")
    fp, ms, err = run_architect(text, craft)
    if err:
        return _failed_row(case, "knowledge_architect", ms, err, case.get("expected_fingerprint_keys", []))
    expected = case.get("expected_fingerprint_keys", [])
    matched = [k for k in expected if fp.get(k)]  # present AND non-empty
    missed = [k for k in expected if not fp.get(k)]
    score = _score(matched, expected, bool(fp))
    return {
        "id": case["id"], "label": "knowledge_architect", "craft": craft,
        "agent": "knowledge_architect", "passed": score == 1.0, "score": score,
        "expected": expected, "matched": matched, "missed": missed,
        "latency_ms": ms, "detail": f"{len(fp)} fingerprint fields; {len(matched)}/{len(expected)} expected keys present",
    }


def score_curriculum_quiz(case: dict) -> dict:
    text = case.get("text", "")
    craft = case.get("craft", "Traditional Craft")
    fp, ms_fp, err_fp = run_architect(text, craft)
    if err_fp:
        return _failed_row(case, "curriculum_quiz", ms_fp, err_fp, [case.get("expected_answer", "")])
    lesson, ms_lc, err_lc = run_curriculum(fp)
    total_ms = ms_fp + ms_lc
    if err_lc:
        return _failed_row(case, "curriculum_quiz", total_ms, err_lc, [case.get("expected_answer", "")])
    expected_answer = str(case.get("expected_answer", ""))
    answers = _quiz_correct_answers(lesson)
    answers_blob = " ".join(a.lower() for a in answers)
    found = bool(expected_answer) and expected_answer.lower() in answers_blob
    matched = [expected_answer] if found else []
    missed = [] if found else ([expected_answer] if expected_answer else [])
    score = 1.0 if found else 0.0
    return {
        "id": case["id"], "label": "curriculum_quiz", "craft": craft,
        "agent": "curriculum", "passed": found, "score": score,
        "expected": [expected_answer] if expected_answer else [], "matched": matched, "missed": missed,
        "latency_ms": total_ms, "detail": f"{len(answers)} quiz answers checked; expected answer {'found' if found else 'not found'}",
    }


def _failed_row(case: dict, label: str, ms: int, err: str, expected: list) -> dict:
    return {
        "id": case["id"], "label": label, "craft": case.get("craft", ""),
        "agent": label, "passed": False, "score": 0.0,
        "expected": expected, "matched": [], "missed": expected,
        "latency_ms": ms, "detail": f"ERROR: {err}",
    }


SCORERS = {
    "observer": score_observer,
    "interviewer": score_interviewer,
    "knowledge_architect": score_knowledge_architect,
    "curriculum_quiz": score_curriculum_quiz,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python kit/measure.py")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)

    all_cases = [json.loads(l) for l in CASES_FILE.read_text().splitlines() if l.strip()]
    cases = all_cases[:args.limit] if args.limit else all_cases

    rows: list[dict] = []
    print(f"\n{'='*60}")
    print(f"  SKILL DNA — Bench: agents scored against signed cases")
    print(f"  Model: {MODEL_ID}  Region: {REGION}  Cases: {len(cases)}")
    print(f"{'='*60}\n")

    for case in cases:
        label = case.get("label", "observer")
        scorer = SCORERS.get(label)
        if not scorer:
            print(f"  [skip] {case['id']}: unknown label '{label}'")
            continue
        print(f"  [{case['id']}] {label}...", end="", flush=True)
        row = scorer(case)
        rows.append(row)
        icon = "✅" if row["passed"] else "⚠️"
        print(f" {icon} score={row['score']} ({row['detail']})")

    # baseline comparison on observer + interviewer cases
    baseline_rows: list[dict] = []
    bl_gaps, bl_tacit = [], []
    for case in [c for c in cases if c.get("label") in ("observer", "interviewer")]:
        bl = run_baseline(case.get("text", ""))
        r = bl.get("result", {})
        exp = case.get("expected_gaps") or case.get("expected_questions") or []
        matched, _ = _match_concepts(" ".join(str(g) for g in r.get("knowledge_gaps", []) + r.get("questions", [])), exp)
        bl_gaps.append(_score(matched, exp, bool(r)))
        qs = r.get("questions", [])
        tacit_words = ["feel", "sense", "know when", "muscle", "tell", "judge", "temperature", "texture", "resistance", "fingertip"]
        bl_tacit.append(sum(1 for q in qs if any(w in str(q).lower() for w in tacit_words)) / max(len(qs), 1))
        baseline_rows.append({"case": case["id"], "score": _score(matched, exp, bool(r)), "latency_ms": bl.get("latency_ms", 0)})

    # ---- summary by label ----
    summary: dict[str, dict] = {}
    for label in ("observer", "interviewer", "knowledge_architect", "curriculum_quiz"):
        lr = [r for r in rows if r["label"] == label]
        if lr:
            summary[label] = {"cases": len(lr), "score_avg": round(sum(r["score"] for r in lr) / len(lr), 2)}

    passed = sum(1 for r in rows if r["passed"])
    overall_pass_rate = round(passed / len(rows), 2) if rows else 0.0

    report = {
        "when": time.strftime("%Y-%m-%d %H:%M"),
        "model": MODEL_ID,
        "region": REGION,
        "cases_run": len(rows),
        "summary": summary,
        "baseline": {
            "gaps_avg": round(sum(bl_gaps) / len(bl_gaps), 2) if bl_gaps else 0.0,
            "tacit_q_avg": round(sum(bl_tacit) / len(bl_tacit), 3) if bl_tacit else 0.0,
            "rows": baseline_rows,
        },
        "overall_pass_rate": overall_pass_rate,
        "rows": rows,
    }

    (RESULTS_DIR / "results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (RESULTS_DIR / "MEASURE.md").write_text(_markdown(report), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  Cases run: {len(rows)}   Passed: {passed}   Pass rate: {overall_pass_rate:.0%}")
    for label, s in summary.items():
        print(f"  {label:20} {s['cases']} cases · avg score {s['score_avg']}")
    print(f"  Baseline gap avg: {report['baseline']['gaps_avg']}   tacit-q avg: {report['baseline']['tacit_q_avg']:.0%}")
    print(f"  results.json: {RESULTS_DIR / 'results.json'}")
    print(f"  MEASURE.md:   {RESULTS_DIR / 'MEASURE.md'}")
    print(f"{'='*60}\n")
    return 0


def _markdown(r: dict) -> str:
    md = [
        "# SKILL DNA — Measurement Results",
        "",
        f"**Model:** `{r['model']}`  **Region:** `{r['region']}`  **Cases:** {r['cases_run']}  **Run:** {r['when']}",
        "",
        "## What is measured",
        "",
        "Each signed case is dispatched by its `label` to the matching SKILL DNA agent and",
        "scored against that case's `expected_*` field:",
        "",
        "- **observer** — fraction of `expected_gaps` the Observer surfaces (synonym match).",
        "- **interviewer** — fraction of `expected_questions` concepts the Interviewer targets.",
        "- **knowledge_architect** — fraction of `expected_fingerprint_keys` present & non-empty in the fingerprint.",
        "- **curriculum_quiz** — 1.0 if the `expected_answer` appears in a quiz question's correct answer, else 0.0.",
        "",
        "A one-prompt baseline (no agents, no tools, no feedback loop) is run on the",
        "observer/interviewer cases for honest comparison.",
        "",
        "## Summary",
        "",
        "| Label | Cases | Avg score |",
        "|--------|-------|-----------|",
    ]
    for label, s in r["summary"].items():
        md.append(f"| {label} | {s['cases']} | **{s['score_avg']}** |")
    md += [
        f"| **overall** | **{r['cases_run']}** | **pass rate {r['overall_pass_rate']:.0%}** |",
        "",
        f"Baseline gap avg: **{r['baseline']['gaps_avg']}** · baseline tacit-question avg: **{r['baseline']['tacit_q_avg']:.0%}**",
        "",
        "## Per-case results",
        "",
        "| Case | Label | Score | Passed | Detail | Latency |",
        "|------|-------|-------|--------|--------|---------|",
    ]
    for row in r["rows"]:
        md.append(f"| {row['id']} | {row['label']} | {row['score']} | {'✅' if row['passed'] else '⚠️'} | {row['detail']} | {row['latency_ms']} ms |")
    md += [
        "",
        "**Cases signed by:** Madhumitha A",
        "",
        "> Generated by `python kit/measure.py` (run via `python kit/ss.py bench`)",
    ]
    return "\n".join(md) + "\n"


if __name__ == "__main__":
    sys.exit(main())
