
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone

import discord
import requests


# =========================================================
# Discord
# =========================================================
#TOKEN = "67"
TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("ไม่พบ DISCORD_TOKEN ใน Environment Variables")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

BOT_NAME = "鸣潮"

BOT_ICON = (
    "https://raw.githubusercontent.com/"
    "horoyoi-san/Kuro/refs/heads/Webhook/assets/ww.png"
)

CHANNELS = [
    1292097230924283965,  # Test
    1291728736739131402,  # 1
    1267379122338791435,  # 2
]


# =========================================================
# API URLs
# =========================================================

URLS = [
    (
        "https://prod-volcdn-gamestarter.kurogame.xyz/"
        "launcher/app/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/"
        "index.json",
        "鸣潮 Launcher",
    ),
    (
        "https://prod-volcdn-gamestarter.kurogame.xyz/"
        "launcher/game/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/"
        "G152/official/index.json",
        "鸣潮 Game",
    ),
]


# =========================================================
# HTTP
# =========================================================

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 WutheringWavesMonitor/1.0"
})


def fetch_json(url):
    response = SESSION.get(url, timeout=20)
    response.raise_for_status()
    return response.json(), response.text


# =========================================================
# Logging / Change Detection
# =========================================================

def log_and_check(api_url, game_name):
    try:
        data, raw_text = fetch_json(api_url)
    except Exception as exc:
        print(f"❌ Error fetching {game_name}: {exc}")
        return False, None

    current_hash = hashlib.md5(
        raw_text.encode("utf-8")
    ).hexdigest()

    log_dir = os.path.join(
        os.getcwd(), "Kuro", "log", game_name
    )
    os.makedirs(log_dir, exist_ok=True)

    hash_file = os.path.join(log_dir, "last_hash.txt")
    raw_file = os.path.join(log_dir, "raw_log.jsonl")

    try:
        with open(raw_file, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(
                            timezone.utc
                        ).isoformat(),
                        "data": data,
                    },
                    ensure_ascii=False,
                ) + "\n"
            )
    except Exception as exc:
        print(f"❌ Error writing log: {exc}")

    try:
        with open(hash_file, "r", encoding="utf-8") as file:
            last_hash = file.read().strip()
    except FileNotFoundError:
        last_hash = ""

    changed = current_hash != last_hash

    if changed:
        try:
            with open(hash_file, "w", encoding="utf-8") as file:
                file.write(current_hash)
        except Exception as exc:
            print(f"❌ Error saving hash: {exc}")

    return changed, data


# =========================================================
# Size / Version Utilities
# =========================================================

def format_size(size_bytes):
    size_bytes = int(size_bytes or 0)

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def version_key(version):
    """เรียง Version เช่น 1.0.0, 3.6.0, 3.6.1"""
    try:
        return tuple(int(part) for part in str(version).split("."))
    except (TypeError, ValueError):
        return (0,)


def join_url(base_url, path):
    if not path:
        return ""

    if str(path).startswith(("https://", "http://")):
        return str(path)

    if not base_url:
        return str(path)

    return base_url.rstrip("/") + "/" + str(path).lstrip("/")


def get_cdn_base(data):
    for item in data.get("cdnList") or []:
        if isinstance(item, dict) and item.get("url"):
            return item["url"].rstrip("/") + "/"

    return ""


# =========================================================
# Dynamic Background
# =========================================================


def get_background_image(data):
    try:
        bg_id = (
            (data.get("config") or {})
            .get("functionCode", {})
            .get("background")
            or data.get("functionCode", {}).get("background")
        )

        if not bg_id:
            print("⚠️ ไม่พบ Background ID")
            return None

        manifest_url = (
            "https://prod-volcdn-gamestarter.kurogame.xyz/"
            "launcher/game/10003_oLNgHF1CESo51DGHN2odtp40e3oI1HfZ/"
            f"G152/official/background/{bg_id}/zh-Hans.json"
        )

        manifest, _ = fetch_json(manifest_url)
        image_url = manifest.get("firstFrameImage")

        if image_url and image_url.startswith("https://"):
            print(f"🖼️ Background: {image_url}")
            return image_url

        print("⚠️ ไม่พบ firstFrameImage ใน manifest")
        return None

    except Exception as exc:
        print(f"⚠️ Background fetch error: {exc}")
        return None



