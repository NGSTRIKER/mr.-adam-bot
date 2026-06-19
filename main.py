from collections import defaultdict
import time

import os
from selectors import SelectSelector

import discord
from discord.ext import commands
from dotenv import load_dotenv
from attainment_system import *
from attainment_system import get_attainment_data


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    guild = bot.get_guild(1398024265655128194)

    if guild:
        await create_attainment_roles(guild)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    print(f"bot Logged in as {bot.user}")

@bot.tree.command(
    name="quests",
    description="View all available quests"
)
async def quests(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📜 Alliance Quests",
        description="Complete quests to earn ACP.",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Standard quests",
        value=(
            "• Invite 1 Member — 80 ACP\n"
            "• Upload 1 EPUB — 20 ACP\n"

        ),
        inline=False
    )

    embed.add_field(
        name="Limited quests",
        value=(
            "• ---\n"
            "• ---"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)
@bot.tree.command(
    name="profile",
    description="View a user's profile"
)
async def profile(
    interaction: discord.Interaction,
    user: discord.Member = None
):

    if user is None:
        user = interaction.user

    data = get_attainment_data(user.id)

    embed = discord.Embed(
        title=f"{user.display_name}'s Profile",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Highest Attainment",
        value=data["rank"],
        inline=False
    )

    embed.add_field(
        name="Progress",
        value=f"{data['progress']}%",
        inline=True
    )

    embed.add_field(
        name="Next Rank",
        value=data["next_rank"],
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


@bot.tree.command(
    name="attainment",
    description="View Goon Path attainment"
)
async def attainment(
    interaction: discord.Interaction,
    user: discord.Member
):

    data = get_attainment_data(user.id)

    embed = discord.Embed(
        title="🍑 Goon Path Attainment",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Cultivator",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="Rank",
        value=data["rank"],
        inline=True
    )

    embed.add_field(
        name="Progress",
        value=f"{data['progress']}%",
        inline=True
    )

    embed.add_field(
        name="Next Rank",
        value=data["next_rank"],
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )
@bot.event
async def on_message(message):

    await process_goon_message(message)

    await bot.process_commands(message)

bot.run(TOKEN)