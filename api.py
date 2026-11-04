"""
SKILL DNA — FastAPI Backend Service.
Provides RESTful endpoints for the multi-agent skill capture pipeline,
fingerprint persistence, demo mock data, and curriculum modules.
Also serves the compiled React frontend from frontend/dist/.

Run with:
    python -m uvicorn api:app --reload --port 8000
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FINGERPRINTS_DIR = BASE_DIR / "data" / "skill_fingerprints"
SAMPLE_NOTES_PATH = BASE_DIR / "data" / "sample_sungudi_notes.txt"

app = FastAPI(
    title="SKILL DNA API",
    description="Backend API for AI-Powered Traditional Craft Knowledge Preservation",
    version="1.0.0",
)

# Allow CORS for React frontend (default Vite port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Demo data generators (Graceful fallback when AWS Bedrock is not configured)
# ---------------------------------------------------------------------------

def get_demo_fingerprint(craft_name: str = "Madurai Sungudi", artisan_name: str = "Meenakshi Ammal") -> Dict[str, Any]:
    return {
        "craft_name": craft_name,
        "craft_origin": "Madurai, Tamil Nadu, India",
        "craft_heritage": "Geographical Indication (GI) Tag craft of Tamil Nadu",
        "artisan_name": artisan_name or "Meenakshi Ammal",
        "artisan_approved": True,
        "cultural_significance": (
            "Madurai Sungudi is a 2000-year-old tie-dye tradition woven into Tamil cultural "
            "identity. The fabric is considered auspicious and is worn at weddings, temple "
            "festivals, and coming-of-age ceremonies. Each pattern carries regional meaning — "
            "the woven borders signify prosperity, while the central motifs represent the "
            "lotus of creation."
        ),
        "materials": [
            {
                "name": "Sungudi Silk",
                "description": "Fine pure silk handwoven in Madurai — lightweight with a natural lustre",
                "source": "Local Madurai weavers",
            },
            {
                "name": "Natural Dye",
                "description": "Vegetable-based dyes in traditional colours: deep indigo, saffron, and crimson",
                "source": "Natural plant sources — indigo plant, marigold, and pomegranate rind",
            },
            {
                "name": "Tying Thread",
                "description": "Strong cotton thread used to resist dye penetration at the knot points",
                "source": "Local thread suppliers",
            },
            {
                "name": "Chalk / Fabric Marker",
                "description": "Used to mark tying points in a grid before the tying stage",
                "source": "Craft supply shops",
            },
        ],
        "techniques": [
            {
                "name": "Fabric Preparation",
                "stage": "Stage 1",
                "description": "Wash silk in warm water to remove starch, then spread evenly and check for uniform dampness.",
                "duration_estimate": "20 minutes",
                "difficulty": "beginner",
                "tips": [
                    "Water must be warm, not hot — test with your wrist",
                    "Silk should feel uniformly heavy and damp, not dry in patches",
                    "Wring from one end, never twist randomly",
                ],
            },
            {
                "name": "Pattern Marking",
                "stage": "Stage 2",
                "description": "Mark tying points on the fabric with chalk or a fabric marker in a geometric grid.",
                "duration_estimate": "30 minutes",
                "difficulty": "beginner",
                "tips": [
                    "Use a light touch — marks must wash out later",
                    "Traditional patterns use grids spaced 1–2 cm apart",
                    "The spacing determines pattern density — tighter spacing = more detail",
                ],
            },
            {
                "name": "Tying (Bandhani)",
                "stage": "Stage 3",
                "description": (
                    "Pinch fabric at each marked point between thumb and index finger, "
                    "pull up a small peak, and wrap tightly with thread at least 3 times. "
                    "Tie off with a double knot."
                ),
                "duration_estimate": "2–3 hours",
                "difficulty": "advanced",
                "tips": [
                    "Pinch size must be consistent — a good pinch is 3–4 mm across",
                    "Thread must circle at least 3 times to resist dye",
                    "Pull each wrap firmly — you should feel slight resistance",
                    "Masters develop a rhythm: 500 knots per hour is achievable",
                ],
            },
            {
                "name": "Dyeing",
                "stage": "Stage 4",
                "description": "Immerse the tied fabric in a heated dye bath for 20 minutes, monitoring colour saturation.",
                "duration_estimate": "30 minutes",
                "difficulty": "intermediate",
                "tips": [
                    "Dye bath should be hot but not boiling — 80–85°C",
                    "Stir gently every 5 minutes for even penetration",
                    "Colour will appear 2–3 shades darker wet than when dry",
                ],
            },
            {
                "name": "Untying and Reveal",
                "stage": "Stage 5",
                "description": "Cut and remove all thread knots, then rinse and dry the fabric to reveal the pattern.",
                "duration_estimate": "45 minutes",
                "difficulty": "beginner",
                "tips": [
                    "Use small scissors — cut the thread, not the fabric",
                    "Listen for the soft 'snap' of thread releasing — that sound means a crisp circle",
                    "Rinse in cool water to set the colour",
                ],
            },
        ],
        "decisions": [
            {
                "decision_point": "Knot tightness",
                "options": ["Tight", "Medium", "Loose"],
                "artisan_choice": "Tight",
                "reasoning": "Tight knots create crisp white circles; loose knots let dye bleed through, producing grey smudges.",
            },
            {
                "decision_point": "Dye bath duration",
                "options": ["10 minutes", "20 minutes", "30+ minutes"],
                "artisan_choice": "20 minutes",
                "reasoning": "20 minutes achieves full colour saturation without weakening the silk fibres.",
            },
            {
                "decision_point": "Fabric moisture at tying",
                "options": ["Dry fabric", "Damp fabric", "Wet fabric"],
                "artisan_choice": "Damp fabric",
                "reasoning": "Damp fibres are pliable for even tying and ensure uniform dye uptake at later stages.",
            },
        ],
        "common_mistakes": [
            {
                "mistake": "Uneven fabric dampness before tying",
                "consequence": "Dry patches absorb more dye than damp sections, creating an uneven pattern",
                "correction": "Re-soak and wring evenly before beginning the tying stage",
            },
            {
                "mistake": "Loose knots",
                "consequence": "Dye bleeds through the knot — no crisp white circles appear",
                "correction": "Always test one knot by pulling the thread firmly before proceeding with the whole fabric",
            },
            {
                "mistake": "Inconsistent pinch size",
                "consequence": "Circles are different sizes, breaking the geometric pattern",
                "correction": "Practice on a test fabric until pinch size is consistent before starting the real piece",
            },
        ],
        "mastery_requirements": [
            {
                "skill": "Consistent knot tension",
                "how_to_demonstrate": "Tie 100 knots on test fabric — all resulting circles must be the same size after dyeing",
            },
            {
                "skill": "Dye timing intuition",
                "how_to_demonstrate": "Correctly identify fabric readiness by texture and colour without checking a clock",
            },
            {
                "skill": "Pattern planning",
                "how_to_demonstrate": "Mark and tie a 10×10 grid that produces a perfectly symmetrical pattern",
            },
        ],
        "created_at": datetime.utcnow().isoformat(),
        "version": "1.0",
    }


def get_demo_lesson(craft_name: str = "Madurai Sungudi") -> Dict[str, Any]:
    return {
        "title": f"Introduction to {craft_name}: The Art of Tied Resist Dyeing",
        "level": "beginner",
        "craft_name": craft_name,
        "overview": (
            "Madurai Sungudi is one of India's oldest textile traditions, dating back over "
            "2000 years. In this lesson, you will learn the foundational technique of tying — "
            "the heart of the Sungudi process. By the end, you will understand why each knot "
            "matters and how artisans develop their signature touch. This is not just a craft: "
            "it is a living conversation between the artisan, the silk, and 2000 years of "
            "Tamil cultural memory."
        ),
        "learning_objectives": [
            "Understand the cultural significance of Sungudi in Tamil Nadu",
            "Identify the four key materials used in Sungudi dyeing",
            "Demonstrate the correct fabric preparation technique",
            "Tie a basic Bandhani knot with consistent tension",
            "Recognise the signs of a well-dyed vs poorly-dyed Sungudi",
        ],
        "practice_steps": [
            {
                "step_number": 1,
                "instruction": (
                    "Fill a basin with warm water (not hot — you should be able to keep your hand "
                    "in it comfortably). Submerge the silk fabric and gently squeeze until fully "
                    "saturated throughout."
                ),
                "what_to_watch_for": (
                    "The fabric should feel uniformly heavy and damp — no dry patches when you "
                    "hold it up to the light."
                ),
                "common_mistakes": "Using hot water weakens silk fibres and causes uneven shrinkage.",
            },
            {
                "step_number": 2,
                "instruction": (
                    "Remove the fabric and gently wring from one end — never twist randomly. "
                    "Lay flat and check for even dampness before proceeding."
                ),
                "what_to_watch_for": (
                    "Fabric should glisten slightly but not drip. Fold it: it should leave a "
                    "slight damp mark on a dry surface."
                ),
                "common_mistakes": "Over-wringing creates dry patches that absorb dye differently.",
            },
            {
                "step_number": 3,
                "instruction": (
                    "Using chalk or a fabric marker, mark your tying points in a grid pattern. "
                    "Traditional Sungudi uses rows spaced 1–2 cm apart."
                ),
                "what_to_watch_for": (
                    "Marks should be light — they will wash out. The grid spacing determines "
                    "your pattern density."
                ),
                "common_mistakes": "Pressing too hard leaves permanent marks or weakens the silk.",
            },
            {
                "step_number": 4,
                "instruction": (
                    "Pinch the fabric at the first marked point between thumb and index finger, "
                    "pulling up a small peak of 3–4 mm. Wrap your thread around the base of "
                    "this peak at least 3 times, pulling firmly with each wrap."
                ),
                "what_to_watch_for": (
                    "The wrapped thread should feel taut — you should feel slight resistance "
                    "when you pull the knot. That resistance is the dye barrier."
                ),
                "common_mistakes": "Pinching too much fabric creates large blobs instead of crisp circles.",
            },
            {
                "step_number": 5,
                "instruction": (
                    "Tie off with a double knot and cut, leaving 2 cm of thread. Move to the "
                    "next marked point and repeat. Develop a rhythm — masters tie 500 knots "
                    "per hour."
                ),
                "what_to_watch_for": (
                    "All knots should feel the same tension when you roll them between your "
                    "fingers. Inconsistency now means irregular circles later."
                ),
                "common_mistakes": "Inconsistent pinch size creates irregular circle sizes in the final fabric.",
            },
        ],
        "quiz": [
            {
                "question": "Why must the Sungudi fabric be damp (not dry) before tying?",
                "options": [
                    "To make tying easier on the fingers",
                    "Damp fibres are more pliable and accept even dye penetration later",
                    "Dry fabric cannot hold knots",
                    "It is a traditional ritual with no practical reason",
                ],
                "correct_answer": "Damp fibres are more pliable and accept even dye penetration later",
                "explanation": (
                    "Damp silk fibres are softer and more elastic, making even tying easier. "
                    "More importantly, the moisture state at tying time affects how the dye "
                    "later penetrates the fabric — uniform dampness means uniform colour."
                ),
            },
            {
                "question": "What is the minimum number of times thread should be wrapped around a Sungudi knot?",
                "options": ["1 time", "2 times", "3 times", "5 times"],
                "correct_answer": "3 times",
                "explanation": (
                    "Three wraps creates sufficient resistance to prevent dye penetration at "
                    "the knot point. Fewer wraps and the dye bleeds through, producing grey "
                    "smudges instead of crisp white circles."
                ),
            },
            {
                "question": "How do master artisans know a Sungudi knot has the right tension?",
                "options": [
                    "They use a tension gauge",
                    "They count the number of wraps precisely",
                    "They develop a tactile sense through years of practice",
                    "They check with their eyes",
                ],
                "correct_answer": "They develop a tactile sense through years of practice",
                "explanation": (
                    "Tacit knowledge is central to craft mastery. The artisan's fingertips "
                    "learn to recognise the exact resistance that means 'this knot will produce "
                    "a perfect circle'. This cannot be taught by measurement alone — it "
                    "requires practice."
                ),
            },
            {
                "question": "What happens if the fabric has dry patches when you begin tying?",
                "options": [
                    "Nothing — it does not matter",
                    "The dry patches absorb more dye, creating darker areas",
                    "The dry areas completely resist dye",
                    "The knots will not hold in dry areas",
                ],
                "correct_answer": "The dry patches absorb more dye, creating darker areas",
                "explanation": (
                    "Dry silk fibres are more absorbent than wet fibres. When the dye bath "
                    "is applied, dry patches absorb more colour, creating an uneven tie-dye "
                    "pattern that is not traditional Sungudi."
                ),
            },
            {
                "question": "Why is Sungudi considered a GI Tag (Geographical Indication) craft?",
                "options": [
                    "Because it can only be made using machines in Madurai",
                    "Because the specific combination of local silk, local dyes, and generational technique is unique to Madurai",
                    "Because the government registered it for taxation purposes",
                    "Because it uses the most expensive silk in India",
                ],
                "correct_answer": "Because the specific combination of local silk, local dyes, and generational technique is unique to Madurai",
                "explanation": (
                    "A GI Tag legally recognises that a product's quality, reputation, or "
                    "characteristics are essentially due to its geographic origin. Madurai "
                    "Sungudi's GI Tag protects the unique combination of Madurai's fine silk, "
                    "traditional natural dyes, and the tied-and-dyed technique passed through "
                    "generations of artisan families."
                ),
            },
        ],
        "estimated_duration_minutes": 45,
    }


DEMO_QUESTIONS = [
    "How tight should the knots be — and how do you test the tightness without breaking the thread?",
    "How do you know the dye has fully penetrated the fabric before removing from the bath?",
    "What does the fabric feel like when it is ready for the next stage vs when it needs more time?",
    "How do you decide the spacing between knots for different patterns?",
    "What is the first sign that something has gone wrong in the dyeing process?",
    "How long did it take you to develop the feel for the correct knot tension?",
]

DEMO_OBSERVATION = {
    "visible_steps": [
        "Fabric washing in warm water and uniform damp check",
        "Grid marking with chalk at 1.5cm spacing",
        "Pinching 3-4mm fabric peak and wrapping cotton thread tightly 3 times",
        "Double knot tying and trimming thread",
        "Submerging tied fabric in 80-85°C natural crimson dye bath for 20 minutes",
        "Cool water rinsing and careful knot cutting/untying",
    ],
    "tools_identified": [
        "Water basin",
        "Chalk / fabric marker",
        "Small precision scissors",
        "Wooden dye stirrer",
        "Dye vessel / heating element",
    ],
    "materials_identified": [
        "Pure Madurai silk",
        "Natural pomegranate rind crimson dye",
        "Strong cotton tying thread",
        "Warm water",
    ],
    "knowledge_gaps": [
        "Tactile tension and muscle resistance when wrapping the knot",
        "Visual & textural signs of dye saturation readiness",
        "Sensory indicators for fabric dampness vs oversaturation",
        "Error recovery methods when a knot bleeds dye",
    ],
}

# ---------------------------------------------------------------------------
# API Request / Response Schemas
# ---------------------------------------------------------------------------

class ObserveRequest(BaseModel):
    description: str
    craft_name: Optional[str] = "Madurai Sungudi"
    artisan_name: Optional[str] = "Meenakshi Ammal"


class InterviewRequest(BaseModel):
    knowledge_gaps: List[str]
    craft_name: Optional[str] = "Madurai Sungudi"


class FingerprintRequest(BaseModel):
    observation: Dict[str, Any]
    answers: Dict[str, str]
    craft_name: Optional[str] = "Madurai Sungudi"
    artisan_name: Optional[str] = "Meenakshi Ammal"


class RunAllRequest(BaseModel):
    description: str
    craft_name: str = "Madurai Sungudi"
    artisan_name: str = "Meenakshi Ammal"
    answers: Dict[str, str] = Field(default_factory=dict)


class LearnerSessionRequest(BaseModel):
    learner_id: str
    message:    str
    craft_name: str = "Traditional Craft"
    quiz_score: Optional[int] = None
    total_questions: Optional[int] = None
    completed_steps: Optional[List[int]] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Health check — reports all integrated AWS services."""
    services = {
        "bedrock":    "configured",
        "s3":         "unknown",
        "dynamodb":   "unknown",
        "transcribe": "unknown",
        "polly":      "unknown",
    }
    try:
        import boto3
        boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION","us-east-1")).list_buckets()
        services["s3"] = "ok"
    except Exception:
        services["s3"] = "error"
    try:
        import boto3
        boto3.client("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION","us-east-1")).list_tables(Limit=1)
        services["dynamodb"] = "ok"
    except Exception:
        services["dynamodb"] = "error"
    try:
        import boto3
        boto3.client("transcribe", region_name=os.environ.get("AWS_DEFAULT_REGION","us-east-1")).list_transcription_jobs(MaxResults=1)
        services["transcribe"] = "ok"
    except Exception:
        services["transcribe"] = "error"
    try:
        import boto3
        boto3.client("polly", region_name=os.environ.get("AWS_DEFAULT_REGION","us-east-1")).describe_voices(LanguageCode="en-IN")
        services["polly"] = "ok"
    except Exception:
        services["polly"] = "error"

    return {
        "status":    "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service":   "SKILL DNA API",
        "version":   "2.0.0",
        "aws_services": services,
    }


