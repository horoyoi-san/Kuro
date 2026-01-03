import requests
import time
import re
from collections import defaultdict

WEBHOOK_URL = "YOUR_DISCORD"
DATA_URL = "YOUR_DATA_SOURCE_URL JSON OR TXT"

PURPLE = 0x0000ff
GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJuczV2MGVvOWUxa3hsaGZpMDRzOTJ5eGE2ZmczM2lvaWJhcjkzdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1RCKEiSdMbYsMWRfXR/giphy.gif"

EMBED_LIMIT = 4096

# 1) ดึงข้อมูลจาก URL
resp = requests.get(DATA_URL, timeout=15)
resp.raise_for_status()
text = resp.text.strip()

# 2) แยก block ต่อเวอร์ชัน
# ใช้ "Wuthering Waves X.Y" เป็นตัวขึ้นต้น
blocks = re.split(r"\n(?=Wuthering Waves \d+\.\d)", text)
blocks = [b.strip() for b in blocks if b.strip()]

# 3) group ตาม major version (4.x, 5.x, ...)
groups = defaultdict(list)

for block in blocks:
    m = re.search(r"Wuthering Waves (\d+)\.(\d+)", block)
    if not m:
        continue
    major = int(m.group(1))
    minor = int(m.group(2))
    groups[major].append((minor, block))

# 4) เรียง minor และสร้าง Embed
for major in sorted(groups.keys()):
    versions = sorted(groups[major], key=lambda x: x[0])

    current_desc = ""
    embeds_to_send = []

    for _, block in versions:
        candidate = block + "\n\n"
        if len(current_desc) + len(candidate) > EMBED_LIMIT:
            embeds_to_send.append(current_desc.rstrip())
            current_desc = candidate
        else:
            current_desc += candidate

    if current_desc.strip():
        embeds_to_send.append(current_desc.rstrip())

    # 5) ส่ง Embed ทีละอัน
    for desc in embeds_to_send:
        payload = {
            "embeds": [
                {
                    "title": f"Wuthering Waves Timeline (STC)({major}.0)",
                    "description": desc,
                    "color": PURPLE,
                    "image": {"url": GIF_URL}
                }
            ]
        }
        requests.post(WEBHOOK_URL, json=payload)
        time.sleep(1)  # กัน rate limit
