# Insta-to-Nextcloud — AI Second Brain Pipeline
> An agentic workflow that turns Instagram Reels into structured, searchable knowledge — powered by a self-hosted Discord bot running 24/7 on a Raspberry Pi 5.

## The Problem

Educational Instagram Reels get saved and forgotten. This project closes the loop: paste a link, and the content becomes a permanent, LLM-queryable note in a personal knowledge vault — no manual re-watching or note-taking required.

## How It Works

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
  Browse & Query in Obsidian
```

1. **Capture** — Paste an Instagram Reel link into a private Discord channel.
2. **Download** — Audio is extracted from the reel via yt-dlp.
3. **Transcribe** — Speech-to-text runs locally on the Pi using faster-whisper.
4. **Summarize** — The transcript is passed to an LLM (DeepSeek v4 Flash) which produces a structured Markdown note with frontmatter, tags, key takeaways, and the full transcript.
5. **Store** — The note is uploaded to a self-hosted Nextcloud server via WebDAV. A symlink connects the Nextcloud folder into an Obsidian vault for browsing and querying.

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

### Deploying for 24/7 Uptime

This bot is designed to run as a `systemd` service on a Raspberry Pi (or any Linux host) so it stays online continuously and auto-restarts on crash or reboot. See [`second_brain_docs.md`](./second_brain_docs.md) for the full deployment guide, including the systemd unit file and troubleshooting steps.

## Project Structure

```
insta-to-obsidian/
├── bot.py                              # Main Discord bot logic
├── pipeline.py                         # Audio download, transcription, summarization, Nextcloud save
├── bot.env                             # Secrets (gitignored)
├── instagram_reel_obsidian_PRD.md      # Product requirements & architecture
├── second_brain_docs.md                # Setup, ops, and troubleshooting guide
└── .gitignore
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