# =========================================================
# Embed Utilities
# =========================================================



def add_embed_image(embed: discord.Embed, image_url: str | None):
    embed.set_thumbnail(url=BOT_ICON)

    if image_url and image_url.startswith("https://"):
        embed.set_image(url=image_url)

    return embed


def split_text_to_embeds(
    title,
    text,
    color=0x00E5FF,
    max_len=3900,
    image_url=None,
):
    if not text:
        return []

    lines = []

    for line in text.splitlines():
        while len(line) > max_len:
            lines.append(line[:max_len])
            line = line[max_len:]

        lines.append(line)

    embeds = []
    current = ""
    part = 1

    for line in lines:
        candidate = current + ("\n" if current else "") + line

        if len(candidate) > max_len and current:
            embed = discord.Embed(
                title=title if part == 1 else f"{title} {part}",
                description=current,
                color=color,
            )

            add_embed_image(embed, image_url)
            embed.set_footer(text="Horoyoi-san ඞ")
            embeds.append(embed)

            current = line
            part += 1
        else:
            current = candidate

    if current:
        embed = discord.Embed(
            title=title if part == 1 else f"{title} {part}",
            description=current,
            color=color,
        )

        add_embed_image(embed, image_url)
        embed.set_footer(text="Horoyoi-san ඞ")
        embeds.append(embed)

    return embeds


# =========================================================
# Launcher Embed
# =========================================================

def build_launcher_embeds(data, title, background_image=None):
    default = data.get("default") or {}
    resource = default.get("resource") or {}

    if not resource:
        return split_text_to_embeds(
            title,
            "ไม่พบ default.resource ใน Launcher JSON",
            image_url=background_image,
        )

    version = resource.get("version", "ไม่ทราบ")
    size = resource.get("size", 0)
    path = resource.get("path", "")
    cdn_base = get_cdn_base(default)
    download_url = join_url(cdn_base, path)

    desc = (
        f"## Version `{version}`\n\n"
        f"## Size `{format_size(size)}`\n\n"
        f"## Download\n"
        f"{download_url or 'ไม่พบ Download URL'}"
    )

    return split_text_to_embeds(
        title,
        desc,
        image_url=background_image,
    )


# =========================================================
# Game Embed
# =========================================================

