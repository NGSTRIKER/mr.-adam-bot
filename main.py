import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
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

bot.run(TOKEN)