@app.get("/api/sample-notes")
def get_sample_notes():
    """Retrieve sample artisan notes for Madurai Sungudi."""
    if SAMPLE_NOTES_PATH.exists():
        content = SAMPLE_NOTES_PATH.read_text(encoding="utf-8")
        return {
            "success": True,
            "craft_name": "Madurai Sungudi",
            "artisan_name": "Meenakshi Ammal",
            "notes": content,
        }
    raise HTTPException(status_code=404, detail="Sample notes file not found")


@app.get("/api/demo/data")
def get_demo_data(craft_name: str = "Madurai Sungudi", artisan_name: str = "Meenakshi Ammal"):
    """Return pre-generated rich demo data for instant UI exploration."""
    return {
        "success": True,
        "is_demo": True,
        "observation": DEMO_OBSERVATION,
        "questions": DEMO_QUESTIONS,
        "fingerprint": get_demo_fingerprint(craft_name, artisan_name),
        "lesson": get_demo_lesson(craft_name),
    }


@app.post("/api/pipeline/observe")
def run_observer_agent(req: ObserveRequest):
    """Run Observer Agent on craft demonstration text."""
    try:
        from agents.observer_agent import ObserverAgent
        observer = ObserverAgent()
        observation = observer.analyze(req.description)
        return {
            "success": True,
            "is_demo": False,
            "observation": observation,
        }
    except Exception as exc:
        # Fall back gracefully to rich demo observation
        return {
            "success": True,
            "is_demo": True,
            "note": f"Falling back to demo observation data: {exc}",
            "observation": DEMO_OBSERVATION,
        }


