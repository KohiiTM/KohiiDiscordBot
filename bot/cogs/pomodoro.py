import discord
from discord.ext import commands
from discord.ui import Button, View
from asyncio import sleep
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "your_mongo_uri_here"  # Replace with your MongoDB URI
DATABASE_NAME = "pomodoro_db"  # Replace with your database name
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
sessions_collection = db["sessions"]  # Replace with your collection name


class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.work_time = 25 * 60  # Default: 25 minutes
        self.short_break_time = 5 * 60  # Default: 5 minutes
        self.long_break_time = 15 * 60  # Default: 15 minutes
        self.cycles = 4  # Default: 4 cycles
        self.running = False  # To track if the timer is active
        self.completed_cycles = 0  # To track completed cycles
        self.total_work_time = 0  # To log total work time

    @discord.app_commands.command(name="pomodoro", description="Start a Pomodoro session with buttons.")
    async def pomodoro(self, interaction: discord.Interaction):
        """Starts the Pomodoro Timer with buttons."""
        if self.running:
            await interaction.response.send_message("A Pomodoro session is already running!", ephemeral=True)
            return

        self.running = True
        self.completed_cycles = 0
        self.total_work_time = 0

        # Start the interaction with a work phase
        await interaction.response.send_message(
            embed=self.create_embed("Pomodoro Timer", "Click Start to begin your session!", 0x00FF00),
            view=PomodoroView(self, interaction.user.id)
        )

    def create_embed(self, title, description, color):
        """Helper function to create an embed."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Pomodoro Timer Bot")
        return embed

    async def stop_pomodoro(self, user_id, interaction):
        """Stops the Pomodoro session and provides feedback."""
        self.running = False
        # Provide session feedback
        feedback_embed = self.create_embed(
            "Pomodoro Session Stopped",
            f"**Completed Work Cycles:** {self.completed_cycles}\n"
            f"**Total Work Time:** {self.total_work_time // 60} minutes",
            0xFF0000
        )
        await interaction.response.edit_message(embed=feedback_embed, view=None)

        # Save session data to MongoDB
        session_data = {
            "user_id": user_id,
            "completed_cycles": self.completed_cycles,
            "total_work_time": self.total_work_time // 60,  # Store in minutes
        }
        sessions_collection.insert_one(session_data)


class PomodoroView(View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_id = user_id
        self.phase = "work"  # Default phase
        self.cycle_count = 0  # Track completed cycles

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: Button):
        """Starts the Pomodoro Timer."""
        if not self.cog.running:
            await interaction.response.send_message("The Pomodoro session has been stopped.", ephemeral=True)
            return

        if self.phase == "work":
            await self.cog.start_timer(interaction, "Work Time", self.cog.work_time, "Focus on your tasks!")
            self.phase = "short_break"
            self.cog.total_work_time += self.cog.work_time
            self.cog.completed_cycles += 1
        elif self.phase == "short_break":
            await self.cog.start_timer(interaction, "Short Break", self.cog.short_break_time, "Take a short break!")
            self.cycle_count += 1
            if self.cycle_count >= self.cog.cycles:
                self.phase = "long_break"
            else:
                self.phase = "work"
        elif self.phase == "long_break":
            await self.cog.start_timer(interaction, "Long Break", self.cog.long_break_time, "Enjoy your long break!")
            self.phase = "work"  # Reset to work phase after long break
            self.cycle_count = 0  # Reset cycle count

        # Update buttons dynamically
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Stops the Pomodoro Timer."""
        await self.cog.stop_pomodoro(self.user_id, interaction)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """Skips the current phase."""
        if not self.cog.running:
            await interaction.response.send_message("The Pomodoro session is not running.", ephemeral=True)
            return

        if self.phase == "work":
            self.phase = "short_break"
        elif self.phase == "short_break":
            self.cycle_count += 1
            if self.cycle_count >= self.cog.cycles:
                self.phase = "long_break"
            else:
                self.phase = "work"
        elif self.phase == "long_break":
            self.phase = "work"
            self.cycle_count = 0  # Reset cycle count

        await interaction.response.edit_message(
            embed=self.cog.create_embed("Pomodoro Timer", f"Skipped to the next phase: {self.phase.replace('_', ' ').title()}.", 0x00FF00),
            view=self
        )


async def setup(bot):
    """Setup function to add the Pomodoro cog to the bot."""
    await bot.add_cog(Pomodoro(bot))
