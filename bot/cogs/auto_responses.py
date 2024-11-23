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
        responses = {
            "val": [
                "https://tenor.com/view/choso-jjk-choso-choso-panic-insane-choso-anime-insane-gif-5693401929827560865",
                "nah",
                "https://tenor.com/view/valorant-nerd-brimstone-viper-omen-gif-9861738447246078182",
                "RAHHHHHHHHH",
            ],
        }

        # Check if any keyword is in the message content
        for key, possible_responses in responses.items():
            if key in message.content.lower():
                response = random.choice(possible_responses)  # Randomly pick a response
                await message.channel.send(response)
                return  # Stop after the first match

        # Allow command processing to continue
        await self.bot.process_commands(message)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(AutoResponses(bot))
