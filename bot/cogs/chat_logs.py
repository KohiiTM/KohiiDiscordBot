import discord
from discord.ext import commands
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ChatLogs(commands.Cog):
    """Listener to log messages to either MongoDB or in-memory storage."""

    def __init__(self, bot):
        self.bot = bot
        self.use_mongodb = bot.use_mongodb
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        if self.use_mongodb:
            self.collection = self.bot.mongo_client["kohii"]["user_messages"]
        else:
            # Initialize in-memory storage if MongoDB is not available
            if "chat_logs" not in bot.in_memory_storage:
                bot.in_memory_storage["chat_logs"] = []

    def save_message(self, message_data: Dict[str, Any]) -> None:
        """Save a message to either MongoDB or in-memory storage."""
        if self.use_mongodb:
            # Insert message into MongoDB using executor
            def insert_message():
                self.collection.insert_one(message_data)
            self.executor.submit(insert_message)
        else:
            # Save to in-memory storage
            self.bot.in_memory_storage["chat_logs"].append(message_data)

    def get_user_messages(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user messages from either MongoDB or in-memory storage."""
        if self.use_mongodb:
            # Query MongoDB for user messages, sorted by timestamp
            return list(self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
        else:
            # Get from in-memory storage
            return sorted(
                [msg for msg in self.bot.in_memory_storage["chat_logs"] if msg["user_id"] == user_id],
                key=lambda x: x["timestamp"],
                reverse=True
            )[:limit]

    def search_messages(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search messages containing a keyword from either MongoDB or in-memory storage."""
        if self.use_mongodb:
            # Query MongoDB for messages containing the keyword
            return list(self.collection.find(
                {"content": {"$regex": keyword, "$options": "i"}}
            ).sort("timestamp", -1).limit(limit))
        else:
            # Search in-memory storage
            return sorted(
                [msg for msg in self.bot.in_memory_storage["chat_logs"] if keyword.lower() in msg["content"].lower()],
                key=lambda x: x["timestamp"],
                reverse=True
            )[:limit]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Log messages when they are sent."""
        if message.author.bot:
            return

        message_data = {
            "user_id": message.author.id,
            "username": str(message.author),
            "content": message.content,
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
            "timestamp": datetime.utcnow(),
            "guild_id": message.guild.id if message.guild else None,
            "guild_name": message.guild.name if message.guild else None
        }

        self.save_message(message_data)

    @commands.command(name="mylogs")
    async def my_logs(self, ctx, limit: int = 10):
        """View your recent messages."""
        messages = self.get_user_messages(ctx.author.id, limit)
        
        if not messages:
            await ctx.send("No messages found in your history.")
            return

        embed = discord.Embed(title=f"Your Recent Messages", color=discord.Color.blue())
        for msg in messages:
            embed.add_field(
                name=f"Channel: {msg['channel_name']}",
                value=f"{msg['content']}\n{msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="search")
    async def search(self, ctx, *, keyword: str):
        """Search for messages containing a keyword."""
        messages = self.search_messages(keyword)
        
        if not messages:
            await ctx.send(f"No messages found containing '{keyword}'.")
            return

        embed = discord.Embed(title=f"Search Results for '{keyword}'", color=discord.Color.green())
        for msg in messages:
            embed.add_field(
                name=f"From: {msg['username']} in {msg['channel_name']}",
                value=f"{msg['content']}\n{msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChatLogs(bot))
