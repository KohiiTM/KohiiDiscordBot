import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Dict, List, Any
import re
import os
import json

class SwearJar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.use_mongodb = getattr(bot, "use_mongodb", False)
        self.swear_words = self.load_swear_words()
        
        if self.use_mongodb and hasattr(bot, "mongo_client") and bot.mongo_client:
            self.collection = bot.mongo_client["kohii"]["swear_counts"]
        else:
            self.use_mongodb = False
            if "swear_counts" not in bot.in_memory_storage:
                bot.in_memory_storage["swear_counts"] = {}
                
        self.local_file_path = "swear_counts.json"
        self.load_local_counts()
    
    def load_swear_words(self) -> List[str]:
        try:
            with open("swear_words.txt", "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip()]
            return words
        except FileNotFoundError:
            return []
    
    def load_local_counts(self):
        try:
            with open(self.local_file_path, "r", encoding="utf-8") as f:
                self.local_counts = json.load(f)
        except FileNotFoundError:
            self.local_counts = {}
    
    def save_local_counts(self):
        with open(self.local_file_path, "w", encoding="utf-8") as f:
            json.dump(self.local_counts, f, indent=2)
    
    def count_swear_words(self, message: str) -> int:
        message_lower = message.lower()
        count = 0
        for swear_word in self.swear_words:
            pattern = r'\b' + re.escape(swear_word) + r'\b'
            matches = len(re.findall(pattern, message_lower))
            count += matches
        return count
    
    def update_user_count(self, user_id: int, username: str, count: int):
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
                self.bot.in_memory_storage["swear_counts"][user_id_str] = {"count": 0, "username": username}
            self.bot.in_memory_storage["swear_counts"][user_id_str]["count"] += count
            self.bot.in_memory_storage["swear_counts"][user_id_str]["username"] = username
        
        if user_id_str not in self.local_counts:
            self.local_counts[user_id_str] = {"count": 0, "username": username}
        self.local_counts[user_id_str]["count"] += count
        self.local_counts[user_id_str]["username"] = username
        self.save_local_counts()
    
    def get_user_count(self, user_id: int) -> int:
        return self.local_counts.get(str(user_id), {}).get("count", 0)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        sorted_users = sorted(
            [(user_id, data) for user_id, data in self.local_counts.items()],
            key=lambda x: x[1]["count"],
            reverse=True
        )
        return [
            {"user_id": int(user_id), "username": data["username"], "count": data["count"]}
            for user_id, data in sorted_users[:limit]
        ]
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        swear_count = self.count_swear_words(message.content)
        if swear_count > 0:
            self.update_user_count(message.author.id, str(message.author), swear_count)
            new_total = self.get_user_count(message.author.id)
            await message.channel.send(f"{message.author.display_name.lower()}, your swear jar count is now {new_total}.")

    # --- SLASH COMMANDS BELOW ---

    @app_commands.command(name="swearcount", description="Show your or another user's swear count.")
    async def swear_count(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user if user else interaction.user
        count = self.get_user_count(target_user.id)
        if count == 0:
            await interaction.response.send_message(f"{target_user.display_name} has a clean mouth! 😇")
        else:
            await interaction.response.send_message(f"{target_user.display_name} has used {count} swear word{'s' if count != 1 else ''} 🤬")

    @app_commands.command(name="swearleaderboard", description="Show the top swearers.")
    async def swear_leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        if limit > 20: limit = 20
        leaderboard = self.get_leaderboard(limit)
        if not leaderboard:
            await interaction.response.send_message("Everyone has clean mouths! 😇")
            return
        embed = discord.Embed(title="🤬 Swear Jar Leaderboard", color=discord.Color.red())
        for i, entry in enumerate(leaderboard, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.add_field(name=f"{emoji} {entry['username']}", value=f"{entry['count']} swear words", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reloadswears", description="Reload the swear words list (admin only).")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload_swears(self, interaction: discord.Interaction):
        old_count = len(self.swear_words)
        self.swear_words = self.load_swear_words()
        await interaction.response.send_message(f"Reloaded swear words list: {old_count} → {len(self.swear_words)} words")

    

async def setup(bot: commands.Bot):
    await bot.add_cog(SwearJar(bot))