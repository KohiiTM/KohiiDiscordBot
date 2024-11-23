import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# Construct MongoDB URI
MONGO_URI = (
    f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@kohii.763qm.mongodb.net/"
    "?retryWrites=true&w=majority&appName=kohii"
)

# Initialize MongoDB client and database
mongo_client = MongoClient(MONGO_URI)

# Test the connection
try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True

# Set up the bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Attach MongoDB client to the bot
bot.mongo_client = mongo_client


# Graceful shutdown command
@bot.tree.command(name="shutdown", description="Gracefully shuts down the bot.")
async def shutdown(interaction: discord.Interaction):
    """Command to shut down the bot (restricted to bot owner)."""
    bot_owner_id = 696391065317408778  # Replace with your Discord user ID
    if interaction.user.id == bot_owner_id:
        await interaction.response.send_message("Shutting down the bot. Goodbye! 👋", ephemeral=True)
        await bot.close()  # Gracefully close the bot connection
    else:
        await interaction.response.send_message(
            "You do not have permission to shut down the bot.", ephemeral=True
        )

# Event: Triggered when the bot is ready
@bot.event
async def on_ready():
    """Log when the bot is ready and sync slash commands."""
    print(f"Logged in as {bot.user}! Bot is ready.")
    try:
        synced_commands = await bot.tree.sync()  # Sync slash commands with Discord API
        print(f"Successfully synced {len(synced_commands)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Event: Triggered when the bot disconnects
@bot.event
async def on_disconnect():
    """Close MongoDB connection when the bot disconnects."""
    mongo_client.close()
    print("MongoDB connection closed.")

# Load bot cogs
async def load_cogs():
    """Dynamically load bot cogs."""
    cog_list = [
        "cogs.ping",
        "cogs.pomodoro",
        "cogs.auto_responses",
        "cogs.chat_logs",
        "cogs.avatar",
        
    ]
    for cog in cog_list:
        try:
            await bot.load_extension(cog)
            print(f"Successfully loaded cog: {cog}")
        except Exception as e:
            print(f"Error loading cog {cog}: {e}")

# Main function to start the bot
async def main():
    """Main entry point to run the bot."""
    try:
        # Load cogs before starting the bot
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("Invalid token. Please check your DISCORD_TOKEN in the environment variables.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure MongoDB connection is closed on exit
        mongo_client.close()
        print("MongoDB connection closed on exit.")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
