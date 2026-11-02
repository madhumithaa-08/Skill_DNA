"""
Pydantic v2 models for the SKILL DNA Skill Fingerprint.

A SkillFingerprint captures the complete, structured knowledge of a traditional craft
as observed and extracted by the multi-agent pipeline.
"""
import json
from typing import Literal
from pydantic import BaseModel, ConfigDict


class Material(BaseModel):
    """A material or input used in the craft process."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    description: str
    source: str


class Technique(BaseModel):
    """A discrete technique or process step in the craft."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    stage: str
    description: str
    duration_estimate: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    tips: list[str]


class Decision(BaseModel):
    """A critical decision point where artisan judgment is applied."""

    model_config = ConfigDict(str_strip_whitespace=True)

    decision_point: str
    options: list[str]
    artisan_choice: str
    reasoning: str


class CommonMistake(BaseModel):
    """A common error made by learners, its consequence, and the correction."""

    model_config = ConfigDict(str_strip_whitespace=True)

    mistake: str
    consequence: str
    correction: str


class MasteryRequirement(BaseModel):
    """A skill that demonstrates mastery of the craft."""

    model_config = ConfigDict(str_strip_whitespace=True)

    skill: str
    how_to_demonstrate: str


class SkillFingerprint(BaseModel):
    """
    The complete structured knowledge representation of a traditional craft.

    Captures materials, techniques, decision points, common mistakes,
    mastery requirements, and cultural significance in a format that
    enables AI-generated lesson creation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_encoders={},
    )

    craft_name: str
    craft_origin: str
    craft_heritage: str
    artisan_name: str
    artisan_approved: bool = False
    materials: list[Material]
    techniques: list[Technique]
    decisions: list[Decision]
    common_mistakes: list[CommonMistake]
    mastery_requirements: list[MasteryRequirement]
    cultural_significance: str
    created_at: str  # ISO datetime string, e.g. "2024-01-15T10:30:00"
    version: str = "1.0"

    def to_json(self, indent: int = 2) -> str:
        """Serialise the SkillFingerprint to a JSON string."""
        return self.model_dump_json(indent=indent)
