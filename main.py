import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import settings
from config.database import init_sqlite_db
from config.migrations import run_migrations
from middleware.auth import AuthMiddleware

# Import routers
from handlers import start, channel, olympiads, referral, registration, admin


async def main():
    """Main function to run the bot"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize database
    await init_sqlite_db()
    logger.info("Database initialized")
    
    # Run migrations
    await run_migrations()
    logger.info("Migrations completed")

    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middleware (only for non-start commands)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(channel.router)
    dp.include_router(olympiads.router)
    dp.include_router(referral.router)
    dp.include_router(registration.router)
    dp.include_router(admin.router)

    logger.info("Bot starting...")
    logger.info(f"Admin IDs: {settings.admin_ids}")

    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())