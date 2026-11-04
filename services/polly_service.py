"""
SKILL DNA — Amazon Polly Service

Generates spoken audio from lesson practice steps and quiz explanations.
Removes the literacy barrier for learners — they can listen to the lesson
instead of (or alongside) reading it.

Voice selection:
  - Indian English (en-IN): Kajal (neural), Raveena, Aditi
  - Tamil is not available in Polly — we use Kajal (en-IN) which is
    the most natural Indian-accented voice for Indian artisans.
  - Future: integrate Amazon Transcribe + translate pipeline for Tamil audio.

Output: MP3 bytes, stored in S3 under lessons/audio/
"""
import hashlib
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION      = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("SKILL_DNA_S3_BUCKET", "skill-dna-fingerprints-902605180945")

# Best Indian-accented neural voice available
DEFAULT_VOICE   = "Kajal"
DEFAULT_ENGINE  = "neural"
AUDIO_PREFIX    = "lessons/audio/"


def _polly():
    return boto3.client("polly", region_name=REGION)


def _s3():
    return boto3.client("s3", region_name=REGION)


def _cache_key(text: str, voice: str) -> str:
    """Generate a stable S3 key from text hash so we don't re-synthesize identical text."""
    h = hashlib.sha256(f"{voice}:{text}".encode()).hexdigest()[:16]
    return f"{AUDIO_PREFIX}{voice.lower()}/{h}.mp3"


def synthesize_speech(
    text: str,
    voice_id: str = DEFAULT_VOICE,
    engine: str = DEFAULT_ENGINE,
    cache: bool = True,
) -> dict:
    """
    Convert text to speech using Amazon Polly and store the MP3 in S3.

    Args:
        text:     The text to speak (max ~3000 chars per call).
        voice_id: Polly voice ID. Default: Kajal (Indian English neural).
        engine:   'neural' or 'standard'. Neural is higher quality.
        cache:    If True, reuse existing S3 audio for identical text+voice.

    Returns:
        dict with status, s3_uri, audio_url (presigned 1-hour link), bytes_size.
    """
    # Truncate for Polly limits
    text = text[:2900].strip()
    if not text:
        return {"status": "error", "error": "Empty text"}

    s3_key = _cache_key(text, voice_id)

    # Check cache first
    if cache:
        try:
            _s3().head_object(Bucket=BUCKET_NAME, Key=s3_key)
            # Already exists — generate presigned URL
            url = _s3().generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": s3_key},
                ExpiresIn=3600,
            )
            return {
                "status":    "cached",
                "s3_uri":    f"s3://{BUCKET_NAME}/{s3_key}",
                "audio_url": url,
                "voice_id":  voice_id,
            }
        except ClientError:
            pass  # Not cached — synthesize

    try:
        response = _polly().synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine,
            TextType="text",
        )
        audio_bytes = response["AudioStream"].read()

        # Store in S3
        _s3().put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=audio_bytes,
            ContentType="audio/mpeg",
            Metadata={"voice_id": voice_id, "engine": engine},
        )

        url = _s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,
        )
        return {
            "status":     "synthesized",
            "s3_uri":     f"s3://{BUCKET_NAME}/{s3_key}",
            "audio_url":  url,
            "bytes_size": len(audio_bytes),
            "voice_id":   voice_id,
            "engine":     engine,
        }
    except ClientError as exc:
        return {"status": "error", "error": str(exc)}


def synthesize_lesson_step(step: dict, voice_id: str = DEFAULT_VOICE) -> dict:
    """
    Synthesize a full practice step as spoken audio.

    Combines: instruction + sensory checkpoint + common mistake warning.

    Args:
        step:     A PracticeStep dict with instruction, what_to_watch_for, common_mistakes.
        voice_id: Polly voice.

    Returns:
        dict with audio_url for the step.
    """
    instruction = step.get("instruction", "")
    watch_for   = step.get("what_to_watch_for", step.get("watch_for", ""))
    mistake     = step.get("common_mistakes", step.get("common_mistake", ""))

    parts = [f"Step {step.get('step_number', '')}. {instruction}"]
    if watch_for:
        parts.append(f"What to feel and watch for: {watch_for}")
    if mistake:
        parts.append(f"Common mistake to avoid: {mistake}")

    full_text = " ... ".join(parts)
    return synthesize_speech(full_text, voice_id=voice_id)


def synthesize_quiz_explanation(question: dict, voice_id: str = DEFAULT_VOICE) -> dict:
    """
    Synthesize a quiz question and its explanation as audio.

    Args:
        question: A QuizQuestion dict with question, correct_answer, explanation.
        voice_id: Polly voice.

    Returns:
        dict with audio_url.
    """
    q    = question.get("question", "")
    ans  = question.get("correct_answer", "")
    expl = question.get("explanation", "")

    text = f"Question: {q} ... The correct answer is: {ans}. {expl}"
    return synthesize_speech(text, voice_id=voice_id)


def get_available_voices() -> list:
    """List available Indian English voices in Polly."""
    try:
        r = _polly().describe_voices(LanguageCode="en-IN")
        return [
            {"id": v["Id"], "name": v["Name"], "gender": v["Gender"],
             "engine": v.get("SupportedEngines", [])}
            for v in r["Voices"]
        ]
    except ClientError:
        return []
