import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Check the bot's latency")
    async def pingg(self, interaction: discord.Interaction):
        """Slash command to check bot latency."""
        latency = round(self.bot.latency * 1000)  # Convert latency to milliseconds
        await interaction.response.send_message(f"Pong! {latency}ms")

async def setup(bot: commands.Bot):
    """The setup function to add the cog to the bot."""
    await bot.add_cog(Ping(bot))
