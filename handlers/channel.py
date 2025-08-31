from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.sqlite_manager import SQLiteManager
from keyboards.inline import main_menu_keyboard
from utils.helpers import check_user_in_channel
from utils.states import UserStates
from config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "check_joined")
async def check_channel_membership(callback: CallbackQuery, state: FSMContext):
    """Check if user has joined the channel"""
    user_id = callback.from_user.id

    if await check_user_in_channel(callback.bot, user_id):
        # User has joined the channel
        await SQLiteManager.update_channel_status(user_id, True)

        # Check if this user was referred by someone
        user = await SQLiteManager.get_user(user_id)
        if user and user['referred_by']:
            # Give points to the referrer
            await SQLiteManager.add_referral_points(user['referred_by'], settings.referral_points)
            logger.info(f"Gave {settings.referral_points} points to user {user['referred_by']} for referring {user_id}")

        is_admin = await SQLiteManager.is_admin(user_id)
        await callback.message.edit_text(
            "🎉 Great! You've successfully joined our channel.\n\n"
            "Now you can access all bot features. What would you like to do?",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.set_state(UserStates.main_menu)
        await callback.answer("Welcome! Channel membership verified ✅")

    else:
        await callback.answer(
            "❌ You haven't joined our channel yet. Please join first!",
            show_alert=True
        )