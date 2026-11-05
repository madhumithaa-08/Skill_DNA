"""
Knowledge Architect Agent — transforms raw observations and interviews into
a structured Skill Fingerprint.
"""
import json
import os
import re
import sys
from datetime import datetime
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

from models.skill_fingerprint import (
    CommonMistake,
    Decision,
    MasteryRequirement,
    Material,
    SkillFingerprint,
    Technique,
)


KNOWLEDGE_ARCHITECT_SYSTEM_PROMPT = """You are a master knowledge architect who transforms raw craft observations
and artisan interviews into structured, reusable Skill DNA.
You synthesise multiple information sources — visual observations, tacit knowledge from interviews,
cultural context — into a comprehensive Skill Fingerprint that can teach future learners.
Your fingerprints are precise, actionable, and honour the cultural heritage of the craft.
Every decision point you document preserves the 'why' behind craft choices.
You think in terms of: What must a learner know? What must they feel? What must they decide?"""


if _STRANDS_AVAILABLE:
    @tool
    def build_skill_fingerprint(
        craft_name: str,
        craft_origin: str,
        craft_heritage: str,
        artisan_name: str,
        materials_json: str,
        techniques_json: str,
        decisions_json: str,
        common_mistakes_json: str,
        mastery_requirements_json: str,
        cultural_significance: str,
    ) -> dict:
        """Build and save a complete Skill Fingerprint from structured craft knowledge.

        Args:
            craft_name: Name of the craft (e.g. 'Madurai Sungudi').
            craft_origin: Geographic origin.
            craft_heritage: Heritage classification (e.g. GI tag).
            artisan_name: Name of the master artisan.
            materials_json: JSON string of materials list.
            techniques_json: JSON string of techniques list.
            decisions_json: JSON string of decisions list.
            common_mistakes_json: JSON string of common mistakes list.
            mastery_requirements_json: JSON string of mastery requirements list.
            cultural_significance: Text description of cultural importance.

        Returns:
            dict with 'status', 'path', and 'fingerprint' keys.
        """
        try:
            def _load(v: str) -> list:
                return json.loads(v) if isinstance(v, str) else v

            fingerprint = SkillFingerprint(
                craft_name=craft_name,
                craft_origin=craft_origin,
                craft_heritage=craft_heritage,
                artisan_name=artisan_name,
                artisan_approved=True,
                materials=_load(materials_json),
                techniques=_load(techniques_json),
                decisions=_load(decisions_json),
                common_mistakes=_load(common_mistakes_json),
                mastery_requirements=_load(mastery_requirements_json),
                cultural_significance=cultural_significance,
                created_at=datetime.utcnow().isoformat(),
                version="1.0",
            )

            save_dir = Path("/Users/madhumithaa/Desktop/Skill DNA/data/skill_fingerprints")
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_name = craft_name.lower().replace(" ", "_")
            filepath = save_dir / f"{safe_name}_{timestamp}.json"

            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(fingerprint.model_dump_json(indent=2))

            return {
                "status": "success",
                "path": str(filepath),
                "fingerprint": fingerprint.model_dump(),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}


class KnowledgeArchitectAgent:
    """Strands Agent that builds structured Skill Fingerprints from craft
    observations and artisan interviews."""

    def __init__(self) -> None:
        if not _STRANDS_AVAILABLE:
            raise ImportError(
                f"strands-agents is required for KnowledgeArchitectAgent: {_STRANDS_IMPORT_ERROR}"
            )
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")

        os.environ.setdefault("AWS_DEFAULT_REGION", region)
        model = BedrockModel(model_id=model_id)

        self.agent = Agent(
            model=model,
            system_prompt=KNOWLEDGE_ARCHITECT_SYSTEM_PROMPT,
            tools=[build_skill_fingerprint],
            callback_handler=None,
        )

    def build_fingerprint(
        self,
        observation: dict,
        qa_answers: dict,
        craft_name: str,
        artisan_name: str,
    ) -> dict:
        """Build a Skill Fingerprint from observation data and artisan Q&A.

        Args:
            observation: Structured output from ObserverAgent.
            qa_answers: Dict mapping question strings to artisan answer strings.
            craft_name: Name of the craft.
            artisan_name: Name of the master artisan.

        Returns:
            dict with 'fingerprint' key (or 'status'/'raw' on failure).
        """
        prompt = f"""Build a complete Skill Fingerprint for the craft '{craft_name}' by master artisan '{artisan_name}'.

OBSERVATION DATA:
{json.dumps(observation, indent=2)}

ARTISAN Q&A ANSWERS:
{json.dumps(qa_answers, indent=2)}

Use the build_skill_fingerprint tool to create a comprehensive fingerprint.
Infer craft_origin and craft_heritage from the craft name and context:
- If the craft has a known geographic origin (e.g. Madurai Sungudi → "Madurai, Tamil Nadu, India"), use it
- If it has a GI tag or UNESCO recognition, mention that in craft_heritage
- For any craft worldwide, document cultural_significance accurately from the Q&A and observation

Extract and structure:
- materials: Every material mentioned with description and source
- techniques: Each step as a technique with difficulty and tips
- decisions: Critical judgment points (when to stop, how tight, what quality looks like)
- common_mistakes: Things beginners get wrong and how to fix them
- mastery_requirements: What skills demonstrate mastery"""

        result = self.agent(prompt)
        return self._extract_fingerprint(str(result))

    def _extract_fingerprint(self, response_text: str) -> dict:
        """Extract fingerprint data from agent response text."""
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {"status": "partial", "raw": response_text}
