from discord.ext import commands
from discord import Embed
import json
from utils.inventory import load_inventory, save_inventory, modify_item


class CharacterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def normalize_item(self, item_name: str) -> str:
        """Ensure the item is title-cased for internal storage consistency."""
        return item_name.title()

    def find_item_case_insensitive(self, items: dict, search_item: str):
        """Find an item case-insensitively within a dict."""
        search_item_lower = search_item.lower()
        for item, quantity in items.items():
            if item.lower() == search_item_lower:
                return item, quantity
        return None, 0

    def get_item_value(self, item_name: str):
        """Fetch the item value from values.json in a case-insensitive manner."""
        try:
            with open("data/values.json", "r") as f:
                values = json.load(f)
            for key, value in values.items():
                if key.lower() == item_name.lower():
                    return value
        except FileNotFoundError:
            print("[ERROR] values.json file not found!")
        return None

    @commands.command(name="move_item")
    async def move_item(self, ctx, character_name: str, from_section: str, to_section: str, item_name: str, amount: int):
        from_section = from_section.lower()
        to_section = to_section.lower()
        normalized_item = self.normalize_item(item_name)

        print(f"[DEBUG] move_item called with character_name={character_name}, from_section={from_section}, to_section={to_section}, item_name={item_name}, amount={amount}")
        print(f"[DEBUG] Normalized item name: {normalized_item}")

        if from_section not in ["items", "inventory", "stash"] or to_section not in ["items", "inventory", "stash"]:
            await ctx.send("Invalid section. Valid sections are: items, inventory, stash.", delete_after=5)
            return

        character = load_inventory(character_name)
        if not character:
            await ctx.send(f"Character {character_name} not found.", delete_after=5)
            return

        actual_item, current_amount = self.find_item_case_insensitive(character[from_section], normalized_item)

        if not actual_item:
            await ctx.send(f"{item_name} not found in {from_section}.", delete_after=5)
            return

        if current_amount < amount:
            await ctx.send(f"Not enough {actual_item} in {from_section}.", delete_after=5)
            return

        modify_item(character, from_section, actual_item, -amount)
        modify_item(character, to_section, actual_item, amount)

        save_inventory(character_name, character)

        await ctx.send(f"Moved {amount} {actual_item}(s) from {from_section} to {to_section}.", delete_after=5)

    @commands.command(name="show_inventory")
    async def show_inventory(self, ctx, character_name: str):
        character = load_inventory(character_name)
        if not character:
            await ctx.send(f"Character {character_name} not found.", delete_after=5)
            return

        inventory_items = character["inventory"]
        if not inventory_items:
            await ctx.send("Inventory is empty.", delete_after=5)
            return

        embed = Embed(
            title=f"{character_name}'s Inventory",
            description="\n".join([f"{item}: {quantity}" for item, quantity in inventory_items.items()])
        )
        message = await ctx.send(embed=embed, delete_after=30)
        await message.add_reaction("\U0001f5d1")

    @commands.command(name="show_stash")
    async def show_stash(self, ctx, character_name: str):
        character = load_inventory(character_name)
        if not character:
            await ctx.send(f"Character {character_name} not found.", delete_after=5)
            return

        stash_items = character["stash"]
        if not stash_items:
            await ctx.send("Stash is empty.", delete_after=5)
            return

        embed = Embed(
            title=f"{character_name}'s Stash",
            description="\n".join([f"{item}: {quantity}" for item, quantity in stash_items.items()])
        )
        message = await ctx.send(embed=embed, delete_after=30)
        await message.add_reaction("\U0001f5d1")

    @commands.command(name="donate")
    async def donate(self, ctx, character_name: str, *, item_and_amount: str):
        print(f"[DEBUG] donate called with character_name='{character_name}', item_and_amount='{item_and_amount}'")

        # Split the string from the right to handle multi-word items
        parts = item_and_amount.rsplit(" ", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            print(f"[DEBUG] Invalid item_and_amount format: '{item_and_amount}'")
            await ctx.send("Invalid format. Use `!donate <character_name> <item_name> <amount>`.", delete_after=5)
            return

        item_name = parts[0].strip()
        amount = int(parts[1])

        normalized_item = self.normalize_item(item_name)
        print(f"[DEBUG] Parsed item_name='{item_name}', normalized='{normalized_item}', amount={amount}")

        character = load_inventory(character_name)
        if not character:
            print("[DEBUG] Character not found.")
            await ctx.send(f"Character {character_name} not found.", delete_after=5)
            return

        print(f"[DEBUG] Loaded character data for {character_name}")

        # Donations are always from the "items" section
        actual_item, current_amount = self.find_item_case_insensitive(character["items"], normalized_item)

        if not actual_item:
            print(f"[DEBUG] {item_name} not found in 'items'.")
            await ctx.send(f"{item_name} not found in items.", delete_after=5)
            return

        if current_amount < amount:
            print(f"[DEBUG] Not enough {actual_item}. Current: {current_amount}, Needed: {amount}")
            await ctx.send(f"Not enough {actual_item} in items.", delete_after=5)
            return

        print(f"[DEBUG] Found {actual_item} in items with quantity {current_amount}")

        item_value = self.get_item_value(actual_item)
        if item_value is None:
            item_value = 0.001
            print(f"[DEBUG] Value not found for '{actual_item}' in values.json. Defaulting to {item_value}")

        total_value = item_value * amount
        print(f"[DEBUG] Item Value: {item_value}, Total Value: {total_value}")

        modify_item(character, "items", actual_item, -amount)
        save_inventory(character_name, character)

        # Update donations.json
        try:
            with open("data/donations.json", "r") as f:
                donations = json.load(f)
        except FileNotFoundError:
            donations = {}

        if character_name not in donations:
            donations[character_name] = {"items": {}, "total_value": 0}

        if actual_item not in donations[character_name]["items"]:
            donations[character_name]["items"][actual_item] = 0

        donations[character_name]["items"][actual_item] += amount
        donations[character_name]["total_value"] += total_value

        with open("data/donations.json", "w") as f:
            json.dump(donations, f, indent=4)

        print(f"[DEBUG] Donation complete: {amount} {actual_item}(s) worth {total_value} points.")
        await ctx.send(f"{character_name} donated {amount} {actual_item}(s) worth {total_value:.3f} points.", delete_after=5)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.emoji == "\U0001f5d1":
            await reaction.message.delete()


async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
