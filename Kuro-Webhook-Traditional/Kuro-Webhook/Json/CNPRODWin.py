import requests
import time
import json
import logging
from datetime import datetime, timezone  # เพิ่ม timezone ที่นี่



# Webhook
webhook_urls = {
    "Wuthering Waves": 'https://discord.com/api/webhooks/1315273814132785273/KCEkUloeo75HpgwrEVhXDfRzLSuOB7LHf0Nm1zCme0I1s-bl_jkujpcVZC8KSKifEkNU',
    "Wuthering Waves 2": 'https://discord.com/api/webhooks/1313874393532989532/0mN1RuiIcN9zDC4HmE4PIOcAPN7B73tgX2TUHMpQH3EkmRTiy5LizlR1PZsnf-J0RSQs',
    "Teat": 'https://discord.com/api/webhooks/1291725154937999444/CeBZotZNDREE7KM7mFx7DJ--Z2TD8tKKmfgZ8gqPUrLs2Bs2rALXjm6HPqv_VKNxGfQJ'
}

# Log setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.StreamHandler()])

# เก็บข้อมูลล่าสุด
last_data = {
    "launcher": None,
    "game": None
}

# URLs ที่จะตรวจสอบ
url_1 = "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json"
url_2 = "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json"

# แบ่งข้อความให้อยู่ในขีดจำกัดของ Discord
# แบ่งข้อความให้อยู่ในขีดจำกัดของ Discord
# ส่งข้อมูลไปยัง Discord
# ส่งข้อมูลไปยัง Discord
def send_to_discord(source, content):
    for name, webhook_url in webhook_urls.items():
        try:
            pretty_content = json.dumps(json.loads(content), indent=4, ensure_ascii=False)
            chunks = split_text(pretty_content, max_total=7000)

            embeds = []
            for chunk in chunks:
                # ตรวจสอบขนาดของ embed ก่อนเพิ่ม
                if len(chunk) <= 6000:
                    embeds.append({
                        "title": f"{name} - Wuthering Waves CN PROD {source}" if len(embeds) == 0 else None,
                        "description": f"```json\n{chunk}\n```",
                        "color": 0x00ecff,
                        "footer": {
                            "text": "Wuthering Waves Update Monitor",
                            "icon_url": "https://cdn.discordapp.com/emojis/1263843556976623659.webp?size=96&animated=true"
                        } if len(embeds) == len(chunks) - 1 else None,
                        "timestamp": datetime.now(timezone.utc).isoformat() if len(embeds) == 0 else None
                    })
                else:
                    logging.error(f"❌ ข้อความเกินขีดจำกัดที่ Discord กำหนด: {len(chunk)}")
            
            # ตรวจสอบการส่งข้อมูล
            if embeds:
                for embed in embeds:
                    if len(json.dumps(embed)) <= 6000:
                        response = requests.post(webhook_url, json={"username": "Kuro-Game Monitor", "embeds": [embed]})
                        if response.status_code == 6000 or response.status_code == 204:
                            logging.info(f"✅ ส่งสำเร็จไปยัง {name} ({source})")
                        else:
                            logging.error(f"❌ ล้มเหลว ({response.status_code}) สำหรับ {name} ({source}) - {response.text}")
                    else:
                        logging.error(f"❌ ข้อความ embed เกินขีดจำกัด: {len(json.dumps(embed))}")

        except Exception as e:
            logging.error(f"❗ ข้อผิดพลาดในการส่งข้อมูลไปยัง {name} ({source}): {e}")

# แบ่งข้อความให้อยู่ในขีดจำกัดของ Discord
def split_text(text, max_total=7000, max_each=4096):
    parts = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) <= max_each:
            current += line
        else:
            parts.append(current)
            current = line
        # เพิ่มการตรวจสอบว่าแต่ละข้อความที่รวมกันไม่เกิน max_total
        if sum(len(part) for part in parts) + len(current) >= max_total:
            break
    if current:
        parts.append(current)
    return parts


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
