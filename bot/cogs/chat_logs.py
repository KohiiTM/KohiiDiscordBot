from discord.ext import commands
import discord

class ChatLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener to log messages to MongoDB.
        """
        # Ignore messages from bots
        if message.author.bot:
            return

        # Access MongoDB collection
        collection = self.bot.mongo_client["kohii"]["user_messages"]

        # Prepare message data
        message_data = {
            "user_id": message.author.id,
            "username": message.author.name,
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
        }

        # Insert message into MongoDB
        collection.insert_one(message_data)
        print(f"Logged message: {message_data}")

    @commands.command(name="view_logs", help="View chat logs for a specific user.")
    async def view_logs(self, ctx, user_id: int, limit: int = 10):
        """
        Command to view chat logs for a specific user.
        """
        # Access MongoDB collection
        collection = self.bot.mongo_client["kohii"]["user_messages"]

        # Query MongoDB for user messages, sorted by timestamp
        messages = collection.find({"user_id": user_id}).sort("timestamp", 1).limit(limit)

        # Check if any messages exist
        if messages.count() == 0:
            await ctx.send(f"No chat logs found for user ID: {user_id}.")
            return

        # Build a response string
        response = [f"**{msg['timestamp']}** - {msg['content']}" for msg in messages]
        await ctx.send(f"Chat logs for user ID `{user_id}` (up to {limit} messages):\n" + "\n".join(response))

    @commands.command(name="search_logs", help="Search chat logs by keyword.")
    async def search_logs(self, ctx, keyword: str, limit: int = 10):
        """
        Command to search chat logs for a specific keyword.
        """
        # Access MongoDB collection
        collection = self.bot.mongo_client["kohii"]["user_messages"]

        # Query MongoDB for messages containing the keyword
        messages = collection.find(
            {"content": {"$regex": keyword, "$options": "i"}}  # Case-insensitive search
        ).sort("timestamp", 1).limit(limit)

        # Check if any messages exist
        if messages.count() == 0:
            await ctx.send(f"No messages found containing the keyword: `{keyword}`.")
            return

        # Build a response string
        response = [f"**{msg['timestamp']}** - {msg['content']}" for msg in messages]
        await ctx.send(f"Messages containing `{keyword}` (up to {limit} messages):\n" + "\n".join(response))

    @commands.command(name="paginate_logs", help="Paginate user chat logs.")
    async def paginate_logs(self, ctx, user_id: int, page: int = 1, per_page: int = 10):
        """
        Command to paginate chat logs for a user.
        """
        # Access MongoDB collection
        collection = self.bot.mongo_client["kohii"]["user_messages"]

        # Calculate skip and limit
        skip = (page - 1) * per_page

        # Query MongoDB for user messages
        messages = collection.find({"user_id": user_id}).sort("timestamp", 1).skip(skip).limit(per_page)

        # Check if any messages exist
        if messages.count() == 0:
            await ctx.send(f"No messages found for user ID `{user_id}` on page {page}.")
            return

        # Build a response string
        response = [f"**{msg['timestamp']}** - {msg['content']}" for msg in messages]
        await ctx.send(
            f"Page {page} of chat logs for user ID `{user_id}` (up to {per_page} messages per page):\n"
            + "\n".join(response)
        )

async def setup(bot):
    """
    Setup function to add this cog to the bot.
    """
    await bot.add_cog(ChatLogs(bot))
