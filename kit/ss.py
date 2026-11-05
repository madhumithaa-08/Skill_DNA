"""
SKILL DNA automation CLI — mirrors the strands-ship `ss` commands.

Commands:
    python kit/ss.py bench                  — score all signed cases -> results.json + MEASURE.md
    python kit/ss.py video --target local   — record the live demo -> demo.mp4 + video_run.json
    python kit/ss.py article                — write the honest-numbers article + FACTS.md
    python kit/ss.py check                  — verify all submission artifacts present
    python kit/ss.py status                 — pre-submission env checklist
    python kit/ss.py measure [--limit N]    — alias for bench
    python kit/ss.py bedrock                — verify AWS + Bedrock are working
    python kit/ss.py blocks                 — list available Strands blocks
    python kit/ss.py block <name>           — run one block live (e.g. block sessions)
    python kit/ss.py pipeline               — run the live Observer → Curriculum pipeline

Usage:
    python kit/ss.py <command> [args]
    ./kit <command> [args]          # via the executable wrapper at the project root
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
BLOCKS_DIR = ROOT / "kit" / "strands-ship" / "kit" / "blocks"
SAMPLE_NOTES = ROOT / "data" / "sample_sungudi_notes.txt"

sys.path.insert(0, str(ROOT))


def _load_env() -> None:
    from dotenv import load_dotenv
    load_dotenv()


def _load_module(name: str, path: Path):
    """Import a sibling kit module by absolute path (runs in this process)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# bench / measure — score all signed cases, write results.json + MEASURE.md
# ---------------------------------------------------------------------------
def cmd_bench(args):
    _load_env()
    measure = _load_module("measure", ROOT / "kit" / "measure.py")
    argv = ["--limit", str(args.limit)] if getattr(args, "limit", None) else []
    return measure.main(argv)


# alias kept for backward compatibility
cmd_measure = cmd_bench


# ---------------------------------------------------------------------------
# video — record the live demo (Playwright drives the real website)
# ---------------------------------------------------------------------------
def cmd_video(args):
    _load_env()
    if args.target != "local":
        print("ERROR: AgentCore deployment is not supported by this kit; use --target local")
        return 1
    url = getattr(args, "url", "http://localhost:8000")
    make_video = _load_module("make_video", ROOT / "kit" / "make_video.py")
    result = make_video.record(base_url=url, dry_run=args.dry_run)
    if args.dry_run:
        return 0
    return 0 if result.get("under_3_min") else 1


# ---------------------------------------------------------------------------
# article — generate the honest-numbers article + FACTS.md
# ---------------------------------------------------------------------------
def cmd_article(_args):
    make_article = _load_module("make_article", ROOT / "kit" / "make_article.py")
    return make_article.main()


# ---------------------------------------------------------------------------
# check — submission artifact completeness
# ---------------------------------------------------------------------------
def cmd_check(_args):
    check_submission = _load_module("check_submission", ROOT / "kit" / "check_submission.py")
    return check_submission.main()


# ---------------------------------------------------------------------------
# bedrock
# ---------------------------------------------------------------------------
def cmd_bedrock(_args):
    _load_env()
    print("\n🔍 Checking AWS + Bedrock credentials...\n")
    import boto3
    from dotenv import load_dotenv
    load_dotenv()

    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"  ✅ AWS identity: {identity['Arn']}")
    except Exception as e:
        print(f"  ❌ AWS credentials error: {e}")
        return 1

    model_id = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
    region   = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    print(f"  Model: {model_id}  Region: {region}")

    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        body = json.dumps({"messages": [{"role": "user", "content": [{"text": "Reply: SKILL DNA online"}]}], "inferenceConfig": {"maxTokens": 30}})
        r = client.invoke_model(modelId=model_id, body=body, contentType="application/json")
        result = json.loads(r["body"].read())
        reply = result.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", str(result))
        print(f"  ✅ Bedrock live: {reply.strip()}")
    except Exception as e:
        print(f"  ❌ Bedrock error: {e}")
        return 1

    print("\n  ✅ All checks passed — ready to run live agents\n")
    return 0


