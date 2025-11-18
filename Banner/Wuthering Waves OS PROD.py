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

# ================= Embed Helpers =================
def create_main_embed(title, version, size, md5, url, thumbnail=None, image=None, color=65535):
    embed = {
        "title": title,
        "color": color,
        "fields": [
            {"name": "Version", "value": version, "inline": True},
            {"name": "File Size", "value": f"{size/1024/1024:.2f} MB", "inline": True},
            {"name": "MD5", "value": md5, "inline": False},
            {"name": "Download", "value": url, "inline": False},
        ]
    }
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}
    if image:
        embed["image"] = {"url": image}
    return embed

def create_patch_embeds(title, patch_versions, thumbnail=None, image=None):
    """สร้าง embed แยกทีละข้อความ (line) ไม่เกิน 1024 ตัวอักษร"""
    embeds = []
    for line in patch_versions:
        embed = {
            "title": title + " - Patch",
            "description": line,
            "color": 65535
        }
        if thumbnail:
            embed["thumbnail"] = {"url": thumbnail}
        if image:
            embed["image"] = {"url": image}
        embeds.append(embed)
    return embeds

def send_webhook_blocks(blocks):
    """ส่ง embed หลาย block แบ่ง batch 10 embed ต่อ webhook"""
    for webhook_url in webhook_urls:
        if not webhook_url:
            continue
        for i in range(0, len(blocks), 10):
            batch = blocks[i:i+10]
            try:
                resp = requests.post(webhook_url, json={"embeds": batch}, timeout=10)
                if resp.status_code not in (200, 204):
                    print(f"❌ ส่งไม่ได้: {resp.status_code} {resp.text}")
                else:
                    print(f"✅ ส่ง Embed จำนวน {len(batch)} สำเร็จ")
            except Exception as e:
                print(f"❌ Error sending webhook: {e}")

def send_game_webhooks(title, data):
    default = data.get("default")
    predownload = data.get("predownload")
    if not default:
        print(f"❌ JSON ไม่ถูกต้อง: {title}")
        return

    blocks = []

    thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"
    image = "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"

    # ================= Default =================
    resource = default.get("resource") or default.get("config", {})
    cdn_list = default.get("cdnList", [])
    path = resource.get("path", "") or resource.get("indexFile", "")
    url = (cdn_list[0]["url"] + path) if cdn_list and path else "No URL"
    version = resource.get("version", "No version")
    size = resource.get("size", 0)
    md5 = resource.get("md5", resource.get("indexFileMd5", ""))

    blocks.append(create_main_embed(title + " - Default", version, size, md5, url, thumbnail, image))

    # ================= Patch =================
    config = default.get("config", {})
    patch_configs = config.get("patchConfig", [])
    patch_versions = []
    for p in patch_configs:
        ver = p.get("version")
        idx_file = p.get("indexFile")
        full_url = (cdn_list[0]["url"] + idx_file) if cdn_list else idx_file
        patch_versions.append(f"{ver}: {full_url}")

    if patch_versions:
        blocks += create_patch_embeds(title, patch_versions, thumbnail, image)

    # ================= Predownload =================
    if predownload:
        resource = predownload.get("resource") or predownload.get("config", {})
        cdn_list = predownload.get("cdnList", [])
        path = resource.get("path", "") or resource.get("indexFile", "")
        url = (cdn_list[0]["url"] + path) if cdn_list and path else "No URL"
        version = resource.get("version", "No version")
        size = resource.get("size", 0)
        md5 = resource.get("md5", resource.get("indexFileMd5", ""))
        blocks.append(create_main_embed(title + " - Predownload", version, size, md5, url, thumbnail, image))

    send_webhook_blocks(blocks)

# ================= Main =================
def check_for_updates():
    urls = [
        # CN
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json", "Wuthering Waves CN (Launcher)"),
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json", "Wuthering Waves CN (Game)"),
        # OS
        ("https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json", "Wuthering Waves OS (Launcher)"),
        ("https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json", "Wuthering Waves OS (Game)")
    ]

    for api_url, game_name in urls:
        changed, data = log_and_check(api_url, game_name)
        if changed and data:
            print(f"🔔 Detected update for {game_name}")
            send_game_webhooks(game_name, data)
        else:
            print(f"[{game_name}] No changes detected")

if __name__ == "__main__":
    check_for_updates()