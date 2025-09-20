import requests
import time
import json
import logging
from datetime import datetime

# Webhook
webhook_urls = {
    "Wuthering Waves Beta": 'YOUR_DISCORD_WEBHOOK_URL',
    "Wuthering Waves Beta 2": 'YOUR_DISCORD_WEBHOOK_URL',
    "Teat": 'YOUR_DISCORD_WEBHOOK_URL'
}

# Log setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.StreamHandler()])

# เก็บข้อมูลล่าสุด
last_data = {
    "launcher": None,
    "game": None
}

# URLs ที่จะตรวจสอบ
url_1 = "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/G153/index.json"
url_2 = "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json"

# แบ่งข้อความให้อยู่ในขีดจำกัดของ Discord
def split_text(text, max_total=6000, max_each=4096):
    parts = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) <= max_each:
            current += line
        else:
            parts.append(current)
            current = line
        if sum(len(p) for p in parts) + len(current) >= max_total:
            break
    if current:
        parts.append(current)
    return parts

# ส่งข้อมูลไปยัง Discord
def send_to_discord(source, content):
    for name, webhook_url in webhook_urls.items():
        try:
            pretty_content = json.dumps(json.loads(content), indent=4, ensure_ascii=False)
            chunks = split_text(pretty_content, max_total=6000)

            embeds = []
            for chunk in chunks:
                embeds.append({
                    "title": f"{name} - Wuthering Waves CN BETA {source}" if len(embeds) == 0 else None,
                    "description": f"```json\n{chunk}\n```",
                    "color": 0x00ecff,
                    "thumbnail": {
                        "url": ""
                    } if len(embeds) == 0 else None,
                    "image": {
                        "url": ""
                    } if len(embeds) == 0 else None,
                    "footer": {
                        "text": "Wuthering Waves Update Monitor",
                        "icon_url": "https://cdn.discordapp.com/emojis/1263843556976623659.webp?size=96&animated=true"
                    } if len(embeds) == len(chunks) - 1 else None,
                    "timestamp": datetime.utcnow().isoformat() if len(embeds) == 0 else None
                })
            response = requests.post(webhook_url, json={"username": "Kuro-Game Monitor", "embeds": embeds})
            if response.status_code == 1000 or response.status_code == 204:
                logging.info(f"✅ ส่งสำเร็จไปยัง {name} ({source})")
            else:
                logging.error(f"❌ ล้มเหลว ({response.status_code}) สำหรับ {name} ({source}) - {response.text}")
        except Exception as e:
            logging.error(f"❗ ข้อผิดพลาดในการส่งข้อมูลไปยัง {name} ({source}): {e}")

# ตรวจสอบการอัปเดต
def check_update():
    global last_data

    for label, url in [("launcher", url_1), ("game", url_2)]:
        try:
            res = requests.get(url)
            if res.status_code == 200:
                content = res.text.strip()
                if content != last_data[label]:
                    last_data[label] = content
                    logging.info(f"🟢 ตรวจพบการเปลี่ยนแปลงจาก {label}")
                    send_to_discord(label, content)
                else:
                    logging.info(f"🟡 ไม่มีการเปลี่ยนแปลงจาก {label}")
            else:
                logging.error(f"🔴 ดึงข้อมูลล้มเหลวจาก {label}: {res.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"❗ เกิดข้อผิดพลาดจาก {label}: {e}")
            time.sleep(5)

# วนลูปทุก 60 วินาที
while True:
    check_update()
    time.sleep(60)
