import discord
import asyncio
import time

import requests
import json
import os
import hashlib

from datetime import datetime, timezone

# =========================================================
# Discord
# =========================================================

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = discord.Client(intents=intents)

# =========================================================
# Branding
# =========================================================

BOT_NAME = "鸣潮"

BOT_ICON = (
    "https://raw.githubusercontent.com/"
    "horoyoi-san/Kuro/refs/heads/Webhook/assets/ww.png"
)

# =========================================================
# Dynamic Background
# =========================================================


def get_background_image(data):

    try:
        print("[DEBUG] Background JSON keys:", list(data.keys()))
        print("[DEBUG] functionCode:", data.get("functionCode"))
        print(
            "[DEBUG] config.functionCode:",
            data.get("config", {}).get("functionCode")
        )

        bg_id = (
            data.get("config", {}).get("functionCode", {}).get("background")
            or data.get("functionCode", {}).get("background")
        )

        if not bg_id:
            print("⚠️ ไม่พบ Background ID ใน JSON")
            return None

        manifest_url = (
            "https://prod-volcdn-gamestarter.kurogame.xyz/"
            "launcher/game/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/"
            f"G152/official/background/{bg_id}/zh-Hans.json"
        )

        print(f"🎨 Background Manifest: {manifest_url}")

        manifest = requests.get(manifest_url, timeout=10).json()

        image = manifest.get("firstFrameImage")

        if image:

            print(f"🖼️ Background Image: {image}")

            return image

        print("⚠️ No firstFrameImage found")

    except Exception as e:

        print(f"❌ Background fetch error: {e}")

    return None


# =========================================================
# Channels
# =========================================================

CHANNELS = [
    1292097230924283965,  # Test
    1291728736739131402,  # 1
    1267379122338791435,  # 2
]

# =========================================================
# Logging
# =========================================================


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

    # =====================================================
    # Write Raw Log
    # =====================================================

    try:

        with open(raw_file, "a", encoding="utf-8") as f:

            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": data_json,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

        print(f"✅ Wrote raw log for {game_name}")

    except Exception as e:

        print(f"❌ Error writing log file for {game_name}: {e}")

    # =====================================================
    # Read Last Hash
    # =====================================================

    last_hash = ""

    if os.path.exists(hash_file):

        with open(hash_file, "r", encoding="utf-8") as f:

            last_hash = f.read().strip()

    # =====================================================
    # Changed
    # =====================================================

    if current_hash != last_hash:

        with open(hash_file, "w", encoding="utf-8") as f:

            f.write(current_hash)

        return True, data_json

    return False, data_json


# =========================================================
# Size Formatter
# =========================================================


def format_size(size_bytes):

    gb = size_bytes / 1024 / 1024 / 1024

    if gb >= 1:
        return f"{gb:.2f} GB"

    mb = size_bytes / 1024 / 1024

    return f"{mb:.2f} MB"



def collect_game_file_links(data, limit=30):
    """เก็บเฉพาะข้อมูลไฟล์จาก resourcePacks และ bundles"""

    found = []
    seen = set()

    # ไม่ไล่เก็บ URL จาก config หรือข้อมูลข่าวทั่วทั้ง JSON
    sources = {
        "resourcePacks": data.get("resourcePacks"),
        "bundles": data.get("bundles"),
    }

    file_keys = {
        "url", "downloadurl", "download_url",
        "path", "filepath", "file_path",
        "downloadpath", "download_path",
        "indexfile", "index_file",
        "manifest", "manifesturl", "manifest_url",
    }

    def walk(obj, location="$"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_lower = str(key).lower()
                current = f"{location}.{key}"

                if isinstance(value, str) and value.strip():
                    value_clean = value.strip()
                    is_url = value_clean.startswith(("https://", "http://"))
                    is_file_field = key_lower in file_keys

                    if not (is_url or is_file_field):
                        continue

                    # ตัด URL ที่เป็นเพียง CDN root เช่น https://example.com/
                    if is_url:
                        from urllib.parse import urlparse

                        parsed = urlparse(value_clean)

                        if parsed.path in ("", "/") and not parsed.query:
                            continue

                        # ไม่เอาลิงก์ข่าวหรือเว็บไซต์ข่าว
                        path_lower = parsed.path.lower()
                        if any(word in path_lower for word in (
                            "/news/", "/notice/", "/article/",
                            "/announcement/",
                        )):
                            continue

                    item = (current, value_clean)

                    if item not in seen:
                        seen.add(item)
                        found.append(item)

                elif isinstance(value, (dict, list)):
                    walk(value, current)

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, f"{location}[{index}]")

    for name, obj in sources.items():
        if obj is not None:
            walk(obj, name)

    if not found:
        return "ไม่พบ URL ไฟล์โดยตรงใน resourcePacks หรือ bundles"

    lines = []

    for location, value in found[:limit]:
        lines.append(f"**{location}**\n{value}")

    if len(found) > limit:
        lines.append(f"... ยังมีข้อมูลอีก {len(found) - limit} รายการ")

    return "\n\n".join(lines)


