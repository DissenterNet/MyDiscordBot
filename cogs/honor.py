from discord.ext import commands
import json
import os

# Directory where character inventories are stored
INVENTORY_DIR = "data/inventories/"


def normalize_character_name(name: str) -> str:
    """Normalize a character name by trimming whitespace and capitalizing the first letter."""
    return name.strip().lower().capitalize()


def get_inventory_file(character_name: str) -> str:
    """Return the file path for a character's JSON file."""
    normalized = normalize_character_name(character_name)
    return os.path.join(INVENTORY_DIR, f"{normalized}.json")


def load_character(character_name: str) -> dict:
    """Load a character's data from its JSON file. Returns None if the file doesn't exist."""
    normalized = normalize_character_name(character_name)
    file_path = get_inventory_file(normalized)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)


def save_character(character_name: str, data: dict):
    """Save a character's data to its JSON file."""
    normalized = normalize_character_name(character_name)
    os.makedirs(INVENTORY_DIR, exist_ok=True)
    file_path = get_inventory_file(normalized)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


class HonorCog(commands.Cog):
    """Cog for managing Honor. Authorized users can award Honor, and characters can consume it for XP."""

    def __init__(self, bot):
        self.bot = bot
        # Load configuration to get the list of authorized Discord IDs for awarding Honor.
        with open("config.json") as f:
            config = json.load(f)
        self.honor_admins = config.get("honorAdmins", [])
        print(f"[DEBUG] HonorCog initialized. Authorized IDs: {self.honor_admins}")

    @commands.group(name="honor", invoke_without_command=True)
    async def honor(self, ctx, honor_amount: int, *, character_name: str):
        """
        Award Honor to a character.
        Usage: !honor <Honor Amount> <Character Name>
        Only authorized users (whose Discord ID is in config["honorAdmins"]) can award Honor.
        """
        await ctx.message.delete(delay=0)
        author_id = ctx.author.id
        if author_id not in self.honor_admins:
            await ctx.send("🚫 You are not authorized to award Honor.", delete_after=5)
            return

        normalized_char = normalize_character_name(character_name)
        data = load_character(normalized_char)
        if data is None:
            await ctx.send(f"⚠️ Character '{normalized_char}' not found.", delete_after=5)
            return

        # Initialize Honor field if it doesn't exist
        if "honor" not in data:
            data["honor"] = 0

        data["honor"] += honor_amount
        save_character(normalized_char, data)
        await ctx.send(f"✅ Awarded {honor_amount} Honor to {normalized_char}. ``Total: {data['honor']}", delete_after=5)

    @honor.command(name="consume")
    async def honor_consume(self, ctx, honor_amount: int, *, character_name: str):
        """
        Consume Honor from a character to gain XP.
        Usage: !honor consume <Honor Amount> <Character Name>
        Consumes the specified Honor (cannot consume more than available)
        and adds 25 experience per Honor consumed.
        """
        await ctx.message.delete(delay=0)
        normalized_char = normalize_character_name(character_name)
        data = load_character(normalized_char)
        if data is None:
            await ctx.send(f"⚠️ Character '{normalized_char}' not found.", delete_after=5)
            return

        # Ensure the character has an Honor field; if not, initialize it.
        if "honor" not in data:
            data["honor"] = 0

        if data["honor"] < honor_amount:
            await ctx.send(f"⚠️ {normalized_char} does not have enough Honor to consume. Has: {data['honor']}", delete_after=5)
            return

        data["honor"] -= honor_amount

        # Add 25 XP for each Honor consumed.
        if "total_xp" not in data:
            data["total_xp"] = 0
        xp_gain = 25 * honor_amount
        data["total_xp"] += xp_gain

        save_character(normalized_char, data)
        await ctx.send(f"✅ {normalized_char} consumed {honor_amount} Honor and gained {xp_gain} XP. Remaining Honor: {data['honor']}", delete_after=5)


async def setup(bot):
    await bot.add_cog(HonorCog(bot))
