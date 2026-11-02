"""
General-purpose helpers for the SKILL DNA platform.
"""
import logging
import os
import re

logger = logging.getLogger(__name__)


def format_fingerprint_summary(fingerprint: dict) -> str:
    """Return a human-readable summary of a Skill Fingerprint.

    Args:
        fingerprint: Dict representation of a SkillFingerprint object.

    Returns:
        A multi-line string summarising the key fields.
    """
    lines = [
        f"Craft: {fingerprint.get('craft_name', 'Unknown')}",
        f"Origin: {fingerprint.get('craft_origin', 'Unknown')}",
        f"Heritage: {fingerprint.get('craft_heritage', 'Unknown')}",
        f"Artisan: {fingerprint.get('artisan_name', 'Unknown')}",
        f"Artisan Approved: {fingerprint.get('artisan_approved', False)}",
        f"Version: {fingerprint.get('version', '1.0')}",
        f"Created: {fingerprint.get('created_at', 'Unknown')}",
        "",
        f"Materials ({len(fingerprint.get('materials', []))}): "
        + ", ".join(m.get("name", "") if isinstance(m, dict) else str(m)
                    for m in fingerprint.get("materials", [])),
        f"Techniques ({len(fingerprint.get('techniques', []))}): "
        + ", ".join(t.get("name", "") if isinstance(t, dict) else str(t)
                    for t in fingerprint.get("techniques", [])),
        f"Decision Points ({len(fingerprint.get('decisions', []))}): "
        + ", ".join(d.get("decision_point", "") if isinstance(d, dict) else str(d)
                    for d in fingerprint.get("decisions", [])),
        f"Common Mistakes: {len(fingerprint.get('common_mistakes', []))}",
        f"Mastery Requirements: {len(fingerprint.get('mastery_requirements', []))}",
        "",
        "Cultural Significance:",
        fingerprint.get("cultural_significance", "Not documented."),
    ]
    return "\n".join(lines)


def sanitise_craft_name(name: str) -> str:
    """Convert a craft name to a filesystem-safe string.

    Lowercases, replaces spaces with underscores, and strips any characters
    that are not alphanumeric, underscores, or hyphens.

    Args:
        name: Human-readable craft name, e.g. "Madurai Sungudi".

    Returns:
        Sanitised string, e.g. "madurai_sungudi".
    """
    lower = name.lower().strip()
    underscored = lower.replace(" ", "_")
    safe = re.sub(r"[^\w\-]", "", underscored)
    return safe


def load_env_or_default(key: str, default: str) -> str:
    """Load an environment variable, falling back to a default.

    Logs a warning at DEBUG level when the default is used, so callers know
    the real value was not configured.

    Args:
        key: Environment variable name.
        default: Value to return when the variable is absent or empty.

    Returns:
        The env var value, or the default.
    """
    value = os.environ.get(key, "").strip()
    if not value:
        logger.debug(
            "Environment variable %r not set — using default %r", key, default
        )
        return default
    return value
