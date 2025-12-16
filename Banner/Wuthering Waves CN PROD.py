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

# ================= Discord =================
def split_text_to_embeds(title, text, color=65535, max_len=1024):
    """ แบ่งข้อความยาวเป็นหลาย embed """
    if not text:
        return []
    embeds = []
    lines = text.split("\n")
    current = ""
    part = 1
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            embeds.append({
                "title": f"{title} {part}",
                "description": current,
                "color": color,
                "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
                "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
            })
            current = line
            part += 1
        else:
            current += ("\n" if current else "") + line
    if current:
        embeds.append({
            "title": f"{title} {part}",
            "description": current,
            "color": color,
            "thumbnail": {"url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkmsLi-PweF4K3vppsBMmbrQ2zFikTpYHdNg&s"},
            "image": {"url": "https://wutheringwaves.kurogames.com/website-preface/video/bg/bg-poster.webp"}
        })
    return embeds

def extract_cmd_options(data, key, title_prefix):
    options = []
    cmd_list = data.get(key, [])

    for cmd in cmd_list:
        if cmd.get("isShow") != 1:
            continue

        option = cmd.get("cmdOption", "").strip()
        if not option:
            continue

        text = cmd.get("text", {})

        desc_lines = [f"{option}: "]

        # เรียงภาษาให้อ่านง่าย
        for lang in ["zh-Hans", "de", "zh-Hant", "ko", "th", "ja", "en", "fr", "es"]:
            if lang in text:
                desc_lines.append(f"`{lang}` {text[lang]}")

        options.append("\n".join(desc_lines))

    if not options:
        return []

    return split_text_to_embeds(
        title_prefix,
        "\n\n".join(options),
        color=0x9B59B6  # ม่วง
    )


def send_webhooks(data, title):
    for webhook_url in webhook_urls:
        send_webhook(data, title, webhook_url)

def send_webhook(data, title, webhook_url, batch_size=1):
    if not webhook_url:
        print("⚠️ Webhook URL ไม่ถูกต้อง")
        return

    blocks = []

    # ================= Launch Commands =================
    if data.get("commandSwitch") == 1:
        blocks += extract_cmd_options(
            data,
            "commandList",
            title + " — Launch Commands"
        )

    # ================= RHI / DX Options =================
    if data.get("RHIOptionSwitch") == 1:
        blocks += extract_cmd_options(
            data,
            "RHIOptionList",
            title + " — Graphics Options"
        )

    # ================= Default =================
    default = data.get("default")
    if default:
        resource = default.get("resource")
        if resource:  # Launcher
            version = resource.get("version", "No version")
            size = resource.get("size", 0)
            md5 = resource.get("md5", "")
            cdn_list = default.get("cdnList", [])
            path = resource.get("path", "")
            url_full = cdn_list[0]["url"] + path if cdn_list and path else path
            desc = f"Version: {version}\nSize: {size/1024/1024:.2f} MB\nMD5: {md5}\nDownload: {url_full}"
            blocks += split_text_to_embeds(title + " — Launcher", desc)
        else:  # Game
            config = default.get("config", {})
            version = config.get("version", "No version")
            size = config.get("size", 0)
            md5 = config.get("indexFileMd5", "")

            # ====== new fields ======
            index_file_main = config.get("indexFile", "N/A")
            resources_file = default.get("resources", "N/A")
            # =========================

            cdn_list = default.get("cdnList", [])
            patch_lines = []
            for patch in config.get("patchConfig", []):
                ver = patch.get("version")
                index_file = patch.get("indexFile")
                full_url_patch = cdn_list[0]["url"] + index_file if cdn_list else index_file
                patch_lines.append(f"{ver}: {full_url_patch}")

            url_full = patch_lines[-1] if patch_lines else "No URL"

            # === description now includes indexFile + resources ===
            desc = (
                f"Version: {version}\n"
                f"Size: {size/1024/1024:.2f} MB\n"
                f"MD5: {md5}\n"
                f"Download: {url_full}\n"
                f"IndexFile: {cdn_list[0]['url'] + index_file_main if cdn_list else index_file_main}\n"
                f"Resources: {cdn_list[0]['url'] + resources_file if cdn_list else resources_file}"
            )

            blocks += split_text_to_embeds(title + " — Game", desc)
            blocks += split_text_to_embeds(title + " — Hdiff", "\n".join(patch_lines))

    # ================= Predownload =================
    predownload = data.get("predownload")
    if predownload:
        config = predownload.get("config", {})
        version = config.get("version", "No version")
        size = config.get("size", 0)
        md5 = config.get("indexFileMd5", "")

        # ====== new fields ======
        index_file_main = config.get("indexFile", "N/A")
        resources_file = predownload.get("resources", "N/A")
        # =========================

        cdn_list = default.get("cdnList", [])
        patch_lines = []
        for patch in config.get("patchConfig", []):
            ver = patch.get("version")
            index_file = patch.get("indexFile")
            full_url_patch = cdn_list[0]["url"] + index_file if cdn_list else index_file
            patch_lines.append(f"{ver}: {full_url_patch}")

        # Main predownload info
        full_url_predownload = patch_lines[-1] if patch_lines else "No URL"
        desc = (
            f"Version: {version}\n"
            f"Size: {size/1024/1024:.2f} MB\n"
            f"MD5: {md5}\n"
            f"Download: {full_url_predownload}\n"
            f"IndexFile: {cdn_list[0]['url'] + index_file_main if cdn_list else index_file_main}\n"
            f"Resources: {cdn_list[0]['url'] + resources_file if cdn_list else resources_file}"
        )

        blocks += split_text_to_embeds(title + " — Predownload", desc, color=65535)
        blocks += split_text_to_embeds(title + " — Predownload Hdiff", "\n".join(patch_lines), color=65535)

    # ================= Send in batches =================
    for i, embed in enumerate(blocks, start=1):
        try:
            response = requests.post(webhook_url, json={"embeds": [embed]}, timeout=10)
            if response.status_code == 204:
                print(f"✅ ส่ง embed {i} ของ {title} แล้ว")
            else:
                print(f"❌ ส่ง embed {i} ไม่สำเร็จ: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")

# ================= Main =================
def check_for_updates():
    urls = [
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json", "Wuthering Waves PROD-L CN"),
        ("https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json", "Wuthering Waves PROD-G CN")
    ]
    for api_url, game_name in urls:
        changed, data = log_and_check(api_url, game_name)
        if changed and data:
            send_webhooks(data, game_name)
        else:
            print(f"[{game_name}] No changes detected")

if __name__ == "__main__":
    check_for_updates()