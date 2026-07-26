# 📸 Insta-to-Obsidian — AI Second Brain Pipeline

> An agentic workflow that turns Instagram Reels into structured, searchable knowledge inside Obsidian — powered by a self-hosted Discord bot running 24/7 on a Raspberry Pi 5.

## 🧠 The Problem

Educational Instagram Reels get saved and forgotten. This project closes the loop: paste a link, and the content becomes a permanent, LLM-queryable note in a personal knowledge vault — no manual re-watching or note-taking required.

## ⚙️ How It Works

```
Instagram Reel Link
        │
        ▼
  Discord Bot (Python)
        │
        ▼
  Download Reel (yt-dlp / API)
        │
        ▼
  Transcribe Audio (Whisper / API)
        │
        ▼
  Summarize into Markdown (LLM)
        │
        ▼
  Save to Obsidian Vault
        │
        ▼
  Query via LLM / RAG plugin
```

1. **Capture** — Paste an Instagram Reel link into a private Discord channel.
2. **Detect** — A Python bot (`discord.py`) listens for messages matching the Reel URL pattern.
3. **Process** *(in progress)* — The reel is downloaded, transcribed, and summarized into a clean Markdown note with frontmatter (source, date, tags, key takeaways).
4. **Store** — The note is written directly into an Obsidian vault, structured for both human browsing and LLM retrieval.
5. **Query** — An Obsidian RAG plugin (e.g. Smart Connections) enables natural-language search across all saved reel knowledge.

## 🏗️ Tech Stack

| Layer | Tool |
|---|---|
| Bot framework | Python, discord.py |
| Hosting | Raspberry Pi 5 (Linux ARM64), systemd |
| Secrets management | python-dotenv |
| Transcription (planned) | OpenAI Whisper / transcript API |
| Summarization (planned) | LLM API (GPT-4o-mini / Claude Haiku) |
| Knowledge store | Obsidian (Markdown vault) |
| Retrieval (planned) | Obsidian RAG plugin (Smart Connections / ObsidianRAG) |

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- A Discord server you control

### Setup

```bash
git clone https://github.com/marvv0905/insta-to-obsidian.git
cd insta-to-obsidian

python3 -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv
```

Create a `bot.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
```

Run it:

```bash
python bot.py
```

### Deploying for 24/7 Uptime

This bot is designed to run as a `systemd` service on a Raspberry Pi (or any Linux host) so it stays online continuously and auto-restarts on crash or reboot. See [`second_brain_bot_documentation.md`](./second_brain_bot_documentation.md) for the full deployment guide, including the systemd unit file and troubleshooting steps.

## 📁 Project Structure

```
insta-to-obsidian/
├── bot.py                              # Main Discord bot logic
├── bot.env                             # Secrets (gitignored)
├── instagram_reel_obsidian_PRD.md      # Product requirements & architecture
├── second_brain_bot_documentation.md   # Setup, ops, and troubleshooting guide
└── .gitignore
```

## 🗺️ Roadmap

- [x] Discord bot detects and acknowledges Instagram Reel links
- [x] 24/7 deployment on Raspberry Pi 5 via systemd
- [ ] Reel download integration (yt-dlp / transcript API)
- [ ] Audio transcription (Whisper)
- [ ] LLM-based Markdown summarization
- [ ] Automated write-to-Obsidian-vault
- [ ] RAG-based querying inside Obsidian
- [ ] Weekly digest notes for unread summaries

## 📄 Docs

- [Product Requirements Document](./instagram_reel_obsidian_PRD.md)
- [Setup & Maintenance Guide](./second_brain_bot_documentation.md)

## 📝 License

MIT