# ---------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------
def cmd_blocks(_args):
    if not BLOCKS_DIR.exists():
        print("❌ strands-ship blocks not found. Run: git clone in kit/strands-ship")
        return 1

    files = sorted(BLOCKS_DIR.glob("b*.py"))
    print(f"\n{'='*55}")
    print(f"  Strands Blocks ({len(files)} available from strands-ship)")
    print(f"{'='*55}")
    for f in files:
        first_line = ""
        for line in f.read_text().splitlines():
            if line.startswith('"""'):
                first_line = line.lstrip('"').split(".")[0].strip()
                break
        print(f"  {f.stem:30s}  {first_line[:45]}")
    print(f"\n  Run one: python kit/ss.py block <name>")
    print(f"  Example: python kit/ss.py block sessions\n")
    return 0


# ---------------------------------------------------------------------------
# block <name>
# ---------------------------------------------------------------------------
def cmd_block(args):
    if not args.name:
        print("Usage: python kit/ss.py block <name>  e.g. block sessions")
        return 1

    name = args.name.replace("-", "_")
    matches = list(BLOCKS_DIR.glob(f"*{name}*.py"))
    matches = [m for m in matches if not m.name.startswith("_")]
    if not matches:
        print(f"❌ Block '{args.name}' not found. Run `python kit/ss.py blocks` to list.")
        return 1
    block_file = matches[0]
    print(f"\n▶ Running block: {block_file.name}\n")

    env = {**os.environ, "PYTHONPATH": str(BLOCKS_DIR)}
    result = subprocess.run(
        [sys.executable, str(block_file)],
        cwd=str(BLOCKS_DIR),
        env=env,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# pipeline — live end-to-end run on Sungudi sample
# ---------------------------------------------------------------------------
def cmd_pipeline(_args):
    _load_env()
    print("\n🧬 SKILL DNA — Live Pipeline Run\n")
    print("  Using: Madurai Sungudi sample notes (pilot demo)\n")

    notes = SAMPLE_NOTES.read_text() if SAMPLE_NOTES.exists() else (
        "I wash silk in warm water, tie knots with cotton thread at chalk marks, dip in crimson dye for 20 minutes, then untie."
    )
    craft_name = "Madurai Sungudi"

    print("[Stage 1] Observer Agent →", end="", flush=True)
    t0 = time.time()
    from agents.observer_agent import ObserverAgent
    obs = ObserverAgent().analyze(notes[:800])
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {len(obs.get('visible_steps',[]))} steps | {len(obs.get('knowledge_gaps',[]))} gaps")

    print("[Stage 2] Interviewer Agent →", end="", flush=True)
    t0 = time.time()
    from agents.interviewer_agent import InterviewerAgent
    questions = InterviewerAgent().generate_questions(obs.get("knowledge_gaps", []), craft_name)
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {len(questions)} questions generated")
    for i, q in enumerate(questions[:3], 1):
        print(f"   Q{i}: {q[:90]}")

    print("[Stage 3] Knowledge Architect →", end="", flush=True)
    t0 = time.time()
    sample_qa = {questions[0]: "You feel the resistance in your fingertips when the knot is secure."} if questions else {}
    from agents.knowledge_architect import KnowledgeArchitectAgent
    fp_result = KnowledgeArchitectAgent().build_fingerprint(obs, sample_qa, craft_name, "Demo Artisan")
    fp = fp_result.get("fingerprint", fp_result)
    techniques = len(fp.get("techniques", [])) if isinstance(fp, dict) else 0
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {techniques} techniques in fingerprint")

    print("[Stage 4] Curriculum Agent →", end="", flush=True)
    t0 = time.time()
    from agents.curriculum_agent import CurriculumAgent
    lesson = CurriculumAgent().create_lesson(fp if isinstance(fp, dict) else {})
    steps = len(lesson.get("practice_steps", []))
    quiz  = len(lesson.get("quiz", []))
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {steps} practice steps | {quiz} quiz questions")

    print("\n✅ Full pipeline complete — live AI on Amazon Bedrock Nova Pro\n")
    return 0


# ---------------------------------------------------------------------------
# status — pre-submission env checklist (the former `check`)
# ---------------------------------------------------------------------------
def cmd_status(_args):
    _load_env()
    print("\n📋 SKILL DNA — Environment Status\n")
    checks = []

    try:
        import boto3
        boto3.client("sts").get_caller_identity()
        checks.append(("✅", "AWS credentials configured"))
    except Exception as e:
        checks.append(("❌", f"AWS credentials: {e}"))

    env_file = ROOT / ".env"
    checks.append(("✅" if env_file.exists() else "❌", ".env file exists"))

    dist = ROOT / "frontend" / "dist" / "index.html"
    checks.append(("✅" if dist.exists() else "⚠️", "React frontend built (frontend/dist/)"))

    cases = ROOT / "kit" / "cases" / "cases.jsonl"
    n = len(cases.read_text().splitlines()) if cases.exists() else 0
    checks.append(("✅" if n >= 5 else "⚠️", f"cases.jsonl: {n} signed cases"))

    measure = ROOT / "kit" / "results" / "MEASURE.md"
    checks.append(("✅" if measure.exists() else "⚠️", "MEASURE.md generated (run: python kit/ss.py bench)"))

    try:
        from agents.orchestrator import run_skill_capture_pipeline
        checks.append(("✅", "All Strands agents import cleanly"))
    except Exception as e:
        checks.append(("❌", f"Agent import error: {e}"))

    blocks = list(BLOCKS_DIR.glob("b*.py")) if BLOCKS_DIR.exists() else []
    checks.append(("✅" if len(blocks) >= 10 else "⚠️", f"strands-ship blocks: {len(blocks)} available"))

    readme = ROOT / "README.md"
    checks.append(("✅" if readme.exists() else "❌", "README.md exists"))

    for icon, msg in checks:
        print(f"  {icon}  {msg}")

    passed = sum(1 for i, _ in checks if i == "✅")
    print(f"\n  {passed}/{len(checks)} environment checks passed\n")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
COMMANDS = {
    "bench": cmd_bench,
    "measure": cmd_measure,
    "video": cmd_video,
    "article": cmd_article,
    "check": cmd_check,
    "status": cmd_status,
    "bedrock": cmd_bedrock,
    "blocks": cmd_blocks,
    "block": cmd_block,
    "pipeline": cmd_pipeline,
}


def main():
    ap = argparse.ArgumentParser(
        prog="python kit/ss.py",
        description="SKILL DNA automation CLI (strands-ship pattern)",
    )
    sub = ap.add_subparsers(dest="cmd")

    mp = sub.add_parser("measure", help="Alias for bench")
    mp.add_argument("--limit", type=int, help="Limit number of cases")

    bp = sub.add_parser("bench", help="Score all signed cases -> results.json + MEASURE.md")
    bp.add_argument("--limit", type=int, help="Limit number of cases")

    vp = sub.add_parser("video", help="Record the live demo video")
    vp.add_argument("--target", default="local", help="local (default); agentcore not supported by this kit")
    vp.add_argument("--url", default="http://localhost:8000", help="URL of the running app (default: http://localhost:8000)")
    vp.add_argument("--dry-run", action="store_true", help="Show scenes without recording")

    sub.add_parser("article", help="Generate the honest-numbers article + FACTS.md")
    sub.add_parser("check", help="Verify all submission artifacts are present")
    sub.add_parser("status", help="Pre-submission environment checklist")

    sub.add_parser("bedrock", help="Verify AWS + Bedrock credentials")
    sub.add_parser("blocks", help="List available Strands blocks")
    blp = sub.add_parser("block", help="Run a Strands block live")
    blp.add_argument("name", nargs="?", help="Block name (e.g. sessions, graph, hooks)")
    sub.add_parser("pipeline", help="Run live end-to-end SKILL DNA pipeline")

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        return 0

    fn = COMMANDS.get(args.cmd)
    if not fn:
        print(f"Unknown command: {args.cmd}")
        ap.print_help()
        return 1

    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
