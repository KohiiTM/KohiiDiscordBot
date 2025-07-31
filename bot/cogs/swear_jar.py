import discord
from discord.ext import commands
import re
import json
from typing import List, Dict, Any

# Global set to track processed messages across all instances
_processed_messages = set()

class SwearJar(commands.Cog):
    """Tracks swear word usage by users and stores counts locally."""
    
    def __init__(self, bot):
        self.bot = bot
        self.swear_words = self.load_swear_words()
        self.slur_words = self.load_slur_words()
        self.local_file_path = "swear_counts.json"
        self.load_local_counts()
        print("SwearJar: Cog initialized")
    
    def load_swear_words(self) -> List[str]:
        """Load swear words from swear_words.txt file."""
        try:
            with open("swear_words.txt", "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip()]
            print(f"SwearJar: Loaded {len(words)} swear words")
            return words
        except FileNotFoundError:
            print("SwearJar: swear_words.txt not found, using empty list")
            return []
    
    def load_slur_words(self) -> List[str]:
        """Load slur words from swear_words2.txt file."""
        try:
            with open("swear_words2.txt", "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip()]
            print(f"SwearJar: Loaded {len(words)} slur words")
            return words
        except FileNotFoundError:
            print("SwearJar: swear_words2.txt not found, using empty list")
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
    
    def count_swear_words(self, message: str) -> tuple:
        """Count swear words and slurs in a message. Returns (swear_count, slur_count)."""
        if not message.strip():
            return 0, 0
            
        message_lower = message.lower()
        swear_count = 0
        slur_count = 0
        
        # Count regular swear words
        for swear_word in self.swear_words:
            pattern = r'\b' + re.escape(swear_word) + r'\b'
            matches = len(re.findall(pattern, message_lower))
            swear_count += matches
        
        # Count slur words
        for slur_word in self.slur_words:
            pattern = r'\b' + re.escape(slur_word) + r'\b'
            matches = len(re.findall(pattern, message_lower))
            slur_count += matches
            
        return swear_count, slur_count
    
    def update_user_count(self, user_id: int, username: str, count: int):
        """Update swear count for a user in local storage."""
        user_id_str = str(user_id)
        
        if user_id_str not in self.local_counts:
            self.local_counts[user_id_str] = {"count": 0, "username": username}
        
        self.local_counts[user_id_str]["count"] += count
        self.local_counts[user_id_str]["username"] = username
        self.save_local_counts()
    
    def get_user_count(self, user_id: int) -> int:
        """Get swear count for a user from local storage."""
        return self.local_counts.get(str(user_id), {}).get("count", 0)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top swearers from local storage."""
        sorted_users = sorted(
            self.local_counts.items(),
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
    
    @commands.Cog.listener('on_message')
    async def handle_swear_detection(self, message: discord.Message):
        """Listen for messages and count swear words."""
        global _processed_messages
        
        # Skip bot messages
        if message.author.bot:
            return
        
        # Skip if already processed (global deduplication)
        if message.id in _processed_messages:
            print(f"SwearJar: Message {message.id} already processed, skipping")
            return
        
        # Mark as processed immediately
        _processed_messages.add(message.id)
        
        # Clean up old message IDs to prevent memory bloat
        if len(_processed_messages) > 1000:
            _processed_messages.clear()
            print("SwearJar: Cleared processed messages cache")
        
        # Count swear words
        swear_count, slur_count = self.count_swear_words(message.content)
        
        if swear_count > 0 or slur_count > 0:
            total_points = swear_count + (slur_count * 2)
            print(f"SwearJar: Processing message {message.id} - {swear_count} swears, {slur_count} slurs = {total_points} points")
            
            # Update user count
            self.update_user_count(message.author.id, str(message.author), total_points)
            
            # Get updated total
            new_total = self.get_user_count(message.author.id)
            
            # Send response
            try:
                await message.channel.send(f"+{total_points} added to {message.author.display_name}'s swear jar (Total: {new_total})")
                print(f"SwearJar: Successfully sent response for message {message.id}")
            except Exception as e:
                print(f"SwearJar: Error sending message: {e}")
    
    @discord.app_commands.command(name="swearcount", description="Check swear count for yourself or another user")
    async def swear_count(self, interaction: discord.Interaction, user: discord.Member = None):
        """Check swear count for yourself or another user."""
        target_user = user if user else interaction.user
        count = self.get_user_count(target_user.id)
        
        if count == 0:
            await interaction.response.send_message(f"{target_user.display_name} has a clean mouth! 😇")
        else:
            await interaction.response.send_message(f"{target_user.display_name} has used {count} swear word{'s' if count != 1 else ''} 🤬")
    
    @discord.app_commands.command(name="swearleaderboard", description="Show the top swearers")
    async def swear_leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        """Show the top swearers."""
        if limit > 20:
            limit = 20
        
        leaderboard = self.get_leaderboard(limit)
        
        if not leaderboard:
            await interaction.response.send_message("Everyone has clean mouths! 😇")
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
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="reloadswears", description="Reload the swear words list from file (admin only)")
    @discord.app_commands.default_permissions(administrator=True)
    async def reload_swears(self, interaction: discord.Interaction):
        """Reload the swear words list from file (admin only)."""
        old_swear_count = len(self.swear_words)
        old_slur_count = len(self.slur_words)
        self.swear_words = self.load_swear_words()
        self.slur_words = self.load_slur_words()
        new_swear_count = len(self.swear_words)
        new_slur_count = len(self.slur_words)
        
        await interaction.response.send_message(
            f"Reloaded word lists:\n"
            f"Swear words: {old_swear_count} → {new_swear_count}\n"
            f"Slur words: {old_slur_count} → {new_slur_count}"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(SwearJar(bot))