# 🧬 SKILL DNA — Preserving Traditional Craft Knowledge with AI

> *The knowledge that lives in hands deserves to live forever.*

**Track:** Education · AWS Strands SDK Hackathon · November 2026  
**Pilot craft:** Madurai Sungudi, Tamil Nadu, India  
**Built by:** Madhumitha A

---

## The Problem

India has **6.46 million** handloom and handicraft artisan workers, **64% of them women** *(PIB, 2026)*. Madurai Sungudi — a 2,000-year-old tie-dye technique with a GI tag (December 12, 2005) — has fewer than **20 traditional hand-tiers remaining**, each earning roughly ₹600 (~$7) per sari for a week tying 4,500 knots *(The Hindu, 2019)*.

The real loss is not the object. It is the knowledge behind it.

> *"I can feel the resistance in my fingertips when the thread is secure. It is a small, firm tension — not so tight that the silk is damaged, but tight enough that no dye will pass through. My fingers know the motion by feel now."*  
> — Meenakshi Ammal, Sungudi master, Madurai

That sensory, embodied knowledge — muscle memory, timing, tactile judgment — cannot be captured by filming a demonstration. SKILL DNA was built to do something about it.

---

## What SKILL DNA Does

SKILL DNA uses a **multi-agent pipeline built on the Strands Agents SDK** to capture tacit craft knowledge and turn it into interactive learning experiences.

The core innovation is the **Observer → Interviewer feedback loop**: one agent watches the craft and flags what it *can't* see; the next agent asks questions about exactly those gaps. Missing knowledge becomes the next question.

```
Craft description
      ↓
  Observer Agent          ← extracts visible steps + knowledge_gaps[]
      ↓
  Interviewer Agent        ← asks targeted tacit-knowledge questions
      ↓
  Artisan answers
      ↓
Knowledge Architect       ← builds the Skill Fingerprint (JSON)
      ↓
  Curriculum Agent         ← builds the lesson + quiz
      ↓
  Learner Studio           ← learn, listen (Polly), take quizzes
      ↓
   Mentor Agent            ← remembers progress across sessions (DynamoDB)
```

**Measured result:** SKILL DNA's Observer→Interviewer loop generates **~30% tacit-knowledge questions** (sensory cues, muscle memory, decision-making). A one-prompt baseline averages **~0%** across the signed evaluation cases.

---

## Agent Architecture

```
Lead Orchestrator   (Agent.as_tool() composition)
      │
      ├── Observer Agent        agents/observer_agent.py
      ├── Interviewer Agent     agents/interviewer_agent.py
      ├── Knowledge Architect   agents/knowledge_architect.py
      ├── Curriculum Agent      agents/curriculum_agent.py
      └── Mentor Agent          agents/orchestrator.py → get_learner_session_agent()
```

The four capture-pipeline agents are wired as tools on the Lead Orchestrator using `Agent.as_tool()` — Strands' native multi-agent composition pattern. The Mentor is a separate session-backed agent on the learner side.

| Strands Pattern | Where |
|---|---|
| `Agent.as_tool()` | `agents/orchestrator.py` — specialist agents as tools on the orchestrator |
| `FileSessionManager` | Mentor Agent — persists learner memory across API calls |
| `SlidingWindowConversationManager` | Mentor Agent — keeps last 30 turns in context |
| `BeforeModelCallEvent` hook | Artisan approval check before fingerprint is published |

---

## AWS Services

All four AWS data services are real boto3 integrations (best-effort, graceful fallback), verified by execution against provisioned resources in `us-east-1`.

