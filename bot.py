import asyncio
import io
import os
import re
from datetime import datetime

import discord
from dotenv import load_dotenv

from pipeline import download_audio, transcribe, summarize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "bot.env"))

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

IG_REEL_PATTERN = re.compile(r"(https?://(www\.)?instagram\.com/reel/[^\s]+)")


def _extract_preview(markdown: str, max_chars: int = 1900) -> str:
    lines = markdown.strip().split("\n")
    result = []
    dashes_seen = 0
    for line in lines:
        if line.strip() == "---" and dashes_seen < 2:
            dashes_seen += 1
            continue
        if dashes_seen < 2:
            continue
        result.append(line)
        joined = "\n".join(result)
        if len(joined) > max_chars:
            result[-1] = result[-1][:max_chars - len("\n".join(result[:-1])) - 3] + "..."
            break
    return "\n".join(result)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    match = IG_REEL_PATTERN.search(message.content)
    if not match:
        return

    reel_url = match.group(1)
    status_msg = await message.channel.send("Processing reel...")

    temp_path = None
    try:
        await status_msg.edit(content="Downloading audio...")
        temp_path = await asyncio.to_thread(download_audio, reel_url)

        await status_msg.edit(content="Transcribing (this may take a minute)...")
        transcript = await asyncio.to_thread(transcribe, temp_path)

        await status_msg.edit(content="Summarizing with AI...")
        markdown = await asyncio.to_thread(summarize, transcript, reel_url)

        preview = _extract_preview(markdown)
        filename = f"reel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file = discord.File(io.BytesIO(markdown.encode("utf-8")), filename=filename)

        await status_msg.delete()
        await message.channel.send(content=preview, file=file)

    except FileNotFoundError as e:
        await status_msg.edit(content=f"Dependency missing: {e}. Run `pip install yt-dlp faster-whisper openai` on the host.")
    except Exception as e:
        await status_msg.edit(content=f"Failed: {e}")
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


client.run(TOKEN)
