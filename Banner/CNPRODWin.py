import requests
import json
import os
import hashlib
from datetime import datetime, timezone

# ================= Webhook =================
webhook_urls = [
    os.environ.get("WEBHOOK1"),
  #  os.environ.get("WEBHOOK2"),
  #  os.environ.get("WEBHOOK3"),
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

    cdn_list = default_data.get("cdnList", [])
    resource = default_data.get("resource", {})
    version = resource.get("version", "No version")
    path = resource.get("path", "")
    md5 = resource.get("md5", "")
    size = resource.get("size", 0)

    # ✅ รวม URL เต็มจาก CDN แรก
    full_url = cdn_list[0]["url"] + path if cdn_list and path else "No URL"

    embed_fields = [
        {"name": "Version", "value": version, "inline": True},
        {"name": "File Size", "value": f"{size/1024/1024:.2f} MB", "inline": True},
        {"name": "MD5", "value": md5, "inline": False},
        {"name": "Download (CDN 1)", "value": f"{full_url}", "inline": False},
    ]

    extra_url = "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"

    webhook_data = {
        "embeds": [
            {
                "title": title,
                "description": f"[เปิดในเบราว์เซอร์]({url})",
                "color": 65535,
                "fields": embed_fields,
                "thumbnail": {
                    "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"
                },
                "image": {"url": extra_url}
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
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json", "Wuthering Waves CN (Launcher)"),
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json", "Wuthering Waves CN (Game)")
    ]
    for api_url, game_name in urls:
        changed, data = log_and_check(api_url, game_name)
        if changed and data:
            send_webhooks(data, api_url, game_name)
        else:
            print(f"[{game_name}] No changes detected")

if __name__ == "__main__":
    check_for_updates()
