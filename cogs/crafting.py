import os
import asyncio
from discord.ext import commands, tasks
from utils.inventory import load_inventory, save_inventory
from utils.json_io import load_recipes, load_scavenge_table
from utils.functions import find_wildcard_match, normalize_components

INVENTORY_DIR = "data/inventories/"  # Directory for storing character inventories


class Crafting(commands.Cog):
    """Crafting system for the bot."""

    def __init__(self, bot):
        self.bot = bot
        self.recipes = load_recipes()
        self.scavenge_table = load_scavenge_table()
        self.check_crafting_completion.start()  # Start background task

    @commands.command(name="craft")
    async def craft(self, ctx, character_name: str, *, item_name: str):
        """Start crafting an item."""
        item_name = item_name.title()
        inventory = load_inventory(character_name)
        recipes = load_recipes()

        # Delete the triggering message
        await ctx.message.delete(delay=0)

        # Ensure expected keys exist
        inventory.setdefault("items", {})
        inventory.setdefault("active_crafting", None)
        inventory.setdefault("active_disassembling", None)
        inventory.setdefault("active_scavenge", None)

        # Look for the recipe in all recipe categories
        recipe = None
        for category, items in recipes.items():
            if item_name in items:
                recipe = items[item_name]
                break
        if recipe is None:
            await ctx.send(f"❌ `{item_name}` is not craftable.", delete_after=5)
            return

        if inventory.get("active_crafting"):
            await ctx.send(
                f"⏳ `{character_name}` is already crafting `{inventory['active_crafting']['item']}`.", delete_after=5)
            return

        if any(inventory.get(task) for task in ["active_scavenge", "active_disassembling", "active_labor"]):
            await ctx.send(f"❌ {character_name} is already busy with another task.", delete_after=15)
            return

        # Normalize components in case they're defined as a list (as in Wood Planks)
        required_components = normalize_components(recipe["components"])
        crafting_time = recipe.get("time", 30)  # Default crafting time in minutes

        # Process required tools from the recipe.
        tools_field = recipe.get("requires", "")
        if isinstance(tools_field, str):
            required_tools_raw = [tool.strip() for tool in tools_field.split(",") if tool.strip()]
        elif isinstance(tools_field, list):
            required_tools_raw = tools_field
        else:
            required_tools_raw = []
        # Use wildcard matching for each tool requirement.
        required_tools = [find_wildcard_match(inventory, tool) for tool in required_tools_raw]

        outputs = recipe.get("outputs", [])

        # Check if all required tools are in the inventory.
        if not all(tool in inventory["items"] for tool in required_tools):
            await ctx.send(
                f"⚠️ `{character_name}` lacks the required tools: `{', '.join(required_tools)}`.",
                delete_after=5)
            return

        # Check and deduct required components (using wildcard matching if applicable).
        for component, amount in required_components.items():
            matched_component = find_wildcard_match(inventory, component)
            if inventory["items"].get(matched_component, 0) < amount:
                await ctx.send(
                    f"⚠️ `{character_name}` does not have enough `{component}` to craft `{item_name}`.",
                    delete_after=5)
                return

        for component, amount in required_components.items():
            matched_component = find_wildcard_match(inventory, component)
            inventory["items"][matched_component] -= amount

        # Record the active crafting project along with its outputs.
        inventory["active_crafting"] = {
            "item": item_name,
            "outputs": outputs,
            "completion_time": asyncio.get_event_loop().time() + crafting_time * 60
        }
        save_inventory(character_name, inventory)

        await ctx.send(
            f"🛠️ `{character_name}` has started crafting `{item_name}`. This will take {crafting_time} minutes.",
            delete_after=10)

    @tasks.loop(minutes=7)
    async def check_crafting_completion(self):
        """Check and complete crafting projects."""
        current_time = asyncio.get_event_loop().time()

        for filename in os.listdir(INVENTORY_DIR):
            if not filename.endswith('.json'):
                continue
            character_name = filename[:-5]
            inventory = load_inventory(character_name)

            if inventory.get("active_crafting") and inventory["active_crafting"]["completion_time"] <= current_time:
                outputs = inventory["active_crafting"].get("outputs", [])
                for output in outputs:
                    output_item = output["item"]
                    output_quantity = output["quantity"]
                    inventory["items"][output_item] = inventory["items"].get(output_item, 0) + output_quantity

                inventory["active_crafting"] = None
                save_inventory(character_name, inventory)


async def setup(bot):
    """Setup function for adding the cog."""
    await bot.add_cog(Crafting(bot))
