import os
import json
from typing import Any
import aiohttp
from PIL import Image
import io
from discord.ext import commands
import discord

INVENTORY_DIR = "data/inventories/"
AVATAR_DIR = "data/avatars/"
LOGGING_CHANNEL_ID = 1333897746444193886  # Replace with your private logging channel ID

os.makedirs(INVENTORY_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)


def normalize_character_name(name: str) -> str:
    return name.strip().lower().capitalize()


def get_inventory_file(character_name: str) -> str:
    normalized = normalize_character_name(character_name)
    return os.path.join(INVENTORY_DIR, f"{normalized}.json")


def get_avatar_file(character_name: str) -> str:
    normalized = normalize_character_name(character_name)
    return os.path.join(AVATAR_DIR, f"{normalized}.png")


def load_character(character_name: str) -> Any | None:
    file_path = get_inventory_file(character_name)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)


class RoleplayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rp")
    async def rp(self, ctx, character_name: str, *, message: str):
        try:
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] rp: Failed to delete trigger message: {e}")

        normalized_char = normalize_character_name(character_name)
        data = load_character(normalized_char)

        if data is None:
            await ctx.send(f"⚠️ Character '{normalized_char}' not found.", delete_after=5)
            return

        if "discord_name" not in data or data["discord_name"] != ctx.author.name:
            await ctx.send(f"🚫 You do not own the character '{normalized_char}'.", delete_after=5)
            return

        formatted_message = f"**{normalized_char} says** *\"{message}\"*"
        avatar_path = get_avatar_file(normalized_char)

        try:
            webhooks = await ctx.channel.webhooks()
            webhook = next((wh for wh in webhooks if wh.name == "RPBotWebhook"), None)

            if webhook is None:
                webhook = await ctx.channel.create_webhook(name="RPBotWebhook")

            avatar_url = ctx.author.avatar.url if ctx.author.avatar else None

            if os.path.exists(avatar_path):
                logging_channel = self.bot.get_channel(LOGGING_CHANNEL_ID)
                if logging_channel:
                    with open(avatar_path, "rb") as avatar_file:
                        avatar_upload = await logging_channel.send(file=discord.File(avatar_file, filename=f"{normalized_char}.png"), delete_after=1)
                        avatar_url = avatar_upload.attachments[0].url

            await webhook.send(
                content=formatted_message,
                username=normalized_char,
                avatar_url=avatar_url
            )
        except Exception as e:
            print(f"[DEBUG] rp: Failed to use webhook, sending regular message instead: {e}")
            await ctx.send(formatted_message)

    @commands.command(name="emote")
    async def emote(self, ctx, character_name: str, *, message: str):
        try:
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] emote: Failed to delete trigger message: {e}")

        normalized_char = normalize_character_name(character_name)
        data = load_character(normalized_char)

        if data is None:
            await ctx.send(f"⚠️ Character '{normalized_char}' not found.", delete_after=5)
            return

        if "discord_name" not in data or data["discord_name"] != ctx.author.name:
            await ctx.send(f"🚫 You do not own the character '{normalized_char}'.", delete_after=5)
            return

        formatted_message = f"**{normalized_char}** *{message}*"
        avatar_path = get_avatar_file(normalized_char)

        try:
            webhooks = await ctx.channel.webhooks()
            webhook = next((wh for wh in webhooks if wh.name == "RPBotWebhook"), None)

            if webhook is None:
                webhook = await ctx.channel.create_webhook(name="RPBotWebhook")

            avatar_url = ctx.author.avatar.url if ctx.author.avatar else None

            if os.path.exists(avatar_path):
                logging_channel = self.bot.get_channel(LOGGING_CHANNEL_ID)
                if logging_channel:
                    with open(avatar_path, "rb") as avatar_file:
                        avatar_upload = await logging_channel.send(file=discord.File(avatar_file, filename=f"{normalized_char}.png"), delete_after=1)
                        avatar_url = avatar_upload.attachments[0].url

            await webhook.send(
                content=formatted_message,
                username=normalized_char,
                avatar_url=avatar_url
            )
        except Exception as e:
            print(f"[DEBUG] emote: Failed to use webhook, sending regular message instead: {e}")
            await ctx.send(formatted_message)

    @commands.command(name="setavatar")
    async def set_avatar(self, ctx, character_name: str):
        try:
            await ctx.message.delete(delay=5)
        except Exception as e:
            print(f"[DEBUG] set_avatar: Failed to delete trigger message: {e}")

        normalized_char = normalize_character_name(character_name)
        data = load_character(normalized_char)

        if data is None:
            await ctx.send(f"⚠️ Character '{normalized_char}' not found.", delete_after=5)
            return

        if "discord_name" not in data or data["discord_name"] != ctx.author.name:
            await ctx.send(f"🚫 You do not own the character '{normalized_char}'.", delete_after=5)
            return

        if not ctx.message.attachments:
            await ctx.send("⚠️ Please attach an image when using `!setavatar`.", delete_after=5)
            return

        image_url = ctx.message.attachments[0].url
        avatar_path = get_avatar_file(normalized_char)

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()

                    image = Image.open(io.BytesIO(image_data))
                    resized_image = image.resize((100, 100))

                    with open(avatar_path, "wb") as f:
                        resized_image.save(f, format="PNG")

                    await ctx.send(f"✅ Avatar set successfully as a 100x100 image!", delete_after=5)
                else:
                    await ctx.send("❌ Failed to download the image. Please try again.", delete_after=5)


async def setup(bot):
    await bot.add_cog(RoleplayCog(bot))
