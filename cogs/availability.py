import uuid
import logging
from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from utils.json_io import save_json, load_json

CONFIG_FILE = "config.json"
DATA_FILE = "data/availability.json"
TIMEZONES_FILE = "data/timezones.json"
OVERLAPS_FILE = "data/overlaps.json"
SESSIONS_CHANNEL_ID = 1335991687243104328

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


class Availability(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_availability.start()

    @commands.group(name="availability", invoke_without_command=True)
    async def availability(self, ctx):
        await ctx.send("Use `!availability add`, `!availability list`, or `!availability remove`.", delete_after=5)

    @availability.command(name="add")
    async def availability_add(self, ctx, date: str, start: str, end: str):
        """Add availability using local time (e.g., `!availability add 2025-02-20 1600 0400`)."""
        timezones = load_json(TIMEZONES_FILE)
        data = load_json(DATA_FILE)

        user_id = str(ctx.author.id)

        if user_id not in timezones:
            await ctx.send(
                "🌍 You haven't set a timezone yet! Please enter your UTC offset (e.g., `-5` for EST, `+2` for CEST):", delete_after=5)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                response = await self.bot.wait_for("message", check=check, timeout=60)
                offset = int(response.content)
                timezones[user_id] = offset
                save_json(TIMEZONES_FILE, timezones)
                await ctx.send(f"✅ Timezone set to UTC{offset:+d}. You can now add availability.", delete_after=5)
            except ValueError:
                await ctx.send("❌ Invalid offset. Please enter a number (e.g., -5, 0, +3).", delete_after=5)
                return
            except TimeoutError:
                await ctx.send("❌ You took too long. Try again.", delete_after=15)
                return

        offset = timezones[user_id]
        offset_delta = timedelta(hours=offset)
        tz_info = timezone(offset_delta)

        # Convert simplified input like 1600 to 16:00
        try:
            start = f"{start[:2]}:{start[2:]}"
            end = f"{end[:2]}:{end[2:]}"
        except IndexError:
            await ctx.send("❌ Invalid time format. Use HHMM like `1600`.", delete_after=5)
            return

        try:
            start_local = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
            end_local = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")
            if end_local <= start_local:
                end_local += timedelta(days=1)
        except ValueError:
            await ctx.send("❌ Invalid date or time. Use `YYYY-MM-DD 1600 0400`.", delete_after=5)
            return

        start_utc = start_local.replace(tzinfo=tz_info).astimezone(timezone.utc)
        end_utc = end_local.replace(tzinfo=tz_info).astimezone(timezone.utc)

        discord_name = ctx.author.name.strip().lower().capitalize()
        availability_entry = {
            "id": str(uuid.uuid4()),
            "discord_name": discord_name,
            "user_id": user_id,
            "start": start_utc.strftime("%Y-%m-%d %H:%M"),
            "end": end_utc.strftime("%Y-%m-%d %H:%M"),
        }

        data.setdefault("availability", []).append(availability_entry)
        save_json(DATA_FILE, data)

        await ctx.send(
            f"✅ Availability added for **{discord_name}**: {start_local.strftime('%Y-%m-%d %H:%M')} to {end_local.strftime('%Y-%m-%d %H:%M')} (Local Time)", delete_after=5)

    @availability.command(name="list")
    async def availability_list(self, ctx):
        data = load_json(DATA_FILE)
        timezones = load_json(TIMEZONES_FILE)
        user_id = str(ctx.author.id)

        if user_id not in timezones:
            await ctx.send("❌ You haven't set a timezone yet. Use `!availability add` to set one.", delete_after=5)
            return

        offset = timezones[user_id]
        offset_delta = timedelta(hours=offset)
        tz_info = timezone(offset_delta)

        user_availabilities = [a for a in data.get("availability", []) if a["user_id"] == user_id]

        if not user_availabilities:
            await ctx.send("❌ You have no availability set.", delete_after=5)
            return

        response = f"**Your Availability (UTC{offset:+d}):**\n"
        for entry in user_availabilities:
            start_utc = datetime.strptime(entry["start"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            end_utc = datetime.strptime(entry["end"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

            start_local = start_utc.astimezone(tz_info).strftime("%Y-%m-%d %H:%M")
            end_local = end_utc.astimezone(tz_info).strftime("%Y-%m-%d %H:%M")

            response += f"- `{entry['id']}`: {start_local} → {end_local}\n"

        await ctx.send(response, delete_after=30)

    @availability.command(name="remove")
    async def availability_remove(self, ctx, availability_id: str):
        data = load_json(DATA_FILE)
        user_id = str(ctx.author.id)

        initial_count = len(data.get("availability", []))
        data["availability"] = [
            a for a in data["availability"] if not (a["id"] == availability_id and a["user_id"] == user_id)
        ]

        if len(data["availability"]) < initial_count:
            save_json(DATA_FILE, data)
            await ctx.send(f"✅ Removed availability with ID `{availability_id}`.", delete_after=5)
        else:
            await ctx.send(f"❌ Availability with ID `{availability_id}` not found.", delete_after=5)

    @tasks.loop(minutes=5)
    async def check_availability(self):
        data = load_json(DATA_FILE)
        overlaps = load_json(OVERLAPS_FILE)
        now = datetime.utcnow()
        channel = self.bot.get_channel(SESSIONS_CHANNEL_ID)

        updated_overlaps = []

        for i, a1 in enumerate(data.get("availability", [])):
            for j, a2 in enumerate(data.get("availability", [])):
                if i >= j or a1["user_id"] == a2["user_id"]:
                    continue

                overlap_start = max(a1["start"], a2["start"])
                overlap_end = min(a1["end"], a2["end"])

                if overlap_start < overlap_end:
                    overlap_key = f"{overlap_start}_{overlap_end}"
                    existing = next((o for o in overlaps.get("overlaps", []) if o["key"] == overlap_key), None)

                    if not existing:
                        msg = await channel.send(
                            f"**Overlap Found:** {overlap_start} → {overlap_end}\n"
                            f"Players: <@{a1['user_id']}> <@{a2['user_id']}>"
                        )
                        updated_overlaps.append({"key": overlap_key, "start": overlap_start, "end": overlap_end, "message_id": msg.id})
                    else:
                        updated_overlaps.append(existing)

        overlaps["overlaps"] = updated_overlaps
        save_json(OVERLAPS_FILE, overlaps)

    @check_availability.before_loop
    async def before_check_availability(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Availability(bot))
