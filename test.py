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

# TOKEN = os.environ.get("DISCORD_TOKEN")
TOKEN = "xxxxxxxxxxxxxxxx"
intents = discord.Intents.default()

bot = discord.Client(
    intents=intents
)

# =========================================================
# Branding
# =========================================================

BOT_NAME = "Wuthering Waves"

BOT_ICON = (
    "https://raw.githubusercontent.com/"
    "horoyoi-san/Kuro/refs/heads/Webhook/assets/images.png"
)

MAIN_IMAGE = "https://nanoka.cc/images/ww.webp"

# =========================================================
# Channels
# =========================================================

CHANNELS = [
    99999999999999,
    99999999999999,
]

# =========================================================
# Logging
# =========================================================

def log_and_check(api_url, game_name):

    try:
        resp = requests.get(
            api_url,
            timeout=10
        )

        data_text = resp.text

        data_json = json.loads(
            data_text
        )

    except Exception as e:

        print(
            f"❌ Error fetching {game_name}: {e}"
        )

        return False, None

    current_hash = hashlib.md5(
        data_text.encode()
    ).hexdigest()

    log_dir = os.path.join(
        os.getcwd(),
        "Kuro",
        "log",
        game_name
    )

    os.makedirs(
        log_dir,
        exist_ok=True
    )

    hash_file = os.path.join(
        log_dir,
        "last_hash.txt"
    )

    raw_file = os.path.join(
        log_dir,
        "raw_log.jsonl"
    )

    # =====================================================
    # Write Raw Log
    # =====================================================

    try:

        with open(
            raw_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(json.dumps({

                "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

                "data":
                data_json

            }, ensure_ascii=False) + "\n")

        print(
            f"✅ Wrote raw log for {game_name}"
        )

    except Exception as e:

        print(
            f"❌ Error writing log file for {game_name}: {e}"
        )

    # =====================================================
    # Read Last Hash
    # =====================================================

    last_hash = ""

    if os.path.exists(hash_file):

        with open(
            hash_file,
            "r",
            encoding="utf-8"
        ) as f:

            last_hash = f.read().strip()

    # =====================================================
    # Changed
    # =====================================================

    if current_hash != last_hash:

        with open(
            hash_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(current_hash)

        return True, data_json

    return False, data_json

# =========================================================
# Embed Utils
# =========================================================

def split_text_to_embeds(
    title,
    text,
    color=0x3498DB,
    max_len=4000
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
                title=f"{title} {part}",
                description=current,
                color=color
            )

            embed.set_thumbnail(
                url=BOT_ICON
            )

            embed.set_image(
                url=MAIN_IMAGE
            )

            embed.set_footer(
                text="Horoyoi-san ඞ"
            )

            embeds.append(embed)

            current = line

            part += 1

        else:

            current += (
                "\n" if current else ""
            ) + line

    # =====================================================
    # Last Block
    # =====================================================

    if current:

        embed = discord.Embed(
            title=f"{title} {part}",
            description=current,
            color=color
        )

        embed.set_thumbnail(
            url=BOT_ICON
        )

        embed.set_image(
            url=MAIN_IMAGE
        )

        embed.set_footer(
            text="Horoyoi-san ඞ"
        )

        embeds.append(embed)

    return embeds

# =========================================================
# Extract Command Options
# =========================================================

def extract_cmd_options(
    data,
    key,
    title_prefix
):

    options = []

    cmd_list = data.get(
        key,
        []
    )

    for cmd in cmd_list:

        if cmd.get("isShow") != 1:
            continue

        option = cmd.get(
            "cmdOption",
            ""
        ).strip()

        if not option:
            continue

        text = cmd.get(
            "text",
            {}
        )

        desc_lines = [
            f"# {option}"
        ]

        # language order
        for lang in [
            "zh-Hans",
            "de",
            "zh-Hant",
            "ko",
            "th",
            "ja",
            "en",
            "fr",
            "es"
        ]:

            if lang in text:

                desc_lines.append(
                    f"{lang}: ```{text[lang]}```"
                )

        options.append(
            "\n".join(desc_lines)
        )

    if not options:
        return []

    return split_text_to_embeds(
        title_prefix,
        "\n\n".join(options),
        color=0x9B59B6
    )

# =========================================================
# Discord Send
# =========================================================

async def send_discord(
    channel_id,
    embeds
):

    try:

        channel = await bot.fetch_channel(
            channel_id
        )

    except Exception as e:

        print(
            f"❌ Channel fetch error: {channel_id}"
        )

        print(e)

        return

    for i, embed in enumerate(
        embeds,
        1
    ):

        try:

            await channel.send(
                embed=embed
            )

            print(
                f"✅ sent embed {i} -> {channel_id}"
            )

            # anti rate limit
            await asyncio.sleep(1)

        except Exception as e:

            print(
                f"❌ send error -> {channel_id}"
            )

            print(e)

# =========================================================
# Build Embeds
# =========================================================

def build_embeds(
    data,
    title
):

    blocks = []

    # =====================================================
    # Launch Commands
    # =====================================================

    if data.get("commandSwitch") == 1:

        blocks += extract_cmd_options(
            data,
            "commandList",
            title + " — Launch Commands"
        )

    # =====================================================
    # RHI Options
    # =====================================================

    if data.get("RHIOptionSwitch") == 1:

        blocks += extract_cmd_options(
            data,
            "RHIOptionList",
            title + " — lang"
        )

    # =====================================================
    # Default
    # =====================================================

    default = data.get("default")

    if default:

        resource = default.get(
            "resource"
        )

        # =================================================
        # Launcher
        # =================================================

        if resource:

            version = resource.get(
                "version",
                "No version"
            )

            size = resource.get(
                "size",
                0
            )

            md5 = resource.get(
                "md5",
                ""
            )

            cdn_list = default.get(
                "cdnList",
                []
            )

            path = resource.get(
                "path",
                ""
            )

            url_full = (
                cdn_list[0]["url"] + path
                if cdn_list and path
                else path
            )

            desc = (
                f"## Version {version}\n" 
                f"## Size `{size/1024/1024:.2f}` MB\n"
                f"## Download\n"
                f"{url_full}"
            )

            blocks += split_text_to_embeds(
                title,
                desc
            )

        # =================================================
        # Game
        # =================================================

        else:

            config = default.get(
                "config",
                {}
            )

            version = config.get(
                "version",
                "No version"
            )

            size = config.get(
                "size",
                0
            )

            md5 = config.get(
                "indexFileMd5",
                ""
            )

            index_file_main = config.get(
                "indexFile",
                "N/A"
            )

            resources_file = default.get(
                "resources",
                "N/A"
            )

            cdn_list = default.get(
                "cdnList",
                []
            )

            patch_lines = []

            for patch in config.get(
                "patchConfig",
                []
            ):

                ver = patch.get(
                    "version"
                )

                index_file = patch.get(
                    "indexFile"
                )

                full_url_patch = (
                    cdn_list[0]["url"] + index_file
                    if cdn_list
                    else index_file
                )

                patch_lines.append(
                    f"{ver}: {full_url_patch}"
                )

            url_full = (
                patch_lines[-1]
                if patch_lines
                else "No URL"
            )

            desc = (
                f"## Version {version}\n" 

                f"## Size `{size/1024/1024:.2f}` MB\n"

                f"## Download\n"
                f"{url_full}\n"

                f"## IndexFile\n"
                f"{cdn_list[0]['url'] + index_file_main if cdn_list else index_file_main}\n"

                f"## Resources\n"
                f"{cdn_list[0]['url'] + resources_file if cdn_list else resources_file}"
            )

            blocks += split_text_to_embeds(
                title,
                desc
            )

            blocks += split_text_to_embeds(
                title + " — Hdiff",
                "\n".join(patch_lines)
            )

    # =====================================================
    # Predownload
    # =====================================================

    predownload = data.get(
        "predownload"
    )

    if predownload:

        config = predownload.get(
            "config",
            {}
        )

        version = config.get(
            "version",
            "No version"
        )

        size = config.get(
            "size",
            0
        )

        md5 = config.get(
            "indexFileMd5",
            ""
        )

        index_file_main = config.get(
            "indexFile",
            "N/A"
        )

        resources_file = predownload.get(
            "resources",
            "N/A"
        )

        cdn_list = default.get(
            "cdnList",
            []
        )

        patch_lines = []

        for patch in config.get(
            "patchConfig",
            []
        ):

            ver = patch.get(
                "version"
            )

            index_file = patch.get(
                "indexFile"
            )

            full_url_patch = (
                cdn_list[0]["url"] + index_file
                if cdn_list
                else index_file
            )

            patch_lines.append(
                f"{ver}: {full_url_patch}"
            )

        full_url_predownload = (
            patch_lines[-1]
            if patch_lines
            else "No URL"
        )

        desc = (
            f"## Version\n"
            f"`{version}`\n\n"

            f"## Size\n"
            f"`{size/1024/1024:.2f} MB`\n\n"

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
            title + " — Predownload",
            desc,
            color=0xF1C40F
        )

        blocks += split_text_to_embeds(
            title + " — Predownload Hdiff",
            "\n".join(patch_lines),
            color=0xF1C40F
        )

    return blocks

# =========================================================
# Main
# =========================================================

async def main():

    await bot.login(TOKEN)

    print(
        f"✅ Logged in as {bot.user}"
    )

    urls = [

        (
            "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/G153/index.json",
            "Wuthering Waves Launcher"
        ),

        (
            "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json",
            "Wuthering Waves Game"
        )
    ]

    for api_url, game_name in urls:

        changed, data = log_and_check(
            api_url,
            game_name
        )

        if changed and data:

            embeds = build_embeds(
                data,
                game_name
            )

            for channel_id in CHANNELS:

                await send_discord(
                    channel_id,
                    embeds
                )

        else:

            print(
                f"[{game_name}] No changes detected"
            )

# =========================================================
# Start
# =========================================================

async def runner():

    task = asyncio.create_task(
        bot.start(TOKEN)
    )

    await asyncio.sleep(5)

    await main()

    await asyncio.sleep(15)

    await bot.close()

    await task

asyncio.run(runner())