from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.sqlite_manager import SQLiteManager
from utils.helpers import check_user_in_channel


class AuthMiddleware(BaseMiddleware):
    """Middleware to check user authentication and channel membership"""

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Skip auth check for start command (to handle referrals)
        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
            return await handler(event, data)

        # Check if user exists in database
        user = await SQLiteManager.get_user(user_id)
        if not user:
            if isinstance(event, CallbackQuery):
                await event.answer("Please start the bot first by sending /start", show_alert=True)
            else:
                await event.answer("Please start the bot by sending /start")
            return

        # Check if user has joined the channel
        if not user['joined_channel']:
            bot = data['bot']
            if not await check_user_in_channel(bot, user_id):
                if isinstance(event, CallbackQuery):
                    await event.answer("Please join our channel first!", show_alert=True)
                else:
                    await event.answer("Please join our channel first to use the bot!")
                return
            else:
                # User has joined, update database
                await SQLiteManager.update_channel_status(user_id, True)

        # Add user data to handler data
        data['user'] = user
        return await handler(event, data)