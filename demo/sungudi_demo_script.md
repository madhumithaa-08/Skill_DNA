# SKILL DNA — 3-Minute Demo Script
## AWS Strands SDK Hackathon | Education Track

---

## [0:00–0:20] Opening Hook: The Disappearing Craft Problem

**[Slide / screen: a photo of an artisan tying Sungudi knots — aged hands, intricate work]**

> "Somewhere in Madurai right now, a master artisan is sitting with forty years of knowledge in her fingertips — knowledge she has never written down, knowledge her students struggle to absorb before she retires. When she stops working, that knowledge disappears. Permanently.
>
> There are over 3,000 traditional craft clusters in India alone. Most of them face the same crisis. The knowledge is in the hands. It is not in any book, any video, any database."

**[Speaker note]:** Pause for 2 seconds after the last line. The silence makes the problem land.

---

## [0:20–0:40] What SKILL DNA Is

**[Switch to the SKILL DNA app in the browser — sidebar visible]**

> "SKILL DNA is an AI-powered platform that captures that knowledge. We use a multi-agent pipeline — built on the AWS Strands SDK — to do something no single AI model can do alone.
>
> Four specialised agents work in sequence: an Observer Agent extracts visible process steps. An Interviewer Agent generates targeted questions to draw out what's invisible — the sensory cues, the judgment calls, the tacit knowledge. A Knowledge Architect builds a structured Skill Fingerprint. And a Curriculum Agent turns that fingerprint into an interactive learning module."

**[Speaker note]:** Gesture to the sidebar pipeline list as you name each agent.

---

## [0:40–1:20] Live Demo: Paste Artisan Notes, Generate Questions

**[Click on the Artisan Studio tab]**

> "Our pilot craft is Madurai Sungudi — a 2000-year-old tie-dye technique with a GI tag. We interviewed a master artisan named Meenakshi Ammal, and here are her notes."

**[Click 'Load Sample Sungudi Notes' expander → click 'Use This Sample']**

> "The Observer Agent reads this description and identifies what it can see — and crucially, what it *cannot* see. Those gaps become the interview questions."

**[Click '🔍 Generate Questions']**

> "Watch the multi-agent pipeline fire. The Observer Agent analyses the craft description and passes the knowledge gaps to the Interviewer Agent, which generates targeted questions designed to extract tacit knowledge."

**[Wait for spinner to resolve — questions appear]**

> "Six targeted questions. Not generic questions — questions calibrated to this specific craft. 'How do you know the dye has fully penetrated the fabric?' That's a question about sensory judgment. You can't answer it without decades of experience."

**[Speaker note]:** If AWS credentials aren't configured, the app gracefully falls back to demo questions — mention this as a feature: "The app degrades gracefully — you get a full demo experience without credentials."

---

## [1:20–1:50] Answer 2 Questions: Show the Q&A Interface

**[Click to expand Q1 and Q2]**

> "Now the artisan answers. Let me fill in two of these."

**[Type into Q1 answer box:]**
> *"You can feel it in your thumb — when the thread is right, there's a firm resistance, like the knot is pushing back against you. If it feels loose, it will leak. I always do a test pull before I move on."*

**[Type into Q2 answer box:]**
> *"I press a corner of the fabric against a white cloth. If it leaves a rich colour, it's ready. If it looks pale, I give it five more minutes and test again."*

> "These answers are gold. 'Firm resistance, like the knot is pushing back.' That's the kind of sensory knowledge that takes years to articulate. We've just captured it."

**[Speaker note]:** Speak slowly here — the audience needs to appreciate the value of what was just typed, not just that typing happened.

---

## [1:50–2:20] Create Fingerprint: Show the Skill Fingerprint JSON

**[Click '🏗️ Create Skill Fingerprint']**

> "The Knowledge Architect Agent now synthesises everything — the observations, the Q&A, the cultural context — into a Skill Fingerprint. This is the core artifact of SKILL DNA."

**[Wait for spinner → metrics appear: 4 Techniques, 3 Decisions, 4 Materials, 3 Mastery Skills]**

> "Look at these metrics. Four techniques, three critical decision points, four materials, three mastery requirements. This is 40 years of knowledge, structured in under 30 seconds."

**[Click 'View Full Skill Fingerprint JSON' expander]**

> "The Skill Fingerprint is a structured JSON. It's machine-readable, version-controlled, and — crucially — artisan-approved. It can be stored in DynamoDB, used to generate multiple lessons at different difficulty levels, or shared with craft preservation institutions. It's a living digital archive."

**[Speaker note]:** Scroll down slowly through the JSON — don't read it, just let the audience see the structure. Point to the `decisions` block: "This is where we capture the 'why' behind craft choices — not just what the artisan does, but why."

---

## [2:20–2:40] Switch to Learner Studio: Show the Lesson

**[Click the 📚 Learner Studio tab]**

> "The Curriculum Agent has already generated a lesson from the Skill Fingerprint. Here it is."

**[Scroll to show: title, overview, learning objectives, first two practice steps]**

> "Notice the language in the practice steps: 'The fabric should feel uniformly heavy and damp.' 'You should feel slight resistance when you pull the knot.' This is the artisan's sensory knowledge, translated into beginner-friendly instructions."

> "A YouTube video shows you what to do. SKILL DNA teaches you what to *feel*."

**[Speaker note]:** This is the key differentiator line — say it clearly and let it land.

---

## [2:40–2:55] Take One Quiz Question

**[Scroll to the quiz section]**

> "And the lesson ends with a quiz — not a memorisation test. Watch this question."

**[Read Q3 aloud:]** *"How do master artisans know a Sungudi knot has the right tension?"*

> "The options include 'they use a tension gauge' and 'they count the number of wraps precisely.' But the correct answer is: 'They develop a tactile sense through years of practice.' That answer teaches the learner something profound about craft mastery — and why they need to practice, not just watch."

**[Select the correct answer → click Check Answers]**

**[Speaker note]:** The quiz is designed to be educational even when you answer wrong. Point this out if time permits.

---

## [2:55–3:00] Closing: Social Impact Statement

**[Return to the SKILL DNA title screen or the sidebar]**

> "Meenakshi Ammal has been tying Sungudi knots for forty years. SKILL DNA just gave those forty years a future. We're starting with one craft, one artisan, one Indian GI tag. But the platform scales to any craft, any artisan, anywhere in the world.
>
> The knowledge that lives in hands deserves to live forever. That is SKILL DNA."

**[Speaker note]:** Hold eye contact with the audience through the final line. Do not advance any slides or click anything. The silence after is part of the close.

---

## Backup Notes

- If the agent pipeline fails (no AWS credentials): the app displays demo data automatically — note it as "graceful degradation with demo mode"
- If asked about cost: Claude 3.5 Sonnet on Bedrock charges per token; a full pipeline run is approximately 8,000–12,000 input tokens and 2,000–4,000 output tokens
- If asked about scaling: DynamoDB for fingerprint storage, S3 for media, Bedrock for inference — all managed services, no infra to maintain
- If asked about artisan consent: the `artisan_approved` flag in the Skill Fingerprint is designed for an artisan sign-off workflow (phase 2 feature)