@app.post("/api/pipeline/interview")
def run_interviewer_agent(req: InterviewRequest):
    """Run Interviewer Agent to generate questions for identified gaps."""
    try:
        from agents.interviewer_agent import InterviewerAgent
        interviewer = InterviewerAgent()
        questions = interviewer.generate_questions(req.knowledge_gaps, req.craft_name or "Craft")
        return {
            "success": True,
            "is_demo": False,
            "questions": questions,
        }
    except Exception as exc:
        return {
            "success": True,
            "is_demo": True,
            "note": f"Falling back to demo questions: {exc}",
            "questions": DEMO_QUESTIONS,
        }


@app.post("/api/pipeline/fingerprint")
def create_fingerprint(req: FingerprintRequest):
    """Synthesize Skill Fingerprint, save to S3, index in DynamoDB, generate lesson."""
    craft_name   = req.craft_name   or "Traditional Craft"
    artisan_name = req.artisan_name or "Master Artisan"

    try:
        from agents.knowledge_architect import KnowledgeArchitectAgent
        from agents.curriculum_agent import CurriculumAgent

        architect   = KnowledgeArchitectAgent()
        fp_result   = architect.build_fingerprint(req.observation, req.answers, craft_name, artisan_name)
        fingerprint = fp_result.get("fingerprint", fp_result)

        curriculum  = CurriculumAgent()
        lesson      = curriculum.create_lesson(fingerprint if isinstance(fingerprint, dict) else {})

        # --- Save to Amazon S3 ---
        s3_result = {"status": "skipped"}
        try:
            from services.s3_service import save_fingerprint_to_s3, list_fingerprints_in_s3
            s3_result = save_fingerprint_to_s3(fingerprint, craft_name)
        except Exception as s3_err:
            s3_result = {"status": "error", "error": str(s3_err)}

        # --- Index in DynamoDB ---
        ddb_result = {"status": "skipped"}
        try:
            from services.dynamodb_service import index_fingerprint
            ddb_result = index_fingerprint(fingerprint, s3_result.get("s3_uri", ""))
        except Exception as ddb_err:
            ddb_result = {"status": "error", "error": str(ddb_err)}

        return {
            "success":    True,
            "is_demo":    False,
            "fingerprint": fingerprint,
            "lesson":     lesson,
            "s3":         s3_result,
            "dynamodb":   ddb_result,
        }
    except Exception as exc:
        demo_fp  = get_demo_fingerprint(craft_name, artisan_name)
        demo_les = get_demo_lesson(craft_name)
        return {
            "success":    True,
            "is_demo":    True,
            "note":       f"Falling back to demo: {exc}",
            "fingerprint": demo_fp,
            "lesson":     demo_les,
            "s3":         {"status": "demo"},
            "dynamodb":   {"status": "demo"},
        }