| Service | Role in SKILL DNA | Status |
|---|---|---|
| **Amazon Bedrock** (`amazon.nova-pro-v1:0`) | All five agents — observation, interviewing, knowledge synthesis, curriculum, mentoring | ✅ Live |
| **Amazon S3** | Skill Fingerprint persistence to `s3://skill-dna-fingerprints-902605180945/fingerprints/{craft}/{timestamp}.json` | ✅ Live |
| **Amazon DynamoDB** | Learner quiz scores, completed steps, mentor notes in `skill-dna-learner-progress` | ✅ Live |
| **Amazon Transcribe** | Artisan audio → text. Supports `en-IN` and `ta-IN` routing | ✅ Live |
| **Amazon Polly** | 🔊 Listen button on every practice step — Kajal (Indian English neural voice) | ✅ Live |

```
          ARTISAN
             │
       Audio / Notes
             │
             ▼
   Amazon Transcribe
             │
             ▼
      Observer Agent → knowledge_gaps[]
             │
             ▼
     Interviewer Agent → Artisan Answers
             │
             ▼
   Knowledge Architect → Skill Fingerprint
             │
   ┌─────────┴──────────┐
   ▼                    ▼
Amazon S3         Curriculum Agent → Learner
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Amazon Polly          Amazon DynamoDB
             └──────────┬──────────┘
                        ▼
                   Mentor Agent
```

---

## The Skill Fingerprint

The central knowledge artifact — a versioned, artisan-approved JSON that captures:

**what to do + how to judge + what to feel + what can go wrong + how an expert recovers**

```json
{
  "craft_name": "Madurai Sungudi",
  "craft_origin": "Madurai, Tamil Nadu, India",
  "craft_heritage": "Geographical Indication No. 53, December 12, 2005",
  "artisan_name": "Meenakshi Ammal",
  "artisan_approved": true,
  "materials": [...],
  "techniques": [...],
  "decisions": [...],
  "common_mistakes": [...],
  "mastery_requirements": [...],
  "cultural_significance": "...",
  "provenance": { "source": "artisan-provided knowledge" },
  "approval": { "status": "pending", "approved_by": null },
  "version": "1.0"
}
```

The schema is craft-agnostic — the same pipeline works for any traditional craft worldwide.

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Amazon Bedrock enabled in `us-east-1`
- Access to `amazon.nova-pro-v1:0` in Bedrock
- AWS IAM credentials with `bedrock:InvokeModel` permission

### Installation

```bash
# 1. Clone
git clone https://github.com/madhumithaa-08/Skill_DNA.git
cd Skill_DNA

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
cp .env.example .env
# Edit .env — add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

# 4. Install frontend dependencies
cd frontend && npm install && cd ..
```

### Run

**One command** (builds frontend + serves API on port 8000):

```bash
./start.sh
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

**Or run separately** (two terminals):

```bash
# Terminal 1 — FastAPI backend
python -m uvicorn api:app --reload --port 8000

# Terminal 2 — React frontend
cd frontend && npm run dev
# → http://localhost:5173
```

> **No AWS credentials?** The app runs in demo mode automatically — all agents fall back to rich pre-built Sungudi demo data, so you can explore the full UI without provisioning anything.

---

## Demo Walkthrough

1. Open the app (`http://localhost:5173` or `:8000`)
2. **Artisan Studio** → click **Load Sample Sungudi Notes** → **Use This Sample**
3. Click **🔍 Analyze & Reveal Tacit Knowledge Gaps** — watch the Observer and Interviewer fire
4. Expand the first two questions and type artisan answers
5. Click **🏗️ Synthesize Skill Fingerprint** — Knowledge Architect + Curriculum run
6. Review the fingerprint metrics and full JSON
7. Switch to **📚 Learner Studio** → read the lesson, click 🔊 **Listen** (Polly speaks the step)
8. Take the quiz — your score saves to DynamoDB
9. Chat with the **Mentor** — it remembers your history across sessions

---

## Project Structure

