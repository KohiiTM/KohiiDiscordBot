import discord
from discord.ext import commands
from google import genai
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List

load_dotenv()

class Gemini(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API"))
        self.model = "gemini-2.5-flash-preview-05-20"
        self.model_display = "Gemini 2.5 Flash"
        self.active_sessions: Dict[int, bool] = {}  # Track active sessions by user ID
        self.conversation_history: Dict[int, List[str]] = {}  # Track conversation history by user ID
        
        # response styles
        self.styles = {
            "default": "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
            "concise": "You are a concise AI assistant. Keep responses brief and to the point, using bullet points when possible.",
            "detailed": "You are a detailed AI assistant. Provide comprehensive explanations with examples and context.",
            "friendly": "You are a friendly AI assistant. Use a warm, conversational tone and include encouraging language.",
            "technical": "You are a technical AI assistant. Focus on technical accuracy and include relevant technical details.",
            "creative": "You are a creative AI assistant. Think outside the box and provide unique perspectives."
        }

    def split_response(self, text: str, max_length: int = 1900) -> list[str]:
        # fit discord msg limits
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
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

    def get_conversation_context(self, user_id: int) -> str:
        """Get the conversation history for a user."""
        if user_id not in self.conversation_history:
            return ""
        
        # Get the last 5 exchanges to keep context manageable
        history = self.conversation_history[user_id][-10:]  # Last 5 Q&A pairs
        return "\n".join(history)

    def add_to_history(self, user_id: int, message: str, is_user: bool = True):
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        prefix = "User: " if is_user else "Assistant: "
        self.conversation_history[user_id].append(f"{prefix}{message}")

    @discord.app_commands.command(name="ask_kohii", description="Start a chat session with Kohii")
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
            system_prompt = self.styles.get(style.lower(), self.styles["default"])
            
            self.add_to_history(interaction.user.id, question)
            
            context = self.get_conversation_context(interaction.user.id)
            
            full_prompt = f"{system_prompt}\n\n"
            if context:
                full_prompt += f"Previous conversation:\n{context}\n\n"
            full_prompt += f"Current question: {question}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            self.add_to_history(interaction.user.id, response.text, is_user=False)
            
            self.active_sessions[interaction.user.id] = True
            
            header = f" **{self.model_display}** ({style.capitalize()})\n"
            header += f" **Question:** {question}\n\n"
            
            response_chunks = self.split_response(response.text)
            
            first_msg = header + "**Answer:**\n" + response_chunks[0]
            if len(first_msg) > 1900:
                await interaction.followup.send(header)
                await interaction.followup.send("**Answer:**\n" + response_chunks[0])
                await interaction.followup.send("*Chat session started. Type your next question or 'stop session' to end.*")
            else:
                await interaction.followup.send(first_msg)
                await interaction.followup.send("*Chat session started. Type your next question or 'stop session' to end.*")
            
            for i, chunk in enumerate(response_chunks[1:], 2):
                await interaction.followup.send(f"**Answer (Part {i}):**\n{chunk}")
                await interaction.followup.send("*Chat session started. Type your next question or 'stop session' to end.*")
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return

        if message.author.id in self.active_sessions and self.active_sessions[message.author.id]:
            if message.content.lower() == "stop session":
                self.active_sessions[message.author.id] = False
                if message.author.id in self.conversation_history:
                    del self.conversation_history[message.author.id]
                await message.channel.send("Chat session ended. Use `/ask_kohii` to start a new one")
                return

            try:
                thinking_msg = await message.channel.send("Pondering...")
                
                self.add_to_history(message.author.id, message.content)
                
                context = self.get_conversation_context(message.author.id)
                
                full_prompt = f"Previous conversation:\n{context}\n\nCurrent question: {message.content}"
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt
                )
                
                self.add_to_history(message.author.id, response.text, is_user=False)
                
                response_chunks = self.split_response(response.text)
                
                await thinking_msg.delete()
                
                for chunk in response_chunks:
                    await message.channel.send(chunk)
                    await message.channel.send("*Type your next question or 'stop session' to end.*")
                    
            except Exception as e:
                if 'thinking_msg' in locals():
                    await thinking_msg.delete()
                await message.channel.send(f"❌ Error: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gemini(bot)) 