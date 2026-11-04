"""
SKILL DNA — Amazon S3 Service

Stores and retrieves Skill Fingerprints as JSON objects in S3.
Replaces the local data/skill_fingerprints/ file storage with
a proper cloud-native, persistent, shareable store.

Bucket: skill-dna-fingerprints-{account_id}
Key pattern: fingerprints/{craft_id}/{version}.json
"""
import json
import os
from datetime import datetime
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION      = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("SKILL_DNA_S3_BUCKET", "skill-dna-fingerprints-902605180945")


def _s3():
    return boto3.client("s3", region_name=REGION)


def save_fingerprint_to_s3(fingerprint: dict, craft_name: str) -> dict:
    """
    Save a Skill Fingerprint to Amazon S3.

    Args:
        fingerprint: The SkillFingerprint dict.
        craft_name:  Human-readable craft name (used in the S3 key).

    Returns:
        dict with status, s3_uri, craft_name.
    """
    try:
        timestamp  = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        craft_id   = craft_name.lower().replace(" ", "_").replace("/", "_")
        s3_key     = f"fingerprints/{craft_id}/{timestamp}.json"

        _s3().put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(fingerprint, ensure_ascii=False, indent=2).encode("utf-8"),
            ContentType="application/json",
            Metadata={
                "craft_name":    craft_name,
                "artisan_name":  fingerprint.get("artisan_name", ""),
                "version":       fingerprint.get("version", "1.0"),
                "created_at":    timestamp,
            },
        )
        s3_uri = f"s3://{BUCKET_NAME}/{s3_key}"
        return {
            "status":     "saved",
            "s3_uri":     s3_uri,
            "s3_key":     s3_key,
            "craft_name": craft_name,
            "timestamp":  timestamp,
        }
    except ClientError as exc:
        return {"status": "error", "error": str(exc), "craft_name": craft_name}


def load_fingerprint_from_s3(craft_name: str, version: Optional[str] = None) -> dict:
    """
    Load the latest (or specific) Skill Fingerprint from S3 for a given craft.

    Args:
        craft_name: Human-readable craft name.
        version:    Optional timestamp string to load a specific version.

    Returns:
        dict with status and fingerprint data.
    """
    try:
        craft_id = craft_name.lower().replace(" ", "_").replace("/", "_")
        prefix   = f"fingerprints/{craft_id}/"

        if version:
            s3_key = f"{prefix}{version}.json"
        else:
            # List all versions and pick the most recent
            paginator = _s3().get_paginator("list_objects_v2")
            objects   = []
            for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
                objects.extend(page.get("Contents", []))

            if not objects:
                return {"status": "not_found", "error": f"No fingerprint for craft: {craft_name}"}

            # Most recent by LastModified
            s3_key = max(objects, key=lambda o: o["LastModified"])["Key"]

        response = _s3().get_object(Bucket=BUCKET_NAME, Key=s3_key)
        data     = json.loads(response["Body"].read().decode("utf-8"))
        return {
            "status":      "loaded",
            "s3_uri":      f"s3://{BUCKET_NAME}/{s3_key}",
            "craft_name":  craft_name,
            "fingerprint": data,
        }
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            return {"status": "not_found", "error": f"No fingerprint found for: {craft_name}"}
        return {"status": "error", "error": str(exc)}


def list_fingerprints_in_s3() -> list:
    """
    List all Skill Fingerprints stored in S3, grouped by craft.

    Returns:
        List of dicts with craft_name, s3_uri, timestamp, metadata.
    """
    try:
        paginator = _s3().get_paginator("list_objects_v2")
        results   = []
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="fingerprints/"):
            for obj in page.get("Contents", []):
                key    = obj["Key"]
                parts  = key.split("/")
                if len(parts) >= 3:
                    craft_id  = parts[1]
                    timestamp = parts[2].replace(".json", "")
                    results.append({
                        "craft_id":   craft_id,
                        "craft_name": craft_id.replace("_", " ").title(),
                        "s3_key":     key,
                        "s3_uri":     f"s3://{BUCKET_NAME}/{key}",
                        "timestamp":  timestamp,
                        "size_bytes": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                    })
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)
    except ClientError as exc:
        return []
