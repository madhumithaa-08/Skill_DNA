"""
SKILL DNA — AI-Powered Traditional Craft Knowledge Preservation Platform
Streamlit demo application.

Run with:
    streamlit run app.py
"""
import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Page configuration (must be the FIRST Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SKILL DNA",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Demo data helpers — defined early so tab1 button handlers can call them
# ---------------------------------------------------------------------------

def _get_demo_fingerprint(craft_name: str, artisan_name: str) -> dict:
    """Return a rich demo Skill Fingerprint for UI testing without AWS credentials."""
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
                "stage": "1",
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
                "stage": "2",
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
                "stage": "3",
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
                "stage": "4",
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
                "stage": "5",
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
        "created_at": "2024-01-15T10:30:00",
        "version": "1.0",
    }


def _get_demo_lesson(craft_name: str) -> dict:
    """Return a rich demo lesson for UI testing without AWS credentials."""
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


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧬 SKILL DNA")
    st.markdown("*Preserving Traditional Craft Knowledge*")
    st.divider()
    st.markdown("### Agent Pipeline")
    st.markdown(
        """
🔍 **Observer Agent**
Extracts visible process steps

❓ **Interviewer Agent**
Generates targeted questions

🏗️ **Knowledge Architect**
Builds the Skill Fingerprint

📚 **Curriculum Agent**
Creates the learning module

🎯 **Orchestrator**
Coordinates the pipeline
        """
    )
    st.divider()
    st.caption("AWS Strands SDK Hackathon — Education Track")
    st.caption("Pilot craft: Madurai Sungudi")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
