
import sqlite3

conn = sqlite3.connect(
    "attainment.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attainment (
    user_id INTEGER PRIMARY KEY,
    goon_xp INTEGER DEFAULT 0
)
""")

conn.commit()


def ensure_user(user_id):

    cursor.execute(
        "INSERT OR IGNORE INTO attainment (user_id, goon_xp) VALUES (?, ?)",
        (user_id, 0)
    )

    conn.commit()


def get_goon_xp(user_id):

    ensure_user(user_id)

    cursor.execute(
        "SELECT goon_xp FROM attainment WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    return result[0]


def add_goon_xp(user_id, amount):

    ensure_user(user_id)

    cursor.execute(
        "UPDATE attainment SET goon_xp = goon_xp + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()