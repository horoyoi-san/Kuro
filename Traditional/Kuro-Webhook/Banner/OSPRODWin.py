import requests
import time
import json

# กำหนด Webhook URLs
webhook_urls = {
    "Wuthering Waves": ' ',
    "Wuthering Waves 2": ' ',
     "Teat": ' '
}

# ตัวแปรสำหรับเก็บข้อมูลล่าสุด
last_data_1 = None
last_data_2 = None

# ฟังก์ชันในการตรวจสอบและส่งข้อความไปยัง Discord Webhook
def check_for_updates():
    global last_data_1, last_data_2

    url_1 = "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json"
    url_2 = "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json"

    # ตรวจสอบข้อมูลจาก URL ที่ 1
    response_1 = requests.get(url_1)
    if response_1.status_code == 200:
        data_1 = response_1.json()
        if data_1 != last_data_1:
            send_webhooks(data_1, url_1, "Wuthering Waves OS (LAUNCHER)", last_data_1)
            last_data_1 = data_1
    else:
        print(f"ไม่สามารถดึงข้อมูลจาก URL 1: {response_1.status_code}, {response_1.text}")

    # ตรวจสอบข้อมูลจาก URL ที่ 2
    response_2 = requests.get(url_2)
    if response_2.status_code == 200:
        data_2 = response_2.json()
        if data_2 != last_data_2:
            send_webhooks(data_2, url_2, "Wuthering Waves OS (Game)", last_data_2)
            last_data_2 = data_2
    else:
        print(f"ไม่สามารถดึงข้อมูลจาก URL 2: {response_2.status_code}, {response_2.text}")

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

    webhook_url = webhook_urls.get(webhook_key)
    if webhook_url:
        response = requests.post(webhook_url, json=webhook_data)
        if response.status_code == 204:
            print(f"ส่งข้อความ {title} ไปยัง Discord ({webhook_key}) เรียบร้อยแล้ว!")
        else:
            print(f"ไม่สามารถส่งข้อความ {title} ได้ที่ Webhook {webhook_key}: {response.status_code}, {response.text}")

# ตรวจสอบข้อมูลทุก 60 วินาที
while True:
    check_for_updates()
    time.sleep(60)
