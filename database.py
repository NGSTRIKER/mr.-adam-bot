import sqlite3

# DATABASE CONNECTION

conn = sqlite3.connect(
    "attainment.db",
    check_same_thread=False
)

cursor = conn.cursor()

# TABLE SETUP

cursor.execute("""
               CREATE TABLE IF NOT EXISTS attainment
               (
                   user_id
                   INTEGER
                   PRIMARY
                   KEY,

                   goon_xp
                   INTEGER
                   DEFAULT
                   0,
                   gaming_xp
                   INTEGER
                   DEFAULT
                   0,
                   debate_xp
                   INTEGER
                   DEFAULT
                   0,
                   novel_xp
                   INTEGER
                   DEFAULT
                   0

               )
               """)

conn.commit()


# USER SETUP

def ensure_user(user_id):
    cursor.execute(
        """
        INSERT
        OR IGNORE INTO attainment (
            user_id
        )
        VALUES (?)
        """,
        (user_id,)
    )

    conn.commit()


# XP GETTERS

def get_path_xp(user_id, path):
    ensure_user(user_id)

    cursor.execute(
        f"SELECT {path}_xp FROM attainment WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return 0


# XP ADDERS

def add_path_xp(user_id, path, amount):
    ensure_user(user_id)

    cursor.execute(
        f"""
        UPDATE attainment
        SET {path}_xp = {path}_xp + ?
        WHERE user_id = ?
        """,
        (amount, user_id)
    )

    conn.commit()


# XP SETTERS

def set_path_xp(user_id, path, amount):
    ensure_user(user_id)

    cursor.execute(
        f"""
        UPDATE attainment
        SET {path}_xp = ?
        WHERE user_id = ?
        """,
        (amount, user_id)
    )

    conn.commit()


# PROFILE DATA

def get_all_path_xp(user_id):
    ensure_user(user_id)

    cursor.execute(
        """
        SELECT goon_xp,
               gaming_xp,
               debate_xp,
               novel_xp

        FROM attainment
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    return {
        "goon": result[0],
        "gaming": result[1],
        "debate": result[2],
        "novel": result[3]

    }



# LEADERBOARD DATA

def get_path_leaderboard(path, limit=10):

    cursor.execute(
        f"""
        SELECT
            user_id,
            {path}_xp
        FROM attainment
        ORDER BY {path}_xp DESC
        LIMIT ?
        """,
        (limit,)
    )

    return cursor.fetchall()