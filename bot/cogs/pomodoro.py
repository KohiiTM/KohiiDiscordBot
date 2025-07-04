import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.use_mongodb = bot.use_mongodb
        self.active_sessions: Dict[int, Dict[str, Any]] = {}  # Store active sessions in memory
        
        if self.use_mongodb:
            self.collection = self.bot.mongo_client["kohii"]["pomodoro"]
        else:
            if "pomodoro_sessions" not in bot.in_memory_storage:
                bot.in_memory_storage["pomodoro_sessions"] = {}

    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.use_mongodb:
            return self.collection.find_one({"user_id": user_id})
        else:
            return self.bot.in_memory_storage["pomodoro_sessions"].get(str(user_id))

    def save_session(self, user_id: int, session_data: Dict[str, Any]) -> None:
        if self.use_mongodb:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": session_data},
                upsert=True
            )
        else:
            self.bot.in_memory_storage["pomodoro_sessions"][str(user_id)] = session_data

    @commands.command(name="pomodoro")
    async def pomodoro(self, ctx, duration: int = 25):
        if ctx.author.id in self.active_sessions:
            await ctx.send("You already have an active pomodoro session!")
            return

        session_data = {
            "user_id": ctx.author.id,
            "start_time": datetime.utcnow(),
            "duration": duration,
            "status": "active"
        }

        self.save_session(ctx.author.id, session_data)
        self.active_sessions[ctx.author.id] = session_data

        message = await ctx.send(f"Pomodoro session started! Focus for {duration} minutes.")
        
        await asyncio.sleep(duration * 60)
        
        if ctx.author.id in self.active_sessions:
            await message.edit(content=f"Time's up! Take a 5-minute break, {ctx.author.mention}!")
            
            session_data["status"] = "completed"
            session_data["end_time"] = datetime.utcnow()
            self.save_session(ctx.author.id, session_data)
            del self.active_sessions[ctx.author.id]

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.author.id not in self.active_sessions:
            await ctx.send("You don't have an active pomodoro session!")
            return

        session_data = self.active_sessions[ctx.author.id]
        session_data["status"] = "stopped"
        session_data["end_time"] = datetime.utcnow()
        
        self.save_session(ctx.author.id, session_data)
        del self.active_sessions[ctx.author.id]
        
        await ctx.send("Pomodoro session stopped!")

    @discord.app_commands.command(name="session_history", description="View your Pomodoro session history.")
    async def session_history(self, interaction: discord.Interaction, limit: int = 5):
        user_id = interaction.user.id
        collection = self.bot.mongo_client["kohii"]["pomodoro"]

        sessions = list(
            collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        )

        if not sessions:
            await interaction.response.send_message("No session history found for your account.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Pomodoro Session History",
            description=f"Here are your last {len(sessions)} Pomodoro sessions:",
            color=discord.Color.blue(),
        )

        for session in sessions:
            timestamp = session["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            work_sessions = session["work_sessions_completed"]
            embed.add_field(
                name=f"Session on {timestamp}",
                value=f"Work Sessions Completed: **{work_sessions}**",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Pomodoro(bot))
