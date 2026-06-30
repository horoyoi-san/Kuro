import os
import re
import time
from collections import defaultdict
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parent
DISCORD_API_URL = "https://discord.com/api/v10"

WEBHOOK_URL = "YOUR_DISCORD"
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"

DATA_URL = ""
DATA_FILE = REPO_ROOT / "data" / "wuwa_legacy.txt"

GAME_NAME = "Wuthering Waves"
TITLE_PREFIX = "Wuthering Waves Timeline (STC)"
EMBED_COLOR = 0x0000FF
GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJuczV2MGVvOWUxa3hsaGZpMDRzOTJ5eGE2ZmczM2lvaWJhcjkzdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1RCKEiSdMbYsMWRfXR/giphy.gif"
EMBED_LIMIT = 4096


def load_env_file():
    env_path = REPO_ROOT / ".env"

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def load_settings():
    load_env_file()

    return {
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", WEBHOOK_URL),
        "bot_token": os.getenv("DISCORD_BOT_TOKEN", BOT_TOKEN),
        "channel_id": os.getenv(
            "DISCORD_WUWA_CHANNEL_ID",
            os.getenv("DISCORD_CHANNEL_ID", CHANNEL_ID),
        ),
        "data_url": os.getenv("WUWA_DATA_URL", DATA_URL),
        "data_file": Path(os.getenv("WUWA_DATA_FILE", str(DATA_FILE))),
    }


def send_discord_message(payload, settings):
    bot_token = settings["bot_token"]
    channel_id = settings["channel_id"]
    webhook_url = settings["webhook_url"]

    if bot_token != "YOUR_BOT_TOKEN" and channel_id != "YOUR_CHANNEL_ID":
        url = f"{DISCORD_API_URL}/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return "bot"

    if webhook_url != "YOUR_DISCORD":
        response = requests.post(webhook_url, json=payload, timeout=15)
        response.raise_for_status()
        return "webhook"

    raise RuntimeError(
        "Please set DISCORD_WEBHOOK_URL or set DISCORD_BOT_TOKEN and "
        "DISCORD_WUWA_CHANNEL_ID."
    )


def load_timeline_text(settings):
    data_url = settings["data_url"]

    if data_url:
        try:
            print("Loading data from URL...")
            response = requests.get(data_url, timeout=15)
            response.raise_for_status()
            print("Loaded data from URL")
            return response.text.strip()
        except Exception as exc:
            print(f"Failed to load URL: {exc}")

    data_file = settings["data_file"]
    if not data_file.is_absolute():
        data_file = REPO_ROOT / data_file

    try:
        print("Loading data from local file...")
        text = data_file.read_text(encoding="utf-8").strip()
        print("Loaded data from local file")
        return text
    except Exception as exc:
        raise SystemExit(f"No data source available: {exc}") from exc


def group_timeline_blocks(text):
    blocks = re.split(rf"\n(?={re.escape(GAME_NAME)} \d+\.\d)", text)
    blocks = [block.strip() for block in blocks if block.strip()]
    groups = defaultdict(list)

    for block in blocks:
        match = re.search(rf"{re.escape(GAME_NAME)} (\d+)\.(\d+)", block)

        if not match:
            continue

        major = int(match.group(1))
        minor = int(match.group(2))
        groups[major].append((minor, block))

    return groups


def build_embed_descriptions(versions):
    current_desc = ""
    descriptions = []

    for _, block in sorted(versions, key=lambda item: item[0]):
        candidate = block + "\n\n"

        if len(current_desc) + len(candidate) > EMBED_LIMIT:
            descriptions.append(current_desc.rstrip())
            current_desc = candidate
        else:
            current_desc += candidate

    if current_desc.strip():
        descriptions.append(current_desc.rstrip())

    return descriptions


def main():
    settings = load_settings()
    text = load_timeline_text(settings)
    groups = group_timeline_blocks(text)

    for major in sorted(groups.keys()):
        for description in build_embed_descriptions(groups[major]):
            payload = {
                "embeds": [
                    {
                        "title": f"{TITLE_PREFIX} ({major}.0)",
                        "description": description,
                        "color": EMBED_COLOR,
                        "image": {"url": GIF_URL},
                    }
                ]
            }

            try:
                send_mode = send_discord_message(payload, settings)
                print(f"Sent embed for {major}.0 via {send_mode}")
            except Exception as exc:
                print(f"Failed to send Discord message: {exc}")

            time.sleep(1)


if __name__ == "__main__":
    main()
