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
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data_json
            }, ensure_ascii=False) + "\n")
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


# ================= Create Patch Embeds =================
def create_patch_embeds(text, max_len=1024):
    if not text:
        return []

    embeds = []
    current = ""
    part = 1

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            embeds.append({
                "title": f"Patch Versions Part {part}",
                "description": current,
                "color": 65535,
                "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
                "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
            })
            current = line
            part += 1
        else:
            current += ("\n" if current else "") + line

    if current:
        embeds.append({
            "title": f"Patch Versions Part {part}",
            "description": current,
            "color": 65535,
            "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
            "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
        })

    return embeds


# ================= Send Discord =================
def send_webhook_block(data, title, webhook_url):
    default_data = data.get("default")
    predownload_data = data.get("predownload")

    if not default_data:
        print(f"❌ Unexpected JSON structure, missing 'default': {title}")
        return

    # -------- Parse function --------
    def parse_block(block):
        resource = block.get("resource")
        cdn_list = block.get("cdnList", [])

        if resource:
            version = resource.get("version", "No version")
            path = resource.get("path", "")
            md5 = resource.get("md5", "")
            size = resource.get("size", 0)
            full_url = (cdn_list[0]["url"] + path) if (cdn_list and path) else "No URL"
            patch_embeds = []

        else:
            config = block.get("config", {})
            version = config.get("version", "No version")
            size = config.get("size", 0)
            md5 = config.get("indexFileMd5", "")
            full_url = "No URL"

            patch_texts = []
            for patch in config.get("patchConfig", []):
                ver = patch.get("version")
                fpath = patch.get("indexFile")
                full_patch_url = cdn_list[0]["url"] + fpath if cdn_list else fpath
                patch_texts.append(f"{ver}: {full_patch_url}")

            patch_text = "\n".join(patch_texts)
            patch_embeds = create_patch_embeds(patch_text)

            if patch_texts:
                full_url = patch_texts[-1].split(": ")[-1]

        return version, size, md5, full_url, patch_embeds

    # Parse default
    d_version, d_size, d_md5, d_url, d_patches = parse_block(default_data)

    embeds = [{
        "title": f"{title} — Default",
        "color": 65535,
        "fields": [
            {"name": "Version", "value": d_version, "inline": True},
            {"name": "File Size", "value": f"{d_size/1024/1024:.2f} MB", "inline": True},
            {"name": "MD5", "value": d_md5, "inline": False},
            {"name": "Download", "value": d_url, "inline": False},
        ],
        "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
        "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
    }] + d_patches

    # Parse predownload
    if predownload_data:
        p_version, p_size, p_md5, p_url, p_patches = parse_block(predownload_data)
        pre_embed = {
            "title": f"{title} — Predownload",
            "color": 16776960,
            "fields": [
                {"name": "Version", "value": p_version, "inline": True},
                {"name": "File Size", "value": f"{p_size/1024/1024:.2f} MB", "inline": True},
                {"name": "MD5", "value": p_md5, "inline": False},
                {"name": "Download", "value": p_url, "inline": False},
            ],
            "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
            "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
        }
        embeds += [pre_embed] + p_patches

    payload = {"embeds": embeds}

    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        if r.status_code == 204:
            print(f"✅ ส่ง {title} สำเร็จ → {webhook_url}")
        else:
            print(f"❌ ส่งไม่สำเร็จ ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")


# ================= Wrapper (ส่งทุก Webhook) =================
def send_webhooks(data, title):
    for url in webhook_urls:
        if url:
            send_webhook_block(data, title, url)
        else:
            print("⚠️ ข้าม Webhook URL (ว่าง)")


# ================= Main =================
def check_for_updates():
    urls = [
        ("https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json", "Wuthering Waves OS (Launcher)"),
        ("https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json", "Wuthering Waves OS (Game)")
    ]

    for api_url, game_name in urls:
        changed, data = log_and_check(api_url, game_name)
        if changed and data:
            send_webhooks(data, game_name)
        else:
            print(f"[{game_name}] No changes detected")


if __name__ == "__main__":
    check_for_updates()