@app.post("/api/pipeline/run-all")
def run_all_pipeline(req: RunAllRequest):
    """Run the complete end-to-end multi-agent pipeline."""
    try:
        from agents.orchestrator import run_skill_capture_pipeline
        result = run_skill_capture_pipeline(
            artisan_description=req.description,
            craft_name=req.craft_name,
            artisan_name=req.artisan_name,
            artisan_qa=req.answers,
        )
        if result.get("success"):
            return {
                "success": True,
                "is_demo": False,
                **result,
            }
        raise RuntimeError(result.get("error", "Pipeline failed"))
    except Exception as exc:
        demo_fp = get_demo_fingerprint(req.craft_name, req.artisan_name)
        demo_les = get_demo_lesson(req.craft_name)
        return {
            "success": True,
            "is_demo": True,
            "note": f"Using demo pipeline result: {exc}",
            "fingerprint": demo_fp,
            "lesson": demo_les,
            "questions_asked": DEMO_QUESTIONS,
            "pipeline_status": {"stages": [{"stage": "all", "status": "demo_fallback"}]},
        }


@app.get("/api/fingerprints")
def list_fingerprints():
    """List all saved Skill Fingerprints — from DynamoDB index (S3 is source of truth)."""
    # Try DynamoDB index first
    try:
        from services.dynamodb_service import list_all_fingerprints_index
        items = list_all_fingerprints_index()
        if items:
            return {"success": True, "source": "dynamodb", "fingerprints": items}
    except Exception:
        pass

    # Fallback: S3 listing
    try:
        from services.s3_service import list_fingerprints_in_s3
        items = list_fingerprints_in_s3()
        if items:
            return {"success": True, "source": "s3", "fingerprints": items}
    except Exception:
        pass

    # Last resort: local files
    results = []
    if FINGERPRINTS_DIR.exists():
        for f in sorted(FINGERPRINTS_DIR.glob("*.json"), reverse=True):
            try:
                content = json.loads(f.read_text(encoding="utf-8"))
                results.append({
                    "filename":        f.name,
                    "craft_name":      content.get("craft_name", "Unknown"),
                    "artisan_name":    content.get("artisan_name", "Unknown"),
                    "created_at":      content.get("created_at", ""),
                    "version":         content.get("version", "1.0"),
                    "materials_count": len(content.get("materials", [])),
                    "techniques_count":len(content.get("techniques", [])),
                })
            except Exception:
                continue
    return {"success": True, "source": "local", "fingerprints": results}


