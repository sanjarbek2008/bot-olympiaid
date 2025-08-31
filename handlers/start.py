from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from database.sqlite_manager import SQLiteManager
from keyboards.inline import channel_join_keyboard, main_menu_keyboard
from utils.helpers import extract_referrer_id, check_user_in_channel
from utils.states import UserStates
from config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command with referral support"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Extract referrer from start parameter
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
        referrer_id = extract_referrer_id(start_param)

    # Check if user already exists
    existing_user = await SQLiteManager.get_user(user_id)


    if not existing_user:
        # Create new user
        success = await SQLiteManager.create_user(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
            referred_by=referrer_id
        )

        if success and referrer_id:
            logger.info(f"New user {user_id} referred by {referrer_id}")

        welcome_text = f"👋 Welcome {first_name}!\n\n"
        welcome_text += "To start using our Olympiad Registration Bot, please join our official channel first."

        await message.answer(
            welcome_text,
            reply_markup=channel_join_keyboard(settings.channel_invite_link)
        )
        await state.set_state(UserStates.waiting_for_channel_join)


    else:

        # Existing user - handle re-referral first

        if referrer_id:

            current_referrer = existing_user['referred_by']

            # If user has no current referrer OR has a different referrer

            if not current_referrer or current_referrer != referrer_id:

                # Update referrer

                await SQLiteManager.update_user_referrer(user_id, referrer_id)

                logger.info(f"User {user_id} re-referred by {referrer_id}")

                # If user already joined channel, give points immediately

                if existing_user['joined_channel'] or await check_user_in_channel(message.bot, user_id):
                    await SQLiteManager.add_referral_points(referrer_id, settings.referral_points)

                    logger.info(f"Immediate points given to {referrer_id} for re-referring {user_id}")

        # Existing user - check channel membership

        if await check_user_in_channel(message.bot, user_id):

            if not existing_user['joined_channel']:
                await SQLiteManager.update_channel_status(user_id, True)

            is_admin = await SQLiteManager.is_admin(user_id)

            await message.answer(

                f"Welcome back, {first_name}! 🎉\n\nWhat would you like to do?",

                reply_markup=main_menu_keyboard(is_admin)

            )

            await state.set_state(UserStates.main_menu)

        else:

            await message.answer(

                "Please join our channel to continue using the bot:",

                reply_markup=channel_join_keyboard(settings.channel_invite_link)

            )

            await state.set_state(UserStates.waiting_for_channel_join)