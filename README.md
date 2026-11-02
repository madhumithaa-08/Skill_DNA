# 🧬 SKILL DNA — Preserving Traditional Craft Knowledge with AI

> *The knowledge that lives in hands deserves to live forever.*

---

## The Problem

Across the world, thousands of traditional craft traditions are disappearing — not because people have stopped making them, but because the knowledge required to make them has no reliable way to be passed on. A master weaver in Madurai, a ceramicist in Oaxaca, a lacemaker in Bruges: each carries decades of expertise that exists almost entirely as tacit knowledge — in their fingertips, their eyes, their intuition.

This knowledge is not in books. It is not on YouTube. It cannot be fully captured by filming a demonstration, because the most important knowledge is invisible: how the silk *feels* when it is ready, the exact resistance of a correctly-tied knot, the moment when the dye bath has done its work. This sensory, judgment-based knowledge takes years to develop and is catastrophically easy to lose.

When a master artisan retires without a successor, or when a craft cluster loses its last practitioner to economic pressure, that knowledge is gone permanently. UNESCO estimates that thousands of intangible cultural heritage practices are at risk of extinction in the next generation.

SKILL DNA was built to do something about it.

---

## What SKILL DNA Does

- **Captures tacit knowledge** from artisans via structured multi-agent interview pipelines
- **Generates targeted questions** that draw out sensory, judgment-based, and cultural knowledge that artisans struggle to articulate unprompted
- **Builds Skill Fingerprints** — structured, versioned JSON documents that encode a craft's complete knowledge graph: materials, techniques, decision points, common mistakes, mastery requirements, and cultural significance
- **Creates interactive lesson modules** from Skill Fingerprints, with practice steps, sensory guidance, and quizzes that test real understanding
- **Scales across crafts, languages, and regions** — any traditional craft can be digitised using the same pipeline
- **Honours artisan ownership** via the `artisan_approved` flag and attribution fields in every Skill Fingerprint
- **Degrades gracefully** — the full demo runs without AWS credentials using built-in demo data

---

## Agent Architecture

