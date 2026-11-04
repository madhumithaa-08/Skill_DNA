"""
SKILL DNA automation CLI — mirrors the strands-ship `ss` commands.

Commands:
    python kit/ss.py bedrock          — verify AWS + Bedrock are working
    python kit/ss.py blocks           — list available Strands blocks
    python kit/ss.py block <name>     — run one block live (e.g. block sessions)
    python kit/ss.py pipeline         — run the live Observer → Curriculum pipeline on Sungudi sample
    python kit/ss.py measure          — run SKILL DNA vs baseline on cases.jsonl
    python kit/ss.py check            — pre-submission checklist

Usage:
    python kit/ss.py <command> [args]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
BLOCKS_DIR = ROOT / "kit" / "strands-ship" / "kit" / "blocks"
SAMPLE_NOTES = ROOT / "data" / "sample_sungudi_notes.txt"

sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# bedrock
# ---------------------------------------------------------------------------
def cmd_bedrock(_args):
    print("\n🔍 Checking AWS + Bedrock credentials...\n")
    import boto3, os
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
    # Find matching block file
    matches = list(BLOCKS_DIR.glob(f"*{name}*.py"))
    matches = [m for m in matches if not m.name.startswith("_")]
    if not matches:
        print(f"❌ Block '{args.name}' not found. Run `python kit/ss.py blocks` to list.")
        return 1
    block_file = matches[0]
    print(f"\n▶ Running block: {block_file.name}\n")

    env = {**__import__("os").environ, "PYTHONPATH": str(BLOCKS_DIR)}
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
    from dotenv import load_dotenv
    load_dotenv()

    print("\n🧬 SKILL DNA — Live Pipeline Run\n")
    print("  Using: Madurai Sungudi sample notes (pilot demo)\n")

    notes = SAMPLE_NOTES.read_text() if SAMPLE_NOTES.exists() else (
        "I wash silk in warm water, tie knots with cotton thread at chalk marks, dip in crimson dye for 20 minutes, then untie."
    )
    craft_name = "Madurai Sungudi"  # demo craft — the platform works with any craft

    # Stage 1
    print("[Stage 1] Observer Agent →", end="", flush=True)
    t0 = time.time()
    from agents.observer_agent import ObserverAgent
    obs = ObserverAgent().analyze(notes[:800])
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {len(obs.get('visible_steps',[]))} steps | {len(obs.get('knowledge_gaps',[]))} gaps")

    # Stage 2
    print("[Stage 2] Interviewer Agent →", end="", flush=True)
    t0 = time.time()
    from agents.interviewer_agent import InterviewerAgent
    questions = InterviewerAgent().generate_questions(obs.get("knowledge_gaps", []), craft_name)
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {len(questions)} questions generated")
    for i, q in enumerate(questions[:3], 1):
        print(f"   Q{i}: {q[:90]}")

    # Stage 3
    print("[Stage 3] Knowledge Architect →", end="", flush=True)
    t0 = time.time()
    sample_qa = {questions[0]: "You feel the resistance in your fingertips when the knot is secure."} if questions else {}
    from agents.knowledge_architect import KnowledgeArchitectAgent
    fp_result = KnowledgeArchitectAgent().build_fingerprint(obs, sample_qa, craft_name, "Demo Artisan")
    fp = fp_result.get("fingerprint", fp_result)
    techniques = len(fp.get("techniques", [])) if isinstance(fp, dict) else 0
    print(f" ✅ {int((time.time()-t0)*1000)}ms | {techniques} techniques in fingerprint")

    # Stage 4
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
# measure
# ---------------------------------------------------------------------------
def cmd_measure(args):
    from dotenv import load_dotenv
    load_dotenv()
    import importlib.util, sys as _sys
    spec = importlib.util.spec_from_file_location("measure", ROOT / "kit" / "measure.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    limit = ["--limit", str(args.limit)] if getattr(args, "limit", None) else []
    return mod.main(limit)


# ---------------------------------------------------------------------------
# check — pre-submission checklist
# ---------------------------------------------------------------------------
def cmd_check(_args):
    from dotenv import load_dotenv
    load_dotenv()

    print("\n📋 SKILL DNA — Submission Checklist\n")
    checks = []

    # AWS
    try:
        import boto3
        boto3.client("sts").get_caller_identity()
        checks.append(("✅", "AWS credentials configured"))
    except Exception as e:
        checks.append(("❌", f"AWS credentials: {e}"))

    # .env
    env_file = ROOT / ".env"
    checks.append(("✅" if env_file.exists() else "❌", ".env file exists"))

    # Frontend build
    dist = ROOT / "frontend" / "dist" / "index.html"
    checks.append(("✅" if dist.exists() else "⚠️", "React frontend built (frontend/dist/)"))

    # cases.jsonl
    cases = ROOT / "kit" / "cases" / "cases.jsonl"
    n = len(cases.read_text().splitlines()) if cases.exists() else 0
    checks.append(("✅" if n >= 5 else "⚠️", f"cases.jsonl: {n} signed cases"))

    # MEASURE.md
    measure = ROOT / "kit" / "results" / "MEASURE.md"
    checks.append(("✅" if measure.exists() else "⚠️", "MEASURE.md generated (run: python kit/ss.py measure)"))

    # agents importable
    try:
        from agents.orchestrator import run_skill_capture_pipeline
        checks.append(("✅", "All Strands agents import cleanly"))
    except Exception as e:
        checks.append(("❌", f"Agent import error: {e}"))

    # strands-ship blocks
    blocks = list(BLOCKS_DIR.glob("b*.py")) if BLOCKS_DIR.exists() else []
    checks.append(("✅" if len(blocks) >= 10 else "⚠️", f"strands-ship blocks: {len(blocks)} available"))

    # README
    readme = ROOT / "README.md"
    checks.append(("✅" if readme.exists() else "❌", "README.md exists"))

    # demo script
    demo = ROOT / "demo" / "sungudi_demo_script.md"
    checks.append(("✅" if demo.exists() else "⚠️", "Demo script exists"))

    required_items = [
        ("❓", "Builder Center article (write after testing)"),
        ("❓", "GitHub public repo (push to GitHub)"),
        ("❓", "Demo video under 3 minutes (record from live run)"),
        ("❓", "Workshop completion on Builder Center"),
    ]

    for icon, msg in checks:
        print(f"  {icon}  {msg}")

    print()
    for icon, msg in required_items:
        print(f"  {icon}  {msg}")

    print()
    passed = sum(1 for i, _ in checks if i == "✅")
    print(f"  {passed}/{len(checks)} automated checks passed\n")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
COMMANDS = {
    "bedrock": cmd_bedrock,
    "blocks": cmd_blocks,
    "block": cmd_block,
    "pipeline": cmd_pipeline,
    "measure": cmd_measure,
    "check": cmd_check,
}


def main():
    ap = argparse.ArgumentParser(
        prog="python kit/ss.py",
        description="SKILL DNA automation CLI (strands-ship pattern)",
    )
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("bedrock", help="Verify AWS + Bedrock credentials")
    sub.add_parser("blocks", help="List available Strands blocks")
    bp = sub.add_parser("block", help="Run a Strands block live")
    bp.add_argument("name", nargs="?", help="Block name (e.g. sessions, graph, hooks)")
    sub.add_parser("pipeline", help="Run live end-to-end SKILL DNA pipeline")
    mp = sub.add_parser("measure", help="Run SKILL DNA vs baseline measurement")
    mp.add_argument("--limit", type=int, help="Limit number of cases")
    sub.add_parser("check", help="Pre-submission checklist")

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
