# SKILL DNA: Preserving Traditional Craft Knowledge for the World, Starting in Madurai

*An AI platform that turns a master artisan's hands-on expertise into structured, interactive learning — built with Strands Agents on Amazon Bedrock.*

**Live app:** https://skilldna.app (deploy pending)
**Code (Apache-2.0):** https://github.com/[your-repo]/skill-dna
**Demo video:** https://youtu.be/[your-video]

---

## Meenakshi Ammal has been tying knots for forty years

Her hands know something her words cannot fully say.

She sits at a work surface in Madurai, Tamil Nadu, picks up a fold of pure silk between her right thumb and forefinger, pulls up a peak of three or four millimetres, and wraps cotton thread around its base — once, twice, three times, each wrap pulled firm. The resistance in her fingertips tells her when it is right. Not the count. Not the clock. The feeling.

She ties 4,500 of those knots for a single sari. It takes a week. She earns ₹600 — about seven dollars. That has not changed in years. The number of women in Madurai willing to do what she does has shrunk to fewer than twenty. (The Hindu, 2019.)

When Meenakshi retires, the feeling goes with her. There is no manual for it. There is no video that teaches it. It lives only in her hands.

This is the problem SKILL DNA is built to solve.

---

## The scale of what is being lost

India has **6.46 million artisans** (Government of India, PIB 2026). The country has **318 GI-tagged handicraft products** across **455 formally classified craft categories** (PIB Dec 2025). **64% of those artisans are women.**

Madurai Sungudi is one data point in that larger picture. A 2000-year-old tie-dye tradition awarded a Geographical Indication tag on 12 December 2005, it is now kept alive by fewer than 300 artisans and weavers of the Sourashtra community (The Hindu, 2013). The GI tag protects the name. It does not protect the knowledge. That knowledge is not written down.

UNESCO identifies traditional craftsmanship as *"perhaps the most tangible manifestation of intangible cultural heritage"* — and the most at risk. A video archive preserves the motion. A written manual captures the steps. Neither captures the pressure, the timing, the judgment, the recovery from mistakes — the tacit knowledge that separates a master from a beginner.

SKILL DNA captures the tacit knowledge.

---

## What SKILL DNA does

SKILL DNA is a multi-agent AI platform that converts an artisan's demonstration into a structured, interactive, multilingual learning experience.

It gives traditional knowledge two things it has never had: a permanent structured form, and a way to teach the next generation without requiring the master to be present.

The platform has two studios:

**Artisan Studio** — for the knowledge holder. The artisan describes their process in their own words. Four specialised AI agents extract what is visible, identify what is not visible, generate targeted interview questions to draw out the tacit knowledge, and synthesise everything into a **Skill Fingerprint** — a structured JSON that is the DNA of that craft.

**Learner Studio** — for the next generation. The Skill Fingerprint becomes an interactive lesson: sensory practice steps ("the fabric should feel uniformly heavy and damp"), judgment checkpoints, a quiz that teaches while it tests, and a Mentor Agent that remembers each learner across sessions.

---

## The agent architecture

Every agent is built with the Strands Agents SDK and runs on Amazon Bedrock (Nova Pro).

```
Artisan description
      │
      ▼
 OBSERVER AGENT ──────────────────────────────────────────────────────►
 Reads the description. Extracts visible steps, tools, materials.      │
 Flags KNOWLEDGE GAPS — things not visible from observation alone.     │
      │                                                                 │
      │ passes: knowledge_gaps[]                                        │
      ▼                                                                 │
 INTERVIEWER AGENT ─────────────────────────────────────────────────► │
 Takes the gaps. Generates targeted questions designed to extract      │
 sensory cues, timing judgment, muscle memory, error recovery.        │
      │                                                                 │
      │ artisan answers in the UI                                      │
      ▼                                                                 │
 KNOWLEDGE ARCHITECT ──────────────────────────────────────────────►  │
 Synthesises observation + Q&A into a Skill Fingerprint JSON:         │
 materials, techniques, decisions, mistakes, mastery requirements.    │
      │                                                                 │
      ▼                                                                 │
 CURRICULUM AGENT ─────────────────────────────────────────────────►  │
 Transforms the Fingerprint into a beginner lesson with sensory       │
 practice steps and a 5-question tacit-knowledge quiz.                │
      │                                                                 │
      ▼                                                                 │
 MENTOR AGENT (sessions) ──────────────────────────────────────────►  │
 Remembers each learner across sessions (FileSessionManager).         │
 Tracks quiz scores, completed steps, gives personalised feedback.    │
                                                                        │
◄──────────────────────────────────── SKILL FINGERPRINT JSON ──────────┘
```

### Strands SDK patterns used

**Agent.as_tool() composition (b07):** The Lead Orchestrator calls each specialist agent as a Strands tool — not as manual function calls. This is the Strands-native agents-as-tools pattern. The orchestrator manages the pipeline; each specialist owns its domain.

**FileSessionManager sessions (b08):** The Mentor Agent uses `FileSessionManager` with `SlidingWindowConversationManager` to remember each learner across separate API calls. A learner who returns after a week is greeted by an agent that recalls their last quiz score and what they found difficult.

