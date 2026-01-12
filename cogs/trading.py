import json
import os
import uuid
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from utils.inventory import normalize_character_name, load_inventory, save_inventory

# Constants
INVENTORY_DIR = "data/inventories/"
TRADE_PROPOSALS_FILE = "data/trade_proposals.json"
TRADING_CHANNEL_ID = 1336354629109289092  # Replace with your actual trading channel ID


# --- Trade Proposal Helper Functions ---
def load_trade_proposals() -> list:
    """Load trade proposals from file."""
    if not os.path.isfile(TRADE_PROPOSALS_FILE):
        print(f"[DEBUG] load_trade_proposals: File '{TRADE_PROPOSALS_FILE}' not found. Returning empty list.")
        return []
    try:
        with open(TRADE_PROPOSALS_FILE, "r") as f:
            proposals = json.load(f)
            print(f"[DEBUG] load_trade_proposals: Loaded {len(proposals)} proposals.")
            return proposals
    except Exception as e:
        print(f"[DEBUG] load_trade_proposals: Error reading '{TRADE_PROPOSALS_FILE}': {e}")
        return []


def save_trade_proposals(trades: list):
    """Save trade proposals to file."""
    try:
        with open(TRADE_PROPOSALS_FILE, "w") as f:
            json.dump(trades, f, indent=4)
        print(f"[DEBUG] save_trade_proposals: Successfully saved {len(trades)} trade proposals.")
    except Exception as e:
        print(f"[DEBUG] save_trade_proposals: Error saving proposals to '{TRADE_PROPOSALS_FILE}': {e}")


# --- Parsing Helper ---
def parse_trade_args(args: list) -> tuple:
    """
    Parse a list of arguments to extract offered item, offered amount,
    requested item, and requested amount.

    Expected format (all words separated by spaces):
      <offered item words> <offered amount> <requested item words> <requested amount>
    For example:
      ["Mulberry", "Log", "2", "Gold", "1"] returns ("Mulberry Log", 2, "Gold", 1)
    """
    print(f"[DEBUG] parse_trade_args: Received args: {args}")
    # Find the first numeric token (offered amount)
    offered_amount = None
    i = None
    for idx, token in enumerate(args):
        if token.isdigit():
            offered_amount = int(token)
            i = idx
            break
    if offered_amount is None or i is None or i == 0:
        raise ValueError("Offered amount or offered item missing.")
    offered_item = " ".join(args[:i])
    # Now, in the remaining tokens, find the next numeric token (requested amount)
    remaining = args[i + 1:]
    requested_amount = None
    j = None
    for idx, token in enumerate(remaining):
        if token.isdigit():
            requested_amount = int(token)
            j = idx
            break
    if requested_amount is None or j is None or j == 0:
        raise ValueError("Requested amount or requested item missing.")
    requested_item = " ".join(remaining[:j])
    print(
        f"[DEBUG] parse_trade_args: Parsed offered_item='{offered_item}', offered_amount={offered_amount}, "
        f"requested_item='{requested_item}', requested_amount={requested_amount}")
    return offered_item, offered_amount, requested_item, requested_amount


