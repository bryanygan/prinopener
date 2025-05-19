# bot.py
import os
import time
from collections import deque

import discord
from discord.ext import commands
from discord.errors import HTTPException
from dotenv import load_dotenv

# load config
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

# keep track of rename timestamps (monotonic seconds)
# store all renames here and prune older than 600s
rename_history = deque()

# bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    content = message.content.lower().strip()
    if content == "open":
        new_name = "open🟢🟢"
    elif content in ("close", "closed"):
        new_name = "closed🔴🔴"
    else:
        await bot.process_commands(message)
        return

    now = time.monotonic()
    # remove entries older than 600 seconds
    while rename_history and now - rename_history[0] > 600:
        rename_history.popleft()

    if len(rename_history) >= 2:
        # our own rate-limit hit
        await message.channel.send(
            f"{message.author.mention} ⚠️ Rename limit reached (2 per 10 min). Try again later.",
            delete_after=10
        )
    else:
        try:
            await message.channel.edit(name=new_name)
        except HTTPException as e:
            await message.channel.send(
                f"{message.author.mention} ❌ Failed to rename channel: {e.status} {e.text}",
                delete_after=10
            )
        else:
            # record successful rename
            rename_history.append(now)

            # send notification
            if content == "open":
                # text + embed for opening
                await message.channel.send(
                    "ZR Eats is now OPEN! <@&1352022044614590494>"
                )
                embed = discord.Embed(
                    title="ZR Eats is now OPEN!",
                    description="We are now accepting orders! Click the order button in <#1350935337269985334> to place an order."
                )
                await message.channel.send(embed=embed)
            elif content in ("close", "closed"):
                # embed for closing
                embed = discord.Embed(
                    title="ZR Eats is now CLOSED.",
                    description="We are currently closed. Please come back later when we're open for new orders! Do not open a ticket, you will not get a response."
                )
                await message.channel.send(embed=embed)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("❌ Missing DISCORD_TOKEN or TARGET_CHANNEL_ID in .env")
        exit(1)
    bot.run(TOKEN)