```
                        ┌─────────────────────────┐
                        │      ORCHESTRATOR        │
                        │  (coordinates pipeline)  │
                        └────────────┬────────────┘
                                     │
         ┌───────────────────────────▼───────────────────────────┐
         │                    PIPELINE                            │
         │                                                        │
  ┌──────▼──────┐    ┌──────────────┐    ┌──────────────────┐   │
  │  ARTISAN    │    │   OBSERVER   │    │   INTERVIEWER    │   │
  │   INPUT     ├───►│    AGENT     ├───►│     AGENT        │   │
  │(description)│    │(visible steps│    │(targeted tacit-  │   │
  └─────────────┘    │ + gaps)      │    │ knowledge Qs)    │   │
                     └──────────────┘    └────────┬─────────┘   │
                                                  │              │
                                    ┌─────────────▼──────────┐  │
                                    │  KNOWLEDGE ARCHITECT   │  │
                                    │  (Skill Fingerprint)   │  │
                                    └─────────────┬──────────┘  │
                                                  │              │
                                    ┌─────────────▼──────────┐  │
                                    │   CURRICULUM AGENT     │  │
                                    │  (lesson module)       │  │
                                    └─────────────┬──────────┘  │
                                                  │              │
                                         ┌────────▼────────┐    │
                                         │  LEARNER OUTPUT │    │
                                         │(interactive UI) │    │
                                         └─────────────────┘    │
         └──────────────────────────────────────────────────────┘
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or later
- An AWS account with Amazon Bedrock enabled in `us-east-1`
- Access enabled for `claude-3-5-sonnet-20241022` and `amazon.nova-pro-v1:0` in Bedrock
- AWS IAM credentials with `bedrock:InvokeModel` permission

### Installation

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/skill-dna.git
cd skill-dna

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
cp .env.example .env
# Edit .env and fill in your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# 4. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

> **No AWS credentials?** The app runs in demo mode automatically — all four agents gracefully fall back to rich pre-built demo data for Madurai Sungudi, so you can explore the full UI without AWS access.

---

## Agent Descriptions

**Observer Agent** (`agents/observer_agent.py`)
Receives a free-text description of a craft demonstration and extracts structured visible knowledge: ordered process steps, tools identified, materials identified, and — most importantly — knowledge gaps: the things that cannot be inferred from the description alone. These gaps become the Interviewer Agent's target list.

**Interviewer Agent** (`agents/interviewer_agent.py`)
Specialises in extracting tacit knowledge — the unspoken expertise that masters carry in their bodies. Given a list of knowledge gaps from the Observer Agent, it generates 6–8 targeted questions that ask about sensory cues (how things feel, sound, smell), timing and judgment (when to stop, how to recognise quality), decision-making rationale, error recovery, and cultural significance.

**Knowledge Architect Agent** (`agents/knowledge_architect.py`)
Synthesises the observation data and artisan Q&A answers into a comprehensive Skill Fingerprint — a structured JSON document that encodes the craft's complete knowledge graph. Every decision point preserves the 'why' behind craft choices, not just the 'what'. Fingerprints are versioned, artisan-attributed, and saved to disk (production: DynamoDB).

**Curriculum Agent** (`agents/curriculum_agent.py`)
Transforms a Skill Fingerprint into an interactive lesson module. Every lesson uses concrete sensory language derived from the artisan's own words, includes step-by-step practice guidance with sensory checkpoints, and ends with a quiz that tests conceptual understanding rather than memorisation.

**Orchestrator** (`agents/orchestrator.py`)
Coordinates the full four-agent pipeline via `run_skill_capture_pipeline()`. Manages stage sequencing, passes context between agents, monitors pipeline health, and returns a unified result containing the Skill Fingerprint, the lesson module, and the questions asked.

---

## Demo Walkthrough

1. Open the app: `streamlit run app.py`
2. In the **Artisan Studio** tab, click **Load Sample Sungudi Notes** and select "Use This Sample"
3. Click **🔍 Generate Questions** — watch the Observer and Interviewer agents run
4. Expand the first two questions and type sample answers
5. Click **🏗️ Create Skill Fingerprint** — the Knowledge Architect and Curriculum agents run
6. Review the metrics (techniques, decisions, materials, mastery skills) and the full JSON
7. Switch to the **📚 Learner Studio** tab
8. Read the lesson overview and practice steps
9. Take the quiz and check your answers

Without AWS credentials, each agent step falls back to demo data automatically — you will see a blue info banner confirming demo mode.

---

## AWS Services Used

| Service | Purpose | Status (Hackathon) |
|---|---|---|
| Amazon Bedrock (Claude 3.5 Sonnet) | All four agents: observation, interviewing, knowledge synthesis, curriculum generation | **Live** (requires credentials) |
| Amazon Bedrock (Nova Pro) | Multimodal image analysis via `vision_tools.py` | **Mocked** — text descriptions used |
| Amazon S3 | Media storage (craft images, audio) | **Mocked** — local filesystem used |
| Amazon DynamoDB | Skill Fingerprint persistence | **Mocked** — local JSON files used |

---

## Hackathon Submission

- **Event:** AWS Strands SDK Hackathon
- **Track:** Education
- **Submission deadline:** November 4, 2026
- **Primary SDK:** [Strands Agents](https://strandsagents.com) — multi-agent orchestration with `@tool` decorators and `BedrockModel`
- **Pilot craft:** Madurai Sungudi (Tamil Nadu, India)
- **Agent count:** 4 specialised agents + 1 orchestrator

---

## Cultural Acknowledgement

Madurai Sungudi is a living craft tradition with roots stretching back over 2000 years in Tamil Nadu, India. It holds a Geographical Indication (GI) tag, recognising that its quality and character are inseparable from its place of origin and the communities that have sustained it across generations.

SKILL DNA is built in deep respect for the artisans — primarily women — whose knowledge, patience, and skill have kept this tradition alive. The platform is designed to amplify and preserve their expertise, not to replace or commodify it. Any deployment of SKILL DNA in real craft preservation work requires the free, prior, and informed consent of participating artisans, and artisan attribution is a first-class feature of the Skill Fingerprint format.

We acknowledge the Tamil artisan community of Madurai and thank the master artisans whose tradition inspired this work.

---

*Built with ❤️ and 🧵 for the AWS Strands SDK Hackathon*
