"""
SKILL DNA — Amazon Transcribe Service

Converts artisan audio recordings to text for the Artisan Studio.
Supports Tamil (ta-IN) and English (en-IN) — artisans can speak their
craft description instead of typing it.

This removes the literacy barrier for artisans who are more comfortable
speaking than writing.

Supported: .mp3, .mp4, .wav, .flac, .ogg, .amr, .webm
"""
import os
import time
import uuid
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION      = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("SKILL_DNA_S3_BUCKET", "skill-dna-fingerprints-902605180945")
AUDIO_PREFIX = "artisan-audio/"


def _transcribe():
    return boto3.client("transcribe", region_name=REGION)


def _s3():
    return boto3.client("s3", region_name=REGION)


LANGUAGE_MAP = {
    "tamil":   "ta-IN",
    "ta":      "ta-IN",
    "ta-in":   "ta-IN",
    "english": "en-IN",
    "en":      "en-IN",
    "en-in":   "en-IN",
    "hindi":   "hi-IN",
    "hi":      "hi-IN",
}


def upload_audio_and_transcribe(
    audio_bytes: bytes,
    filename: str,
    language: str = "en-IN",
    artisan_name: str = "artisan",
) -> dict:
    """
    Upload audio to S3 and start an Amazon Transcribe job.

    Args:
        audio_bytes:  Raw audio file bytes.
        filename:     Original filename (used to determine format).
        language:     Language code or name (e.g. 'tamil', 'ta-IN', 'en-IN').
        artisan_name: Used to label the Transcribe job.

    Returns:
        dict with job_name and status. Poll with get_transcription_result().
    """
    lang_code = LANGUAGE_MAP.get(language.lower(), language)

    # Upload to S3
    job_id   = uuid.uuid4().hex[:12]
    ext      = Path(filename).suffix.lower().lstrip(".")
    s3_key   = f"{AUDIO_PREFIX}{job_id}/{filename}"
    job_name = f"skill-dna-{artisan_name.lower().replace(' ', '-')[:20]}-{job_id}"

    try:
        _s3().put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=audio_bytes,
            ContentType=f"audio/{ext}",
        )
        s3_uri = f"s3://{BUCKET_NAME}/{s3_key}"

        # Start Transcribe job
        media_format = ext if ext in ("mp3", "mp4", "wav", "flac", "ogg", "amr", "webm") else "mp3"
        _transcribe().start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat=media_format,
            LanguageCode=lang_code,
            OutputBucketName=BUCKET_NAME,
            OutputKey=f"transcripts/{job_id}/",
            Settings={
                "ShowSpeakerLabels": False,
                "ShowAlternatives":  False,
            },
        )
        return {
            "status":    "started",
            "job_name":  job_name,
            "s3_uri":    s3_uri,
            "language":  lang_code,
            "job_id":    job_id,
        }
    except ClientError as exc:
        return {"status": "error", "error": str(exc)}


def get_transcription_result(job_name: str, wait: bool = True, timeout_sec: int = 120) -> dict:
    """
    Poll for a Transcribe job result.

    Args:
        job_name:    The Transcribe job name from upload_audio_and_transcribe().
        wait:        If True, poll until complete or timeout.
        timeout_sec: Max seconds to wait.

    Returns:
        dict with status and transcript text if complete.
    """
    t0 = time.time()
    while True:
        try:
            resp   = _transcribe().get_transcription_job(TranscriptionJobName=job_name)
            job    = resp["TranscriptionJob"]
            status = job["TranscriptionJobStatus"]

            if status == "COMPLETED":
                # Fetch the transcript JSON from S3
                transcript_uri = job["Transcript"]["TranscriptFileUri"]
                # Parse the S3 key from the URI
                import urllib.parse
                parsed    = urllib.parse.urlparse(transcript_uri)
                s3_key    = parsed.path.lstrip("/")
                # Remove bucket name prefix if present
                if s3_key.startswith(BUCKET_NAME + "/"):
                    s3_key = s3_key[len(BUCKET_NAME) + 1:]

                try:
                    obj      = _s3().get_object(Bucket=BUCKET_NAME, Key=s3_key)
                    data     = __import__("json").loads(obj["Body"].read())
                    text     = data["results"]["transcripts"][0]["transcript"]
                    return {"status": "completed", "transcript": text, "job_name": job_name}
                except Exception as exc:
                    # Fallback: return raw transcript URI
                    return {"status": "completed", "transcript": "", "transcript_uri": transcript_uri, "error": str(exc)}

            elif status == "FAILED":
                reason = job.get("FailureReason", "Unknown failure")
                return {"status": "failed", "error": reason, "job_name": job_name}

            elif not wait:
                return {"status": status.lower(), "job_name": job_name}

            # Still in progress
            if time.time() - t0 > timeout_sec:
                return {"status": "timeout", "job_name": job_name, "elapsed_sec": int(time.time() - t0)}

            time.sleep(5)

        except ClientError as exc:
            return {"status": "error", "error": str(exc)}


def transcribe_sync(
    audio_bytes: bytes,
    filename: str,
    language: str = "en-IN",
    artisan_name: str = "artisan",
    timeout_sec: int = 120,
) -> dict:
    """
    Convenience wrapper: upload, start, and wait for transcription.

    Returns the transcript text directly when complete.
    """
    start = upload_audio_and_transcribe(audio_bytes, filename, language, artisan_name)
    if start["status"] != "started":
        return start
    return get_transcription_result(start["job_name"], wait=True, timeout_sec=timeout_sec)
