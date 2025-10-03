import requests
import time
import json
import os
import hashlib
from datetime import datetime, timezone

# กำหนด Webhook URLs
webhook_urls = [
    os.environ.get("WEBHOOK1"),
    os.environ.get("WEBHOOK2"),
    os.environ.get("WEBHOOK3"),
]

# ============ Logging System ============
def log_and_check(api_url, game_name):
    try:
        resp = requests.get(api_url, timeout=10)
        data_text = resp.text
    except Exception as e:
        print(f"❌ Error fetching {game_name}: {e}")
        return False, None

    current_hash = hashlib.md5(data_text.encode()).hexdigest()

    # directory แยกตามเกม
    log_dir = os.path.join(os.getcwd(), "Kuro", "log", game_name)
    os.makedirs(log_dir, exist_ok=True)

    hash_file = os.path.join(log_dir, "last_hash.txt")
    raw_file = os.path.join(log_dir, "raw_log.jsonl")

    # Save raw JSON ทุกครั้ง
    try:
        with open(raw_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": json.loads(data_text)
            }, ensure_ascii=False) + "\n")
        print(f"✅ Wrote raw log for {game_name}")
    except Exception as e:
        print(f"❌ Error writing log file for {game_name}: {e}")

    # load last hash
    last_hash = ""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            last_hash = f.read().strip()

    if current_hash != last_hash:
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True, json.loads(data_text)
    return False, None

# ฟังก์ชันในการส่งข้อมูลไปยัง Discord Webhook หลายอัน
def send_webhooks(data, url, title, last_data):
    for webhook_key in webhook_urls:
        send_webhook(data, url, title, webhook_key, last_data)

# ฟังก์ชันในการส่งข้อมูลไปยัง Discord Webhook หนึ่งอัน
def send_webhook(data, url, title, webhook_key, last_data):
    embed_fields = []

    # ดึงข้อมูลจาก index.json
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

    # ✅ ดึงรูปจาก en.json
    extra_url = "https://prod-alicdn-gamestarter.kurogame.com/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/background/U82Wn9dbNc2o7zZBWz1cOnJm9r52qFKH/en.json"
    try:
        extra_resp = requests.get(extra_url, timeout=10).json()
    except:
        extra_resp = {}

    first_frame_img = extra_resp.get("firstFrameImage", "")
    slogan_img = extra_resp.get("slogan", "")

    # สร้าง embed
    webhook_data = {
        "embeds": [
            {
                "title": title,
                "description": f"{url}",  
                "color": 65535,
                "fields": embed_fields,
                "thumbnail": {"url": slogan_img if slogan_img else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
                "image": {"url": first_frame_img}
            }
        ]
    }

    webhook_url = webhook_urls.get(webhook_key)
    if webhook_url:
        try:
            response = requests.post(webhook_url, json=webhook_data, timeout=10)
            if response.status_code == 204:
                print(f"✅ ส่งข้อความ {title} ไปยัง Discord ({webhook_key}) เรียบร้อยแล้ว!")
            else:
                print(f"❌ ไม่สามารถส่ง {title} ได้: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")

# ฟังก์ชันหลัก
def check_for_updates():
    url_1 = "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json"
    url_2 = "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json"

    # URL 1
    changed_1, data_1 = log_and_check(url_1, "Wuthering Waves CN (Launcher)")
    if changed_1 and data_1:
        send_webhooks(data_1, url_1, "Wuthering Waves CN (Launcher)", None)

    # URL 2
    changed_2, data_2 = log_and_check(url_2, "Wuthering Waves CN (Game)")
    if changed_2 and data_2:
        send_webhooks(data_2, url_2, "Wuthering Waves CN (Game)", None)

# ตรวจสอบข้อมูลทุก 60 วินาที
while True:
    check_for_updates()
    time.sleep(60)