# =========================================================
# Embed Utils
# =========================================================


def split_text_to_embeds(
    title, text, color=0x3498DB, max_len=4000, image_url=None
):
    """
    Split long text into multiple embeds
    """

    if not text:
        return []

    embeds = []

    lines = text.split("\n")

    current = ""

    part = 1

    for line in lines:

        if len(current) + len(line) + 1 > max_len:

            embed = discord.Embed(
                title=f"{title} {part}", description=current, color=color
            )

            embed.set_thumbnail(url=BOT_ICON)

            if image_url:
                embed.set_image(url=image_url)

            embed.set_footer(text="Horoyoi-san ඞ")

            embeds.append(embed)

            current = line

            part += 1

        else:

            current += ("\n" if current else "") + line

    # =====================================================
    # Last Block
    # =====================================================

    if current:

        embed = discord.Embed(title=f"{title} {part}", description=current, color=color)

        embed.set_thumbnail(url=BOT_ICON)

        if image_url:
            embed.set_image(url=image_url)

        embed.set_footer(text="Horoyoi-san ඞ")

        embeds.append(embed)

    return embeds


# =========================================================
# Extract Command Options
# =========================================================


# =========================================================
# Discord Send
# =========================================================


async def send_discord(channel_id, embeds):

    try:

        channel = await bot.fetch_channel(channel_id)

    except Exception as e:

        print(f"❌ Channel fetch error: {channel_id}")

        print(e)

        return

    for i, embed in enumerate(embeds, 1):

        try:

            await channel.send(embed=embed)

            print(f"✅ sent embed {i} -> {channel_id}")

            # anti rate limit
            await asyncio.sleep(1)

        except Exception as e:

            print(f"❌ send error -> {channel_id}")

            print(e)


# =========================================================
# Build Embeds
# =========================================================


