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
MAX_DESC = 4000  # Discord limit per embed description

def chunk_text(text, max_len=MAX_DESC):
    """แบ่งข้อความยาว ๆ เป็นหลาย embed description"""
    lines = text.splitlines()
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks

def create_embeds(title, text, color=65535):
    """สร้าง embeds จากข้อความยาว"""
    chunks = chunk_text(text)
    embeds = []
    for idx, chunk in enumerate(chunks, start=1):
        embeds.append({
            "title": f"{title} (Part {idx})" if len(chunks) > 1 else title,
            "description": chunk,
            "color": color
        })
    return embeds

def send_to_webhooks(title, data):
    """ส่งข้อมูลไป webhook แต่ละตัว"""
    # แปลง JSON เป็น string แบบสวยงาม
    full_text = json.dumps(data, indent=2, ensure_ascii=False)
    embeds = create_embeds(title, full_text)
    for webhook in webhook_urls:
        if not webhook:
            continue
        # Discord limit: max 10 embeds per request
        for i in range(0, len(embeds), 10):
            batch = embeds[i:i+10]
            payload = {"embeds": batch}
            try:
                resp = requests.post(webhook, json=payload, timeout=10)
                if resp.status_code not in (200, 204):
                    print(f"❌ ส่งไม่ได้: {resp.status_code} {resp.text}")
                else:
                    print(f"✅ ส่ง Embed จำนวน {len(batch)} สำเร็จ")
            except Exception as e:
                print(f"❌ Error sending webhook: {e}")

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
            send_to_webhooks(game_name, data)
        else:
            print(f"[{game_name}] No changes detected")

# ================= Run =================
if __name__ == "__main__":
    check_for_updates()