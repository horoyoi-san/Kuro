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

# ================= Discord =================
def split_text_to_embeds(title, text, color=255, max_len=1024):
    """ แบ่งข้อความยาวเป็นหลาย embed """
    if not text:
        return []
    embeds = []
    lines = text.split("\n")
    current = ""
    part = 1
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            embeds.append({
                "title": f"{title} {part}",
                "description": current,
                "color": color,
                "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
                "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
            })
            current = line
            part += 1
        else:
            current += ("\n" if current else "") + line
    if current:
        embeds.append({
            "title": f"{title} {part}",
            "description": current,
            "color": color,
            "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
            "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
        })
    return embeds

def send_webhooks(data, title):
    for webhook_url in webhook_urls:
        send_webhook(data, title, webhook_url)

def send_webhook(data, title, webhook_url, batch_size=5):
    if not webhook_url:
        print("⚠️ Webhook URL ไม่ถูกต้อง")
        return

    blocks = []

    # ================= Default =================
    default = data.get("default")
    if default:
        resource = default.get("resource")
        if resource:  # Launcher
            version = resource.get("version", "No version")
            size = resource.get("size", 0)
            md5 = resource.get("md5", "")
            cdn_list = default.get("cdnList", [])
            path = resource.get("path", "")
            url_full = cdn_list[0]["url"] + path if cdn_list and path else path
            desc = f"Version: {version}\nSize: {size/1024/1024:.2f} MB\nMD5: {md5}\nDownload: {url_full}"
            blocks += split_text_to_embeds(title + " — Pord", desc)
        else:  # Game
            config = default.get("config", {})
            version = config.get("version", "No version")
            size = config.get("size", 0)
            md5 = config.get("indexFileMd5", "")
            cdn_list = default.get("cdnList", [])
            patch_lines = []
            for patch in config.get("patchConfig", []):
                ver = patch.get("version")
                index_file = patch.get("indexFile")
                full_url_patch = cdn_list[0]["url"] + index_file if cdn_list else index_file
                patch_lines.append(f"{ver}: {full_url_patch}")
            url_full = patch_lines[-1] if patch_lines else "No URL"
            desc = f"Version: {version}\nSize: {size/1024/1024:.2f} MB\nMD5: {md5}\nDownload: {url_full}"
            blocks += split_text_to_embeds(title + " — Pord", desc)
            blocks += split_text_to_embeds(title + " — Hdiff", "\n".join(patch_lines))

    # ================= Predownload =================
    predownload = data.get("predownload")
    if predownload:
        config = predownload.get("config", {})
        version = config.get("version", "No version")
        size = config.get("size", 0)
        md5 = config.get("indexFileMd5", "")
        cdn_list = default.get("cdnList", [])
        patch_lines = []
        for patch in config.get("patchConfig", []):
            ver = patch.get("version")
            index_file = patch.get("indexFile")
            full_url_patch = cdn_list[0]["url"] + index_file if cdn_list else index_file
            patch_lines.append(f"{ver}: {full_url_patch}")
        # Pre-download main info with URL from cdnList
        full_url_predownload = patch_lines[-1] if patch_lines else "No URL"
        desc = f"Version: {version}\nSize: {size/1024/1024:.2f} MB\nMD5: {md5}\nDownload: {full_url_predownload}"
        blocks += split_text_to_embeds(title + " — Predownload", desc, color=9699168)
        blocks += split_text_to_embeds(title + " — Predownload Hdiff", "\n".join(patch_lines), color=9699168)

    # ================= Send in batches =================
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        try:
            response = requests.post(webhook_url, json={"embeds": batch}, timeout=10)
            if response.status_code == 204:
                print(f"✅ ส่ง batch {i//batch_size+1} ของ {title} เรียบร้อยแล้ว")
            else:
                print(f"❌ ไม่สามารถส่ง {title} batch {i//batch_size+1}: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")

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