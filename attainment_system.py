import discord
import time

from database import (
    get_path_xp,
    add_path_xp,
    get_all_path_xp
)

# PATH CONFIG
# Add role IDs and channel IDs yourself

PATHS = {
    "goon": {
        "display_name": "Goon Path",
        "role_id": 1405631400551645194,
        "channels": [
            1405074443549671506,
            1517114760947040286,
            1517114810104414308
        ]
    },

    "gaming": {
        "display_name": "Game Path",
        "role_id": 1405630919594872872,
        "channels": [1403715740196147280]
    },

    "debate": {
        "display_name": "Debate Path",
        "role_id": 1517871971981987921,
        "channels": []
    },

    "novel": {
        "display_name": "Novel Path",
        "role_id": 1517872875967877312,
        "channels": [1411764479833800865]
    },






}

# RANK CONFIG

ATTAINMENT_RANKS = [
    ("Quasi Master", 1075),
    ("Master", 4025),
    ("Quasi Grandmaster", 10100),
    ("Grandmaster", 36635),
    ("Quasi Great Grandmaster", 90650),
    ("Great Grandmaster", 182175),
    ("Quasi Supreme Grandmaster", 411650),
    ("Supreme Grandmaster", 640675)
]

# XP CONFIG

NORMAL_MESSAGE_XP = 1
LONG_MESSAGE_XP = 5

LONG_MESSAGE_WORDS = 20

XP_CAP_PER_MINUTE = 50

# XP TRACKING

# XP TRACKING

user_xp_tracker = {}
user_cooldowns = {}

# RANK FUNCTIONS

def get_rank(xp):

    rank = "Ordinary"

    for rank_name, requirement in ATTAINMENT_RANKS:

        if xp >= requirement:
            rank = rank_name
        else:
            break

    return rank


def get_progress_data(xp):

    ranks = [("Ordinary", 0)] + ATTAINMENT_RANKS

    for i in range(len(ranks) - 1):

        current_rank, current_requirement = ranks[i]
        next_rank, next_requirement = ranks[i + 1]

        if xp < next_requirement:

            return {
                "current_rank": current_rank,
                "next_rank": next_rank,
                "current_xp": xp,
                "required_xp": next_requirement
            }

    return {
        "current_rank": "Supreme Grandmaster",
        "next_rank": "MAX",
        "current_xp": xp,
        "required_xp": xp
    }

# ROLE CREATION

async def create_attainment_roles(guild):

    for path_data in PATHS.values():

        path_name = path_data["display_name"]

        for rank_name, _ in ATTAINMENT_RANKS:

            role_name = f"{path_name} - {rank_name}"

            role_exists = discord.utils.get(
                guild.roles,
                name=role_name
            )

            if not role_exists:

                await guild.create_role(
                    name=role_name,
                    reason="Automatic attainment role creation"
                )

# ROLE UPDATES

async def update_attainment_role(member, path_name):

    path_data = PATHS[path_name]

    xp = get_path_xp(
        member.id,
        path_name
    )

    rank = get_rank(xp)

    path_display = path_data["display_name"]

    path_attainment_roles = {

        f"{path_display} - {rank_name}"

        for rank_name, _ in ATTAINMENT_RANKS
    }

    roles_to_remove = []

    for role in member.roles:

        if role.name in path_attainment_roles:
            roles_to_remove.append(role)

    if roles_to_remove:

        await member.remove_roles(
            *roles_to_remove
        )

    if rank == "Ordinary":
        return

    role = discord.utils.get(
        member.guild.roles,
        name=f"{path_display} - {rank}"
    )

    if role:

        await member.add_roles(role)

# XP PROCESSING

async def process_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    current_time = time.time()
    if user_id in user_cooldowns:

        if current_time < user_cooldowns[user_id]:
            return

        del user_cooldowns[user_id]

    if user_id not in user_xp_tracker:

        user_xp_tracker[user_id] = {
            "window_start": current_time,
            "xp_gained": 0
        }

    user_data = user_xp_tracker[user_id]

    remaining_xp = XP_CAP_PER_MINUTE - user_data["xp_gained"]

    if remaining_xp <= 0:
        user_cooldowns[user_id] = current_time + 60

        user_data["xp_gained"] = 0

        return

    words = len(message.content.split())

    xp_to_give = (
        LONG_MESSAGE_XP
        if words >= LONG_MESSAGE_WORDS
        else NORMAL_MESSAGE_XP
    )

    xp_to_give = min(
        xp_to_give,
        remaining_xp
    )

    for path_name, path_data in PATHS.items():

        if message.channel.id not in path_data["channels"]:
            continue

        has_role = any(
            role.id == path_data["role_id"]
            for role in message.author.roles
        )

        if not has_role:
            continue

        add_path_xp(
            user_id,
            path_name,
            xp_to_give
        )

        user_data["xp_gained"] += xp_to_give
        if user_data["xp_gained"] >= XP_CAP_PER_MINUTE:
            user_cooldowns[user_id] = current_time + 60

            user_data["xp_gained"] = 0

        await update_attainment_role(
            message.author,
            path_name
        )

        break

# ATTAINMENT HELPER

def get_attainment_data(user_id, path_name):

    xp = get_path_xp(
        user_id,
        path_name
    )

    rank = get_rank(xp)

    progress = get_progress_data(xp)

    return {
        "path": path_name,
        "rank": rank,
        "xp": xp,
        "next_rank": progress["next_rank"],
        "required_xp": progress["required_xp"]
    }

# PROFILE HELPER

def get_profile_data(user_id):

    profile = []

    all_xp = get_all_path_xp(user_id)

    for path_name, xp in all_xp.items():

        if xp <= 0:
            continue

        rank = get_rank(xp)

        progress = get_progress_data(xp)

        profile.append({
            "path": path_name,
            "rank": rank,
            "xp": xp,
            "required_xp": progress["required_xp"],
            "next_rank": progress["next_rank"]
        })

    return profile