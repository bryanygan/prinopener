# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # enable reading message content

# Instantiate bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    # Only watch the designated channel
    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.lower().strip()
    # Exactly "open"
    if content == "open":
        await message.channel.edit(name="open🟢🟢")
    # Exactly "close" or "closed"
    elif content in ("close", "closed"):
        await message.channel.edit(name="closed🔴🔴")

    # Allow other commands to be processed
    await bot.process_commands(message)

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("❌ Missing DISCORD_TOKEN or TARGET_CHANNEL_ID in .env")
        exit(1)
    bot.run(TOKEN)