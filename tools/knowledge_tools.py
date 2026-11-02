"""
Knowledge persistence tools for the SKILL DNA platform.

Handles saving and loading Skill Fingerprints to/from the local filesystem.
In a production deployment these would be backed by Amazon DynamoDB and S3.
"""
import json
import pathlib
from datetime import datetime

try:
    from strands import tool
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "strands-agents is not installed. Run: pip install strands-agents"
    ) from exc

# Base directory for all persisted fingerprints
_FINGERPRINT_DIR = pathlib.Path("/Users/madhumithaa/Desktop/Skill DNA/data/skill_fingerprints")


@tool
def save_skill_fingerprint(fingerprint_json: str, craft_name: str) -> dict:
    """Save a Skill Fingerprint JSON string to disk.

    The file is written to:
        data/skill_fingerprints/{craft_name}_{timestamp}.json

    Args:
        fingerprint_json: JSON string representation of the Skill Fingerprint.
        craft_name: Human-readable craft name used in the filename.

    Returns:
        dict with keys: status ("saved" | "error"), path (str), craft_name (str).
    """
    try:
        _FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)

        # Validate JSON
        data = json.loads(fingerprint_json)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = craft_name.lower().replace(" ", "_").replace("/", "_")
        filepath = _FINGERPRINT_DIR / f"{safe_name}_{timestamp}.json"

        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

        return {
            "status": "saved",
            "path": str(filepath),
            "craft_name": craft_name,
            "timestamp": timestamp,
        }
    except json.JSONDecodeError as exc:
        return {"status": "error", "error": f"Invalid JSON: {exc}", "craft_name": craft_name}
    except OSError as exc:
        return {"status": "error", "error": f"File write failed: {exc}", "craft_name": craft_name}


@tool
def load_skill_fingerprint(craft_name: str) -> dict:
    """Load the most recent Skill Fingerprint for the given craft name.

    Searches the skill_fingerprints directory for files whose name starts with
    the sanitised craft_name and returns the most recently saved one.

    Args:
        craft_name: Human-readable craft name to search for.

    Returns:
        dict with the parsed fingerprint data, or an error dict if not found.
    """
    try:
        if not _FINGERPRINT_DIR.exists():
            return {
                "status": "error",
                "error": f"Fingerprint directory does not exist: {_FINGERPRINT_DIR}",
            }

        safe_name = craft_name.lower().replace(" ", "_").replace("/", "_")
        matches = sorted(
            _FINGERPRINT_DIR.glob(f"{safe_name}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not matches:
            return {
                "status": "not_found",
                "error": f"No fingerprint found for craft: {craft_name}",
                "craft_name": craft_name,
            }

        with open(matches[0], "r", encoding="utf-8") as fh:
            data = json.load(fh)

        return {
            "status": "loaded",
            "path": str(matches[0]),
            "craft_name": craft_name,
            "fingerprint": data,
        }
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "error", "error": str(exc), "craft_name": craft_name}
