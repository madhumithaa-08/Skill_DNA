"""
Curriculum formatting tools for the SKILL DNA platform.

Transforms raw lesson JSON produced by the Curriculum Agent into
display-ready structures for the Streamlit Learner Studio.
"""
import json

try:
    from strands import tool
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "strands-agents is not installed. Run: pip install strands-agents"
    ) from exc


@tool
def format_lesson_for_display(lesson_json: str) -> dict:
    """Format a lesson module JSON for Streamlit display.

    Parses the lesson JSON produced by the Curriculum Agent and returns a
    dict whose sections map directly to Streamlit UI components.

    Args:
        lesson_json: JSON string of a LessonModule object.

    Returns:
        dict with keys:
            header (dict): title, craft_name, level, duration_minutes.
            overview (str): lesson overview paragraph.
            objectives (list[str]): bullet-point learning objectives.
            practice_steps (list[dict]): each step with instruction,
                watch_for, and mistake fields.
            quiz (list[dict]): each question with question, options,
                correct_answer, and explanation fields.
            metadata (dict): raw fields for debugging / JSON display.
    """
    try:
        lesson: dict = json.loads(lesson_json) if isinstance(lesson_json, str) else lesson_json
    except json.JSONDecodeError as exc:
        return {
            "error": f"Invalid lesson JSON: {exc}",
            "header": {},
            "overview": "",
            "objectives": [],
            "practice_steps": [],
            "quiz": [],
            "metadata": {},
        }

    # ------------------------------------------------------------------ #
    # Header block                                                          #
    # ------------------------------------------------------------------ #
    header = {
        "title": lesson.get("title", "Untitled Lesson"),
        "craft_name": lesson.get("craft_name", ""),
        "level": lesson.get("level", "beginner").title(),
        "duration_minutes": lesson.get("estimated_duration_minutes", 45),
    }

    # ------------------------------------------------------------------ #
    # Practice steps — normalise varied key names the LLM might produce   #
    # ------------------------------------------------------------------ #
    raw_steps = lesson.get("practice_steps", [])
    practice_steps = []
    for step in raw_steps:
        practice_steps.append({
            "step_number": step.get("step_number", 0),
            "instruction": step.get("instruction", ""),
            "watch_for": step.get("what_to_watch_for", step.get("watch_for", "")),
            "mistake": step.get("common_mistakes", step.get("common_mistake", "")),
        })

    # ------------------------------------------------------------------ #
    # Quiz — ensure consistent key names                                   #
    # ------------------------------------------------------------------ #
    raw_quiz = lesson.get("quiz", [])
    quiz = []
    for q in raw_quiz:
        options = q.get("options", [])
        # Ensure exactly 4 options (pad or truncate if LLM produced wrong count)
        while len(options) < 4:
            options.append("(no option)")
        options = options[:4]
        quiz.append({
            "question": q.get("question", ""),
            "options": options,
            "correct_answer": q.get("correct_answer", ""),
            "explanation": q.get("explanation", ""),
        })

    return {
        "header": header,
        "overview": lesson.get("overview", ""),
        "objectives": lesson.get("learning_objectives", []),
        "practice_steps": practice_steps,
        "quiz": quiz,
        "metadata": lesson,
    }
