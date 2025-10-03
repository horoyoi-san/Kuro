import requests
import time
import json
import os
import hashlib
from datetime import datetime, timezone

# ================== Discord Webhook URLs ==================
webhook_urls = [
    os.environ.get("WEBHOOK1"),
    os.environ.get("WEBHOOK2"),
    os.environ.get("WEBHOOK3"),
]

# ================== Logging System ==================
def log_and_check(api_url, game_name):
    """ดึงข้อมูลจาก API, เก็บ log, และตรวจสอบการเปลี่ยนแปลง"""
    try:
        resp = requests.get(api_url, timeout=10)
        data_text = resp.text
    except Exception as e:
        print(f"❌ Error fetching {game_name}: {e}")
        return False, None

    current_hash = hashlib.md5(data_text.encode()).hexdigest()

    log_dir = os.path.join(os.getcwd(), "Kuro", "log", game_name)
    os.makedirs(log_dir, exist_ok=True)

    hash_file = os.path.join(log_dir, "last_hash.txt")
    raw_file = os.path.join(log_dir, "raw_log.jsonl")

    # Save raw JSON
    try:
        with open(raw_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": json.loads(data_text)
            }, ensure_ascii=False) + "\n")
        print(f"✅ Wrote raw log for {game_name}")
    except Exception as e:
        print(f"❌ Error writing log file for {game_name}: {e}")

    # Load last hash
    last_hash = ""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            last_hash = f.read().strip()

    # เปรียบเทียบ hash
    if current_hash != last_hash:
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True, json.loads(data_text)

    return False, None

# ================== Discord Webhook Sender ==================
def send_webhooks(data, url, title, last_data=None):
    """ส่งข้อมูลไปยัง Discord Webhook ทุกตัว"""
    for webhook_url in webhook_urls:
        send_webhook(data, url, title, webhook_url, last_data)

def send_webhook(data, url, title, webhook_url, last_data=None):
    """ส่งข้อมูลไปยัง Discord Webhook ตัวเดียว"""
    if not webhook_url:
        print(f"⚠️ Webhook URL ไม่ถูกต้อง, ข้ามการส่ง")
        return

    # ================== Prepare Embed Fields ==================
    embed_fields = []

    current_version = data["default"].get("version", "No data")
    current_installer = data["default"].get("installer", "No data")
    current_resources = data["default"].get("resources", "No data")
    resource_path = data["default"].get("resource", {}).get("path", "No data")
    predownload = data.get("predownload", {})
    predownload_resources = predownload.get("resources", "No data")

    embed_fields.extend([
        {"name": "Version", "value": current_version, "inline": True},
        {"name": "Installer", "value": json.dumps(current_installer, ensure_ascii=False), "inline": False},
        {"name": "Resources", "value": str(current_resources), "inline": False},
        {"name": "Resource Path", "value": resource_path, "inline": False},
        {"name": "Predownload Resources", "value": str(predownload_resources), "inline": False},
    ])

    # ================== Extra Images ==================
    extra_url = "https://prod-alicdn-gamestarter.kurogame.com/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/background/U82Wn9dbNc2o7zZBWz1cOnJm9r52qFKH/en.json"
    try:
        extra_resp = requests.get(extra_url, timeout=10).json()
    except:
        extra_resp = {}

    first_frame_img = extra_resp.get("firstFrameImage", "")
    slogan_img = extra_resp.get("slogan", "")

    # ================== Build Webhook Payload ==================
    webhook_data = {
        "embeds": [
            {
                "title": title,
                "description": url,
                "color": 65535,
                "fields": embed_fields,
                "thumbnail": {"url": slogan_img or "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
                "image": {"url": first_frame_img}
            }
        ]
    }

    # ================== Send to Discord ==================
    try:
        response = requests.post(webhook_url, json=webhook_data, timeout=10)
        if response.status_code == 204:
            print(f"✅ ส่งข้อความ {title} ไปยัง Discord เรียบร้อยแล้ว!")
        else:
            print(f"❌ ไม่สามารถส่ง {title} ได้: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")

# ================== Main Function ==================
def check_for_updates():
    urls = [
        ("https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json", "Wuthering Waves OS (Launcher)"),
        ("https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json", "Wuthering Waves OS (Game)")
    ]
    for api_url, game_name in urls:
        changed, data = log_and_check(api_url, game_name)
        if changed and data:
            send_webhooks(data, api_url, game_name, None)
        else:
            print(f"[{game_name}] No changes detected")

# ================== Run Loop ==================
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(60)

