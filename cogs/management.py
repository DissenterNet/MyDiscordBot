import os
import json
import asyncio
from discord.ext import commands

INVENTORY_DIR = "data/inventories/"
MAX_CHARACTERS_PER_USER = 10

# Template for new character profiles
CHARACTER_TEMPLATE = {
    "character_name": "",
    "discord_name": "",
    "user_id": None,
    "total_xp": 0,
    "total_gold": 0,
    "items": {},
    "active_crafting": None,
    "active_scavenge": None,
    "active_disassembling": None,
    "active_labor": None
}


def get_inventory_file(character_name):
    return os.path.join(INVENTORY_DIR, f"{character_name.lower()}.json")


def load_inventory(character_name):
    file_path = get_inventory_file(character_name)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)


def save_inventory(character_name, inventory):
    os.makedirs(INVENTORY_DIR, exist_ok=True)
    with open(get_inventory_file(character_name), "w") as f:
        json.dump(inventory, f, indent=4)


def list_user_characters(user_id):
    """Return a list of character names that belong to a given user ID."""
    characters = []
    if not os.path.exists(INVENTORY_DIR):
        return characters
    for filename in os.listdir(INVENTORY_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(INVENTORY_DIR, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                if data.get("user_id") == user_id:
                    characters.append(data.get("character_name", filename[:-5]))
            except Exception as e:
                print(f"[DEBUG] Failed to load {filename}: {e}")
    return characters


class Management(commands.Cog):
    """Cog for managing player characters: initializing new characters and deleting (killing) them."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="life")
    async def init_character(self, ctx, *, character_name: str):
        """
        Initialize a new character for the user.
        This command creates a character.json file from an internal template and locks it to your Discord ID.

        Usage: !life <character name>
        Example: !life Taco
        """
        character_name = character_name.strip()
        # Check if the character already exists
        if load_inventory(character_name) is not None:
            await ctx.send(f"❌ Character **{character_name}** already exists.", delete_after=10)
            return

        # Check if the user already has too many characters
        user_chars = list_user_characters(ctx.author.id)
        if len(user_chars) >= MAX_CHARACTERS_PER_USER:
            await ctx.send(
                f"❌ You already have {len(user_chars)} characters (maximum allowed is {MAX_CHARACTERS_PER_USER}).",
                delete_after=5)
            return

        # Create new character from the template
        new_character = CHARACTER_TEMPLATE.copy()
        new_character["character_name"] = character_name
        new_character["discord_name"] = ctx.author.name.strip()
        new_character["user_id"] = ctx.author.id
        new_character["total_xp"] = 0
        new_character["total_gold"] = 0
        new_character["inventory"] = {}  # Inventory section where the items will go
        new_character["active_crafting"] = None
        new_character["active_scavenge"] = None
        new_character["active_disassembling"] = None
        new_character["active_labor"] = None
        new_character["stash"] = {}  # Stash section for stored items
        new_character["items"] = {}  # Items section moved to the end

        # You can add any default items to the items section here if needed
        # new_character["items"]["sword"] = 10
        # new_character["items"]["shield"] = 5

        save_inventory(character_name, new_character)
        await ctx.send(f"✅ Character **{character_name}** has been initialized and locked to your Discord account.",
                       delete_after=10)

    @commands.command(name="death")
    async def death(self, ctx, *, character_name: str):
        """
        Delete (kill) a character.
        This command can only be executed by the server owner or by the character’s owner. After the command is issued,
        the bot will ask for confirmation with 👍 and 👎 reactions. The character is deleted only if you react with 👍
        within 30 seconds. The confirmation message is deleted afterward.\n
        Usage: !death <character name>\nExample: !death Taco
        """
        character_name = character_name.strip()
        inventory = load_inventory(character_name)
        if inventory is None:
            await ctx.send(f"❌ Character **{character_name}** does not exist.", delete_after=10)
            return

        # Check permission: must be character owner or server owner
        if ctx.author.id != inventory.get("user_id") and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You do not have permission to delete this character.", delete_after=10)
            return

        confirm_msg = await ctx.send(
            f"⚠️ {ctx.author.mention}, do you really want to delete **{character_name}**? React with 👍 to confirm or 👎 to cancel.",
            delete_after=30
        )
        try:
            await confirm_msg.add_reaction("👍")
            await confirm_msg.add_reaction("👎")
        except Exception as e:
            await ctx.send("❌ Failed to add reactions.", delete_after=10)
            return

        def check(reaction, user):
            return (reaction.message.id == confirm_msg.id and
                    user.id == ctx.author.id and
                    str(reaction.emoji) in ["👍", "👎"])

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) == "👍":
                file_path = get_inventory_file(character_name)
                try:
                    os.remove(file_path)
                    await ctx.send(f"✅ Character **{character_name}** has been deleted.", delete_after=10)
                except Exception as e:
                    await ctx.send(f"❌ Failed to delete character **{character_name}**.", delete_after=10)
                    return
            else:
                await ctx.send(f"ℹ️ Deletion of **{character_name}** canceled.", delete_after=10)
        except asyncio.TimeoutError:
            await ctx.send(f"ℹ️ Deletion of **{character_name}** timed out.", delete_after=10)
        finally:
            try:
                await confirm_msg.delete()
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(Management(bot))
