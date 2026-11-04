"""
Interviewer Agent — generates targeted questions to extract tacit craft knowledge.

Tacit knowledge (how things feel, sound, smell; when to stop; how to recover
from mistakes) is the hardest craft knowledge to capture and the most valuable
for learners. This agent specialises in drawing it out.
"""
import json
import os
import re

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


INTERVIEWER_SYSTEM_PROMPT = """You are an expert ethnographic interviewer specialising in tacit craft knowledge extraction.
You understand that the most valuable craft knowledge is often unspoken: muscle memory, sensory cues, judgment calls,
and experiential wisdom that masters cannot easily articulate. Your questions draw out this hidden knowledge.
Ask about: physical sensations (how it feels, sounds, smells), timing and pace, when to stop,
how to recognise quality vs defects, what to do when things go wrong, and the 'why' behind each choice.
Questions should be specific, practical, and avoid yes/no answers."""


if _STRANDS_AVAILABLE:
    @tool
    def generate_artisan_questions(knowledge_gaps: list, craft_name: str) -> dict:
        """Generate targeted interview questions to fill knowledge gaps in craft documentation.

        Args:
            knowledge_gaps: List of identified gaps from the ObserverAgent.
            craft_name: Name of the craft being documented.

        Returns:
            dict with instruction for the LLM to generate question strings.
        """
        return {
            "knowledge_gaps": knowledge_gaps,
            "craft_name": craft_name,
            "instruction": (
                "Generate specific, practical questions that extract tacit knowledge for each gap"
            ),
        }


class InterviewerAgent:
    """Strands Agent that generates targeted questions to extract tacit craft knowledge."""

    def __init__(self) -> None:
        if not _STRANDS_AVAILABLE:
            raise ImportError(
                f"strands-agents is required for InterviewerAgent: {_STRANDS_IMPORT_ERROR}"
            )
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")

        os.environ.setdefault("AWS_DEFAULT_REGION", region)
        model = BedrockModel(model_id=model_id)

        self.agent = Agent(
            model=model,
            system_prompt=INTERVIEWER_SYSTEM_PROMPT,
            tools=[generate_artisan_questions],
        )

    def generate_questions(self, knowledge_gaps: list, craft_name: str) -> list:
        """Generate targeted questions based on identified knowledge gaps.

        Args:
            knowledge_gaps: List of gaps identified by the ObserverAgent.
            craft_name: Name of the craft being documented.

        Returns:
            list of question strings.
        """
        gaps_text = "\n".join(f"- {gap}" for gap in knowledge_gaps)
        prompt = f"""For the craft '{craft_name}', generate targeted interview questions for these knowledge gaps:

{gaps_text}

Use the generate_artisan_questions tool. Create 6-8 specific questions that:
1. Extract sensory/tactile knowledge (how it feels, sounds)
2. Capture timing and judgment (when to stop, how to know it's right)
3. Reveal decision-making (why this material/technique over alternatives)
4. Document error recovery (what to do when things go wrong)
5. Preserve cultural context and significance

Return a JSON list of question strings."""

        result = self.agent(prompt)
        return self._parse_questions(str(result))

    def _parse_questions(self, response_text: str) -> list:
        """Parse the agent response to extract a list of question strings."""
        # Try to extract a JSON array
        json_match = re.search(r"\[[\s\S]*\]", response_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Fallback: pull out lines that look like questions
        questions = [
            line.strip().lstrip("0123456789.-) ")
            for line in response_text.split("\n")
            if "?" in line and len(line.strip()) > 20
        ]
        return questions if questions else [
            "How do you know when the process is complete?",
            "What does the material feel like at each stage?",
            "What are the most common mistakes beginners make?",
        ]
