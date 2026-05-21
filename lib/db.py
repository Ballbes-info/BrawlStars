"""
База данных SQLite для Brawl Stars Stats.
Единая для сайта и бота.
"""
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "brawlstats.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            selected_tag TEXT,
            psi REAL,
            psi_updated REAL,
            trophies INTEGER,
            created_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tag TEXT,
            player_name TEXT,
            psi REAL,
            trophies INTEGER,
            timestamp REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tag TEXT,
            player_name TEXT,
            psi REAL,
            trophies INTEGER,
            added_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tag TEXT,
            player_name TEXT,
            added_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            tag TEXT,
            active INTEGER DEFAULT 1,
            time_hour INTEGER DEFAULT 10
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            badge_name TEXT,
            earned_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            player_tag TEXT,
            player_name TEXT,
            psi REAL,
            collected_at REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_brawler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brawler_name TEXT,
            date TEXT UNIQUE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_feed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            tag TEXT,
            player_name TEXT,
            psi REAL,
            timestamp REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS player_psi (
            tag TEXT PRIMARY KEY,
            player_name TEXT,
            psi REAL,
            trophies INTEGER,
            updated_at REAL
        )
    """)

    conn.commit()
    conn.close()

# ─── Пользователи ───────────────────────────────────────────────────────────

def get_or_create_user(telegram_id: int, username: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (telegram_id, username, created_at) VALUES (?, ?, ?)",
                  (telegram_id, username, time.time()))
        conn.commit()
        c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = c.fetchone()
    elif username:
        c.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (username, telegram_id))
        conn.commit()
    conn.close()
    return dict(row) if row else None

def update_user_psi(telegram_id: int, tag: str, psi: float, trophies: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET selected_tag=?, psi=?, psi_updated=?, trophies=? WHERE telegram_id=?",
              (tag, psi, time.time(), trophies, telegram_id))
    conn.commit()
    conn.close()

def get_top_users(limit: int = 10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE psi IS NOT NULL ORDER BY psi DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── История поиска ─────────────────────────────────────────────────────────

def add_search(user_id: int, tag: str, player_name: str, psi: float, trophies: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO search_history (user_id, tag, player_name, psi, trophies, timestamp) VALUES (?,?,?,?,?,?)",
              (user_id, tag, player_name, psi, trophies, time.time()))
    conn.commit()
    conn.close()

def get_search_history(user_id: int, limit: int = 20):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM search_history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── Избранное ──────────────────────────────────────────────────────────────

def add_favorite(user_id: int, tag: str, player_name: str, psi: float, trophies: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM favorites WHERE user_id=? AND tag=?", (user_id, tag))
    if not c.fetchone():
        c.execute("INSERT INTO favorites (user_id, tag, player_name, psi, trophies, added_at) VALUES (?,?,?,?,?,?)",
                  (user_id, tag, player_name, psi, trophies, time.time()))
        conn.commit()
    conn.close()

def remove_favorite(user_id: int, tag: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE user_id=? AND tag=?", (user_id, tag))
    conn.commit()
    conn.close()

def get_favorites(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM favorites WHERE user_id=? ORDER BY added_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── Друзья ─────────────────────────────────────────────────────────────────

def add_friend(user_id: int, tag: str, player_name: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM friends WHERE user_id=? AND tag=?", (user_id, tag))
    if not c.fetchone():
        c.execute("INSERT INTO friends (user_id, tag, player_name, added_at) VALUES (?,?,?,?)",
                  (user_id, tag, player_name, time.time()))
        conn.commit()
    conn.close()

def remove_friend(user_id: int, tag: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM friends WHERE user_id=? AND tag=?", (user_id, tag))
    conn.commit()
    conn.close()

def get_friends(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM friends WHERE user_id=? ORDER BY added_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── Карточки ───────────────────────────────────────────────────────────────

def add_card(user_id: int, player_tag: str, player_name: str, psi: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO cards (user_id, player_tag, player_name, psi, collected_at) VALUES (?,?,?,?,?)",
              (user_id, player_tag, player_name, psi, time.time()))
    conn.commit()
    conn.close()

def get_cards(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE user_id=? ORDER BY collected_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_card_count(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM cards WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["count"] if row else 0

# ─── Бейджи ─────────────────────────────────────────────────────────────────

def add_badge(user_id: int, badge_name: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM badges WHERE user_id=? AND badge_name=?", (user_id, badge_name))
    if not c.fetchone():
        c.execute("INSERT INTO badges (user_id, badge_name, earned_at) VALUES (?,?,?)",
                  (user_id, badge_name, time.time()))
        conn.commit()
    conn.close()

def get_badges(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM badges WHERE user_id=?", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── Активность ─────────────────────────────────────────────────────────────

def add_activity(user_id: int, action: str, tag: str, player_name: str, psi: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO activity_feed (user_id, action, tag, player_name, psi, timestamp) VALUES (?,?,?,?,?,?)",
              (user_id, action, tag, player_name, psi, time.time()))
    conn.commit()
    conn.close()

def get_friends_activity(user_id: int, limit: int = 10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tag FROM friends WHERE user_id=?", (user_id,))
    friend_tags = [r["tag"] for r in c.fetchall()]
    if not friend_tags:
        conn.close()
        return []

    placeholders = ",".join("?" * len(friend_tags))
    c.execute(f"SELECT * FROM activity_feed WHERE tag IN ({placeholders}) ORDER BY timestamp DESC LIMIT ?",
              (*friend_tags, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── PSI игроков ─────────────────────────────────────────────────────────────

def save_player_psi(tag: str, player_name: str, psi: float, trophies: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO player_psi (tag, player_name, psi, trophies, updated_at) VALUES (?,?,?,?,?)",
              (tag, player_name, psi, trophies, time.time()))
    conn.commit()
    conn.close()

def get_top_player_psi(limit: int = 10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM player_psi ORDER BY psi DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ─── Инициализация ──────────────────────────────────────────────────────────

init_db()