"""
Vision tools for the SKILL DNA platform.

Accepts text descriptions of craft images or demonstrations and extracts
structured observable knowledge. For the hackathon, actual image bytes are
not required — the tool operates on rich text descriptions of what is visible.
"""
import re

try:
    from strands import tool
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "strands-agents is not installed. Run: pip install strands-agents"
    ) from exc


@tool
def analyze_craft_image(image_description: str, craft_context: str) -> dict:
    """Analyse a craft image description and extract observable process details.

    Accepts a textual description of a craft demonstration image (or an actual
    image description from a vision model) together with background context
    about the craft, and returns a structured breakdown of what is observable.

    Args:
        image_description: A detailed text description of what is visible in
            the craft image or video frame.
        craft_context: Background context about the craft being documented
            (e.g. "Madurai Sungudi tie-dye").

    Returns:
        dict with keys:
            observable_steps (list[str]): Visible process steps in sequence.
            materials_visible (list[str]): Materials or tools seen.
            techniques_visible (list[str]): Techniques that can be inferred.
            quality_indicators (list[str]): Visual cues for quality assessment.
            knowledge_gaps (list[str]): Things NOT visible that need follow-up.
    """
    description_lower = image_description.lower()

    # ------------------------------------------------------------------ #
    # Heuristic extraction: pull observable elements from the description  #
    # ------------------------------------------------------------------ #

    # Observable steps — sentences that contain action verbs
    action_verbs = [
        "wash", "soak", "wring", "mark", "pinch", "tie", "wrap", "knot",
        "cut", "dip", "immerse", "stir", "remove", "untie", "reveal",
        "spread", "fold", "dry", "press", "boil", "mix", "pour",
    ]
    sentences = re.split(r"[.!?]", image_description)
    observable_steps = [
        s.strip()
        for s in sentences
        if any(verb in s.lower() for verb in action_verbs) and len(s.strip()) > 15
    ]

    # Materials visible — look for known craft-related nouns
    material_keywords = [
        "silk", "fabric", "thread", "dye", "water", "basin", "chalk",
        "needle", "cotton", "yarn", "pot", "vessel", "mordant", "salt",
        "indigo", "turmeric", "marigold", "natural", "chemical",
    ]
    materials_visible = list({
        kw.title()
        for kw in material_keywords
        if kw in description_lower
    })

    # Techniques visible
    technique_keywords = [
        "tying", "binding", "resist", "dyeing", "folding", "pleating",
        "stitching", "clamping", "waxing", "printing", "weaving",
    ]
    techniques_visible = list({
        kw.title()
        for kw in technique_keywords
        if kw in description_lower
    })

    # Quality indicators — sensory / visual quality language
    quality_patterns = [
        r"even[ly]*\s+\w+",
        r"consistent\s+\w+",
        r"crisp\s+\w+",
        r"vibrant\s+\w+",
        r"uniform\s+\w+",
        r"sharp\s+\w+",
        r"colour\s+\w+",
        r"color\s+\w+",
    ]
    quality_indicators = []
    for pattern in quality_patterns:
        matches = re.findall(pattern, description_lower)
        quality_indicators.extend(matches)
    quality_indicators = list(set(quality_indicators)) or [
        "Uniform colour saturation",
        "Consistent knot size",
        "Clean resist boundaries",
    ]

    # Knowledge gaps — what cannot be inferred from a visual alone
    knowledge_gaps = [
        "Exact knot tension (tactile — not visible)",
        "Dye temperature and duration",
        "Artisan's timing judgments and internal cues",
        "Thread type and strength specification",
        "Sequence of pattern decisions",
    ]
    if not observable_steps:
        knowledge_gaps.append("Process sequence unclear — more description needed")

    return {
        "observable_steps": observable_steps or [
            "Could not extract steps automatically — please provide more detail"
        ],
        "materials_visible": materials_visible or ["No specific materials identified"],
        "techniques_visible": techniques_visible or ["No specific techniques identified"],
        "quality_indicators": quality_indicators,
        "knowledge_gaps": knowledge_gaps,
        "craft_context": craft_context,
    }
