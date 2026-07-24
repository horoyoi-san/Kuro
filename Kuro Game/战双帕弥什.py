import discord
import asyncio
import time

import requests
import json
import os
import hashlib

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

BOT_NAME = "战双帕弥什"

BOT_ICON = (
	"https://raw.githubusercontent.com/"
	"horoyoi-san/Kuro/refs/heads/Webhook/assets/pgr.png"
)

# =========================================================
# Dynamic Background
# =========================================================


def get_background_image(data, base_index_url):

	try:

		bg_id = data.get("functionCode", {}).get("background")

		if not bg_id:
			return None
        # https://prod-alicdn-gamestarter.kurogame.com/launcher/10012_LWdk9D2Ep9mpJmqBZZkcPBU2YNraEWBQ/G148/background/{bg_id}/zh-Hans.json
		# Normalize base so that URLs like
		# .../launcher/launcher/10012_.../G148/index.json
		# become
		# .../launcher/10012_.../G148/background/{bg_id}/zh-Hans.json
		base = base_index_url.rsplit("/", 1)[0]
		base = base.replace("/launcher/launcher/", "/launcher/")
		manifest_url = base + f"/background/{bg_id}/zh-Hans.json"

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


# =========================================================
# Embed Utils
# =========================================================


def split_text_to_embeds(
	title, text, color=0x3498DB, max_len=4000, image_url=None
):
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

	if current:

		embed = discord.Embed(title=f"{title} {part}", description=current, color=color)

		embed.set_thumbnail(url=BOT_ICON)

		if image_url:
			embed.set_image(url=image_url)

		embed.set_footer(text="Horoyoi-san ඞ")

		embeds.append(embed)

	return embeds


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

			await asyncio.sleep(1)

		except Exception as e:

			print(f"❌ send error -> {channel_id}")

			print(e)


# =========================================================
# Build Embeds
# =========================================================


def build_embeds(data, title, background_image=None):

	blocks = []

	default = data.get("default")

	if default:

		resource = default.get("resource")

		# =================================================
		# Launcher
		# =================================================

		if resource:

			version = resource.get("version", "No version")

			size = resource.get("size", 0)

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

	return blocks


# =========================================================
# Main
# =========================================================


async def main():

	await bot.login(TOKEN)

	print(f"✅ Logged in as {bot.user}")

	urls = [
		(
			"https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10012_RnIUKs3r59Csliu3N0rl5uRWWBOFDaJL/G148/index.json",
			"战双帕弥什 Launcher",
		),
		(
			"https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G148/10012_RnIUKs3r59Csliu3N0rl5uRWWBOFDaJL/index.json",
			"战双帕弥什 Game",
		),
	]

	launcher_background = None

	for api_url, game_name in urls:

		changed, data = log_and_check(api_url, game_name)

		if not data:
			continue

		# ดึงรูปใหม่ทุกครั้ง
		if "Launcher" in game_name:
			launcher_background = get_background_image(data, api_url)

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
