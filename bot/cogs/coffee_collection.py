import discord
from discord.ext import commands
from discord import app_commands
import random
from pymongo import MongoClient

# Define your coffee cards with the test image URL
coffee_cards = {
    "Espresso": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 1},
    "Cappuccino": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 2},
    "Latte": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 3},
    "Mug": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 4},
    "Coffee Bean": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 5},
}

class CoffeeCollection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = bot.mongo_client
        self.db = self.mongo_client["coffee_bot"]
        self.user_collections = self.db["user_collections"]

    # Function to load a user's collection from MongoDB
    def load_user_collection(self, user_id):
        user = self.user_collections.find_one({"discord_id": str(user_id)})
        if user:
            return user["cards"]
        return []

    # Function to save or update a user's collection
    def save_user_collection(self, user_id, collection):
        user = self.user_collections.find_one({"discord_id": str(user_id)})
        if user:
            # Update existing user's collection
            self.user_collections.update_one({"discord_id": str(user_id)}, {"$set": {"cards": collection}})
        else:
            # Create new document for user
            self.user_collections.insert_one({"discord_id": str(user_id), "cards": collection})

    # Slash command to collect a coffee card with a cooldown
    @app_commands.command(name="collect", description="Collect a pair of coffee-related cards!")
    @commands.cooldown(1, 300, commands.BucketType.user)  # 1 use per 300 seconds (5 minutes) per user
    async def collect(self, interaction: discord.Interaction):
        # Randomly choose one card from the coffee-related cards
        card_1 = random.choice([key for key in coffee_cards.keys() if key != "Mug" and key != "Coffee Bean"])
        card_2 = random.choice([key for key in coffee_cards.keys() if key == "Mug" or key == "Coffee Bean"])

        # Load user's collection and append the new cards
        user_collection = self.load_user_collection(interaction.user.id)
        user_collection.append(card_1)
        user_collection.append(card_2)
        self.save_user_collection(interaction.user.id, user_collection)

        # Get card details
        card_1_details = coffee_cards[card_1]
        card_2_details = coffee_cards[card_2]

        # Create embed with images
        embed = discord.Embed(title=f"{interaction.user.name} has collected new cards!", color=discord.Color.blue())

        # Add both cards to the embed
        embed.add_field(
            name=card_1,
            value=f"Rarity: {card_1_details['rarity']}",
            inline=False
        )
        embed.set_image(url=card_1_details['image_url'])

        embed.add_field(
            name=card_2,
            value=f"Rarity: {card_2_details['rarity']}",
            inline=False
        )
        embed.set_image(url=card_2_details['image_url'])

        # Send the embed with the collected cards
        await interaction.response.send_message(embed=embed)

    # Slash command to view a user's cards
    @app_commands.command(name="my_cards", description="View your collected coffee cards.")
    async def my_cards(self, interaction: discord.Interaction):
        user_collection = self.load_user_collection(interaction.user.id)
        
        if not user_collection:
            await interaction.response.send_message("You have no cards yet! Start collecting by using the `/collect` command.")
        else:
            collection_list = "\n".join(user_collection)
            await interaction.response.send_message(f"Your cards: \n{collection_list}")

    # Slash command to trade cards with another user
    @app_commands.command(name="trade", description="Trade a coffee card with another user.")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, card_to_trade: str):
        user_collection = self.load_user_collection(interaction.user.id)
        target_user_collection = self.load_user_collection(user.id)

        if card_to_trade not in user_collection:
            await interaction.response.send_message(f"You don't have the {card_to_trade} card to trade!")
            return
        
        # Remove the card from the user's collection and add it to the target user's collection
        user_collection.remove(card_to_trade)
        target_user_collection.append(card_to_trade)
        
        # Save the updated collections
        self.save_user_collection(interaction.user.id, user_collection)
        self.save_user_collection(user.id, target_user_collection)
        
        await interaction.response.send_message(f"Trade successful! You traded a {card_to_trade} card with {user.name}.")

# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(CoffeeCollection(bot))
