import discord
from discord.ext import commands
import random
import re  # Import re for regular expressions

class AutoResponses(commands.Cog):
    """Cog for handling auto-responses."""

    def __init__(self, bot):
        self.bot = bot  # Correctly assign the bot instance

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Define the role ID
        role_id = '1128759195202760854'
        role_mention = f'<@&{role_id}>'  # Create the role mention format

        # Define a dictionary with keywords and list of potential responses
        response_groups = {
            ("val", "valorant", role_mention): [
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

        # Get the message content
        content = message.content.lower()
        
        # Check if any keyword in the group matches as a whole word
        for keywords, possible_responses in response_groups.items():
            for keyword in keywords:
                # For role mentions, we need an exact match (not lowercase)
                if keyword == role_mention and keyword in message.content:
                    response = random.choice(possible_responses)
                    await message.channel.send(response)
                    return
                
                # For regular keywords, use word boundary matching with regex
                elif keyword != role_mention:
                    # The \b represents a word boundary in regex
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, content):
                        response = random.choice(possible_responses)
                        await message.channel.send(response)
                        return  # Stop after the first match

        # Allow command processing to continue
        await self.bot.process_commands(message)

# Setup function to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponses(bot))