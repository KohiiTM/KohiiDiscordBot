import discord
from discord.ext import commands
from datetime import datetime
from typing import Dict, List, Any
import re
import os
import json

class SwearJar(commands.Cog):
    """Tracks swear word usage by users and stores counts locally."""
    
    def __init__(self, bot):
        self.bot = bot
        self.use_mongodb = bot.use_mongodb
        self.swear_words = self.load_swear_words()
        
        if self.use_mongodb:
            self.collection = self.bot.mongo_client["kohii"]["swear_counts"]
        else:
            if "swear_counts" not in bot.in_memory_storage:
                bot.in_memory_storage["swear_counts"] = {}
                
        self.local_file_path = "swear_counts.json"
        self.load_local_counts()
    
    def load_swear_words(self) -> List[str]:
        """Load swear words from swear_words.txt file."""
        try:
            with open("swear_words.txt", "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip()]
            return words
        except FileNotFoundError:
            print("swear_words.txt not found, using empty list")
            return []
    
    def load_local_counts(self):
        """Load swear counts from local JSON file."""
        try:
            with open(self.local_file_path, "r", encoding="utf-8") as f:
                self.local_counts = json.load(f)
        except FileNotFoundError:
            self.local_counts = {}
    
    def save_local_counts(self):
        """Save swear counts to local JSON file."""
        with open(self.local_file_path, "w", encoding="utf-8") as f:
            json.dump(self.local_counts, f, indent=2)
    
    def count_swear_words(self, message: str) -> int:
        """Count the number of swear words in a message."""
        message_lower = message.lower()
        count = 0
        
        for swear_word in self.swear_words:
            pattern = r'\b' + re.escape(swear_word) + r'\b'
            matches = len(re.findall(pattern, message_lower))
            count += matches
            
        return count
    
    def update_user_count(self, user_id: int, username: str, count: int):
        """Update swear count for a user in both MongoDB and local storage."""
        user_id_str = str(user_id)
        
        if self.use_mongodb:
            self.collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"count": count},
                    "$set": {
                        "username": username,
                        "last_updated": datetime.utcnow()
                    }
                },
                upsert=True
            )
        else:
            if user_id_str not in self.bot.in_memory_storage["swear_counts"]:
                self.bot.in_memory_storage["swear_counts"][user_id_str] = {
                    "count": 0,
                    "username": username
                }
            self.bot.in_memory_storage["swear_counts"][user_id_str]["count"] += count
            self.bot.in_memory_storage["swear_counts"][user_id_str]["username"] = username
        
        if user_id_str not in self.local_counts:
            self.local_counts[user_id_str] = {
                "count": 0,
                "username": username
            }
        self.local_counts[user_id_str]["count"] += count
        self.local_counts[user_id_str]["username"] = username
        self.save_local_counts()
    
    def get_user_count(self, user_id: int) -> int:
        """Get swear count for a user from local storage."""
        user_id_str = str(user_id)
        return self.local_counts.get(user_id_str, {}).get("count", 0)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top swearers from local storage."""
        sorted_users = sorted(
            [(user_id, data) for user_id, data in self.local_counts.items()],
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        return [
            {
                "user_id": int(user_id),
                "username": data["username"],
                "count": data["count"]
            }
            for user_id, data in sorted_users[:limit]
        ]
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for messages and count swear words."""
        if message.author.bot:
            return
        
        swear_count = self.count_swear_words(message.content)
        
        if swear_count > 0:
            self.update_user_count(
                message.author.id,
                str(message.author),
                swear_count
            )
    
    @commands.command(name="swearcount")
    async def swear_count(self, ctx, user: discord.Member = None):
        """Check swear count for yourself or another user."""
        target_user = user if user else ctx.author
        count = self.get_user_count(target_user.id)
        
        if count == 0:
            await ctx.send(f"{target_user.display_name} has a clean mouth! 😇")
        else:
            await ctx.send(f"{target_user.display_name} has used {count} swear word{'s' if count != 1 else ''} 🤬")
    
    @commands.command(name="swearleaderboard", aliases=["swearboard"])
    async def swear_leaderboard(self, ctx, limit: int = 10):
        """Show the top swearers."""
        if limit > 20:
            limit = 20
        
        leaderboard = self.get_leaderboard(limit)
        
        if not leaderboard:
            await ctx.send("Everyone has clean mouths! 😇")
            return
        
        embed = discord.Embed(
            title="🤬 Swear Jar Leaderboard",
            description="Top swearers in the server",
            color=discord.Color.red()
        )
        
        for i, entry in enumerate(leaderboard, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.add_field(
                name=f"{emoji} {entry['username']}",
                value=f"{entry['count']} swear word{'s' if entry['count'] != 1 else ''}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="reloadswears")
    @commands.has_permissions(administrator=True)
    async def reload_swears(self, ctx):
        """Reload the swear words list from file (admin only)."""
        old_count = len(self.swear_words)
        self.swear_words = self.load_swear_words()
        new_count = len(self.swear_words)
        
        await ctx.send(f"Reloaded swear words list: {old_count} → {new_count} words")

async def setup(bot: commands.Bot):
    await bot.add_cog(SwearJar(bot))