def build_embeds(data, title, background_image=None):

    blocks = []

    # =====================================================
    # Default
    # =====================================================

    default = data.get("default")

    if default:

        resource = default.get("resource")

        # =================================================
        # Launcher
        # =================================================

        if resource:

            version = resource.get("version", "No version")

            size = resource.get("size", 0)

            md5 = resource.get("md5", "")

            cdn_list = default.get("cdnList", [])

            path = resource.get("path", "")

            url_full = cdn_list[0]["url"] + path if cdn_list and path else path

            desc = (
                f"## Version {version}\n"
                f"## Size `{format_size(size)}`\n"
                f"## Download\n"
                f"{url_full}"
            )

            blocks += split_text_to_embeds(title, desc, image_url=background_image)

        # =================================================
        # Game
        # =================================================

        else:

            config = default.get("config", {})

            version = config.get("version", "No version")

            size = config.get("size", 0)

            md5 = config.get("indexFileMd5", "")

            index_file_main = config.get("indexFile", "N/A")

            resources_file = default.get("resources", "N/A")

            cdn_list = default.get("cdnList", [])

            patch_lines = []

            for patch in config.get("patchConfig", []):

                ver = patch.get("version")

                index_file = patch.get("indexFile")

                full_url_patch = (
                    cdn_list[0]["url"] + index_file if cdn_list else index_file
                )

                patch_lines.append(f"{ver}: {full_url_patch}")

            url_full = patch_lines[-1] if patch_lines else "No URL"

            desc = (
                f"## Version {version}\n"
                f"## Size `{format_size(size)}`\n"
                f"## Download\n"
                f"{url_full}\n"
                f"## IndexFile\n"
                f"{cdn_list[0]['url'] + index_file_main if cdn_list else index_file_main}\n"
                f"## Resources\n"
                f"{cdn_list[0]['url'] + resources_file if cdn_list else resources_file}"
            )

            blocks += split_text_to_embeds(title, desc, image_url=background_image)

            blocks += split_text_to_embeds(
                title + " — Hdiff", "\n".join(patch_lines), image_url=background_image
            )

    # =====================================================
    # Predownload
    # =====================================================

    predownload = data.get("predownload")

    if predownload:

        config = predownload.get("config", {})

        version = config.get("version", "No version")

        size = config.get("size", 0)

        md5 = config.get("indexFileMd5", "")

        index_file_main = config.get("indexFile", "N/A")

        resources_file = predownload.get("resources", "N/A")

        cdn_list = default.get("cdnList", [])

        patch_lines = []

        for patch in config.get("patchConfig", []):

            ver = patch.get("version")

            index_file = patch.get("indexFile")

            full_url_patch = cdn_list[0]["url"] + index_file if cdn_list else index_file

            patch_lines.append(f"{ver}: {full_url_patch}")

        full_url_predownload = patch_lines[-1] if patch_lines else "No URL"

        desc = (
            f"## Version\n"
            f"`{version}`\n\n"
            f"## Size\n"
            f"`{format_size(size)}`\n\n"
            f"## MD5\n"
            f"`{md5}`\n\n"
            f"## Download\n"
            f"{full_url_predownload}\n\n"
            f"## IndexFile\n"
            f"{cdn_list[0]['url'] + index_file_main if cdn_list else index_file_main}\n\n"
            f"## Resources\n"
            f"{cdn_list[0]['url'] + resources_file if cdn_list else resources_file}"
        )

        blocks += split_text_to_embeds(
            title + " — Predownload", desc, color=0xF1C40F, image_url=background_image
        )

        blocks += split_text_to_embeds(
            title + " — Predownload Hdiff",
            "\n".join(patch_lines),
            color=0xF1C40F,
            image_url=background_image,
        )


    # =====================================================
    # Game Index รูปแบบใหม่ที่ไม่มี top-level "default"
    # =====================================================

    if not default and (
        data.get("config") is not None
        or data.get("resourcePacks") is not None
        or data.get("bundles") is not None
    ):
        config = data.get("config") or {}

        function_code = config.get("functionCode") or {}
        background_id = (
            function_code.get("background")
            or data.get("functionCode", {}).get("background")
            or "N/A"
        )

        # ค้นหาค่า Version จากชื่อฟิลด์ที่พบบ่อย
        def find_value(obj, names):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if str(key).lower() in names and value not in (None, ""):
                        if not isinstance(value, (dict, list)):
                            return value

                for value in obj.values():
                    result = find_value(value, names)
                    if result is not None:
                        return result

            elif isinstance(obj, list):
                for value in obj:
                    result = find_value(value, names)
                    if result is not None:
                        return result

            return None

        version = find_value(
            config,
            {"version", "gameversion", "game_version", "resversion"}
        )

        if version is None:
            version = find_value(
                data,
                {"gameversion", "game_version", "resversion"}
            )

        if version is None:
            version = "ไม่พบ Version ใน JSON"

        resource_packs = data.get("resourcePacks")
        bundles = data.get("bundles")

        resource_count = (
            len(resource_packs)
            if isinstance(resource_packs, (dict, list))
            else 0
        )

        bundle_count = (
            len(bundles)
            if isinstance(bundles, (dict, list))
            else 0
        )

        file_links = collect_game_file_links(data)

        # แสดงโครงสร้างจริงจาก JSON เพื่อไม่เดา Size/Download เอง
        def json_preview(value, max_chars=1400):
            if value is None:
                return "ไม่มีข้อมูล"

            text = json.dumps(
                value,
                ensure_ascii=False,
                indent=2
            )

            if len(text) > max_chars:
                text = text[:max_chars] + "\n... (ตัดข้อความส่วนที่เหลือ)"

            return f"```json\n{text}\n```"

        desc = (
            "## Game Index\n"
            f"**Version:** `{version}`\n"
            f"**Resource Packs:** `{resource_count}`\n"
            f"**Bundles:** `{bundle_count}`\n"
            f"**Background ID:** `{background_id}`\n"
            f"**Predownload:** "
            f"`{'มีข้อมูล' if data.get('predownload') else 'ไม่มีข้อมูล'}`\n\n"
            "## File URLs / Paths\n"
            f"{file_links}"
        )

        blocks += split_text_to_embeds(
            title,
            desc,
            color=0x00E5FF,
            image_url=background_image,
        )

        # ส่งรายละเอียดจริงแยก Embed เพื่อไม่ให้ข้อมูลถูกซ่อน
        for section_name, section_data in (
            ("Resource Packs", resource_packs),
            ("Bundles", bundles),
        ):
            if section_data is not None:
                detail = (
                    f"## {section_name} — JSON Structure\n"
                    f"{json_preview(section_data)}"
                )

                blocks += split_text_to_embeds(
                    f"{title} — {section_name}",
                    detail,
                    color=0x00E5FF,
                    image_url=background_image,
                )

    return blocks


# =========================================================
# Main
# =========================================================


async def main():

    await bot.login(TOKEN)

    print(f"✅ Logged in as {bot.user}")

    urls = [
        (
            "https://prod-volcdn-gamestarter.kurogame.xyz/launcher/app/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/index.json",
            "鸣潮 Launcher",
        ),
        (
            "https://prod-volcdn-gamestarter.kurogame.xyz/launcher/game/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/G152/official/index.json",
            "鸣潮 Game",
        ),
    ]

    launcher_background = None

    for api_url, game_name in urls:

        changed, data = log_and_check(api_url, game_name)

        if not data:
            continue

        # ดึงรูปใหม่ทุกครั้ง

        # ดึง Background ID จาก JSON ของ Game
        if "Game" in game_name:
            launcher_background = get_background_image(data)


        if changed:
            embeds = build_embeds(data, game_name, launcher_background)

            for channel_id in CHANNELS:
                await send_discord(channel_id, embeds)


# =========================================================
# Start
# =========================================================


async def runner():

    task = asyncio.create_task(bot.start(TOKEN))

    await asyncio.sleep(5)

    await main()

    await asyncio.sleep(15)

    await bot.close()

    await task


asyncio.run(runner())
