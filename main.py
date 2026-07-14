from collections import defaultdict
import time

import os
from selectors import SelectSelector

import discord
from discord.ext import commands
from dotenv import load_dotenv
from attainment_system import *
from database import (
    add_reaction_role,
    get_reaction_role
)


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# REACTION ROLE ADMINS

REACTION_ROLE_ADMINS = [

    123456789012345678,
    987654321098765432,
    1315201910814539859,
    908345530717970492,
    1391209201442881577,
    1338179914716942491

]
# REACTION ROLE EMOJIS

REACTION_ROLE_EMOJIS = [

    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",

    "🇦",
    "🇧",
    "🇨",
    "🇩",
    "🇪"

]

intents = discord.Intents.default()

intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

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
    description="View a user's attainments"
)
async def profile(
        interaction: discord.Interaction,
        user: discord.Member = None
):
    await interaction.response.defer()

    if user is None:
        user = interaction.user

    profile_data = get_profile_data(user.id)

    embed = discord.Embed(
        title=f"{user.display_name}'s Profile",
        color=discord.Color.blue()
    )

    if not profile_data:

        embed.description = "No attainments yet."

    else:

        for path in profile_data:
            embed.add_field(
                name=f"{path['path'].title()} Path",
                value=(
                    f"Rank: {path['rank']}\n"
                    f"XP: {path['xp']} / {path['required_xp']}\n"
                    f"Next: {path['next_rank']}"
                ),
                inline=False
            )

    await interaction.followup.send(
        embed=embed
    )


@bot.tree.command(
    name="attainment",
    description="View attainment in a specific path"
)
async def attainment(
        interaction: discord.Interaction,
        path: str,
        user: discord.Member
):
    path = path.lower()

    if path not in PATHS:
        await interaction.response.send_message(
            "Invalid path.",
            ephemeral=True
        )
        return

    data = get_attainment_data(
        user.id,
        path
    )

    embed = discord.Embed(
        title=f"{PATHS[path]['display_name']} Attainment",
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
        name="XP",
        value=f"{data['xp']} / {data['required_xp']}",
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


# MESSAGE XP HANDLER

@bot.event
async def on_message(message):
    await process_message(message)

    await bot.process_commands(message)


@bot.tree.command(
    name="leaderboard",
    description="View path leaderboard"
)
async def leaderboard(
        interaction: discord.Interaction,
        path: str
):
    path = path.lower()

    if path not in PATHS:
        await interaction.response.send_message(
            "Invalid path.",
            ephemeral=True
        )
        return

    leaderboard_data = get_path_leaderboard(
        path,
        10
    )

    embed = discord.Embed(
        title=f"🏆 {PATHS[path]['display_name']} Leaderboard",
        color=discord.Color.gold()
    )

    if not leaderboard_data:

        embed.description = "No data found."

    else:

        description = ""

        for position, (user_id, xp) in enumerate(
                leaderboard_data,
                start=1
        ):

            member = interaction.guild.get_member(user_id)

            if member is None:

                try:
                    member = await interaction.guild.fetch_member(user_id)
                except:
                    member = None

            if member:
                username = member.display_name
            else:
                username = f"Unknown User"

            description += (
                f"**#{position}** "
                f"{username} — {xp:,} XP\n"
            )

        embed.description = description

    await interaction.response.send_message(
        embed=embed
    )


@bot.tree.command(
    name="autorole",
    description="Create a reaction role message"
)
async def autorole(
        interaction: discord.Interaction,
        description: str,

        role1: discord.Role,
        role2: discord.Role = None,
        role3: discord.Role = None,
        role4: discord.Role = None,
        role5: discord.Role = None,
        role6: discord.Role = None,
        role7: discord.Role = None,
        role8: discord.Role = None,
        role9: discord.Role = None,
        role10: discord.Role = None,
        role11: discord.Role = None,
        role12: discord.Role = None,
        role13: discord.Role = None,
        role14: discord.Role = None,
        role15: discord.Role = None
):
    if interaction.user.id not in REACTION_ROLE_ADMINS:
        await interaction.response.send_message(
            "You cannot use this command.",
            ephemeral=True
        )

        return

    roles = [

        role1,
        role2,
        role3,
        role4,
        role5,
        role6,
        role7,
        role8,
        role9,
        role10,
        role11,
        role12,
        role13,
        role14,
        role15

    ]

    roles = [

        role
        for role in roles
        if role is not None

    ]

    embed = discord.Embed(
        title="Reaction Roles",
        description=description,
        color=discord.Color.blue()
    )

    text = ""

    for index, role in enumerate(roles):
        text += (
            f"{REACTION_ROLE_EMOJIS[index]} "
            f"{role.mention}\n"
        )

    embed.add_field(
        name="Roles",
        value=text,
        inline=False
    )

    await interaction.response.send_message(
        "Reaction role created.",
        ephemeral=True
    )

    message = await interaction.channel.send(
        embed=embed
    )

    for index, role in enumerate(roles):
        emoji = REACTION_ROLE_EMOJIS[index]

        await message.add_reaction(
            emoji
        )

        add_reaction_role(
            message.id,
            emoji,
            role.id
        )


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    data = get_reaction_role(
        payload.message_id,
        str(payload.emoji)
    )

    if not data:
        return

    guild = bot.get_guild(
        payload.guild_id
    )

    if guild is None:
        return

    member = guild.get_member(
        payload.user_id
    )

    if member is None:
        return

    role = guild.get_role(
        data[0]
    )

    if role:
        await member.add_roles(
            role
        )


@bot.event
async def on_raw_reaction_remove(payload):
    data = get_reaction_role(
        payload.message_id,
        str(payload.emoji)
    )

    if not data:
        return

    guild = bot.get_guild(
        payload.guild_id
    )

    if guild is None:
        return

    member = guild.get_member(
        payload.user_id
    )

    if member is None:
        return

    role = guild.get_role(
        data[0]
    )

    if role:
        await member.remove_roles(
            role
        )


bot.run(TOKEN)