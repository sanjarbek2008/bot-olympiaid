import aiosqlite
from typing import Optional, List, Dict, Any
from config.settings import settings
import random


class SQLiteManager:
    @staticmethod
    async def create_user(
            telegram_id: int,
            username: Optional[str] = None,
            first_name: Optional[str] = None,
            referred_by: Optional[int] = None
    ) -> bool:
        """Create a new user in the database"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO telegram_users 
                       (telegram_id, username, first_name, referred_by) 
                       VALUES (?, ?, ?, ?)""",
                    (telegram_id, username, first_name, referred_by)
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False  # User already exists

    @staticmethod
    async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram_id"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM telegram_users WHERE telegram_id = ?",
                (telegram_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def update_channel_status(telegram_id: int, joined: bool = True) -> bool:
        """Update user's channel joining status"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            await db.execute(
                "UPDATE telegram_users SET joined_channel = ? WHERE telegram_id = ?",
                (joined, telegram_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def add_referral_points(telegram_id: int, points: int) -> bool:
        """Add points to user for successful referral"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            await db.execute(
                "UPDATE telegram_users SET points = points + ? WHERE telegram_id = ?",
                (points, telegram_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def deduct_points_and_remove_referrals(telegram_id: int, points_to_deduct: int) -> bool:
        """Deduct points and randomly remove corresponding referrals"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            try:
                # Get current user points
                cursor = await db.execute(
                    "SELECT points FROM telegram_users WHERE telegram_id = ?",
                    (telegram_id,)
                )
                result = await cursor.fetchone()
                if not result or result[0] < points_to_deduct:
                    return False

                # Get referrals made by this user
                cursor = await db.execute(
                    "SELECT telegram_id FROM telegram_users WHERE referred_by = ? AND joined_channel = 1",
                    (telegram_id,)
                )
                referrals = await cursor.fetchall()

                # Calculate how many referrals to remove (assuming each referral = 10 points)
                referrals_to_remove = points_to_deduct // settings.referral_points

                if len(referrals) >= referrals_to_remove:
                    # Randomly select referrals to remove
                    to_remove = random.sample(referrals, referrals_to_remove)

                    # Remove selected referrals
                    # Unlink selected referrals (set referred_by to NULL)
                    for referral in to_remove:
                        await db.execute(
                            "UPDATE telegram_users SET referred_by = NULL WHERE telegram_id = ?",
                            (referral[0],)
                        )

                    # Deduct points
                    await db.execute(
                        "UPDATE telegram_users SET points = points - ? WHERE telegram_id = ?",
                        (points_to_deduct, telegram_id)
                    )

                    await db.commit()
                    return True
                else:
                    return False

            except Exception as e:
                await db.rollback()
                return False

    @staticmethod
    async def get_user_referrals(telegram_id: int) -> List[Dict[str, Any]]:
        """Get all users referred by this user"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT telegram_id, username, first_name, joined_channel, created_at 
                   FROM telegram_users WHERE referred_by = ?""",
                (telegram_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_all_users() -> List[int]:
        """Get all user telegram_ids for broadcasting"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute("SELECT telegram_id FROM telegram_users WHERE joined_channel = 1")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    @staticmethod
    async def user_exists(telegram_id: int) -> bool:
        """Check if user exists in database"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM telegram_users WHERE telegram_id = ?",
                (telegram_id,)
            )
            return await cursor.fetchone() is not None

    @staticmethod
    async def is_admin(telegram_id: int) -> bool:
        """Check if user is admin (you can modify this logic)"""
        # For now, we'll store admin IDs in settings
        # You can extend this to store in database if needed
        admin_ids = getattr(settings, 'admin_ids', [])
        return telegram_id in admin_ids

    # OLYMPIAD MANAGEMENT METHODS
    @staticmethod
    async def create_olympiad(
            olympiad_id: str,
            title: str,
            subject: str,
            date: str,
            link: str = None,
            registration_limit: int = None,
            price: int = 0
    ) -> bool:
        """Create a new olympiad in SQLite"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO olympiads 
                       (id, title, subject, date, link, registration_limit, price) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (olympiad_id, title, subject, date, link, registration_limit, price)
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False  # Olympiad with this ID already exists

    @staticmethod
    async def get_all_olympiads() -> List[Dict[str, Any]]:
        """Get all olympiads from SQLite"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM olympiads ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_olympiad_by_id(olympiad_id: str) -> Optional[Dict[str, Any]]:
        """Get specific olympiad by ID from SQLite"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM olympiads WHERE id = ?",
                (olympiad_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def delete_olympiad(olympiad_id: str) -> bool:
        """Delete olympiad from SQLite"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute(
                "DELETE FROM olympiads WHERE id = ?",
                (olympiad_id,)
            )
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def update_olympiad_price(olympiad_id: str, price: int) -> bool:
        """Update olympiad price"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute(
                "UPDATE olympiads SET price = ? WHERE id = ?",
                (price, olympiad_id)
            )
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def update_olympiad_limit(olympiad_id: str, limit: Optional[int]) -> bool:
        """Update olympiad registration limit"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute(
                "UPDATE olympiads SET registration_limit = ? WHERE id = ?",
                (limit, olympiad_id)
            )
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def update_user_referrer(telegram_id: int, referrer_id: int) -> bool:
        """Update user's referrer (for re-referrals)"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            await db.execute(
                "UPDATE telegram_users SET referred_by = ? WHERE telegram_id = ?",
                (referrer_id, telegram_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def set_user_language(telegram_id: int, language: str) -> bool:
        """Set user's language preference"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            await db.execute(
                "UPDATE telegram_users SET language = ? WHERE telegram_id = ?",
                (language, telegram_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def get_user_language(telegram_id: int) -> str:
        """Get user's language preference, default to 'en'"""
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            cursor = await db.execute(
                "SELECT language FROM telegram_users WHERE telegram_id = ?",
                (telegram_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 'en'