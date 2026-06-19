import discord
import time

from database import get_goon_xp, add_goon_xp

# CONFIG

GOON_PATH_ROLE_ID = 1405631400551645194

GOON_CHANNEL_IDS = [
    1405074443549671506,
    1517114760947040286
]

ATTAINMENT_RANKS = [
    ("Quasi Master", 100),
    ("Master", 2500),
    ("Quasi Grandmaster", 6000),
    ("Grandmaster", 12000),
    ("Quasi Great Grandmaster", 25000),
    ("Great Grandmaster", 50000),
    ("Quasi Supreme Grandmaster", 100000),
    ("Supreme Grandmaster", 500000)
]

# XP TRACKING

user_xp_tracker = {}

# RANK SYSTEM

def get_rank(xp):

    rank = "Ordinary"

    for rank_name, requirement in ATTAINMENT_RANKS:
        if xp >= requirement:
            rank = rank_name
        else:
            break

    return rank


def get_progress(xp):

    ranks = [("Ordinary", 0)] + ATTAINMENT_RANKS

    for i in range(len(ranks) - 1):

        current_name, current_xp = ranks[i]
        next_name, next_xp = ranks[i + 1]

        if xp < next_xp:

            progress = int(
                ((xp - current_xp) / (next_xp - current_xp)) * 100
            )

            return current_name, progress, next_name

    return "Supreme Grandmaster", 100, "MAX"


# ROLE MANAGEMENT

async def create_attainment_roles(guild):

    required_roles = [
        f"Goon Path - {rank}"
        for rank, _ in ATTAINMENT_RANKS
    ]

    existing_roles = {
        role.name
        for role in guild.roles
    }

    for role_name in required_roles:

        if role_name not in existing_roles:

            await guild.create_role(
                name=role_name,
                reason="Automatic attainment role creation"
            )


async def update_attainment_role(member):

    xp = get_goon_xp(member.id)

    rank = get_rank(xp)

    attainment_roles = {
        f"Goon Path - {rank_name}"
        for rank_name, _ in ATTAINMENT_RANKS
    }

    roles_to_remove = []

    for role in member.roles:

        if role.name in attainment_roles:
            roles_to_remove.append(role)

    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)

    if rank == "Ordinary":
        return

    role = discord.utils.get(
        member.guild.roles,
        name=f"Goon Path - {rank}"
    )

    if role:
        await member.add_roles(role)


# XP PROCESSING

async def process_goon_message(message):

    if message.author.bot:
        return

    if message.channel.id not in GOON_CHANNEL_IDS:
        return

    if not any(
        role.id == GOON_PATH_ROLE_ID
        for role in message.author.roles
    ):
        return

    if len(message.content.strip()) < 10:
        return

    user_id = message.author.id
    now = time.time()

    if user_id not in user_xp_tracker:

        user_xp_tracker[user_id] = {
            "window_start": now,
            "xp_gained": 0
        }

    user_data = user_xp_tracker[user_id]

    if now - user_data["window_start"] >= 60:

        user_data["window_start"] = now
        user_data["xp_gained"] = 0

    words = len(message.content.split())

    xp_to_give = 5 if words >= 20 else 1

    remaining_xp = 50 - user_data["xp_gained"]

    if remaining_xp <= 0:
        return

    xp_to_give = min(xp_to_give, remaining_xp)

    add_goon_xp(
        user_id,
        xp_to_give
    )

    user_data["xp_gained"] += xp_to_give

    await update_attainment_role(
        message.author
    )


# COMMAND HELPERS

def get_attainment_data(user_id):

    xp = get_goon_xp(user_id)

    rank = get_rank(xp)

    current_rank, progress, next_rank = get_progress(xp)

    return {
        "xp": xp,
        "rank": rank,
        "current_rank": current_rank,
        "progress": progress,
        "next_rank": next_rank
    }