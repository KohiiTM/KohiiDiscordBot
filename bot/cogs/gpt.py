import discord
from discord.ext import commands
from discord import app_commands
import openai
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class GPT4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="askgpt", 
        description="Ask GPT-4 a question and get a response."
    )
    async def ask_gpt(self, interaction: discord.Interaction):
        """
        Slash command to interact with GPT-4.
        Allows multi-line input and handles long responses.
        """
        await interaction.response.send_message(
            "Please type your question or prompt below. You can use multiple lines. Type `done` when you're finished."
        )

        def check(message: discord.Message):
            return message.author == interaction.user and message.channel == interaction.channel

        prompt = []
        while True:
            try:
                message = await self.bot.wait_for("message", timeout=300.0, check=check)
                if message.content.lower() == "done":
                    break
                prompt.append(message.content)
            except asyncio.TimeoutError:
                await interaction.followup.send("You took too long to respond. Please try again.")
                return

        full_prompt = "\n".join(prompt)

        try:
            # Sending the collected prompt to GPT-4
            response = openai.ChatCompletion.create(
                model="chatgpt-4o-latest",  # Use the requested model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": full_prompt},
                ],
                max_tokens=2048,  # Increase token limit for longer responses
                temperature=0.7,
            )

            reply = response['choices'][0]['message']['content']

            # Split the response into chunks if it's too long for a single Discord message
            if len(reply) > 2000:
                for chunk in [reply[i:i + 2000] for i in range(0, len(reply), 2000)]:
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(reply)

        except openai.error.OpenAIError as e:
            await interaction.followup.send(f"Error communicating with OpenAI: {e}")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(GPT4Cog(bot))