def build_game_embeds(data, title, background_image=None):
    packs = data.get("resourcePacks") or {}
    bundles = data.get("bundles") or {}
    cdn_base = get_cdn_base(data)

    if not packs:
        return split_text_to_embeds(
            title,
            "ไม่พบ resourcePacks ใน Game Index JSON",
            image_url=background_image,
        )

    blocks = []

    # ดึง Bundle ทุกประเภทที่ API มีจริง
    for bundle_name in ("common", "SD", "HD", "UHD"):
        bundle = bundles.get(bundle_name)

        if not isinstance(bundle, dict):
            print(f"ℹ️ ไม่พบ Bundle: {bundle_name}")
            continue

        selected_names = bundle.get("resourcePacks") or []

        if not selected_names:
            print(f"⚠️ {bundle_name} ไม่มี resourcePacks")
            continue

        selected_packs = [
            (name, packs[name])
            for name in selected_names
            if isinstance(packs.get(name), dict)
        ]

        if not selected_packs:
            continue

        version = next(
            (
                pack.get("version")
                for _, pack in selected_packs
                if pack.get("version")
            ),
            "ไม่ทราบ",
        )

        total_size = sum(
            int(pack.get("size", 0) or 0)
            for _, pack in selected_packs
        )

        index_lines = []
        resource_lines = []

        for name, pack in selected_packs:
            index_file = pack.get("indexFile")
            base_url = pack.get("baseUrl")

            if index_file:
                index_lines.append(
                    f"**{name.upper()}**\n"
                    f"{join_url(cdn_base, index_file)}"
                )

            if base_url:
                resource_lines.append(
                    f"**{name.upper()}**\n"
                    f"{join_url(cdn_base, base_url)}"
                )

        desc = (
            f"## Bundle `{bundle_name}`\n\n"
            f"## Version `{version}`\n\n"
            f"## Size `{format_size(total_size)}`\n\n"
            f"## IndexFile\n"
            f"{chr(10).join(index_lines) or 'ไม่พบ indexFile'}\n\n"
            f"## Resources\n"
            f"{chr(10).join(resource_lines) or 'ไม่พบ baseUrl'}"
        )

        blocks += split_text_to_embeds(
            f"{title} — {bundle_name}",
            desc,
            color=0x00E5FF,
            image_url=background_image,
        )

    # แสดง Hdiff จาก common.patchConfig
    common_pack = packs.get("common") or {}
    patches = common_pack.get("patchConfig") or []

    valid_patches = [
        patch for patch in patches
        if isinstance(patch, dict)
        and patch.get("version")
        and patch.get("indexFile")
    ]

    valid_patches.sort(
        key=lambda item: version_key(item["version"])
    )

    if valid_patches:
        hdiff_lines = []

        for patch in valid_patches:
            hdiff_lines.append(
                f"**{patch['version']}**\n"
                f"{join_url(cdn_base, patch['indexFile'])}"
            )

        blocks += split_text_to_embeds(
            f"{title} — Hdiff",
            "\n\n".join(hdiff_lines),
            color=0x00E5FF,
            image_url=background_image,
        )

    return blocks



# =========================================================
# Build Embeds
# =========================================================

def build_embeds(data, title, background_image=None):
    if "Launcher" in title:
        return build_launcher_embeds(
            data, title, background_image
        )

    return build_game_embeds(
        data, title, background_image
    )


# =========================================================
# Discord Send
# =========================================================

async def send_discord(channel_id, embeds):
    try:
        channel = await bot.fetch_channel(channel_id)
    except Exception as exc:
        print(f"❌ Channel fetch error: {channel_id}: {exc}")
        return

    for index, embed in enumerate(embeds, 1):
        try:
            await channel.send(embed=embed)
            print(f"✅ Sent Embed {index} -> {channel_id}")
            await asyncio.sleep(1)
        except Exception as exc:
            print(f"❌ Send error -> {channel_id}: {exc}")


# =========================================================
# Main
# =========================================================

async def main():
    results = []

    # โหลด JSON ทั้งสองชุดก่อน เพื่อให้ Launcher ใช้ Background ได้
    for api_url, game_name in URLS:
        changed, data = log_and_check(api_url, game_name)

        if data is not None:
            results.append((changed, data, game_name))

    game_data = next(
        (
            data for _, data, name in results
            if "Game" in name
        ),
        None,
    )

    background_image = (
        get_background_image(game_data)
        if game_data else None
    )

    for changed, data, game_name in results:
        if not changed:
            print(f"ℹ️ No changes: {game_name}")
            continue

        embeds = build_embeds(
            data,
            game_name,
            background_image,
        )

        for channel_id in CHANNELS:
            await send_discord(channel_id, embeds)


# =========================================================
# Start
# =========================================================

async def runner():
    async with bot:
        task = asyncio.create_task(bot.start(TOKEN))

        try:
            await bot.wait_until_ready()
            print(f"✅ Logged in as {bot.user}")

            await main()

            await asyncio.sleep(5)

        finally:
            await bot.close()
            await task


asyncio.run(runner())
