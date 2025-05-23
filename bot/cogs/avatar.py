import discord
from discord import app_commands
from discord.ext import commands


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Retrieve a user's profile picture")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar", color=discord.Color.dark_orange())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print(f"Commands synced globally for {self.bot.user}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Avatar(bot))
