import os
import random
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from utils.inventory import load_inventory, save_inventory
from utils.json_io import load_scavenge_table

# Directories and file paths
INVENTORY_DIR = "data/inventories/"  # Directory for storing character inventories
SCAVENGE_DURATION = timedelta(minutes=60)  # 1-hour scavenging process

# Scavenging roll settings
GENERAL_ROLL_COUNT = 10  # Number of rolls for general scavenging
SPECIFIC_ROLL_COUNT = 5  # Number of rolls for specific scavenging
ROLL_CHANCE = 0.4  # 50% chance per roll to find an item


class Scavenge(commands.Cog):
    """Handles scavenging for crafting components."""

    def __init__(self, bot):
        self.bot = bot
        self.scavenge_table = load_scavenge_table()
        self.check_scavenge_completion.start()  # Start background task

    @commands.command(name="scavenge")
    async def scavenge(self, ctx, character_name: str, resource_type: str = None):
        """
        Initiates a scavenging attempt that takes 1 hour.

        Usage:
          - !scavenge <character name>  → General scavenging (50% chance for 10 items)
          - !scavenge <character name> <resource type> → Targeted scavenging (50% chance for 5 items)
        """
        await ctx.message.delete(delay=0)
        now = datetime.utcnow()

        # Convert resource type to lowercase if provided
        resource_type = resource_type.lower() if resource_type else None
        inventory = load_inventory(character_name)

        # Check if the character is already scavenging
        active = inventory.get("active_scavenge")
        if active:
            completion_time_str = active.get("completion_time") if isinstance(active, dict) else active
            completion_time = datetime.strptime(completion_time_str, "%Y-%m-%d %H:%M:%S")
            remaining_time = (completion_time - now).total_seconds() // 60
            await ctx.send(
                f"⏳ `{character_name}` is already scavenging and will finish in {int(remaining_time)} minutes.",
                delete_after=15)
            return

        if any(inventory.get(task) for task in ["active_crafting", "active_disassembling", "active_labor"]):
            await ctx.send(f"❌ {character_name} is already busy with another task.", delete_after=15)
            return

        # Set active scavenging, storing completion time and type
        completion_time = now + SCAVENGE_DURATION
        inventory["active_scavenge"] = {
            "completion_time": completion_time.strftime("%Y-%m-%d %H:%M:%S"),
            "resource_type": resource_type
        }
        save_inventory(character_name, inventory)

        if resource_type:
            await ctx.send(
                f"🔍 `{character_name}` has started scavenging for **{resource_type}**. They will return in 1 hour.",
                delete_after=15)
        else:
            await ctx.send(f"🔍 `{character_name}` has started scavenging. They will return in 1 hour.", delete_after=15)

    @tasks.loop(minutes=3)
    async def check_scavenge_completion(self):
        """Check and complete scavenging processes."""
        now = datetime.utcnow()
        for filename in os.listdir(INVENTORY_DIR):
            if not filename.endswith(".json"):
                continue
            character_name = filename[:-5]
            inventory = load_inventory(character_name)
            active = inventory.get("active_scavenge")
            if active:
                completion_time_str = active.get("completion_time") if isinstance(active, dict) else active
                resource_type = active.get("resource_type") if isinstance(active, dict) else None
                completion_time = datetime.strptime(completion_time_str, "%Y-%m-%d %H:%M:%S")
                if now >= completion_time:
                    found_items = []
                    roll_count = GENERAL_ROLL_COUNT if not resource_type else SPECIFIC_ROLL_COUNT

                    # Determine which loot table to use
                    if resource_type and resource_type in self.scavenge_table:
                        group_table = self.scavenge_table[resource_type]
                        items_list = list(group_table.keys())
                        weights = [group_table[item]["weight"] for item in items_list]
                    else:
                        # General scavenging: flatten all groups
                        flat_table = {}
                        for group in self.scavenge_table.values():
                            flat_table.update(group)
                        items_list = list(flat_table.keys())
                        weights = [flat_table[item]["weight"] for item in items_list]

                    # Perform individual rolls
                    for _ in range(roll_count):
                        if random.random() < ROLL_CHANCE:
                            found_item = random.choices(items_list, weights=weights, k=1)[0]
                            inventory["items"][found_item] = inventory["items"].get(found_item, 0) + 1
                            found_items.append(found_item)

                    inventory["active_scavenge"] = None  # Clear active scavenging
                    save_inventory(character_name, inventory)

                    if found_items:
                        print(f"✅ `{character_name}` finished scavenging and found: {', '.join(found_items)}")
                    else:
                        print(f"❌ `{character_name}` scavenged but found nothing.")


async def setup(bot):
    """Asynchronous setup function for adding the cog."""
    await bot.add_cog(Scavenge(bot))