# --- Trading Cog ---
class Trading(commands.Cog):
    """Trading system with extensive debug logging for proposals and acceptance."""

    def __init__(self, bot):
        self.bot = bot
        print("[DEBUG] Trading Cog Initialized")

    async def cog_load(self):
        print("[DEBUG] Trading Cog Loaded; starting cleanup task.")
        self.cleanup_trades.start()

    def cog_unload(self):
        print("[DEBUG] Trading Cog Unloaded. Stopping cleanup task.")
        self.cleanup_trades.cancel()

    @tasks.loop(hours=1)
    async def cleanup_trades(self):
        """Removes expired trade proposals older than one week."""
        print("[DEBUG] cleanup_trades: Running trade cleanup task.")
        trades = load_trade_proposals()
        now = datetime.utcnow()
        updated_trades = []
        channel = self.bot.get_channel(TRADING_CHANNEL_ID)
        for trade in trades:
            try:
                trade_time = datetime.fromisoformat(trade["timestamp"])
            except Exception as e:
                print(f"[DEBUG] cleanup_trades: Error parsing timestamp for trade '{trade.get('id', 'unknown')}': {e}")
                continue
            if now - trade_time > timedelta(weeks=1) and trade["status"] == "open":
                print(f"[DEBUG] cleanup_trades: Removing expired trade '{trade['id']}'")
                if channel:
                    await channel.send(f"ℹ️ Trade `{trade['id']}` expired and was removed.")
            else:
                updated_trades.append(trade)
        save_trade_proposals(updated_trades)
        print("[DEBUG] cleanup_trades: Cleanup complete.")

    @cleanup_trades.before_loop
    async def before_cleanup(self):
        print("[DEBUG] cleanup_trades: Waiting for bot to be ready before starting cleanup task.")
        await self.bot.wait_until_ready()

    @commands.group(name="trade", invoke_without_command=True)
    async def trade(self, ctx):
        """Display trade instructions if no subcommand is provided."""
        instructions = (
            "**Trade Instructions:**\n"
            "To propose a trade, use:\n"
            "`!trade proposal <character_name> <offered item> <offered amount> <requested item> <requested amount>`\n"
            "Example: `!trade proposal Taco Mulberry Log 2 Gold 1`\n\n"
            "To accept a trade, use:\n"
            "`!trade accept <character accepting the trade> <trade_id>`"
        )
        print(f"[DEBUG] trade: Showing trade instructions to {ctx.author}")
        await ctx.message.delete(delay=0)
        await ctx.send(instructions, delete_after=30)

    @trade.command(name="proposal")
    async def proposal(self, ctx, character_name: str, *, args_str: str):
        """
        Propose a trade without using explicit tokens.
        Format: <character_name> <offered item> <offered amount> <requested item> <requested amount>
        Example: !trade proposal Taco Mulberry Log 2 Gold 1
        """
        normalized_char = normalize_character_name(character_name)
        print(
            f"[DEBUG] proposal: Received proposal from '{ctx.author}' for character '{normalized_char}' with args_str: '{args_str}'")

        await ctx.message.delete(delay=0)

        try:
            args = args_str.split()
            offered_item, offered_amount, requested_item, requested_amount = parse_trade_args(args)
        except Exception as e:
            msg = f"Error parsing trade arguments: {e}"
            print(f"[DEBUG] proposal: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        # Reject trading of experience points
        if offered_item.lower() in ("exp", "experience") or requested_item.lower() in ("exp", "experience"):
            msg = "Trading of experience is not allowed."
            print(f"[DEBUG] proposal: {msg}")
            await ctx.send(f"🚫 {msg}", delete_after=15)
            return

        # Load inventory for the proposing character
        char_data = load_inventory(normalized_char)
        if not char_data:
            msg = f"Character '{normalized_char}' not found."
            print(f"[DEBUG] proposal: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        # Check if character has enough of the offered item (if not gold)
        if offered_item.lower() == "gold":
            if char_data.get("total_gold", 0) < offered_amount:
                msg = f"'{normalized_char}' does not have enough Gold. Has: {char_data.get('total_gold', 0)}"
                print(f"[DEBUG] proposal: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return
        else:
            available = char_data.get("items", {}).get(offered_item, 0)
            if available < offered_amount:
                msg = f"'{normalized_char}' does not have enough {offered_item}. Has: {available}"
                print(f"[DEBUG] proposal: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return

        trade_id = f"{ctx.author.id}-{uuid.uuid4().hex[:6]}"
        trade = {
            "id": trade_id,
            "owner": ctx.author.id,
            "character": normalized_char,
            "offer_item": offered_item,
            "offer_amount": offered_amount,
            "request_item": requested_item,
            "request_amount": requested_amount,
            "status": "open",
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"[DEBUG] proposal: Creating trade proposal: {trade}")
        trades = load_trade_proposals()
        trades.append(trade)
        save_trade_proposals(trades)
        print(f"[DEBUG] proposal: Trade proposal saved with ID: {trade_id}")

        channel = self.bot.get_channel(TRADING_CHANNEL_ID)
        if channel is None:
            msg = "Trading channel not found."
            print(f"[DEBUG] proposal: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        trade_message = (
            f"📜 **New Trade Proposal** 📜\n"
            f"**Trade ID:** `{trade_id}`\n"
            f"🔹 **{normalized_char}** offers **{offered_amount} {offered_item}** in exchange for **{requested_amount} {requested_item}**.\n"
            f"To accept, use: `!trade accept <character> {trade_id}`\n"
            f"(Replace `<character>` with the name of the character that will accept the trade.)"
        )
        print(f"[DEBUG] proposal: Sending trade message to channel: {trade_message}")
        await channel.send(trade_message)
        await ctx.send(f"✅ Trade proposal `{trade_id}` created.", delete_after=15)

    @trade.command(name="accept")
    async def trade_accept(self, ctx, accepting_character: str, trade_id: str):
        """
        Accept a trade proposal.
        Command format: !trade accept <character accepting the trade> <trade_id>
        Any character may accept a trade if they have the requested item or gold.
        """
        normalized_acceptor = normalize_character_name(accepting_character)
        print(
            f"[DEBUG] accept: '{ctx.author}' attempting to accept trade '{trade_id}' using character '{normalized_acceptor}'")

        await ctx.message.delete(delay=0)

        trades = load_trade_proposals()
        trade = next((t for t in trades if t["id"] == trade_id and t["status"] == "open"), None)
        if not trade:
            msg = "Trade not found or already completed."
            print(f"[DEBUG] accept: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        print(f"[DEBUG] accept: Found trade: {trade}")

        # Load inventories for proposer and acceptor
        proposer_data = load_inventory(trade["character"])
        acceptor_data = load_inventory(normalized_acceptor)
        if not proposer_data:
            msg = f"Proposer character '{trade['character']}' not found."
            print(f"[DEBUG] accept: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return
        if not acceptor_data:
            msg = f"Acceptor character '{normalized_acceptor}' not found."
            print(f"[DEBUG] accept: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        print(f"[DEBUG] accept: Proposer data: {proposer_data}")
        print(f"[DEBUG] accept: Acceptor data: {acceptor_data}")

        # Check if acceptor has the requested item/gold
        if trade["request_item"].lower() == "gold":
            if acceptor_data.get("total_gold", 0) < trade["request_amount"]:
                msg = f"'{normalized_acceptor}' does not have enough Gold. Has: {acceptor_data.get('total_gold', 0)}"
                print(f"[DEBUG] accept: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return
        else:
            available_req = acceptor_data.get("items", {}).get(trade["request_item"], 0)
            if available_req < trade["request_amount"]:
                msg = f"'{normalized_acceptor}' does not have enough {trade['request_item']}. Has: {available_req}"
                print(f"[DEBUG] accept: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return

        # Verify proposer still has the offered item/gold
        if trade["offer_item"].lower() == "gold":
            if proposer_data.get("total_gold", 0) < trade["offer_amount"]:
                msg = f"Proposer '{trade['character']}' does not have enough Gold. Has: {proposer_data.get('total_gold', 0)}"
                print(f"[DEBUG] accept: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return
        else:
            available_offer = proposer_data.get("items", {}).get(trade["offer_item"], 0)
            if available_offer < trade["offer_amount"]:
                msg = f"Proposer '{trade['character']}' does not have enough {trade['offer_item']}. Has: {available_offer}"
                print(f"[DEBUG] accept: {msg}")
                await ctx.send(f"⚠️ {msg}", delete_after=15)
                return

        # Process trade: Transfer offered item/gold from proposer to acceptor
        try:
            if trade["offer_item"].lower() == "gold":
                proposer_data["total_gold"] -= trade["offer_amount"]
                acceptor_data["total_gold"] = acceptor_data.get("total_gold", 0) + trade["offer_amount"]
                print(
                    f"[DEBUG] accept: Transferred {trade['offer_amount']} Gold from '{trade['character']}' to '{normalized_acceptor}'")
            else:
                proposer_current = proposer_data.get("items", {}).get(trade["offer_item"], 0)
                proposer_data["items"][trade["offer_item"]] = proposer_current - trade["offer_amount"]
                acceptor_current = acceptor_data.get("items", {}).get(trade["offer_item"], 0)
                acceptor_data.setdefault("items", {})[trade["offer_item"]] = acceptor_current + trade["offer_amount"]
                print(
                    f"[DEBUG] accept: Transferred {trade['offer_amount']} {trade['offer_item']} from '{trade['character']}' to '{normalized_acceptor}'")
        except Exception as e:
            msg = f"Error during transfer of offered item: {e}"
            print(f"[DEBUG] accept: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        # Process trade: Transfer requested item/gold from acceptor to proposer
        try:
            if trade["request_item"].lower() == "gold":
                acceptor_data["total_gold"] -= trade["request_amount"]
                proposer_data["total_gold"] = proposer_data.get("total_gold", 0) + trade["request_amount"]
                print(
                    f"[DEBUG] accept: Transferred {trade['request_amount']} Gold from '{normalized_acceptor}' to '{trade['character']}'")
            else:
                acceptor_current = acceptor_data.get("items", {}).get(trade["request_item"], 0)
                acceptor_data["items"][trade["request_item"]] = acceptor_current - trade["request_amount"]
                proposer_current = proposer_data.get("items", {}).get(trade["request_item"], 0)
                proposer_data.setdefault("items", {})[trade["request_item"]] = proposer_current + trade[
                    "request_amount"]
                print(
                    f"[DEBUG] accept: Transferred {trade['request_amount']} {trade['request_item']} from '{normalized_acceptor}' to '{trade['character']}'")
        except Exception as e:
            msg = f"Error during transfer of requested item: {e}"
            print(f"[DEBUG] accept: {msg}")
            await ctx.send(f"⚠️ {msg}", delete_after=15)
            return

        # Save updated inventories
        save_inventory(trade["character"], proposer_data)
        save_inventory(normalized_acceptor, acceptor_data)
        print(
            f"[DEBUG] accept: Saved updated data for proposer '{trade['character']}' and acceptor '{normalized_acceptor}'")

        # Remove the trade proposal
        updated_trades = [t for t in trades if t["id"] != trade_id]
        save_trade_proposals(updated_trades)
        print(f"[DEBUG] accept: Trade '{trade_id}' processed and removed from proposals.")

        # Log success in trading channel
        channel = self.bot.get_channel(TRADING_CHANNEL_ID)
        if channel:
            await channel.send(
                f"✅ Trade `{trade_id}` successfully completed.")
        await ctx.send(f"✅ Trade `{trade_id}` successfully completed.", delete_after=15)

    @trade.command(name="list")
    async def list_trades(self, ctx):
        """List all open trade proposals."""
        print(f"[DEBUG] list_trades: Command triggered by {ctx.author}")
        trades = load_trade_proposals()
        if not trades:
            print("[DEBUG] list_trades: No trades found.")
            await ctx.send("There are no open trades at the moment.")
            return
        open_trades = [t for t in trades if t["status"] == "open"]
        if not open_trades:
            print("[DEBUG] list_trades: No open trades found.")
            await ctx.send("There are no open trades at the moment.")
            return
        output_lines = []
        for trade in open_trades:
            accept_string = f"!trade accept {'<Accepting Character>'} {trade['id']}"
            line = (
                f"Character: **{trade['character']}** | Offers: **{trade['offer_amount']} {trade['offer_item']}** "
                f"for **{trade['request_amount']} {trade['request_item']}**\nTo accept, use: `{accept_string}`"
            )
            output_lines.append(line)
            print(f"[DEBUG] list_trades: Trade {trade['id']} - {line}")
        message = "\n\n".join(output_lines)
        await ctx.message.delete(delay=0)
        await ctx.send(message, delete_after=150)


async def setup(bot):
    """Setup function for adding the Trading cog."""
    await bot.add_cog(Trading(bot))
