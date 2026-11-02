"""
Observer Agent — extracts structured process knowledge from artisan descriptions.

This agent analyses a free-text description of a craft demonstration and
returns a structured dict of visible steps, tools, materials, and knowledge
gaps that the Interviewer Agent will target with follow-up questions.
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


OBSERVER_SYSTEM_PROMPT = """You are an expert craft observer and process analyst specialising in traditional artisan techniques.
Your role is to carefully observe craft demonstrations and extract structured, actionable process knowledge.
You identify: visible steps and their sequence, tools and materials used, techniques applied, and critically —
what is NOT visible or unclear from observation alone (the tacit knowledge gaps).
Be precise, systematic, and thorough. Your output enables the next agent to ask targeted questions."""


if _STRANDS_AVAILABLE:
    @tool
    def extract_craft_steps(artisan_description: str) -> dict:
        """Extract structured craft process steps from an artisan description.

        Args:
            artisan_description: Text description of the craft process from the artisan.

        Returns:
            dict with keys: visible_steps (list), tools_identified (list),
                            materials_identified (list), knowledge_gaps (list)
        """
        return {
            "artisan_description": artisan_description,
            "instruction": (
                "Analyse the description and extract: visible_steps, "
                "tools_identified, materials_identified, knowledge_gaps"
            ),
        }


class ObserverAgent:
    """Strands Agent that observes craft demonstrations and extracts structured knowledge."""

    def __init__(self) -> None:
        if not _STRANDS_AVAILABLE:
            raise ImportError(
                f"strands-agents is required for ObserverAgent: {_STRANDS_IMPORT_ERROR}"
            )
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "claude-3-5-sonnet-20241022")

        bedrock_client = boto3.client("bedrock-runtime", region_name=region)
        model = BedrockModel(model_id=model_id, boto3_client=bedrock_client)

        self.agent = Agent(
            model=model,
            system_prompt=OBSERVER_SYSTEM_PROMPT,
            tools=[extract_craft_steps],
        )

    def analyze(self, artisan_description: str) -> dict:
        """Analyse an artisan description and return structured observation.

        Args:
            artisan_description: Free-text craft process description.

        Returns:
            dict with visible_steps, tools_identified, materials_identified,
            knowledge_gaps, and optionally raw_analysis.
        """
        prompt = f"""Analyse this artisan craft description and extract structured process knowledge:

{artisan_description}

Use the extract_craft_steps tool and return a JSON with:
- visible_steps: ordered list of observable process steps
- tools_identified: list of tools/equipment mentioned or implied
- materials_identified: list of materials mentioned or implied
- knowledge_gaps: list of things NOT visible or unclear that need artisan interview questions"""

        result = self.agent(prompt)
        return self._parse_response(str(result))

    def _parse_response(self, response_text: str) -> dict:
        """Parse the agent response into a structured dict."""
        # Try to extract the first complete JSON object
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: wrap the raw text so callers always get the expected keys
        return {
            "visible_steps": [],
            "tools_identified": [],
            "materials_identified": [],
            "knowledge_gaps": ["Full artisan interview needed"],
            "raw_analysis": response_text,
        }
