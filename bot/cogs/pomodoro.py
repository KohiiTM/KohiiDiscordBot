import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}  # Track active sessions

    @discord.app_commands.command(name="start", description="Start a new Pomodoro session.")
    async def start_pomodoro(self, interaction: discord.Interaction):
        """Start a new Pomodoro session."""
        user_id = interaction.user.id
        if user_id in self.active_sessions:
            await interaction.response.send_message("You already have an active Pomodoro session.", ephemeral=True)
            return

        collection = self.bot.mongo_client["kohii"]["pomodoro"]
        session = PomodoroSession(user_id, interaction.channel, collection)
        self.active_sessions[user_id] = session
        await interaction.response.send_message("Starting your Pomodoro session!", ephemeral=True)
        await session.start_work()

    @discord.app_commands.command(name="stop", description="Stop the current Pomodoro session.")
    async def stop_pomodoro(self, interaction: discord.Interaction):
        """Stop the Pomodoro session."""
        user_id = interaction.user.id
        if user_id not in self.active_sessions:
            await interaction.response.send_message("You don’t have an active Pomodoro session.", ephemeral=True)
            return

        session = self.active_sessions.pop(user_id)
        await session.stop()
        await interaction.response.send_message("Pomodoro session stopped and saved!", ephemeral=True)

    @discord.app_commands.command(name="skip", description="Skip the current Pomodoro phase.")
    async def skip_pomodoro(self, interaction: discord.Interaction):
        """Skip the current phase."""
        user_id = interaction.user.id
        if user_id not in self.active_sessions:
            await interaction.response.send_message("You don’t have an active Pomodoro session.", ephemeral=True)
            return

        session = self.active_sessions[user_id]
        await session.skip_phase()
        await interaction.response.send_message("Skipped to the next phase!", ephemeral=True)
        
    @discord.app_commands.command(name="session_history", description="View your Pomodoro session history.")
    async def session_history(self, interaction: discord.Interaction, limit: int = 5):
        """
        Command to display a user's Pomodoro session history.
        """
        user_id = interaction.user.id
        collection = self.bot.mongo_client["kohii"]["pomodoro"]

        # Query the database for the user's sessions, sorted by timestamp
        sessions = list(
            collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        )

        # Check if the user has any recorded sessions
        if not sessions:
            await interaction.response.send_message("No session history found for your account.", ephemeral=True)
            return

        # Build the response
        embed = discord.Embed(
            title="Pomodoro Session History",
            description=f"Here are your last {len(sessions)} Pomodoro sessions:",
            color=discord.Color.blue(),
        )

        for session in sessions:
            # Format the session data
            timestamp = session["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            work_sessions = session["work_sessions_completed"]
            embed.add_field(
                name=f"Session on {timestamp}",
                value=f"Work Sessions Completed: **{work_sessions}**",
                inline=False,
            )

        # Send the embed as a response
        await interaction.response.send_message(embed=embed, ephemeral=True)
        


class PomodoroSession:
    def __init__(self, user_id, channel, collection):
        self.user_id = user_id
        self.channel = channel
        self.collection = collection
        self.work_sessions_completed = 0
        self.is_running = False
        self.phase = "work"  # "work" or "break"
        self.timer_task = None

    async def start_work(self):
        """Start the work phase."""
        self.is_running = True
        await self.channel.send(f"<@{self.user_id}> Starting work session. Focus for 25 minutes!")
        self.timer_task = asyncio.create_task(self.run_timer(25 * 60))

    async def start_break(self, is_long_break=False):
        """Start the break phase."""
        self.phase = "break"
        duration = 15 * 60 if is_long_break else 5 * 60
        break_type = "long" if is_long_break else "short"
        await self.channel.send(f"<@{self.user_id}> Starting a {break_type} break for {duration // 60} minutes!")
        self.timer_task = asyncio.create_task(self.run_timer(duration))

    async def stop(self):
        """Stop the session and save to MongoDB."""
        self.is_running = False
        if self.timer_task:
            self.timer_task.cancel()
        await self.channel.send(f"<@{self.user_id}> Pomodoro session stopped.")

        # Save session to MongoDB
        session_data = {
            "user_id": self.user_id,
            "work_sessions_completed": self.work_sessions_completed,
            "timestamp": datetime.utcnow(),
        }
        try:
            self.collection.insert_one(session_data)
        except Exception as e:
            logger.error(f"Error saving session data to MongoDB: {e}")
            await self.channel.send("Failed to save session data. Please try again.")

    async def skip_phase(self):
        """Skip the current phase."""
        if self.timer_task:
            self.timer_task.cancel()
        if self.phase == "work":
            await self.start_break()
        else:
            await self.start_work()

    async def run_timer(self, duration):
        """Run the timer for the current phase."""
        try:
            while duration > 0:
                await asyncio.sleep(1)
                duration -= 1
            if self.phase == "work":
                self.work_sessions_completed += 1
                is_long_break = self.work_sessions_completed % 4 == 0
                await self.start_break(is_long_break=is_long_break)
            else:
                await self.start_work()
        except asyncio.CancelledError:
            pass


async def setup(bot):
    """Setup function to add the Pomodoro cog."""
    await bot.add_cog(Pomodoro(bot))
