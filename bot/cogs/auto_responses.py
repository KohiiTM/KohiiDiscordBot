import discord
from discord.ext import commands
import random  # Import the random module for random responses

class AutoResponses(commands.Cog):
    """Cog for handling auto-responses."""

    def __init__(self, bot):
        self.bot = bot  # Correctly assign the bot instance

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Define a dictionary with keywords and list of potential responses
        response_groups = {
            ("val", "valorant"): [
                "https://tenor.com/view/choso-jjk-choso-choso-panic-insane-choso-anime-insane-gif-5693401929827560865",
                "nah",
                "https://tenor.com/view/valorant-nerd-brimstone-viper-omen-gif-9861738447246078182",
                "RAHHHHHHHHH",
            ],
            ("hello", "hi"): [
                "wAZAAAAAAAAAAAAAA",
                ":man_with_probing_cane::skin-tone-3:",
                "https://tenor.com/view/anime-lolis-cute-dancing-girl-gif-25488979",
                "yo",
            ],
        }

        # Check if any keyword in the group is in the message content
        for keywords, possible_responses in response_groups.items():
            if any(keyword in message.content.lower() for keyword in keywords):
                response = random.choice(possible_responses)  # Randomly pick a response
                await message.channel.send(response)
                return  # Stop after the first match

        # Allow command processing to continue
        await self.bot.process_commands(message)

# Setup function to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponses(bot))
