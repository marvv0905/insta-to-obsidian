# Insta-to-Nextcloud

A Discord bot that transcribes Instagram Reels, summarizes them with an LLM, and saves the results as structured Markdown notes. Self-hosted on a Raspberry Pi 5 with Nextcloud for storage.

## What It Does

I built this because I kept saving educational Instagram Reels and never revisiting them. Now when I paste a link into a Discord channel, the bot downloads the audio, transcribes it locally, passes the transcript through an LLM for summarization, and saves a structured Markdown note to Nextcloud. The notes are linked into my Obsidian vault via a symlink for browsing and reference.

## How It Works

The bot listens for Instagram Reel URLs in Discord and runs a pipeline:

```
Instagram Reel Link
        │
        ▼
  Discord Bot (Python)
        │
        ▼
  Download Audio (yt-dlp)
        │
        ▼
  Transcribe (faster-whisper, local)
        │
        ▼
  Summarize into Markdown (DeepSeek)
        │
        ▼
  Save to Nextcloud (WebDAV)
        │
        ▼
  Browse & Reference in Obsidian
```

## Tech Stack

| Layer | Tool |
|---|---|
| Bot framework | Python, discord.py |
| Hosting | Raspberry Pi 5 (Linux ARM64), systemd |
| Audio extraction | yt-dlp + ffmpeg |
| Transcription | faster-whisper (local, ARM-optimized) |
| Summarization | DeepSeek v4 Flash (LLM API) |
| Knowledge store | Nextcloud WebDAV → Obsidian |

## Getting Started

### Prerequisites
- Python 3.12+
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- A Discord server you control
- A DeepSeek API key ([DeepSeek Platform](https://platform.deepseek.com))
- Nextcloud server (for vault storage)
- `ffmpeg` installed on the host (`sudo apt install ffmpeg` on Debian/Ubuntu)

### Setup

```bash
git clone https://github.com/marvv0905/insta-to-obsidian.git
cd insta-to-obsidian

python3 -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv yt-dlp faster-whisper openai
```

Create a `bot.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
DEEPSEEK_API_KEY=your_deepseek_key_here
NEXTCLOUD_URL=https://your-nextcloud-server
NEXTCLOUD_USERNAME=your_username
NEXTCLOUD_APP_PASSWORD=your_app_password
```

Run it:

```bash
python bot.py
```

### Deployment

The bot runs as a `systemd` service on a Raspberry Pi 5 for 24/7 uptime with auto-restart on crash or reboot.

## Project Structure

```
insta-to-obsidian/
├── bot.py                     # Discord bot logic and event handling
├── pipeline.py                # Audio download, transcription, LLM summarization, Nextcloud upload
├── README.md
├── .gitignore
├── bot.env                    # gitignored (API keys and secrets)
└── .venv/                     # gitignored (virtual environment)
```

## Roadmap

- [x] Discord bot detects and acknowledges Instagram Reel links
- [x] 24/7 deployment on Raspberry Pi 5 via systemd
- [x] Reel audio download (yt-dlp + ffmpeg)
- [x] Audio transcription (faster-whisper, local ARM-optimized)
- [x] LLM-based Markdown summarization (DeepSeek v4 Flash)
- [x] Save to Nextcloud via WebDAV (Obsidian-compatible frontmatter + tags)
- [ ] RAG-based querying inside Obsidian
- [ ] Weekly digest notes for unread summaries

