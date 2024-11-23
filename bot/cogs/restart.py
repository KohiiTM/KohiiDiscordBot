import discord
from discord.ext import commands
import os
import sys

class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="restart", description="Restarts the bot (requires admin privileges).")
    async def restart(self, interaction: discord.Interaction):
        """Restarts the bot."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You don't have permission to restart the bot.", ephemeral=True
            )
            return

        await interaction.response.send_message("Restarting bot...")

        # Properly close the bot before restarting
        await self.bot.close()

        # Restart the bot process
        os.execv(sys.executable, ["python"] + sys.argv)


async def setup(bot):
    """Setup function to add the Restart cog to the bot."""
    await bot.add_cog(Restart(bot))
