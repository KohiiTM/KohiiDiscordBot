import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
from typing import Optional, Dict, Any


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")


mongo_client: Optional[MongoClient] = None
use_mongodb = False

if MONGO_USERNAME and MONGO_PASSWORD:
    try:
        MONGO_URI = (
            f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@kohii.763qm.mongodb.net/"
            "?retryWrites=true&w=majority&appName=kohii"
        )
        mongo_client = MongoClient(MONGO_URI)
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        use_mongodb = True
    except Exception as e:
        print(f"Failed to connect to MongoDB, falling back to in-memory storage: {e}")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

bot.mongo_client = mongo_client
bot.use_mongodb = use_mongodb
bot.in_memory_storage = {}  

@bot.tree.command(name="shutdown", description="Gracefully shuts down the bot.")
async def shutdown(interaction: discord.Interaction):
    bot_owner_id = 696391065317408778  
    if interaction.user.id == bot_owner_id:
        await interaction.response.send_message("Shutting down the bot. Goodbye! 👋")
        await bot.close() 
    else:
        await interaction.response.send_message(
            "You do not have permission to shut down the bot.", ephemeral=True
        )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}! Bot is ready.")
    print(f"Using {'MongoDB' if use_mongodb else 'in-memory'} storage")
    try:
        synced_commands = await bot.tree.sync()  # Sync slash commands with Discord API
        print(f"Successfully synced {len(synced_commands)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_disconnect():
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")

async def load_cogs():
    cog_list = [
        "cogs.ping",
        "cogs.pomodoro",
        "cogs.auto_responses",
        "cogs.chat_logs",
        "cogs.avatar",
        "cogs.restart",
        "cogs.coffee_collection",
        "cogs.gemini",
        
    ]
    for cog in cog_list:
        try:
            await bot.load_extension(cog)
            print(f"Successfully loaded cog: {cog}")
        except Exception as e:
            print(f"Error loading cog {cog}: {e}")

async def main():
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("Invalid token. Please check your DISCORD_TOKEN in the environment variables.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if mongo_client:
            mongo_client.close()
            print("MongoDB connection closed on exit.")

if __name__ == "__main__":
    asyncio.run(main())