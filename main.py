import json
import discord
import asyncio
import logging
import os
import shutil
import atexit
from datetime import datetime
from discord.ext import commands, tasks

# ----------------------------
# Logging Setup (Minimal Logging)
# ----------------------------

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "bot.log"),
    level=logging.INFO,  # Only log important events
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


def shutdown_logging():
    """Flush and close all log handlers on shutdown."""
    logging.info("🔻 Bot shutting down. Closing log handlers.")
    logging.shutdown()


atexit.register(shutdown_logging)

# ----------------------------
# Backup Setup (Runs Daily at 4 AM ET)
# ----------------------------

BACKUP_DIR = "backups"


@tasks.loop(hours=6)
async def half_daily_backup():
    """Creates a backup every 12 hours and deletes backups older than 7 days."""
    create_backup()
    delete_old_backups()


def create_backup():
    """Create a backup of the entire 'data' folder."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")  # Include time for uniqueness
    backup_folder = os.path.join(BACKUP_DIR, timestamp)

    if os.path.exists(backup_folder):
        return  # Avoid duplicate backups

    try:
        os.makedirs(backup_folder, exist_ok=True)
        source_dir = "data"
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, os.path.join(backup_folder, "data"))
            logging.info(f"✅ Backup created at {backup_folder}")
        else:
            logging.warning("⚠️ Source 'data' directory does not exist. No backup created.")
    except Exception as e:
        logging.error(f"⚠️ Error creating backup: {e}")


def delete_old_backups():
    """Delete backup folders older than 7 days."""
    now = datetime.utcnow().timestamp()
    cutoff = now - (7 * 24 * 60 * 60)  # 7 days in seconds
    for folder in os.listdir(BACKUP_DIR):
        folder_path = os.path.join(BACKUP_DIR, folder)
        if os.path.isdir(folder_path):
            try:
                folder_timestamp = datetime.strptime(folder, "%Y-%m-%d_%H-%M-%S")
                if folder_timestamp.timestamp() < cutoff:
                    shutil.rmtree(folder_path)
                    logging.info(f"🗑 Deleted old backup: {folder_path}")
            except Exception as e:
                logging.error(f"⚠️ Error deleting backup folder {folder_path}: {e}")

# ----------------------------
# Inventory Cleanup (Runs Daily)
# ----------------------------


@tasks.loop(hours=6)
async def daily_inventory_cleanup():
    """
    Cleans up each character's inventory by removing any items with a quantity of 0.
    This runs once every 24 hours.
    """
    logging.info("Starting daily inventory cleanup.")
    inventory_dir = "data/inventories/"
    if not os.path.exists(inventory_dir):
        logging.info("No inventory directory found; skipping cleanup.")
        return

    for filename in os.listdir(inventory_dir):
        if not filename.endswith(".json"):
            continue
        file_path = os.path.join(inventory_dir, filename)
        try:
            with open(file_path, "r") as f:
                inventory = json.load(f)
        except Exception as e:
            logging.error(f"Error reading inventory file {file_path}: {e}")
            continue

        if "items" in inventory:
            removed_items = []
            for item in list(inventory["items"].keys()):
                if inventory["items"][item] == 0:
                    del inventory["items"][item]
                    removed_items.append(item)
            if removed_items:
                try:
                    with open(file_path, "w") as f:
                        json.dump(inventory, f, indent=4)
                    logging.info(f"Cleaned {filename}: removed items with 0 quantity: {', '.join(removed_items)}")
                except Exception as e:
                    logging.error(f"Error writing inventory file {file_path}: {e}")
    logging.info("Daily inventory cleanup completed.")

# ----------------------------
# Bot Setup
# ----------------------------

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
EVENT_CHANNEL_ID = config["EVENT_CHANNEL_ID"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="shutdown")
async def shutdown(ctx):
    """Shuts down the bot."""
    if ctx.author.id == 1151299746657468486:  # Replace with your own Discord user ID
        await ctx.send("Shutting down...")
        await bot.close()  # This shuts down the bot
    else:
        await ctx.send("You don't have permission to shut me down.")


async def load_cogs():
    cog_names = [
        "cogs.availability",
        "cogs.session",
        "cogs.crafting",
        "cogs.scavenge",
        "cogs.commands",
        "cogs.trading",
        "cogs.honor",
        "cogs.rollplay",
        "cogs.disassemble",
        "cogs.group_projects",
        "cogs.management",
        "cogs.admin",
        "cogs.character"
    ]
    for cog in cog_names:
        await bot.load_extension(cog)

    logging.info("✅ All cogs loaded successfully.")


@bot.event
async def on_ready():
    """Triggered when the bot connects to Discord."""
    logging.info(f"✅ Logged in as {bot.user}")
    print(f"✅ Logged in as {bot.user}")

# ----------------------------
# Hourly Command Message Deletion Task
# ----------------------------


@tasks.loop(minutes=1)
async def hourly_delete_command_messages():
    """
    Runs every hour and deletes any message (from the last 100 messages)
    in every text channel that starts with "!".
    """
    logging.info("Starting hourly deletion of command messages.")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=100):
                    if message.content.startswith("!"):
                        try:
                            await message.delete()
                        except Exception as e:
                            logging.error(f"Failed to delete message {message.id} in channel {channel.name}: {e}")
            except Exception as e:
                logging.error(f"Failed to fetch messages for channel {channel.name}: {e}")
    logging.info("Hourly deletion of command messages completed.")


@bot.event
async def setup_hook():
    """Ensures all background tasks start properly before the bot is ready."""
    logging.info("🔄 Starting background tasks...")
    daily_inventory_cleanup.start()
    hourly_delete_command_messages.start()
    half_daily_backup.start()  # Start the backup task
    logging.info("✅ Daily backup, inventory cleanup, and hourly deletion tasks started.")


async def main():
    """Main function to start the bot and load extensions."""
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
