import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()

# Read from .env and convert to int
CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_channel_id = CHANNEL_ID

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f"Member joined: {member.name}")

        if member.bot:
            return

        channel = member.guild.get_channel(self.welcome_channel_id)

        if channel is None:
            print(f"Channel with ID {self.welcome_channel_id} not found")
            return

        try:
            await channel.send(f"welcome {member.mention}")
        except discord.Forbidden:
            print(f"Missing permissions in {channel.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))