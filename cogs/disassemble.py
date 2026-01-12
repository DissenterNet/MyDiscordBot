import os
import asyncio
from discord.ext import commands, tasks
from utils.json_io import save_json, load_json
from utils.inventory import get_inventory_file
from utils.functions import normalize_components

# File paths
INVENTORY_DIR = "data/inventories/"  # Directory for storing character inventories
RECIPES_FILE = "data/recipes.json"  # Recipes file
SCAVENGE_FILE = "data/scavenge.json"  # Scavenge loot table (loaded for completeness)
BROKEN_FILE = "data/broken.json"  # Broken component replacements (not used in this version)


class Disassembling(commands.Cog):
    """Cog for disassembling crafted items to recover their original components."""

    def __init__(self, bot):
        self.bot = bot
        self.recipes = load_json(RECIPES_FILE)
        self.scavenge_table = load_json(SCAVENGE_FILE)
        self.check_disassembling_completion.start()

    @commands.command(name="disassemble")
    async def disassemble(self, ctx, character_name: str, *, item_name: str):
        """
        Start disassembling an item.

        - Searches for the recipe by item name.
        - Checks that disassembly is allowed.
        - Checks that the character has the full crafted batch (as defined in the recipe's outputs) in inventory.
        - Removes the entire batch from inventory.
        - Saves a disassembly process (with a completion time and the normalized components)
          in the character's inventory under active_disassembling.
        """
        item_name = item_name.title()
        inv_file = get_inventory_file(character_name)
        inventory = load_json(inv_file)
        recipes = self.recipes

        # Delete the command message
        await ctx.message.delete(delay=0)

        # Ensure inventory keys exist
        inventory.setdefault("items", {})
        inventory.setdefault("active_disassembling", None)

        # Find the recipe for the given item (searching each category)
        recipe = None
        for category, items in recipes.items():
            if item_name in items:
                recipe = items[item_name]
                break
        if recipe is None:
            await ctx.send(f"❌ `{item_name}` cannot be disassembled.", delete_after=5)
            return

        # Check if disassembly is allowed for this item
        if recipe.get("disassemble", 1) == 0:
            await ctx.send(f"❌ `{item_name}` cannot be disassembled.", delete_after=5)
            return

        # Ensure no disassembly is already active
        if inventory.get("active_disassembling"):
            active_item = inventory["active_disassembling"].get("item", "Unknown")
            await ctx.send(f"⏳ `{character_name}` is already disassembling `{active_item}`.", delete_after=5)
            return

        if any(inventory.get(task) for task in ["active_crafting", "active_scavenge", "active_labor"]):
            await ctx.send(f"❌ {character_name} is already busy with another task.", delete_after=15)
            return

        # Calculate disassembly duration (in minutes).
        disassembling_time = recipe.get("time", 1) / 2

        # Check if the character has the full crafted batch as defined in outputs
        outputs = recipe.get("outputs", [])
        for output in outputs:
            out_item = output["item"]
            out_qty = output["quantity"]
            if inventory["items"].get(out_item, 0) < out_qty:
                await ctx.send(f"⚠️ `{character_name}` does not have enough `{out_item}` to disassemble.",
                               delete_after=5)
                return

        # Remove each output (i.e. the entire crafted batch) from the inventory
        for output in outputs:
            out_item = output["item"]
            out_qty = output["quantity"]
            inventory["items"][out_item] -= out_qty
            if inventory["items"][out_item] <= 0:
                del inventory["items"][out_item]

        # Normalize the components from the recipe (the items to be returned upon disassembly)
        normalized_components = normalize_components(recipe.get("components", {}))

        # Save the active disassembly process
        inventory["active_disassembling"] = {
            "item": item_name,
            "components": normalized_components,
            "completion_time": asyncio.get_event_loop().time() + disassembling_time * 60,
        }
        save_json(inv_file, inventory)

        await ctx.send(
            f"🔧 `{character_name}` has started disassembling `{item_name}`. It will take {disassembling_time} minutes.",
            delete_after=10)

    @tasks.loop(minutes=6)
    async def check_disassembling_completion(self):
        """
        Checks every minute for any active disassembly processes that have completed.
        When complete, the stored components are added to the character's inventory and the active process is cleared.
        """
        current_time = asyncio.get_event_loop().time()
        for filename in os.listdir(INVENTORY_DIR):
            if not filename.endswith(".json"):
                continue
            character_name = filename[:-5]  # Remove the .json extension
            inv_file = get_inventory_file(character_name)
            inventory = load_json(inv_file)
            active = inventory.get("active_disassembling")
            if active and active.get("completion_time", 0) <= current_time:
                normalized_components = active.get("components", {})
                # Add each component (with its quantity) back into the items section
                for comp_name, comp_qty in normalized_components.items():
                    inventory["items"][comp_name] = inventory["items"].get(comp_name, 0) + comp_qty

                completed_item = active.get("item", "Unknown")
                # Clear the active disassembly process
                inventory["active_disassembling"] = None
                save_json(inv_file, inventory)

                # Notify completion (using print here; replace with a channel message if needed)
                print(f"✅ {character_name} has finished disassembling {completed_item} and received components.")


async def setup(bot):
    """Setup function for adding the cog."""
    await bot.add_cog(Disassembling(bot))
