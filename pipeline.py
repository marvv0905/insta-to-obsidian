import os
import subprocess
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

import httpx
from faster_whisper import WhisperModel
from openai import OpenAI

YT_DLP = os.path.join(os.path.dirname(sys.executable), "yt-dlp")

_whisper_model = None


def _get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        model_size = os.getenv("WHISPER_MODEL", "base")
        print(f"[pipeline] Loading faster-whisper model '{model_size}'...")
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="auto")
        print("[pipeline] Model loaded.")
    return _whisper_model


def download_audio(reel_url: str) -> Path:
    uid = uuid.uuid4().hex[:12]
    output_template = f"/tmp/reel_{uid}.%(ext)s"
    output_path = Path(f"/tmp/reel_{uid}.mp3")

    print(f"[pipeline] Downloading audio from: {reel_url}")
    result = subprocess.run(
        [
            YT_DLP,
            "-x",
            "--audio-format", "mp3",
            "-o", output_template,
            "--no-playlist",
            "--no-simulate",
            "--quiet",
            reel_url,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Download failed: {stderr}")

    if not output_path.exists():
        raise RuntimeError("Download completed but audio file not found")

    print(f"[pipeline] Audio saved to: {output_path}")
    return output_path


def transcribe(audio_path: Path) -> str:
    print(f"[pipeline] Transcribing: {audio_path}")
    model = _get_whisper_model()
    segments, info = model.transcribe(str(audio_path))

    text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())

    if not text:
        raise RuntimeError("Transcription produced empty text — reel may have no speech")

    print(f"[pipeline] Transcription complete ({len(text)} chars)")
    return text


def summarize(transcript: str, reel_url: str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set in bot.env")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    today = date.today().isoformat()

    print(f"[pipeline] Summarizing with {model}...")

    client = OpenAI(base_url=base_url, api_key=api_key)

    template = f"""---
source: {reel_url}
date: {today}
tags: [topic1, topic2, topic3]
---

# [Descriptive Title Here]

## Summary
- [key point 1]
- [key point 2]
- [key point 3]
- [key point 4]
- [key point 5]

## Full Transcript
<details><summary>Raw Transcript</summary>

{{{{paste the full transcript here}}}}

</details>"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise knowledge organizer. "
                    "You receive transcripts from educational Instagram Reels and output structured Markdown notes. "
                    "Fill in the provided template using the transcript content. "
                    "Choose 3-5 relevant tags. Keep the summary brief and focused on key takeaways. "
                    "Return ONLY the completed Markdown, no other text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Transcript:\n---\n{transcript}\n---\n\n"
                    f"Fill in this template using the transcript above:\n\n{template}"
                ),
            },
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Summarization returned empty response")

    print(f"[pipeline] Summarization complete ({len(content)} chars)")
    return content.strip()


def _ensure_webdav_folders(webdav_base: str, folder_path: str, auth: tuple) -> None:
    segments = [s for s in folder_path.strip("/").split("/") if s]
    current = ""
    for segment in segments:
        current += f"/{segment}"
        url = f"{webdav_base}{current}"
        resp = httpx.request("MKCOL", url, auth=auth)
        if resp.status_code not in (201, 405):
            resp.raise_for_status()


def save_to_nextcloud(markdown: str) -> str:
    base_url = os.getenv("NEXTCLOUD_URL")
    username = os.getenv("NEXTCLOUD_USERNAME")
    password = os.getenv("NEXTCLOUD_APP_PASSWORD")
    notes_path = os.getenv("NEXTCLOUD_NOTES_PATH", "IG-Bot")

    if not all([base_url, username, password]):
        raise RuntimeError(
            "NEXTCLOUD_URL, NEXTCLOUD_USERNAME, and NEXTCLOUD_APP_PASSWORD "
            "must be set in bot.env"
        )

    base_url = base_url.rstrip("/")
    if "/remote.php/dav/files/" in base_url:
        base_url = base_url.split("/remote.php/dav/files/")[0]
    auth = (username, password)
    webdav_base = f"{base_url}/remote.php/dav/files/{username}"

    filename = f"reel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    webdav_url = f"{webdav_base}/{notes_path}/{filename}"

    print(f"[pipeline] Saving to Nextcloud: {webdav_url}")
    _ensure_webdav_folders(webdav_base, notes_path, auth)

    resp = httpx.put(webdav_url, content=markdown.encode("utf-8"), auth=auth)
    if resp.status_code not in (200, 201, 204):
        raise RuntimeError(
            f"Nextcloud upload failed (HTTP {resp.status_code}): {resp.text}"
        )

    print(f"[pipeline] Saved to Nextcloud: {webdav_url}")
    return webdav_url
