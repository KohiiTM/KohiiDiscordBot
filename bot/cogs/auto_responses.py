import discord
from discord.ext import commands
import random
import re

class AutoResponses(commands.Cog):
    

    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # Define role ID
        role_id = '1128759195202760854'
        role_mention = f'<@&{role_id}>' 

       
        response_groups = {
            ("val", "valorant", role_mention): [
                "https://tenor.com/view/choso-jjk-choso-choso-panic-insane-choso-anime-insane-gif-5693401929827560865",
                "nah",
                "https://tenor.com/view/valorant-nerd-brimstone-viper-omen-gif-9861738447246078182",
                "RAHHHHHHHHH",
                "https://tenor.com/view/valorant-meme-valorant-valorant-sage-valorant-kms-bruh-moment-gif-24887517",
            ],
            ("hello", "hi", "yo", "hey"): [
                "wAZAAAAAAAAAAAAAA",
                ":man_with_probing_cane::skin-tone-3:",
                "https://tenor.com/view/anime-lolis-cute-dancing-girl-gif-25488979",
                "yo",
                "https://tenor.com/view/%E8%8F%8A%E5%9C%B0%E7%9C%9F-makoto-kikuchi-765production-cute-anime-gif-16341169",
            ],
            ("league", "league of legends", "lol", "league of legends"): [
                "https://tenor.com/view/league-of-legends-gif-24451872",
                "https://tenor.com/view/dog-run-away-scared-jump-out-window-dogs-gif-7549502188035868767",
            ],
            ("1am",): [ 
                "https://tenor.com/view/druski-kai-cenat-kevin-hart-dance-dancing-gif-5733905296005353973",
            ]
        }

        
        content = message.content.lower()
        
        
        matching_responses = None
        for keywords, possible_responses in response_groups.items():
            for keyword in keywords:
               
                if keyword == role_mention and keyword in message.content:
                    matching_responses = possible_responses
                    break
                
                
                elif keyword != role_mention:
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, content):
                        matching_responses = possible_responses
                        break
            
            
            if matching_responses:
                break

       
        if matching_responses:
            response = random.choice(matching_responses)
            await message.channel.send(response)

        
        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponses(bot))