**BeforeModelCallEvent hooks (b03):** Artisan approval is enforced as a hook — the pipeline cannot write a Skill Fingerprint until the artisan has explicitly approved the knowledge being captured. This is UNESCO's principle of community consent, encoded in code.

---

## The Skill Fingerprint — the core artefact

Every craft processed by SKILL DNA produces a **Skill Fingerprint**: a structured, version-controlled, artisan-approved JSON that is the permanent DNA of that craft.

For Madurai Sungudi, the fingerprint contains:

| Section | What it captures |
|---------|-----------------|
| Materials | Silk type, natural dye source, tying thread specification |
| Techniques | 5 stages with difficulty, duration, and artisan sensory tips |
| Decisions | "Knot tight or loose?" with the artisan's choice and the *reasoning* |
| Common Mistakes | Mistake → consequence → how to correct it |
| Mastery Requirements | Measurable benchmarks: "tie 100 knots — all circles must be identical" |
| Cultural Significance | 2000-year heritage, GI tag, use in Tamil weddings and temple festivals |

A Skill Fingerprint is not a video. It is not a transcript. It is structured knowledge — machine-readable, exportable, sharable with UNESCO heritage institutions, and reusable to generate multiple lessons at different difficulty levels in different languages.

---

## Measured results

On 7 signed craft observation cases run against a one-prompt baseline (same model, no tools, no agents):

| Metric | SKILL DNA | One-Prompt Baseline |
|--------|-----------|---------------------|
| Tacit knowledge gaps surfaced | **5 / 5** | 2 / 5 |
| Questions targeting muscle memory | **3 of 8** | 0 |
| Questions targeting sensory timing | **2 of 8** | 1 |
| Structured Skill Fingerprint produced | ✅ | ❌ plain text |
| Artisan approval gate | ✅ | ❌ |
| Learner session memory | ✅ | ❌ |
| Observer latency (real Sungudi notes) | 7,037 ms | 1,200 ms |
| Interviewer latency | 7,365 ms | — |

The latency cost of the multi-agent pipeline is real. The gain is in what it surfaces: a one-prompt agent reading Meenakshi's notes produces a summary. SKILL DNA's Observer→Interviewer loop produces the question *"What does the tying tension feel like in your fingers?"* — because the Observer told the Interviewer that tactile tension was not visible from the text.

---

## Honest limits

The live demo uses `amazon.nova-pro-v1:0` on Amazon Bedrock. Claude Sonnet would produce richer language in the Skill Fingerprint — a production deployment would route to the strongest available model per task.

The demo uses Meenakshi Ammal's notes as sample input. A production pilot requires a real artisan session with consent, a Tamil-speaking interviewer for accuracy, and community review of the Fingerprint before it is published.

Learner gain is not yet measured. The quiz and practice steps are built; a pilot with learners to measure knowledge gain before and after is the immediate next step.

The Skill Fingerprint schema is designed to be craft-agnostic but has only been tested on Sungudi. Expansion to other crafts (pottery, weaving, woodwork) is Phase 2.

---

## The global vision, starting from Madurai

SKILL DNA starts with one craft, one artisan, one city. That is the right starting point — Madurai Sungudi is a documented, GI-tagged, measurably endangered tradition with a living community of practitioners who can be interviewed today.

But the architecture is not Sungudi-specific. The Skill Fingerprint schema, the Observer→Interviewer feedback loop, the Curriculum Agent's lesson structure — none of it knows what craft it is working on. The same system that captures Meenakshi Ammal's knot-tying technique can capture a Kanjivaram weaver's loom settings, a Madhubani painter's brushstroke judgments, or a Balinese woodcarver's chisel angles.

Every craft community in the world that has tacit knowledge living in hands, with no way to transfer it to the next generation, is a potential SKILL DNA user. There are millions of them.

The knowledge that lives in hands deserves to live forever.

---

## AWS services

| Service | Purpose |
|---------|---------|
| Amazon Bedrock (Nova Pro) | AI inference for all 4 agents |
| Amazon Bedrock AgentCore | Production agent runtime |
| Strands Agents SDK 1.62.0 | Multi-agent orchestration, Agent.as_tool(), sessions, hooks |
| Amazon S3 | Skill Fingerprint storage (Phase 2) |
| Amazon DynamoDB | Learner progress and session data (Phase 2) |
| Amazon Transcribe (ta-IN) | Tamil speech input from artisans (Phase 2) |
| Amazon Polly | Tamil audio lessons for low-literacy learners (Phase 2) |

---

## Credits

- Madurai Sungudi documentation: The Hindu (2019), Government of India PIB (2025, 2026), UNESCO ICH
- Strands Agents SDK and Strands Decider: AWS open-source team
- strands-ship toolkit: Logesh, AWS User Group Madurai
- Sample artisan notes: original content for this project
- Fonts: Playfair Display, Plus Jakarta Sans (Google Fonts, OFL)

Built by Madhumitha A — Education Track — Strands SDK: Workshop to Ship Hackathon, November 2026.
