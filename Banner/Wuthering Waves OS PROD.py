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

# ================= Discord Embed Helper =================
MAX_EMBED = 6000
MAX_EMBEDS_PER_REQUEST = 10

def split_text(text, chunk_size=MAX_EMBED):
    """แบ่งข้อความออกเป็นหลายก้อน ไม่เกิน chunk_size"""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def send_big_message(webhook_url, title, full_text):
    """ส่งข้อความยาวเป็น embed หลายตัว และหลาย request ถ้าจำเป็น"""
    if not webhook_url:
        return

    chunks = split_text(full_text, MAX_EMBED)
    embeds = []

    for index, chunk in enumerate(chunks, start=1):
        embeds.append({
            "title": f"{title} (Part {index})" if len(chunks) > 1 else title,
            "description": chunk,
            "color": 0x2ECC71
        })

    batches = [embeds[i:i + MAX_EMBEDS_PER_REQUEST] for i in range(0, len(embeds), MAX_EMBEDS_PER_REQUEST)]

    for batch in batches:
        payload = {"embeds": batch}
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code not in (200, 204):
                print(f"❌ ส่งไม่ได้: {resp.status_code} {resp.text}")
            else:
                print(f"✅ ส่ง Embed จำนวน {len(batch)} สำเร็จ")
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")

# ================= Webhook Sender =================
def send_webhooks(data, title):
    raw_text = json.dumps(data, indent=4, ensure_ascii=False)
    for webhook_url in webhook_urls:
        send_big_message(webhook_url, title, raw_text)

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
            send_webhooks(data, game_name)
        else:
            print(f"[{game_name}] No changes detected")

# ================= Run =================
if __name__ == "__main__":
    check_for_updates()