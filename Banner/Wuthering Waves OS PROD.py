import requests
import json
import os
import hashlib
from datetime import datetime, timezone

# ================= Webhook =================
webhook_urls = [
    os.environ.get("WEBHOOK1"),
    os.environ.get("WEBHOOK2"),
    os.environ.get("WEBHOOK3"),
]

# ================= Logging =================
def log_and_check(api_url, game_name):
    try:
        resp = requests.get(api_url, timeout=10)
        data_text = resp.text
        data_json = json.loads(data_text)
    except Exception as e:
        print(f"❌ Error fetching {game_name}: {e}")
        return False, None

    current_hash = hashlib.md5(data_text.encode()).hexdigest()

    log_dir = os.path.join(os.getcwd(), "Kuro", "log", game_name)
    os.makedirs(log_dir, exist_ok=True)

    hash_file = os.path.join(log_dir, "last_hash.txt")
    raw_file = os.path.join(log_dir, "raw_log.jsonl")

    try:
        with open(raw_file, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"timestamp": datetime.now(timezone.utc).isoformat(), "data": data_json},
                    ensure_ascii=False,
                )
                + "\n"
            )
        print(f"✅ Wrote raw log for {game_name}")
    except Exception as e:
        print(f"❌ Error writing log file for {game_name}: {e}")

    last_hash = ""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            last_hash = f.read().strip()

    if current_hash != last_hash:
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True, data_json

    return False, data_json


# =============== Embed สร้าง Patch ===============
def create_patch_embeds(patch_text, max_len=1024):
    embeds = []
    current_field = ""
    part_num = 1

    for line in patch_text.split("\n"):
        if len(current_field) + len(line) + 1 > max_len:
            embeds.append({
                "title": f"Patch Versions Part {part_num}",
                "description": current_field,
                "color": 65535
            })
            current_field = line
            part_num += 1
        else:
            current_field += ("\n" if current_field else "") + line

    if current_field:
        embeds.append({
            "title": f"Patch Versions Part {part_num}",
            "description": current_field,
            "color": 65535
        })

    return embeds


# =============== ส่งไปหลาย Webhook ===============
def send_webhooks(data, title):
    for url in webhook_urls:
        if url:
            send_webhook(data, title, url)
        else:
            print("⚠️ Webhook URL ว่าง – ข้าม")


# =============== ส่ง Webhook หลัก ===============
def send_webhook(data, title, webhook_url):

    # Discord ต้องการ object {"embeds": [...]} เท่านั้น
    if not webhook_url:
        print("⚠️ ไม่มี URL")
        return

    default_data = data.get("default")
    predownload_data = data.get("predownload")

    if not default_data:
        print("❌ JSON ไม่ถูกต้อง")
        return

    def parse_block(block):
        resource = block.get("resource")
        cdn_list = block.get("cdnList", [])

        if resource:  # Launcher
            version = resource.get("version", "Unknown")
            size = resource.get("size", 0)
            md5 = resource.get("md5", "")
            path = resource.get("path", "")
            full_url = cdn_list[0]["url"] + path if cdn_list and path else ""
            patch_embeds = []
        else:  # Game
            config = block.get("config", {})
            version = config.get("version", "Unknown")
            size = config.get("size", 0)
            md5 = config.get("indexFileMd5", "")
            cdn_list = block.get("cdnList", [])
            full_url = ""

            patch_versions = []
            for p in config.get("patchConfig", []):
                pv = p.get("version")
                idx = p.get("indexFile")
                url = cdn_list[0]["url"] + idx if cdn_list else idx
                patch_versions.append(f"{pv}: {url}")

            patch_text = "\n".join(patch_versions)
            patch_embeds = create_patch_embeds(patch_text) if patch_versions else []

            if patch_versions:
                full_url = patch_versions[-1].split(": ")[1]

        return version, size, md5, full_url, patch_embeds

    # Default block
    d_version, d_size, d_md5, d_url, d_patch_embeds = parse_block(default_data)

    embeds = []

    # Base Embed (Default)
    embeds.append({
        "title": f"{title} — Default",
        "color": 65535,
        "fields": [
            {"name": "Version", "value": d_version, "inline": True},
            {"name": "File Size", "value": f"{d_size/1024/1024:.2f} MB", "inline": True},
            {"name": "MD5", "value": d_md5, "inline": False},
            {"name": "Download", "value": d_url or "No URL", "inline": False},
        ]
    })

    embeds += d_patch_embeds

    # Predownload block
    if predownload_data:
        p_version, p_size, p_md5, p_url, p_patch_embeds = parse_block(predownload_data)

        embeds.append({
            "title": f"{title} — Predownload",
            "color": 16776960,
            "fields": [
                {"name": "Version", "value": p_version, "inline": True},
                {"name": "File Size", "value": f"{p_size/1024/1024:.2f} MB", "inline": True},
                {"name": "MD5", "value": p_md5, "inline": False},
                {"name": "Download", "value": p_url or "No URL", "inline": False},
            ]
        })

        embeds += p_patch_embeds

    # ส่งจริง
    payload = {"embeds": embeds}

    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        if r.status_code == 204:
            print("✅ ส่งสำเร็จ:", title)
        else:
            print("❌ ส่งไม่ได้:", r.status_code, r.text)
    except Exception as e:
        print("❌ Error sending webhook:", e)


# =============== Main ===============
def check_for_updates():
    urls = [
        ("https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json", "Wuthering Waves OS (Launcher)"),
        ("https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json", "Wuthering Waves OS (Game)")
    ]

    for url, name in urls:
        changed, data = log_and_check(url, name)
        if changed and data:
            send_webhooks(data, name)
        else:
            print(f"[{name}] No changes detected")

if __name__ == "__main__":
    check_for_updates()