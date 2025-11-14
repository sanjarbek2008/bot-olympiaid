import aiosqlite
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


async def migrate_add_language_column():
    """Add language column to telegram_users table if it doesn't exist"""
    try:
        logger.info(f"Starting migration on database: {settings.sqlite_db_path}")
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            # Check if column exists
            cursor = await db.execute(
                "PRAGMA table_info(telegram_users)"
            )
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            logger.info(f"Existing columns: {column_names}")
            
            if 'language' not in column_names:
                logger.info("Adding 'language' column to telegram_users table...")
                await db.execute(
                    "ALTER TABLE telegram_users ADD COLUMN language VARCHAR(10) DEFAULT 'en'"
                )
                await db.commit()
                logger.info("✅ Successfully added 'language' column")
            else:
                logger.info("✅ 'language' column already exists")
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}", exc_info=True)
        raise


async def run_migrations():
    """Run all pending migrations"""
    await migrate_add_language_column()