```
Skill_DNA/
├── agents/                     # The five Strands agents
│   ├── observer_agent.py       # Visible steps + knowledge_gaps[]
│   ├── interviewer_agent.py    # Targeted tacit-knowledge questions
│   ├── knowledge_architect.py  # Builds Skill Fingerprint JSON
│   ├── curriculum_agent.py     # Lesson module + quiz
│   └── orchestrator.py         # Agent.as_tool() pipeline + Mentor session agent
├── services/                   # AWS integrations (live boto3)
│   ├── s3_service.py           # Skill Fingerprint → S3
│   ├── dynamodb_service.py     # Learner progress → DynamoDB
│   ├── transcribe_service.py   # Audio → text (en-IN / ta-IN)
│   └── polly_service.py        # Spoken lessons (Kajal neural voice)
├── frontend/src/               # React + TypeScript + Tailwind CSS
│   ├── components/
│   │   ├── ArtisanStudio.tsx
│   │   ├── LearnerStudio.tsx
│   │   ├── SkillFingerprintView.tsx
│   │   ├── PipelineVisualizer.tsx
│   │   └── SavedFingerprintsModal.tsx
│   └── api.ts
├── api.py                      # FastAPI backend (30+ endpoints)
├── agent/app.py                # CLI pipeline runner (video automation)
├── models/                     # Pydantic models (SkillFingerprint, LessonModule)
├── kit/                        # Automation: bench · video · article · check
│   ├── measure.py              # Benchmark runner → results.json
│   ├── make_video.py           # Playwright video recorder
│   ├── make_article.py         # Article generator from real metrics
│   ├── check_submission.py     # Artifact completeness checker
│   ├── ss.py                   # CLI dispatcher
│   └── cases/cases.jsonl       # Signed evaluation cases
├── data/
│   └── sample_sungudi_notes.txt # Meenakshi Ammal's 836-word artisan description
├── demo/                       # Demo script + supporting docs
├── tools/                      # Strands @tool helpers (knowledge, curriculum, vision)
├── utils/                      # Shared helpers
├── Dockerfile
├── start.sh                    # One-command startup
└── requirements.txt
```

---

## Benchmark Results

Measured on `amazon.nova-pro-v1:0`, region `us-east-1`.

| Metric | SKILL DNA | One-Prompt Baseline |
|---|---|---|
| Tacit-knowledge question rate | **~30%** (3/10, live run) | **~0%** (multi-case average) |
| Tacit gaps surfaced | **5/5 expected** | 2/5 |
| Questions targeting muscle memory | **3 of 8** | 0 |
| Questions targeting timing/judgment | **2 of 8** | 1 |
| Knowledge Architect key coverage | **5/5 expected keys** | — |
| Structured Skill Fingerprint | ✅ | ❌ |
| Artisan approval gate | ✅ | ❌ |
| Session memory for learner | ✅ | ❌ |

Run the benchmark:

```bash
python kit/ss.py bench      # runs all cases → kit/results/results.json
python kit/ss.py check      # artifact completeness check
```

---

## Cultural Acknowledgement

Madurai Sungudi is a living craft tradition with roots stretching back over 2,000 years in Tamil Nadu. It holds a Geographical Indication tag recognising that its quality and character are inseparable from its place of origin and the communities that have sustained it.

SKILL DNA is built in deep respect for the artisans — primarily women — whose knowledge, patience, and skill have kept this tradition alive. The platform is designed to amplify and preserve their expertise, not to replace or commodify it. Any real-world deployment requires the free, prior, and informed consent of participating artisans. Artisan attribution and the `artisan_approved` flag are first-class features of the Skill Fingerprint format.

---

## References

1. UNESCO, Traditional Craftsmanship — https://ich.unesco.org/en/traditional-craftsmanship-00057
2. Government of India, PIB — Handicrafts at the Heart of India's Rural Economy, 2025
3. Ministry of Textiles — Fourth All India Handloom Census 2019–20
4. The Hindu — Sungudi artisan decline, 2019
5. IP India — Madurai Sungudi GI Registry (GI tag: December 12, 2005)
6. AWS Strands Agents SDK — https://strandsagents.com
7. Amazon Bedrock — https://aws.amazon.com/bedrock

---

*Built with ❤️ and 🧵 for the AWS Strands SDK Hackathon*
