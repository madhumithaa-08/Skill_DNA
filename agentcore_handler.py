"""
SKILL DNA — Amazon Bedrock AgentCore Runtime Handler

Implements the AgentCore protocol:
  GET  /ping         → {"status": "ok"}
  POST /invocations  → runs the Observer + Interviewer pipeline

AgentCore sends POST /invocations with a JSON body.
This handler runs the SKILL DNA multi-agent pipeline and returns structured JSON.

Input schema:
  {
    "input": "artisan description text",
    "craft_name": "Madurai Sungudi",   (optional)
    "artisan_name": "Meenakshi Ammal", (optional)
    "mode": "observe" | "full"          (optional, default "observe")
  }

Output schema:
  {
    "observation": {...},
    "questions": [...],
    "fingerprint": {...},   (only in "full" mode)
    "lesson": {...},         (only in "full" mode)
    "pipeline_status": {...},
    "is_demo": bool
  }
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="SKILL DNA AgentCore Handler",
    description="Amazon Bedrock AgentCore runtime for the SKILL DNA multi-agent pipeline",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Demo fallback data
# ---------------------------------------------------------------------------
DEMO_OBSERVATION = {
    "visible_steps": [
        "Wash silk in warm water until evenly damp",
        "Mark tying points with chalk in a grid pattern",
        "Pinch fabric peak and wrap thread tightly 3 times",
        "Tie double knot and cut thread close",
        "Submerge in heated dye bath for 20 minutes",
        "Untie all knots to reveal pattern",
    ],
    "tools_identified": ["Water basin", "Chalk / fabric marker", "Small scissors", "Dye vessel"],
    "materials_identified": ["Pure Madurai silk", "Natural crimson dye", "Cotton tying thread"],
    "knowledge_gaps": [
        "Tactile tension when wrapping knots (not visible)",
        "Visual & textural signs of dye saturation readiness",
        "Sensory indicators for fabric dampness vs oversaturation",
        "Error recovery methods when a knot bleeds dye",
    ],
}

DEMO_QUESTIONS = [
    "How do you know the knot tension is right — what does it feel like in your fingers?",
    "How do you test dye saturation without a thermometer?",
    "What does the silk feel like when it is ready for the next stage?",
    "How do you decide the spacing between knots for different patterns?",
    "What is the first sign that something has gone wrong?",
    "How long did it take to develop the feel for correct knot tension?",
]

# ---------------------------------------------------------------------------
# AgentCore protocol endpoints
# ---------------------------------------------------------------------------

@app.get("/ping")
def ping():
    """AgentCore health check — must return 200."""
    return {"status": "ok", "service": "SKILL DNA", "version": "1.0.0"}


class InvocationRequest(BaseModel):
    input: str = ""
    craft_name: str = "Madurai Sungudi"
    artisan_name: str = "Meenakshi Ammal"
    mode: str = "observe"


@app.post("/invocations")
async def invocations(request: Request):
    """
    AgentCore invocation endpoint.
    Runs the SKILL DNA pipeline on the provided artisan description.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    artisan_input = body.get("input", "")
    craft_name = body.get("craft_name", "Madurai Sungudi")
    artisan_name = body.get("artisan_name", "Meenakshi Ammal")
    mode = body.get("mode", "observe")

    if not artisan_input:
        # Load sample notes as default
        sample = Path("data/sample_sungudi_notes.txt")
        if sample.exists():
            artisan_input = sample.read_text()[:800]

    try:
        # Stage 1: Observer
        from agents.observer_agent import ObserverAgent
        observation = ObserverAgent().analyze(artisan_input)

        # Stage 2: Interviewer
        from agents.interviewer_agent import InterviewerAgent
        gaps = observation.get("knowledge_gaps", [])
        questions = InterviewerAgent().generate_questions(gaps, craft_name)

        result = {
            "observation": observation,
            "questions": questions,
            "pipeline_status": {"stages": ["observer", "interviewer"], "mode": "live"},
            "is_demo": False,
            "craft_name": craft_name,
            "artisan_name": artisan_name,
        }

        if mode == "full":
            from agents.knowledge_architect import KnowledgeArchitectAgent
            from agents.curriculum_agent import CurriculumAgent
            fp = KnowledgeArchitectAgent().build_fingerprint(observation, {}, craft_name, artisan_name)
            lesson = CurriculumAgent().create_lesson(fp.get("fingerprint", fp))
            result["fingerprint"] = fp.get("fingerprint", fp)
            result["lesson"] = lesson
            result["pipeline_status"]["stages"] += ["knowledge_architect", "curriculum"]

        return JSONResponse(content=result)

    except Exception as exc:
        # Graceful fallback to demo data
        return JSONResponse(content={
            "observation": DEMO_OBSERVATION,
            "questions": DEMO_QUESTIONS,
            "pipeline_status": {"stages": ["demo_fallback"], "error": str(exc)[:200]},
            "is_demo": True,
            "craft_name": craft_name,
            "artisan_name": artisan_name,
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agentcore_handler:app", host="0.0.0.0", port=8080, reload=False)
