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
| Secrets | Stores bot token | `bot.env` (python-dotenv) |
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
discord_bot_secondBrain/
├── .venv/          # virtual environment (Pi-native, not portable)
├── bot.env         # DISCORD_TOKEN=xxxx (no spaces/quotes)
└── bot.py          # main bot script
```

### 3.3 Raspberry Pi Setup
```bash
# On the Pi, inside the project folder
python3 -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv
deactivate
```

Important: venvs are NOT portable across machines/architectures. Always create `.venv` fresh, directly on the Pi. Only transfer `bot.py`, `bot.env`, and requirements via `scp`/`git` — never the `.venv` folder itself.

### 3.4 systemd Service
File: `/etc/systemd/system/reelbot.service`
```ini
[Unit]
Description=Second Brain Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/ramm/discord_bot_secondBrain
ExecStart=/home/ramm/discord_bot_secondBrain/.venv/bin/python3 /home/ramm/discord_bot_secondBrain/bot.py
Restart=always
RestartSec=10
User=ramm
StandardOutput=append:/home/ramm/discord_bot_secondBrain/bot.log
StandardError=append:/home/ramm/discord_bot_secondBrain/bot.log

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
| View log file directly | `tail -f ~/discord_bot_secondBrain/bot.log` |
| Restart bot | `sudo systemctl restart reelbot.service` |
| Stop bot | `sudo systemctl stop reelbot.service` |
| Disable auto-start on boot | `sudo systemctl disable reelbot.service` |

## 5. Updating the Code

Whenever `bot.py` is edited (locally or via SSH/nano on the Pi directly):

1. If editing locally on Mac, sync only source files to the Pi (not `.venv`):
   ```bash
   scp bot.py bot.env ramm@naspi.local:~/discord_bot_secondBrain/
   ```
2. If new Python packages were added, install them inside the Pi's venv:
   ```bash
   cd ~/discord_bot_secondBrain
   source .venv/bin/activate
   pip install <new-package>
   deactivate
   ```
3. Restart the service to apply changes:
   ```bash
   sudo systemctl restart reelbot.service
   ```
4. Confirm it's healthy:
   ```bash
   sudo systemctl status reelbot.service
   ```

systemd does NOT auto-detect file changes — a manual restart is always required after any code edit.

## 6. Troubleshooting Reference

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'discord'` | venv not activated, or package not installed in the active interpreter | `source .venv/bin/activate` then `pip install discord.py` |
| `TypeError: expected token to be a str, received NoneType` | `.env`/`bot.env` not found or wrong filename passed to `load_dotenv()` | Confirm filename matches `load_dotenv("bot.env")`, check for hidden characters with `cat -A bot.env` |
| `status=203/EXEC` in systemd | Path in service file is wrong or venv binary isn't executable on this OS | Fix paths in `.service` file to match actual username/folder |
| `Exec format error` | venv was copied from another machine (wrong OS/architecture binaries) | `rm -rf .venv` and rebuild fresh with `python3 -m venv .venv` directly on the Pi |
| Bot shows offline in Discord | Service crashed/failed to start | `journalctl -u reelbot.service -n 30` to see the real traceback |

## 7. Maintenance Checklist (Recurring)

- After any Pi OS update or Python version upgrade, verify `.venv` still works; rebuild if broken.
- Rotate/regenerate the Discord bot token if it's ever accidentally exposed (via Developer Portal to Bot to Reset Token), then update `bot.env` and restart the service.
- Periodically check `bot.log` for repeated errors or rate-limit warnings, especially once the download/transcription/summarization pipeline is added (external API failures will show here first).
- Back up `bot.env` (token) and `bot.py` (code) outside the Pi (e.g. private git repo), since local storage failure would otherwise require full reconfiguration.

## 8. Next Development Steps (Pipeline TODOs)
Inside `bot.py`, the `on_message` handler currently has placeholder TODOs for:
1. `download_reel(reel_url)` — fetch video via yt-dlp or a transcript API.
2. `transcribe(video_path)` — Whisper or API-based transcription.
3. `summarize(transcript)` — LLM call to generate structured Markdown.
4. `save_to_obsidian(summary_md)` — write the note into the Obsidian vault (REST API, git sync, or shared folder).

Each of these should be implemented as a separate function/module so they can be tested and updated independently without touching the core Discord listener logic.
