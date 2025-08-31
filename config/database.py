import aiosqlite
from supabase import create_client, Client
from config.settings import settings


# Supabase client
def get_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# Initialize SQLite database
async def init_sqlite_db():
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        # Create telegram_users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telegram_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                referred_by BIGINT,
                points INTEGER DEFAULT 0,
                joined_channel BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referred_by) REFERENCES telegram_users(telegram_id)
            )
        """)

        # Create olympiads table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS olympiads (
                id TEXT PRIMARY KEY,  -- UUID from Supabase
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                date TEXT NOT NULL,
                link TEXT,
                registration_limit INTEGER,
                price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()