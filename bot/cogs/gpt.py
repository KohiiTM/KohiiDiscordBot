import discord
from discord import app_commands
from discord.ext import commands
import openai
import os

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def query_openai(self, question: str) -> str:
        """Query OpenAI's GPT-3.5 Turbo for responses."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=150,  # Limit response length
            )
            return response.choices[0].message.content
        except openai.error.AuthenticationError:
            return "Error: Authentication failed. Please check your OpenAI API key."
        except openai.error.RateLimitError:
            return "Error: Rate limit exceeded. Please try again later."
        except openai.error.OpenAIError as e:
            return f"OpenAI API error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    @app_commands.command(name="ask", description="Ask the AI a question.")
    async def ask(self, interaction: discord.Interaction, question: str):
        """Slash command to ask a question."""
        await interaction.response.defer(thinking=True)  # Defer the response
        
        # Call the synchronous OpenAI query method in a separate thread
        response = await self.bot.loop.run_in_executor(None, self.query_openai, question)

        # Check if response is empty or an error
        if response.startswith("Error:"):
            await interaction.followup.send(response)  # Send error as a follow-up message
        else:
            await interaction.followup.send(f"**Q:** {question}\n**A:** {response}")

async def setup(bot: commands.Bot):
    """Setup function to add the cog to the bot."""
    await bot.add_cog(OpenAIBot(bot))
