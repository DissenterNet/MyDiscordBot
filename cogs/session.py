import os
import json
import logging
from discord.ext import commands
import discord
import asyncio
from utils.inventory import load_inventory, save_inventory

INVENTORY_DIR = "data/inventories/"
MAX_MESSAGE_LENGTH = 1500


def split_message(content):
    """Splits long messages into chunks that fit Discord's character limit."""
    return [content[i: i + MAX_MESSAGE_LENGTH] for i in range(0, len(content), MAX_MESSAGE_LENGTH)]


class Session(commands.Cog):
    """Commands for tracking character sessions and viewing character details."""

    def __init__(self, bot):
        self.bot = bot
        self.bookkeeping_channel_id = None

    @commands.Cog.listener()
    async def on_ready(self):
        """Fetch the bookkeeping channel ID from config.json when the bot is ready."""
        with open("config.json") as f:
            config = json.load(f)
        self.bookkeeping_channel_id = config.get("BOOKKEEPING_CHANNEL_ID")

    @commands.command(name="session")
    async def session(self, ctx, session_id: str, character_name: str, xp_gained: int, gold_earned: int, expenses: int):
        """Log a session entry that updates the character's XP and gold."""
        await ctx.message.delete(delay=0)
        character_name = character_name.strip().lower().capitalize()
        char_data = load_inventory(character_name)

        if char_data is None:
            await ctx.send(f"❌ Character **{character_name}** does not exist.", delete_after=10)
            return

        if not char_data.get("discord_name"):
            char_data["discord_name"] = ctx.author.name

        char_data["total_xp"] += xp_gained
        char_data["total_gold"] += (gold_earned - expenses)
        save_inventory(character_name, char_data)

        session_message = (
            f"📜 **Session {session_id} recorded for {character_name}** (Discord: {ctx.author.name})\n"
            f"🔹 XP Gained: {xp_gained} | Gold Earned: {gold_earned} | Expenses: {expenses}\n"
            f"🏅 **Current Totals** — XP: {char_data['total_xp']}, Gold: {char_data['total_gold']}"
        )

        await ctx.send(session_message, delete_after=15)

        # Send a copy to the bookkeeping channel
        if self.bookkeeping_channel_id:
            bookkeeping_channel = self.bot.get_channel(self.bookkeeping_channel_id)
            if bookkeeping_channel:
                await bookkeeping_channel.send(session_message)
                logging.info(f"✅ Session log posted to bookkeeping channel: {self.bookkeeping_channel_id}")
            else:
                logging.warning(f"⚠️ Could not find bookkeeping channel with ID {self.bookkeeping_channel_id}")

    @commands.command(name="stats")
    async def stats(self, ctx):
        """Display XP and gold totals for all characters owned by the user."""
        await ctx.message.delete(delay=0)
        user_chars = []

        if not os.path.exists(INVENTORY_DIR):
            await ctx.send("You have no characters in the database.", delete_after=5)
            return

        for filename in os.listdir(INVENTORY_DIR):
            if filename.endswith(".json"):
                char_name = filename[:-5]
                char_data = load_inventory(char_name)
                if char_data.get("discord_name") == ctx.author.name:
                    user_chars.append((char_name, char_data.get("total_xp", 0), char_data.get("total_gold", 0)))

        if not user_chars:
            await ctx.send("You have no characters in the database.", delete_after=5)
            return

        response = "**Your Characters:**\n"
        for char_name, xp, gold in user_chars:
            response += f"**{char_name}**: XP: {xp}, Gold: {gold}\n"
        await ctx.send(response, delete_after=15)

    @commands.command(name="inventory")
    async def inventory(self, ctx, character_name: str):
        """Display detailed information about a character (XP, gold, items) and DM inventory upon reaction."""
        await ctx.message.delete(delay=0)
        character_name = character_name.strip().lower().capitalize()
        char_data = load_inventory(character_name)

        if char_data is None:
            await ctx.send(f"❌ Character **{character_name}** does not exist.", delete_after=10)
            return

        if char_data.get("discord_name") != ctx.author.name:
            await ctx.send("⚠️ You do not have permission to view this character's details.", delete_after=10)
            return

        items = char_data.get("items", {})
        item_list = sorted(items.items())
        item_text = "None"

        embed = discord.Embed(title=f"Inventory for {character_name}", color=0x00FF00)
        embed.add_field(
            name="Items",
            value="React 👍 to receive a full inventory thru DM\nReact 👎 to cancel.\n\n"
                  f"{item_text[:500]}{'...' if len(item_text) > 500 else ''}",
            inline=False,
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=45.0, check=check)
            if str(reaction.emoji) == "👍":
                await self.dm_inventory(ctx, character_name, char_data)
            await message.delete()
        except asyncio.TimeoutError:
            await message.delete()

    async def dm_inventory(self, ctx, character_name, char_data=None):
        """DM the full inventory contents to the user in chunks."""
        if char_data is None:
            char_data = load_inventory(character_name)

        if char_data is None:
            await ctx.send(f"❌ Character **{character_name}** does not exist.", delete_after=10)
            return

        items = char_data.get("items", {})
        item_list = sorted(items.items())
        item_text = "\n".join([f"- {item}: {quantity}" for item, quantity in item_list]) or "None"

        messages = split_message(f"**Inventory for {character_name}:**\n{item_text}")

        for msg in messages:
            try:
                await ctx.author.send(msg)
            except discord.errors.Forbidden:
                await ctx.send("❌ Unable to send DM. Please check your privacy settings.", delete_after=10)
                return


async def setup(bot):
    await bot.add_cog(Session(bot))
