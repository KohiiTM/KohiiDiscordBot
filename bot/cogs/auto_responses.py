import discord
from discord.ext import commands
import random
import re
import aiohttp
import os

class AutoResponses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tenor_api_key = os.getenv("TENOR_API_KEY")  # Store your API key in environment variables
        self.session = None
    
    async def cog_load(self):
        # Create an aiohttp session when the cog loads
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        # Close the session when the cog unloads
        if self.session:
            await self.session.close()

    async def get_random_gif(self, search_term, limit=10):
        """Fetch a random GIF related to the search term using Tenor API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        # Construct the Tenor API URL
        url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={self.tenor_api_key}&limit={limit}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    if results:
                        # Pick a random GIF from the results
                        random_gif = random.choice(results)
                        # Get the URL from the media formats
                        gif_url = random_gif["media_formats"]["gif"]["url"]
                        return gif_url
                    else:
                        return None
                else:
                    print(f"Error fetching GIF: {response.status}")
                    return None
        except Exception as e:
            print(f"Error in get_random_gif: {e}")
            return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        role_id = '1128759195202760854'
        role_mention = f'<@&{role_id}>'
        
        role_rivals = '1354559070199091200'
        rivals_mention = f'<@&{role_rivals}>'
        
        response_groups = {
            ("rivals", "marvel", rivals_mention): {
                "type": "gif",
                "search": "marvel rivals",
                "fallback": [
                    "https://tenor.com/view/groot-marvel-marvel-rivaks-ellunya-meme-gif-12648975181727081457",
                ]
            },
            ("val", "valorant", role_mention): {
                "type": "gif",
                "search": "valorant funny",
                "fallback": [
                    "https://tenor.com/view/choso-jjk-choso-choso-panic-insane-choso-anime-insane-gif-5693401929827560865",
                    "nah",
                    "https://tenor.com/view/valorant-nerd-brimstone-viper-omen-gif-9861738447246078182",
                ]
            },
            ("hello", "hi", "yo", "hey"): {
                "type": "gif",
                "search": "anime hello",
                "fallback": [
                    "wAZAAAAAAAAAAAAAA",
                    ":man_with_probing_cane::skin-tone-3:",
                    "https://tenor.com/view/anime-lolis-cute-dancing-girl-gif-25488979",
                ]
            },
            ("league", "league of legends", "lol"): {
                "type": "gif",
                "search": "league of legends funny",
                "fallback": [
                    "https://tenor.com/view/league-of-legends-gif-24451872",
                    "https://tenor.com/view/dog-run-away-scared-jump-out-window-dogs-gif-7549502188035868767",
                ]
            },
            ("1am",): {
                "type": "gif",
                "search": "druski dance",
                "fallback": [
                    "https://tenor.com/view/druski-kai-cenat-kevin-hart-dance-dancing-gif-5733905296005353973",
                ]
            },
            ("juice",): {
                "type": "gif",
                "search": "juice wrld dance",
                "fallback": [
                    "https://tenor.com/view/jw3-juice-wrld-2019-my-year-gif-14321242830957102561",
                ]
            },
        }

        content = message.content.lower()
        
        matching_group = None
        matching_keywords = None
        
        for keywords, response_data in response_groups.items():
            for keyword in keywords:
                if keyword == role_mention and keyword in message.content:
                    matching_group = response_data
                    matching_keywords = keywords
                    break
                
                elif keyword != role_mention:
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, content):
                        matching_group = response_data
                        matching_keywords = keywords
                        break
            
            if matching_group:
                break

        if matching_group:
            if matching_group["type"] == "gif" and self.tenor_api_key:
                search_term = matching_group["search"]
                gif_url = await self.get_random_gif(search_term)
                
                if gif_url:
                    await message.channel.send(gif_url)
                else:
                    response = random.choice(matching_group["fallback"])
                    await message.channel.send(response)
            else:
                response = random.choice(matching_group["fallback"])
                await message.channel.send(response)

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponses(bot))