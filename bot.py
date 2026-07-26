# bot.py
import re
import discord
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "bot.env"))

TOKEN = os.getenv("DISCORD_TOKEN")
print("Token loaded:", TOKEN is not None)
print("Token value preview:", repr(TOKEN)[:15] if TOKEN else None)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

IG_REEL_PATTERN = re.compile(r"(https?://(www\.)?instagram\.com/reel/[^\s]+)")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    match = IG_REEL_PATTERN.search(message.content)
    if match:
        reel_url = match.group(1)
        await message.channel.send(f"Got it, processing reel: {reel_url}")
        # TODO: call your pipeline here
        # 1. download_reel(reel_url)
        # 2. transcript = transcribe(video_path)
        # 3. summary_md = summarize(transcript)
        # 4. save_to_obsidian(summary_md)
        await message.channel.send("Saved to Obsidian vault.")

client.run(TOKEN)