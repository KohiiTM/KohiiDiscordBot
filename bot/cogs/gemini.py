import discord
from discord.ext import commands
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class Gemini(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API"))
        self.model = "gemini-2.5-flash-preview-05-20"
        self.model_display = "Gemini 2.5 Flash"
        
        # Define different response styles
        self.styles = {
            "default": "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
            "concise": "You are a concise AI assistant. Keep responses brief and to the point, using bullet points when possible.",
            "detailed": "You are a detailed AI assistant. Provide comprehensive explanations with examples and context.",
            "friendly": "You are a friendly AI assistant. Use a warm, conversational tone and include encouraging language.",
            "technical": "You are a technical AI assistant. Focus on technical accuracy and include relevant technical details.",
            "creative": "You are a creative AI assistant. Think outside the box and provide unique perspectives."
        }

    def split_response(self, text: str, max_length: int = 1900) -> list[str]:
        """Split a long response into chunks that fit within Discord's limits."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences to keep them intact
        sentences = text.split(". ")
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_length:
                current_chunk += sentence + ". "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    @discord.app_commands.command(name="ask_kohii", description="Dive into any topics you'd like to learn about")
    @discord.app_commands.describe(
        question="Your question or topic to explore",
        style="Response style (default, concise, detailed, friendly, technical, creative)"
    )
    async def gemini(
        self, 
        interaction: discord.Interaction, 
        question: str,
        style: str = "default"
    ):
        await interaction.response.defer()
        
        try:
            # Get the system prompt for the selected style
            system_prompt = self.styles.get(style.lower(), self.styles["default"])
            
            # Construct the full prompt
            full_prompt = f"{system_prompt}\n\nUser question: {question}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            # Format the response header
            header = f" **{self.model_display}** ({style.capitalize()})\n"
            header += f" **Question:** {question}\n\n"
            
            # Split response into chunks if needed
            response_chunks = self.split_response(response.text)
            
            # Send first chunk with header
            await interaction.followup.send(header + "**Answer:**\n" + response_chunks[0])
            
            # Send additional chunks if any
            for i, chunk in enumerate(response_chunks[1:], 2):
                await interaction.followup.send(f"**Answer (Part {i}):**\n{chunk}")
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gemini(bot)) 