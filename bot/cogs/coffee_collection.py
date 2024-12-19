import discord
from discord.ext import commands
from discord import app_commands
import random
from pymongo import MongoClient
import time
import io
import PIL
from PIL import Image
import requests
from io import BytesIO

# Define coffee cards with associated rarity and image URLs
coffee_cards = {
    "Espresso": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 1},
    "Cappuccino": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 2},
    "Latte": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 3},
    "Americano": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 6},
    "Mocha": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 7},
    "Flat White": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 8},
    "Cold Brew": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 9},
    "Turkish Coffee": {"rarity": "legendary", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 10},
    "Iced Latte": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 11},
    "Café au Lait": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 12},
    "Coffee Grinder": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 13},
    "Caffeine Boost": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 14},
    "Barista Kit": {"rarity": "legendary", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 15},
    "Coffee Bean": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 5},
    "Coffee Mug": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 16},
    "Siphon Brewer": {"rarity": "legendary", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 17},
    "French Press": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 18},
    # Add more mug variations
    "Ceramic Mug": {"rarity": "common", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 19},
    "Travel Mug": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 20},
    "Glass Mug": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 21},
    "Enamel Mug": {"rarity": "uncommon", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 22},
    "Personalized Mug": {"rarity": "rare", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 23},
    "Vintage Mug": {"rarity": "legendary", "image_url": "https://cdn.pixabay.com/photo/2021/06/18/10/39/mug-6345793_1280.jpg", "id": 24}
}

# Dictionary to track last command usage time for each user
user_cooldowns = {}
OWNER_ID = 696391065317408778

class CoffeeCollection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = bot.mongo_client
        self.db = self.mongo_client["coffee_bot"]
        self.user_collections = self.db["user_collections"]

    def load_user_collection(self, user_id):
        """Load or initialize the user's collection."""
        user = self.user_collections.find_one({"discord_id": str(user_id)})
        discord_name = user.get("discord_name", f"User_{user_id}") if user else None
        return user.get("cards", []) if user else [], discord_name

    def save_user_collection(self, user_id, collection, discord_name):
        """Save or update the user's collection."""
        user = self.user_collections.find_one({"discord_id": str(user_id)})
        if user:
            self.user_collections.update_one({"discord_id": str(user_id)}, {"$set": {"cards": collection, "discord_name": discord_name}})
        else:
            self.user_collections.insert_one({"discord_id": str(user_id), "discord_name": discord_name, "cards": collection})

    def rarity_to_color(self, rarity):
        """Return embed color based on rarity."""
        if rarity == "common":
            return discord.Color.green()
        elif rarity == "uncommon":
            return discord.Color.blue()
        elif rarity == "rare":
            return discord.Color.purple()
        elif rarity == "legendary":
            return discord.Color.gold()
        return discord.Color.default()

    def combine_images(self, card_images):
        """Combine card images into one image."""
        images = []
        for url in card_images:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            images.append(img)

        # Assuming we want to arrange images side by side in a row
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        # Create a new blank image to fit all card images
        new_img = Image.new('RGB', (total_width, max_height))

        # Paste each image into the new image
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

        # Save the combined image to a bytes buffer
        img_byte_arr = io.BytesIO()
        new_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return img_byte_arr

    @app_commands.command(name="collect", description="Collect a random pair of coffee-related cards!")
    async def collect(self, interaction: discord.Interaction):
        """Collect a random pair of coffee cards."""
        user_id = interaction.user.id
        current_time = time.time()

        # Check if the user has recently collected a card (Cooldown)
        if user_id != OWNER_ID and user_id in user_cooldowns and current_time - user_cooldowns[user_id] < 300:  # 5 minutes cooldown
            await interaction.response.send_message("You need to wait a bit before collecting again!", ephemeral=True)
            return

        # Collect two random cards
        card_1, card_2 = random.sample(list(coffee_cards.keys()), 2)
        card_1_details = coffee_cards[card_1]
        card_2_details = coffee_cards[card_2]

        # Combine images
        card_images = [card_1_details["image_url"], card_2_details["image_url"]]
        combined_image = self.combine_images(card_images)

        # Create embed for the collection
        embed = discord.Embed(title="You collected new cards!", description=f"You collected a {card_1} and {card_2}!", color=self.rarity_to_color(card_1_details["rarity"]))
        embed.set_image(url="attachment://combined_image.png")

        # Send the combined image
        await interaction.response.send_message(embed=embed, file=discord.File(combined_image, "combined_image.png"))

        # Update the user's last usage time to prevent another collection for 5 minutes
        user_cooldowns[user_id] = current_time


    @app_commands.command(name="my_cards", description="View your collected coffee cards.")
    async def my_cards(self, interaction: discord.Interaction):
        """View user's coffee card collection."""
        user_collection, discord_name = self.load_user_collection(interaction.user.id)
        if user_collection:
            await interaction.response.send_message(f"Your cards:\n{', '.join(user_collection)}")
        else:
            await interaction.response.send_message("You have no cards yet! Start collecting by using `/collect`.")

    @app_commands.command(name="trade", description="Trade a coffee card with another user.")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, card_to_trade: str):
        """Trade cards between users."""
        user_collection, target_user_collection = self.load_user_collection(interaction.user.id), self.load_user_collection(user.id)

        if card_to_trade not in user_collection:
            await interaction.response.send_message(f"You don't have the {card_to_trade} card to trade!")
            return

        # Trade cards
        user_collection.remove(card_to_trade)
        target_user_collection.append(card_to_trade)

        self.save_user_collection(interaction.user.id, user_collection, interaction.user.name)
        self.save_user_collection(user.id, target_user_collection, user.name)

        await interaction.response.send_message(f"Trade successful! You traded a {card_to_trade} card with {user.name}.")

    @app_commands.command(name="clear_collection", description="Clear all coffee cards from a user's collection (Owner only)")
    async def clear_collection(self, interaction: discord.Interaction, user: discord.User):
        """Clear a user's collection (Owner only)."""
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Clear the collection for the specified user
        self.save_user_collection(user.id, [], user.name)
        await interaction.response.send_message(f"Cleared {user.name}'s coffee card collection.", ephemeral=True)    
        
# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(CoffeeCollection(bot))