@app.get("/api/fingerprints/s3/{craft_name}")
def get_fingerprint_from_s3(craft_name: str):
    """Retrieve the latest Skill Fingerprint for a craft from Amazon S3."""
    try:
        from services.s3_service import load_fingerprint_from_s3
        result = load_fingerprint_from_s3(craft_name)
        if result["status"] == "loaded":
            return {"success": True, "source": "s3", "fingerprint": result["fingerprint"], "s3_uri": result["s3_uri"]}
        raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/fingerprints/{filename}")
def get_fingerprint_file(filename: str):
    """Retrieve a specific saved Skill Fingerprint JSON."""
    file_path = FINGERPRINTS_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Fingerprint file not found")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return {"success": True, "fingerprint": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {exc}")


@app.post("/api/learner/session")
def learner_session(req: LearnerSessionRequest):
    """
    Talk to the Mentor Agent (b08 sessions pattern) and save progress to DynamoDB.
    The agent remembers this learner's quiz history across calls.
    """
    # --- Save progress to DynamoDB ---
    ddb_result = {"status": "skipped"}
    if req.quiz_score is not None or req.completed_steps is not None:
        try:
            from services.dynamodb_service import save_learner_progress
            ddb_result = save_learner_progress(
                learner_id=req.learner_id,
                craft_name=req.craft_name,
                quiz_score=req.quiz_score,
                total_questions=req.total_questions,
                completed_steps=req.completed_steps,
            )
        except Exception as ddb_err:
            ddb_result = {"status": "error", "error": str(ddb_err)}

    # --- Mentor Agent with session memory ---
    try:
        from agents.orchestrator import get_learner_session_agent
        mentor   = get_learner_session_agent(req.learner_id)
        response = mentor(req.message)

        # Save mentor note to DynamoDB too
        if ddb_result.get("status") != "skipped":
            try:
                from services.dynamodb_service import save_learner_progress
                save_learner_progress(
                    req.learner_id, req.craft_name,
                    session_note=str(response)[:500],
                )
            except Exception:
                pass

        return {
            "success":    True,
            "is_demo":    False,
            "learner_id": req.learner_id,
            "response":   str(response),
            "dynamodb":   ddb_result,
        }
    except Exception as exc:
        return {
            "success":    True,
            "is_demo":    True,
            "learner_id": req.learner_id,
            "response":   f"Great work on your practice! Keep going — consistency is the key to mastery. ({exc})",
            "dynamodb":   ddb_result,
        }


