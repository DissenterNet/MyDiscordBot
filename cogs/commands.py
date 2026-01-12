from discord.ext import commands


class CommandsCog(commands.Cog):
    """Provides a list of bot commands and detailed help for each command."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="commands", invoke_without_command=True)
    async def commands(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        command_list = (
            "**!Available Commands:**\n"
            "🔹 **!scavenge <Character Name> [Resource Type]** - Scavenge for raw materials once per hour.\n"
            "🔹 **!craft <Character Name> <Item Name>** - Craft an item if you have the required materials.\n"
            "🔹 **!disassemble <Character Name> <Item Name>** - Break down an item into materials.\n"
            "🔹 **!trade proposal <Character Name> <Offer Item> <Amount> <Request Item> <Amount>** - Propose a trade.\n"
            "🔹 **!trade accept <Character Name> <Trade ID>** - Accept a trade proposal.\n"
            "🔹 **!trade list** - View all open trade proposals.\n"
            "🔹 **!session <Session ID> <Character Name> <XP Earned> <Gold Earned> <Expenses>** - Log session results.\n"
            "🔹 **!stats** - View a summary of XP and gold for your characters.\n"
            "🔹 **!inventory <Character Name>** - Receive your character's inventory in a DM.\n"
            "🔹 **!availability add <Date> <Start Time> <End Time>** - Add your availability.\n"
            "🔹 **!availability list** - View your availability.\n"
            "🔹 **!availability remove <Availability ID>** - Remove an availability entry.\n"
            "🔹 **!rp <Character Name> <Message>** - Send a roleplay message as your character.\n"
            "🔹 **!emote <Character Name> <Message>** - Send a non-spoken emote message as your character.\n"
            "🔹 **!setavatar <Character Name>** - Upload an image to set as your character's avatar.\n"
            "🔹 **!list_projects** - List all active group projects.\n"
            "🔹 **!contribute <Character Name> <Project ID> <Resource> <Amount>** - Contribute materials to a project.\n"
            "🔹 **!check_project <Project ID>** - View progress of a specific project.\n"
            "🔹 **!work_on_project <Character Name> <Project ID> <Hours>** - Work on a project using labor.\n"
            "🔹 **!life <Character Name>** - Create a new character.\n"
            "🔹 **!death <Character Name>** - Delete a character (requires confirmation).\n"
            "🔹 **!dm <Character Name>** - DM your character's inventory.\n"
            "\n**For detailed instructions on any command, use `!<command name>` or check the pinned message in the bot-spamming channel.**"
        )

        # Split into multiple messages if too long
        chunks = [command_list[i:i + 1900] for i in range(0, len(command_list), 1900)]

        for chunk in chunks:
            await ctx.send(chunk, delete_after=150)

    @commands.command(name="scavenge")
    async def scavenge(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        await ctx.send(
            "**Scavenge Command Help**\n"
            "Usage: `!scavenge <Character Name>`\n"
            "Description: Allows your character to scavenge for raw materials once per hour.\n"
            "Example: `!scavenge Taco`\n"
            "Copy-paste: `!scavenge <YourCharacterName>`\n"
            "\n"
            "**Scavenge Command Help**\n"
            "Usage: `!scavenge <Character Name> <Resource Type>`\n"
            "Description: Allows your character to scavenge for raw materials once per hour.\n"
            "Example: `!scavenge Taco herbs`\n"
            "Copy-paste: `!scavenge <Character Name> <Resource Type>`\n", delete_after=150
        )

    @commands.command(name="craft")
    async def craft(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        await ctx.send(
            "**Craft Command Help**\n"
            "Usage: `!craft <Character Name> <Item Name>`\n"
            "Description: Allows your character to craft an item if the necessary materials are available.\n"
            "Example: `!craft Taco Wooden Mallet`\n"
            "Copy-paste: `!craft <YourCharacterName> <ItemName>`\n", delete_after=150
        )

    @commands.command(name="trade")
    async def trade(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        await ctx.send(
            "**Trade \n"
            "Usage: `!trade proposal <Character Name> <Offer Item> <Amount> <Request Item> <Amount>`\n"
            "Description: Allows players to propose trades with each other.\n"
            "Example: `!trade proposal Taco Mulberry Log 2 Gold 5`\n"
            "Copy-paste: `!trade proposal <YourCharacterName> <OfferItem> <Amount> <RequestItem> <Amount>`\n"
            "\n"
            "**Trade Accept Command**\n"
            "Usage: `!trade accept <Character Name> <Trade ID>`\n"
            "Accept a trade proposal.\n"
            "Example: `!trade accept Taco 12345-abcde`\n"
            "Copy-paste: `!trade accept YourCharacterName TradeID`\n"
            "\n"
            "**View Standing Trade Proposals**\n"
            "Usage: `!trade list`\n"
            "Copy-paste: `!trade list`\n", delete_after=150
        )

    @commands.command(name="availability")
    async def availability(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        await ctx.send(
            "**Availability Command Help**\n"
            "Usage: `!availability add <Date> <Start Time> <End Time>`\n"
            "Description: Allows you to set when you're available for game sessions.\n"
            "Example: `!availability add 2025-02-10 18:00 22:00`\n"
            "Copy-paste: `!availability add <YYYY-MM-DD> <HH:MM> <HH:MM>`\n", delete_after=150
        )

    @commands.command(name="disassemble")
    async def disassemble(self, ctx):
        """Displays a detailed list of all available bot commands with formatting instructions."""
        try:
            # Delete the trigger message after 0 seconds to avoid instant failure
            await ctx.message.delete(delay=0)
        except Exception as e:
            print(f"[DEBUG] Unable to delete message: {e}")

        await ctx.send(
            "**Disassemble Command Help**\n"
            "Usage: `!disassemble <Character Name> <Item Name>`\n"
            "Description: Breaks down an item to recover materials.\n"
            "Example: `!disassemble Taco Wooden Planks`\n"
            "Copy-paste: `!disassemble <YourCharacterName> <ItemName>`\n", delete_after=150
        )


async def setup(bot):
    """Setup function for adding the cog."""
    await bot.add_cog(CommandsCog(bot))
