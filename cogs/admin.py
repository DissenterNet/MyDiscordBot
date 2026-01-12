import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "config.json"


def load_admins():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("config.json not found!")
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config.get("admins", [])


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_ids = load_admins()

    def is_admin(self, user_id):
        return user_id in self.admin_ids

    async def cog_check(self, ctx):
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You are not authorized to use admin commands.", delete_after=5)
            return False
        return True

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.display_name} has been kicked.")

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.display_name} has been banned.")

    @commands.command(name="unban")
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f"✅ {user.name} has been unbanned.")
                return
        await ctx.send(f"❌ User {member_name} not found in ban list.")

    @commands.command(name="mute")
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"✅ {member.display_name} has been muted.")

    @commands.command(name="unmute")
    async def unmute(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"✅ {member.display_name} has been unmuted.")
        else:
            await ctx.send(f"❌ {member.display_name} is not muted.")

    @commands.command(name="clear_channel")
    async def clear_channel(self, ctx):
        await ctx.channel.purge()
        await ctx.send("✅ All messages in this channel have been deleted.", delete_after=5)

    @commands.command(name="clear_user")
    async def clear_user(self, ctx, member: discord.Member):
        def is_user(msg):
            return msg.author == member

        deleted = await ctx.channel.purge(limit=1000, check=is_user)
        await ctx.send(f"✅ Deleted {len(deleted)} messages from {member.display_name}.", delete_after=5)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