@app.get("/api/learner/{learner_id}/progress")
def get_learner_progress(learner_id: str, craft_name: str = ""):
    """Get a learner's progress history from DynamoDB."""
    try:
        from services.dynamodb_service import get_learner_progress, get_all_learner_crafts
        if craft_name:
            data = get_learner_progress(learner_id, craft_name)
        else:
            data = {"crafts": get_all_learner_crafts(learner_id), "learner_id": learner_id}
        return {"success": True, "progress": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Amazon Transcribe — Artisan audio → text
# ---------------------------------------------------------------------------

@app.post("/api/transcribe/upload")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("en-IN"),
    artisan_name: str = Form("artisan"),
):
    """
    Accept an artisan audio recording and transcribe it to text.
    Supports Tamil (ta-IN, routed as en-IN with note) and Indian English (en-IN).
    The transcript replaces manual typing in the Artisan Studio.
    """
    try:
        from services.transcribe_service import transcribe_sync
        audio_bytes = await audio.read()
        result = transcribe_sync(
            audio_bytes=audio_bytes,
            filename=audio.filename or "artisan_recording.mp3",
            language=language,
            artisan_name=artisan_name,
            timeout_sec=120,
        )
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/transcribe/start")
async def start_transcription(
    audio: UploadFile = File(...),
    language: str = Form("en-IN"),
    artisan_name: str = Form("artisan"),
):
    """Start an async transcription job — returns job_name to poll later."""
    try:
        from services.transcribe_service import upload_audio_and_transcribe
        audio_bytes = await audio.read()
        result = upload_audio_and_transcribe(
            audio_bytes=audio_bytes,
            filename=audio.filename or "artisan_recording.mp3",
            language=language,
            artisan_name=artisan_name,
        )
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/transcribe/status/{job_name}")
def check_transcription_status(job_name: str):
    """Poll an async transcription job status."""
    try:
        from services.transcribe_service import get_transcription_result
        result = get_transcription_result(job_name, wait=False)
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Amazon Polly — Text → spoken lesson audio
# ---------------------------------------------------------------------------

@app.post("/api/polly/synthesize")
def synthesize_text(request: dict):
    """
    Convert any text to spoken audio using Amazon Polly (Indian English).
    Returns a presigned S3 URL valid for 1 hour.
    """
    text     = request.get("text", "")
    voice_id = request.get("voice_id", "Kajal")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    try:
        from services.polly_service import synthesize_speech
        result = synthesize_speech(text, voice_id=voice_id)
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/polly/lesson-step")
def synthesize_lesson_step_audio(step: dict):
    """
    Generate spoken audio for a complete practice step
    (instruction + sensory checkpoint + common mistake).
    """
    try:
        from services.polly_service import synthesize_lesson_step
        result = synthesize_lesson_step(step)
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/polly/voices")
def list_polly_voices():
    """List available Indian English voices in Amazon Polly."""
    try:
        from services.polly_service import get_available_voices
        voices = get_available_voices()
        return {"success": True, "voices": voices}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



# ---------------------------------------------------------------------------
# Serve compiled React frontend (must come AFTER all API routes)
# ---------------------------------------------------------------------------
_FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    @app.head("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = _FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        index = _FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Frontend not built. Run: cd frontend && npm run build")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