defaults = {
    "fingerprint": None,
    "lesson": None,
    "questions": [],
    "answers": {},
    "observation": {},
    "quiz_submitted": False,
    "sample_loaded": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# Main heading
# ---------------------------------------------------------------------------
st.markdown("# 🧬 SKILL DNA")
st.markdown("### AI-Powered Traditional Craft Knowledge Preservation")

tab1, tab2 = st.tabs(["🎨 Artisan Studio", "📚 Learner Studio"])

# ===========================================================================
# TAB 1: ARTISAN STUDIO
# ===========================================================================
with tab1:
    st.header("Artisan Studio — Capture Your Craft")
    st.markdown(
        "*Document your craft knowledge step by step. "
        "Our AI agents will help structure it for future learners.*"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        craft_description = st.text_area(
            "Describe your craft demonstration",
            height=200,
            placeholder=(
                "Describe your craft process in detail. For example:\n\n"
                "I start by washing the fabric in warm water to remove any starch. "
                "The silk must be completely damp but not dripping...\n\n"
                "Include: what you do, what materials you use, how things feel, "
                "what to watch for at each step."
            ),
        )
    with col2:
        craft_name = st.text_input("Craft Name", value="Madurai Sungudi")
        artisan_name = st.text_input("Your Name (Artisan)")
        st.info(
            "💡 **Tip:** The more detail you provide, "
            "the richer your Skill Fingerprint will be."
        )

    # Load sample notes if file exists
    sample_path = Path("/Users/madhumithaa/Desktop/Skill DNA/data/sample_sungudi_notes.txt")
    if sample_path.exists():
        with st.expander("📄 Load Sample Sungudi Notes"):
            sample_text = sample_path.read_text(encoding="utf-8")
            st.text(sample_text[:500] + "...")
            if st.button("Use This Sample"):
                st.session_state.sample_loaded = sample_text
                st.rerun()

    if st.session_state.sample_loaded:
        craft_description = st.session_state.sample_loaded

    st.divider()

    # ----------------------------------------------------------------------- #
    # STEP 1: Generate Questions                                               #
    # ----------------------------------------------------------------------- #
    st.subheader("Step 1: Generate Interview Questions")
    if st.button("🔍 Generate Questions", type="primary", disabled=not craft_description):
        with st.spinner(
            "Observer Agent analysing your craft… Interviewer Agent generating questions…"
        ):
            try:
                from agents.observer_agent import ObserverAgent
                from agents.interviewer_agent import InterviewerAgent

                observer = ObserverAgent()
                observation = observer.analyze(craft_description)

                interviewer = InterviewerAgent()
                questions = interviewer.generate_questions(
                    observation.get(
                        "knowledge_gaps",
                        ["Process details", "Material properties", "Quality assessment"],
                    ),
                    craft_name,
                )

                st.session_state.questions = questions
                st.session_state.observation = observation
                st.success(f"✅ Generated {len(questions)} targeted questions!")

            except Exception as exc:
                st.error(
                    f"⚠️ Agent error: {exc}\n\n"
                    "Please check your AWS credentials in .env"
                )
                # Demo fallback
                st.session_state.questions = [
                    "How tight should the knots be — and how do you test the tightness without breaking the thread?",
                    "How do you know the dye has fully penetrated the fabric before removing from the bath?",
                    "What does the fabric feel like when it is ready for the next stage vs when it needs more time?",
                    "How do you decide the spacing between knots for different patterns?",
                    "What is the first sign that something has gone wrong in the dyeing process?",
                    "How long did it take you to develop the feel for the correct knot tension?",
                ]
                st.session_state.observation = {}
                st.info("Using demo questions (AWS credentials not configured)")

    # Show questions and answer inputs
    if st.session_state.questions:
        st.subheader("Interview Questions for the Artisan")
        for i, question in enumerate(st.session_state.questions):
            with st.expander(
                f"Q{i + 1}: {question[:60]}{'...' if len(question) > 60 else ''}",
                expanded=(i < 2),
            ):
                st.markdown(f"**{question}**")
                answer = st.text_area(
                    "Your answer:",
                    key=f"answer_{i}",
                    height=100,
                    placeholder="Share your knowledge here…",
                )
                if answer:
                    st.session_state.answers[question] = answer

        st.divider()

        # ------------------------------------------------------------------- #
        # STEP 2: Create Skill Fingerprint                                     #
        # ------------------------------------------------------------------- #
        st.subheader("Step 2: Create Skill Fingerprint")
        st.markdown("Answer at least a few questions above, then create your Skill Fingerprint.")

        if st.button("🏗️ Create Skill Fingerprint", type="primary"):
            with st.spinner(
                "Knowledge Architect building Skill Fingerprint… "
                "Curriculum Agent creating lesson…"
            ):
                try:
                    from agents.knowledge_architect import KnowledgeArchitectAgent
                    from agents.curriculum_agent import CurriculumAgent

                    architect = KnowledgeArchitectAgent()
                    fp_result = architect.build_fingerprint(
                        st.session_state.observation,
                        st.session_state.answers,
                        craft_name,
                        artisan_name or "Master Artisan",
                    )

                    curriculum = CurriculumAgent()
                    lesson = curriculum.create_lesson(
                        fp_result.get("fingerprint", fp_result)
                    )

                    st.session_state.fingerprint = fp_result.get("fingerprint", fp_result)
                    st.session_state.lesson = lesson
                    st.success("✅ Skill Fingerprint created and lesson generated!")

                except Exception as exc:
                    st.error(f"⚠️ Agent error: {exc}")
                    st.session_state.fingerprint = _get_demo_fingerprint(
                        craft_name, artisan_name
                    )
                    st.session_state.lesson = _get_demo_lesson(craft_name)
                    st.info("Using demo Skill Fingerprint (AWS credentials not configured)")

    # Show fingerprint if available
    if st.session_state.fingerprint:
        fp = st.session_state.fingerprint
        st.success("🧬 **Skill Fingerprint Ready!**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Techniques", len(fp.get("techniques", [])))
        with c2:
            st.metric("Decisions", len(fp.get("decisions", [])))
        with c3:
            st.metric("Materials", len(fp.get("materials", [])))
        with c4:
            st.metric("Mastery Skills", len(fp.get("mastery_requirements", [])))

        with st.expander("📋 View Full Skill Fingerprint JSON"):
            st.json(fp)

# ===========================================================================
# TAB 2: LEARNER STUDIO
# ===========================================================================
with tab2:
    st.header("Learner Studio — Learn the Craft")

    if not st.session_state.lesson:
        st.info(
            "👋 No lesson available yet. Visit the **Artisan Studio** tab to generate "
            "a Skill Fingerprint and lesson first."
        )
        st.markdown(
            """
### How it works:
1. Go to **Artisan Studio**
2. Describe the craft process
3. Answer the generated questions
4. Create the Skill Fingerprint
5. Come back here to learn!
            """
        )

        # Quick-start: load demo lesson directly
        st.divider()
        st.markdown("### 🚀 Quick Start (Demo Mode)")
        st.markdown(
            "Don't have AWS credentials yet? Load the demo Madurai Sungudi lesson to "
            "explore the Learner Studio."
        )
        if st.button("▶ Load Demo Lesson", type="secondary"):
            st.session_state.fingerprint = _get_demo_fingerprint("Madurai Sungudi", "Meenakshi Ammal")
            st.session_state.lesson = _get_demo_lesson("Madurai Sungudi")
            st.rerun()
    else:
        lesson = st.session_state.lesson

        # Lesson header
        st.markdown(f"## {lesson.get('title', 'Craft Lesson')}")
        hcol1, hcol2 = st.columns([3, 1])
        with hcol1:
            st.markdown(f"**Craft:** {lesson.get('craft_name', '')}")
        with hcol2:
            st.markdown(f"**Level:** {lesson.get('level', 'beginner').title()}")
            st.markdown(f"**Duration:** ~{lesson.get('estimated_duration_minutes', 45)} min")

        st.markdown("### Overview")
        st.markdown(lesson.get("overview", ""))

        # Learning objectives
        st.markdown("### 🎯 Learning Objectives")
        for obj in lesson.get("learning_objectives", []):
            st.markdown(f"- {obj}")

        st.divider()

        # Practice steps
        st.markdown("### 🛠️ Practice Steps")
        for step in lesson.get("practice_steps", []):
            step_num = step.get("step_number", 0)
            instruction_preview = step.get("instruction", "")[:60]
            with st.expander(
                f"Step {step_num}: {instruction_preview}{'...' if len(step.get('instruction', '')) > 60 else ''}",
                expanded=(step_num <= 2),
            ):
                st.markdown(f"**Instructions:** {step.get('instruction', '')}")
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.info(
                        f"👁️ **What to watch for:**\n{step.get('what_to_watch_for', '')}"
                    )
                with sc2:
                    st.warning(
                        f"⚠️ **Common mistake:**\n{step.get('common_mistakes', '')}"
                    )

        st.divider()

        # Quiz
        st.markdown("### 📝 Knowledge Quiz")
        st.markdown("Test your understanding of the craft:")

        quiz = lesson.get("quiz", [])
        user_answers: dict = {}

        for i, q in enumerate(quiz):
            st.markdown(f"**Question {i + 1}:** {q.get('question', '')}")
            options = q.get("options", [])
            user_answers[i] = st.radio(
                f"Select your answer for Q{i + 1}:",
                options,
                key=f"quiz_q{i}",
                index=None,
                label_visibility="collapsed",
            )
            st.markdown("")

        qcol1, _ = st.columns([1, 3])
        with qcol1:
            check_btn = st.button("✅ Check Answers", type="primary")

        if check_btn:
            score = 0
            st.markdown("### Results")
            for i, q in enumerate(quiz):
                correct = q.get("correct_answer", "")
                given = user_answers.get(i)
                if given == correct:
                    score += 1
                    st.success(f"Q{i + 1}: ✅ Correct!")
                else:
                    st.error(f"Q{i + 1}: ❌ The correct answer is: *{correct}*")
                st.markdown(f"💡 *{q.get('explanation', '')}*")
                st.markdown("")

            st.markdown(f"### Score: {score}/{len(quiz)}")
            if score == len(quiz):
                st.balloons()
                st.success("Perfect score! You're ready to start your Sungudi journey!")
            elif score >= len(quiz) * 0.6:
                st.success("Good job! Review the steps you missed and try again.")
            else:
                st.info(
                    "Keep practising! Go through the practice steps again and retake the quiz."
                )
