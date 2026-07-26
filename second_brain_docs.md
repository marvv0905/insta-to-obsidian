# Second Brain Discord Bot — Documentation

## 1. What This Is
A Discord bot that runs 24/7 on a Raspberry Pi 5. It listens for Instagram Reel links pasted into a Discord channel, and is designed to trigger an automated pipeline that downloads, transcribes, summarizes, and saves the content as a Markdown note into an Obsidian vault ("second brain").

Currently implemented: link detection + acknowledgment messages in Discord.
Planned (TODO in code): download reel to video to transcript to LLM summary to write to Obsidian vault.

## 2. Architecture Summary

| Component | Role | Tech |
|---|---|---|
| Bot host | Always-on runtime | Raspberry Pi 5 (Linux ARM64), systemd service |
| Bot framework | Listens for messages, detects reel links | Python, discord.py |
| Secrets | Stores bot token | `bot.env` (python-dotenv, gitignored) |
| Version control | Code sync between Mac and Pi | Git + GitHub (private/public repo) |
| Process manager | Keeps bot alive, auto-restarts on crash/reboot | systemd (`reelbot.service`) |
| Pipeline (planned) | Download, transcribe, summarize, write to vault | yt-dlp/API, Whisper/API, LLM API, Obsidian REST/git |

## 3. Initial Setup (Reference)

### 3.1 Discord Developer Portal
1. Create application at discord.com/developers/applications.
2. Add a Bot user, reset and copy the token.
3. Enable **Message Content Intent** under Privileged Gateway Intents.
4. Generate an OAuth2 invite URL with `bot` scope + Send Messages, Read Message History, Attach Files permissions, and invite it to your server.

### 3.2 Project Files
```
insta-to-obsidian/
├── .venv/                              # virtual environment (Pi-native, not portable, gitignored)
├── bot.env                             # DISCORD_TOKEN=xxxx (gitignored, never pushed)
├── bot.py                              # main bot script
├── README.md                           # portfolio-facing project overview
├── instagram_reel_obsidian_PRD.md      # product requirements doc
└── second_brain_docs.md                # this file
```

### 3.3 GitHub Repository Setup
Code lives in a GitHub repo and is synced to the Pi via `git pull` instead of manual file transfer.

**One-time, locally (on Mac):**
```bash
cd ~/Desktop/nerd_stuff/insta-to-obsidian
git init
echo ".venv/
bot.env" > .gitignore
git add .
git commit -m "initial bot"
git remote add origin https://github.com/youruser/insta-to-obsidian.git
git push -u origin main
```

If the remote already has commits (e.g. GitHub auto-created a README), merge histories before pushing:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

**One-time, on the Pi:**
```bash
cd ~
git clone https://github.com/youruser/insta-to-obsidian.git
```

`bot.env` is never stored in git — it must be created manually and directly on each machine that runs the bot (Mac for local testing, Pi for production).

### 3.4 Raspberry Pi Environment Setup
```bash
cd ~/insta-to-obsidian
python3 -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv
deactivate
```

Important: venvs are NOT portable across machines/architectures. Always create `.venv` fresh, directly on the Pi. Never commit or transfer the `.venv` folder itself — it's gitignored for this reason.

### 3.5 systemd Service
File: `/etc/systemd/system/reelbot.service`
```ini
[Unit]
Description=Second Brain Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/youruser/insta-to-obsidian
ExecStart=/home/youruser/insta-to-obsidian/.venv/bin/python3 /home/youruser/insta-to-obsidian/bot.py
Restart=always
RestartSec=10
User=youruser
StandardOutput=append:/home/youruser/insta-to-obsidian/bot.log
StandardError=append:/home/youruser/insta-to-obsidian/bot.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable reelbot.service
sudo systemctl start reelbot.service
```

## 4. Daily Operations

| Task | Command |
|---|---|
| Check bot status | `sudo systemctl status reelbot.service` |
| View live logs | `journalctl -u reelbot.service -f` |
| View log file directly | `tail -f ~/insta-to-obsidian/bot.log` |
| Restart bot | `sudo systemctl restart reelbot.service` |
| Stop bot | `sudo systemctl stop reelbot.service` |
| Disable auto-start on boot | `sudo systemctl disable reelbot.service` |

## 5. Updating the Code (GitHub Workflow)

Whenever `bot.py` (or any file) is edited locally in your IDE on the Mac:

**Step 1 — Commit and push from Mac:**
```bash
cd ~/Desktop/nerd_stuff/insta-to-obsidian
git add .
git commit -m "describe your change"
git push
```

**Step 2 — Pull the update on the Pi:**
```bash
ssh youruser@yourpi.local
cd ~/insta-to-obsidian
git pull
```

**Step 3 — Install any new dependencies (only if imports changed):**
```bash
source .venv/bin/activate
pip install <new-package>
deactivate
```

**Step 4 — Restart the service to apply changes:**
```bash
sudo systemctl restart reelbot.service
sudo systemctl status reelbot.service
```

systemd does NOT auto-detect file changes, and `git pull` does NOT restart the running process — a manual restart is always required after every update.

### Quick Reference: Full Update Cycle
```bash
# On Mac
git add . && git commit -m "update" && git push

# On Pi
ssh youruser@yourpi.local
cd ~/insta-to-obsidian && git pull
sudo systemctl restart reelbot.service
```

## 6. Troubleshooting Reference

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'discord'` | venv not activated, or package not installed in the active interpreter | `source .venv/bin/activate` then `pip install discord.py` |
| `TypeError: expected token to be a str, received NoneType` | `.env`/`bot.env` not found or wrong filename passed to `load_dotenv()` | Confirm filename matches `load_dotenv("bot.env")`, check for hidden characters with `cat -A bot.env` |
| `status=203/EXEC` in systemd | Path in service file is wrong or points to nonexistent binary | Fix paths in `.service` file to match actual username/folder |
| `Exec format error` | venv was copied from another machine (wrong OS/architecture binaries) | `rm -rf .venv` and rebuild fresh with `python3 -m venv .venv` directly on the Pi |
| `! [rejected] main -> main (fetch first)` on `git push` | Remote repo has commits your local repo doesn't (e.g. auto-generated README) | `git pull origin main --allow-unrelated-histories`, resolve conflicts, then push again |
| Bot shows offline in Discord | Service crashed/failed to start | `journalctl -u reelbot.service -n 30` to see the real traceback |

## 7. Maintenance Checklist (Recurring)

- After any Pi OS update or Python version upgrade, verify `.venv` still works; rebuild if broken.
- Rotate/regenerate the Discord bot token if it's ever accidentally exposed (via Developer Portal to Bot to Reset Token), then update `bot.env` on the Pi and restart the service. Never commit a real token to GitHub, even in a private repo.
- Periodically check `bot.log` for repeated errors or rate-limit warnings, especially once the download/transcription/summarization pipeline is added (external API failures will show here first).
- Keep the GitHub repo as the source of truth for code; `bot.env` stays local-only on each machine and is never version-controlled.

## 8. Next Development Steps (Pipeline TODOs)
Inside `bot.py`, the `on_message` handler currently has placeholder TODOs for:
1. `download_reel(reel_url)` — fetch video via yt-dlp or a transcript API.
2. `transcribe(video_path)` — Whisper or API-based transcription.
3. `summarize(transcript)` — LLM call to generate structured Markdown.
4. `save_to_obsidian(summary_md)` — write the note into the Obsidian vault (REST API, git sync, or shared folder).

Each of these should be implemented as a separate function/module so they can be tested and updated independently without touching the core Discord listener logic.
