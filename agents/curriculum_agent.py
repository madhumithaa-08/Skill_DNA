"""
Curriculum Agent — generates structured lesson modules from Skill Fingerprints.
"""
import json
import os
import re
import sys
from pathlib import Path

# Ensure project root is on the path so models can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import boto3
    from dotenv import load_dotenv
    from strands import Agent, tool
    from strands.models import BedrockModel

    load_dotenv()
    _STRANDS_AVAILABLE = True
except ImportError as _err:
    _STRANDS_AVAILABLE = False
    _STRANDS_IMPORT_ERROR = str(_err)

from models.lesson import LessonModule, PracticeStep, QuizQuestion  # noqa: F401


CURRICULUM_SYSTEM_PROMPT = """You are an expert curriculum designer who creates accessible, engaging craft lessons
from structured Skill DNA fingerprints.
You turn expert knowledge into beginner-friendly learning journeys.
Every lesson you create: starts with context and cultural meaning, builds skills progressively,
uses concrete sensory language ('the silk should feel smooth as water'), includes checkpoints for self-assessment,
and ends with a quiz that tests real understanding not just memorisation.
Your lessons honour the craft tradition while making it accessible to global learners."""


if _STRANDS_AVAILABLE:
    @tool
    def generate_lesson_module(
        craft_name: str,
        techniques_json: str,
        decisions_json: str,
        common_mistakes_json: str,
        cultural_significance: str,
        level: str = "beginner",
    ) -> dict:
        """Generate a complete lesson module from a Skill Fingerprint.

        Args:
            craft_name: Name of the craft.
            techniques_json: JSON string of technique objects.
            decisions_json: JSON string of decision objects.
            common_mistakes_json: JSON string of common mistake objects.
            cultural_significance: Cultural context text.
            level: Difficulty level (beginner/intermediate/advanced).

        Returns:
            dict with instruction for the LLM to build the full lesson.
        """
        return {
            "craft_name": craft_name,
            "level": level,
            "techniques": json.loads(techniques_json) if isinstance(techniques_json, str) else techniques_json,
            "instruction": "Create a complete LessonModule with 5-7 practice steps and 5 quiz questions",
        }


class CurriculumAgent:
    """Strands Agent that generates structured lesson modules from Skill Fingerprints."""

    def __init__(self) -> None:
        if not _STRANDS_AVAILABLE:
            raise ImportError(
                f"strands-agents is required for CurriculumAgent: {_STRANDS_IMPORT_ERROR}"
            )
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")

        os.environ.setdefault("AWS_DEFAULT_REGION", region)
        model = BedrockModel(model_id=model_id)

        self.agent = Agent(
            model=model,
            system_prompt=CURRICULUM_SYSTEM_PROMPT,
            tools=[generate_lesson_module],
        )

    def create_lesson(self, fingerprint: dict) -> dict:
        """Create a beginner lesson module from a Skill Fingerprint.

        Args:
            fingerprint: Dict representation of a SkillFingerprint.

        Returns:
            dict with the complete lesson data.
        """
        techniques = json.dumps(fingerprint.get("techniques", []))
        decisions = json.dumps(fingerprint.get("decisions", []))
        mistakes = json.dumps(fingerprint.get("common_mistakes", []))
        cultural = fingerprint.get("cultural_significance", "")
        craft = fingerprint.get("craft_name", "Traditional Craft")

        prompt = f"""Create a complete beginner lesson module for '{craft}'.

Use the generate_lesson_module tool with this Skill Fingerprint data.

The lesson MUST include:
1. A compelling title and cultural overview
2. 4-5 specific learning objectives
3. 5-7 practice steps with:
   - Clear instruction
   - What to watch for (sensory cues)
   - Common mistake to avoid at this step
4. 5 quiz questions testing real understanding, each with:
   - 4 multiple choice options
   - Correct answer
   - Explanation that teaches
5. Estimated duration in minutes

Reference specific techniques from the fingerprint — do not write generic craft lesson content.
Cultural significance: {cultural}"""

        result = self.agent(prompt)
        return self._parse_lesson(str(result))

    def _parse_lesson(self, response_text: str) -> dict:
        """Parse a lesson dict from the agent response text."""
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {"raw": response_text}
