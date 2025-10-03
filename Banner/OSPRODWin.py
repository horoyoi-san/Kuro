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

    # สร้าง hash ของข้อมูล
    current_hash = hashlib.md5(data_text.encode()).hexdigest()

    # สร้างโฟลเดอร์ log
    log_dir = os.path.join(os.getcwd(), "Kuro", "log", game_name)
    os.makedirs(log_dir, exist_ok=True)

    hash_file = os.path.join(log_dir, "last_hash.txt")
    raw_file = os.path.join(log_dir, "raw_log.jsonl")

    # บันทึก JSON ดิบทุกครั้ง
    try:
        with open(raw_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data_json
            }, ensure_ascii=False) + "\n")
        print(f"✅ Wrote raw log for {game_name}")
    except Exception as e:
        print(f"❌ Error writing log file for {game_name}: {e}")

    # อ่าน hash ก่อนหน้า
    last_hash = ""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            last_hash = f.read().strip()

    # ตรวจสอบว่าข้อมูลเปลี่ยนแปลงหรือไม่
    if current_hash != last_hash:
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True, data_json
    return False, data_json  # ส่ง data_json เพื่อให้ส่ง webhook ทุกครั้ง

# ================= Discord =================
def send_webhooks(data, url, title):
    for webhook_url in webhook_urls:
        send_webhook(data, url, title, webhook_url)

def send_webhook(data, url, title, webhook_url):
    if not webhook_url:
        print(f"⚠️ Webhook URL ไม่ถูกต้อง, ข้ามการส่ง")
        return

    if not isinstance(data, dict) or "default" not in data:
        print(f"❌ Unexpected JSON format for {title}, skipping webhook")
        return

    default_data = data["default"]
    current_version = default_data.get("version", "No data")
    current_installer = default_data.get("installer", "No data")
    current_resources = default_data.get("resources", "No data")
    resource_path = default_data.get("resource", {}).get("path", "No data")
    predownload_resources = data.get("predownload", {}).get("resources", "No data")

    embed_fields = [
        {"name": "Version", "value": str(current_version), "inline": True},
        {"name": "Installer", "value": json.dumps(current_installer, ensure_ascii=False), "inline": False},
        {"name": "Resources", "value": str(current_resources), "inline": False},
        {"name": "Resource Path", "value": resource_path, "inline": False},
        {"name": "Predownload Resources", "value": str(predownload_resources), "inline": False},
    ]

    # ✅ ดึงรูปจาก en.json
    extra_url = "https://prod-alicdn-gamestarter.kurogame.com/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/background/U82Wn9dbNc2o7zZBWz1cOnJm9r52qFKH/en.json"
    extra_resp = requests.get(extra_url).json()

    first_frame_img = extra_resp.get("firstFrameImage", "")
    slogan_img = extra_resp.get("slogan", "")

    # สร้าง embed
    webhook_data = {
        "embeds": [
            {
                "title": title,
                "description": f"{url}",  
                "color": 65535,  # สีแดง
                "fields": embed_fields,
                "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},  # ✅ ใช้ slogan เป็น thumbnail
                "image": {"url": first_frame_img}  # ✅ ใช้ firstFrameImage เป็นภาพหลัก
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=webhook_data, timeout=10)
        if response.status_code == 204:
            print(f"✅ ส่งข้อความ {title} ไปยัง Discord เรียบร้อยแล้ว!")
        else:
            print(f"❌ ไม่สามารถส่ง {title} ได้: {response.status_code}, {response.text}")
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
        if data:
            send_webhooks(data, api_url, game_name)
        if not changed:
            print(f"[{game_name}] No changes detected")

if __name__ == "__main__":
    check_for_updates()  # รันครั้งเดียว
