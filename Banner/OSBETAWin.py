import requests
import time
import json
import os

# ================== Discord Webhook URLs ==================
webhook_urls = [
    os.environ.get("WEBHOOK1"),
    os.environ.get("WEBHOOK2"),
    os.environ.get("WEBHOOK3"),
]

# ================== ตัวแปรเก็บข้อมูลล่าสุด ==================
last_data_1 = None
last_data_2 = None

# ================== ฟังก์ชันตรวจสอบและส่ง Discord ==================
def check_for_updates():
    global last_data_1, last_data_2

    url_1 = "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/G153/index.json"
    url_2 = "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json"

    # ====== URL 1 ======
    try:
        response_1 = requests.get(url_1, timeout=10)
        response_1.raise_for_status()
        data_1 = response_1.json()
        if data_1 != last_data_1:
            send_webhooks(data_1, url_1, "Wuthering Waves BETA OS (LAUNCHER)", last_data_1)
            last_data_1 = data_1
        else:
            print("[URL 1] No changes detected")
    except Exception as e:
        print(f"❌ ไม่สามารถดึงข้อมูลจาก URL 1: {e}")

    # ====== URL 2 ======
    try:
        response_2 = requests.get(url_2, timeout=10)
        response_2.raise_for_status()
        data_2 = response_2.json()
        if data_2 != last_data_2:
            send_webhooks(data_2, url_2, "Wuthering Waves BETA OS (Game)", last_data_2)
            last_data_2 = data_2
        else:
            print("[URL 2] No changes detected")
    except Exception as e:
        print(f"❌ ไม่สามารถดึงข้อมูลจาก URL 2: {e}")

# ================== ส่ง webhook หลายตัว ==================
def send_webhooks(data, url, title, last_data):
    for webhook_key, webhook_url in webhook_urls.items():
        send_webhook(data, url, title, webhook_key, webhook_url, last_data)

# ================== ส่ง webhook ตัวเดียว ==================
def send_webhook(data, url, title, webhook_key, webhook_url, last_data):
    if not webhook_url:
        print(f"⚠️ Webhook URL สำหรับ {webhook_key} ไม่ถูกต้อง, ข้ามการส่ง")
        return

    # ================== Prepare Embed Fields ==================
    embed_fields = []
    current_version = data["default"].get("version", "No data")
    current_installer = data["default"].get("installer", "No data")
    current_resources = data["default"].get("resources", "No data")
    resource_path = data["default"].get("resource", {}).get("path", "No data")
    resource_version = data["default"].get("resource", {}).get("version", "No data")
    predownload = data.get("predownload", {})
    predownload_resources = predownload.get("resources", "No data")

    embed_fields.extend([
        {"name": "Version", "value": current_version, "inline": True},
        {"name": "Resource Version", "value": resource_version, "inline": True},
        {"name": "Installer", "value": json.dumps(current_installer, ensure_ascii=False), "inline": False},
        {"name": "Resources", "value": str(current_resources), "inline": False},
        {"name": "Resource Path", "value": resource_path, "inline": False},
        {"name": "Predownload Resources", "value": str(predownload_resources), "inline": False},
    ])

    # ================== Webhook Payload ==================
    webhook_data = {
        "embeds": [
            {
                "title": title,
                "description": url,
                "color": 16711680,  # สีแดง
                "fields": embed_fields,
                "thumbnail": {
                    "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"
                },
                "image": {
                    "url": "https://static1.anpoimages.com/wordpress/wp-content/uploads/2024/05/wuthering-waves-hero-resized-16-9.jpg"
                }
            }
        ]
    }

    # ================== ส่งไปยัง Discord ==================
    try:
        response = requests.post(webhook_url, json=webhook_data, timeout=10)
        if response.status_code == 204:
            print(f"✅ ส่งข้อความ {title} ไปยัง Discord ({webhook_key}) เรียบร้อยแล้ว!")
        else:
            print(f"❌ ไม่สามารถส่ง {title} ได้ที่ {webhook_key}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Error sending webhook {webhook_key}: {e}")

# ================== Loop ทุก 60 วินาที ==================
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(3)
