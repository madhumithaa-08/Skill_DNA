"""
SKILL DNA — Amazon DynamoDB Service

Persists learner progress — quiz scores, completed steps, session history —
across API calls and browser sessions. Replaces the FileSessionManager
disk storage with a proper cloud-native, multi-user store.

Tables:
  skill-dna-learner-progress  — learner quiz scores and step completion
  skill-dna-fingerprints      — fingerprint metadata index (S3 is source of truth)
"""
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION                  = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
PROGRESS_TABLE          = "skill-dna-learner-progress"
FINGERPRINTS_INDEX_TABLE = "skill-dna-fingerprints"


def _ddb():
    return boto3.resource("dynamodb", region_name=REGION)


def _float_to_decimal(obj):
    """DynamoDB requires Decimal for floats."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _float_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_float_to_decimal(i) for i in obj]
    return obj


def _decimal_to_float(obj):
    """Convert DynamoDB Decimal back to float for JSON serialisation."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimal_to_float(i) for i in obj]
    return obj


# ---------------------------------------------------------------------------
# Learner Progress
# ---------------------------------------------------------------------------

def save_learner_progress(
    learner_id: str,
    craft_name: str,
    quiz_score: Optional[int] = None,
    total_questions: Optional[int] = None,
    completed_steps: Optional[list] = None,
    completed_objectives: Optional[list] = None,
    session_note: Optional[str] = None,
) -> dict:
    """
    Save or update a learner's progress for a specific craft.

    Args:
        learner_id:           Unique learner identifier.
        craft_name:           The craft being studied.
        quiz_score:           Score on the most recent quiz attempt.
        total_questions:      Total quiz questions.
        completed_steps:      List of completed practice step indices.
        completed_objectives: List of completed learning objective indices.
        session_note:         Free-text note from the Mentor Agent.

    Returns:
        dict with status.
    """
    try:
        table = _ddb().Table(PROGRESS_TABLE)
        timestamp = datetime.utcnow().isoformat()

        update_expr   = "SET updated_at = :ts"
        expr_values   = {":ts": timestamp}
        expr_names    = {}

        if quiz_score is not None:
            update_expr += ", latest_quiz_score = :qs, total_questions = :tq"
            expr_values[":qs"] = quiz_score
            expr_values[":tq"] = total_questions or 0

            # Append to quiz history
            update_expr += ", quiz_history = list_append(if_not_exists(quiz_history, :empty), :qh)"
            expr_values[":empty"] = []
            expr_values[":qh"] = [{
                "score": quiz_score,
                "total": total_questions or 0,
                "pct":   Decimal(str(round(quiz_score / (total_questions or 1) * 100, 1))),
                "ts":    timestamp,
            }]

        if completed_steps is not None:
            update_expr += ", completed_steps = :cs"
            expr_values[":cs"] = completed_steps

        if completed_objectives is not None:
            update_expr += ", completed_objectives = :co"
            expr_values[":co"] = completed_objectives

        if session_note:
            update_expr += ", last_mentor_note = :mn"
            expr_values[":mn"] = session_note

        table.update_item(
            Key={"learner_id": learner_id, "craft_name": craft_name},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=_float_to_decimal(expr_values),
        )
        return {"status": "saved", "learner_id": learner_id, "craft_name": craft_name}
    except ClientError as exc:
        return {"status": "error", "error": str(exc)}


def get_learner_progress(learner_id: str, craft_name: str) -> dict:
    """
    Retrieve a learner's progress for a specific craft.

    Returns:
        dict with progress data, or empty defaults if not found.
    """
    try:
        table = _ddb().Table(PROGRESS_TABLE)
        result = table.get_item(Key={"learner_id": learner_id, "craft_name": craft_name})
        item = result.get("Item")
        if not item:
            return {
                "status":               "not_found",
                "learner_id":           learner_id,
                "craft_name":           craft_name,
                "latest_quiz_score":    None,
                "quiz_history":         [],
                "completed_steps":      [],
                "completed_objectives": [],
                "last_mentor_note":     None,
            }
        return {"status": "found", **_decimal_to_float(dict(item))}
    except ClientError as exc:
        return {"status": "error", "error": str(exc)}


def get_all_learner_crafts(learner_id: str) -> list:
    """Get all crafts a learner has studied."""
    try:
        table  = _ddb().Table(PROGRESS_TABLE)
        result = table.query(KeyConditionExpression=Key("learner_id").eq(learner_id))
        return [_decimal_to_float(dict(item)) for item in result.get("Items", [])]
    except ClientError:
        return []


# ---------------------------------------------------------------------------
# Fingerprint Index
# ---------------------------------------------------------------------------

def index_fingerprint(fingerprint: dict, s3_uri: str) -> dict:
    """
    Write a lightweight index record for a Skill Fingerprint to DynamoDB.
    S3 holds the full JSON; DynamoDB holds the searchable metadata.
    """
    try:
        table      = _ddb().Table(FINGERPRINTS_INDEX_TABLE)
        craft_id   = fingerprint.get("craft_name", "unknown").lower().replace(" ", "_")
        version    = fingerprint.get("version", "1.0")
        timestamp  = datetime.utcnow().isoformat()

        table.put_item(Item={
            "craft_id":            craft_id,
            "version":             f"{version}_{timestamp}",
            "craft_name":          fingerprint.get("craft_name", ""),
            "artisan_name":        fingerprint.get("artisan_name", ""),
            "craft_origin":        fingerprint.get("craft_origin", ""),
            "techniques_count":    len(fingerprint.get("techniques", [])),
            "materials_count":     len(fingerprint.get("materials", [])),
            "decisions_count":     len(fingerprint.get("decisions", [])),
            "artisan_approved":    fingerprint.get("artisan_approved", False),
            "s3_uri":              s3_uri,
            "created_at":          timestamp,
        })
        return {"status": "indexed", "craft_id": craft_id}
    except ClientError as exc:
        return {"status": "error", "error": str(exc)}


def list_all_fingerprints_index() -> list:
    """List all indexed Skill Fingerprints from DynamoDB."""
    try:
        table  = _ddb().Table(FINGERPRINTS_INDEX_TABLE)
        result = table.scan()
        items  = result.get("Items", [])
        return sorted(
            [_decimal_to_float(dict(i)) for i in items],
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )
    except ClientError:
        return []
