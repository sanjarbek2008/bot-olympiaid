from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from database.sqlite_manager import SQLiteManager
from keyboards.inline import channel_join_keyboard, main_menu_keyboard, language_selection_keyboard
from utils.helpers import extract_referrer_id, check_user_in_channel
from utils.states import UserStates
from utils.language_manager import LanguageManager
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

        # Show language selection for new users
        language_text = LanguageManager.get_text('language_selection', 'en')
        await message.answer(
            language_text,
            reply_markup=language_selection_keyboard()
        )
        await state.set_state(UserStates.selecting_language)


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
        user_language = await SQLiteManager.get_user_language(user_id)

        if await check_user_in_channel(message.bot, user_id):

            if not existing_user['joined_channel']:
                await SQLiteManager.update_channel_status(user_id, True)

            is_admin = await SQLiteManager.is_admin(user_id)

            welcome_text = LanguageManager.get_text('welcome_back', user_language, first_name=first_name)
            await message.answer(
                welcome_text,
                reply_markup=main_menu_keyboard(is_admin, language=user_language)
            )

            await state.set_state(UserStates.main_menu)

        else:

            join_text = LanguageManager.get_text('join_channel', user_language)
            await message.answer(
                join_text,
                reply_markup=channel_join_keyboard(settings.channel_invite_link, language=user_language)
            )

            await state.set_state(UserStates.waiting_for_channel_join)


@router.callback_query(F.data.startswith('lang_'))
async def language_selection_handler(query: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    
    # Extract language code from callback data
    language = query.data.split('_')[1]  # lang_en -> en
    
    # Save language preference
    await SQLiteManager.set_user_language(user_id, language)
    
    # Confirm language selection
    confirmation_text = LanguageManager.get_text('language_selected', language)
    await query.message.edit_text(confirmation_text)
    
    # Check if this is a new user or existing user changing language
    user = await SQLiteManager.get_user(user_id)
    if user and user['joined_channel']:
        # Existing user - show main menu
        is_admin = await SQLiteManager.is_admin(user_id)
        welcome_text = LanguageManager.get_text('welcome_back', language, first_name=first_name)
        await query.message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard(is_admin, language=language)
        )
        await state.set_state(UserStates.main_menu)
    else:
        # New user - show channel join
        welcome_text = LanguageManager.get_text('welcome', language, first_name=first_name)
        await query.message.answer(
            welcome_text,
            reply_markup=channel_join_keyboard(settings.channel_invite_link, language=language)
        )
        await state.set_state(UserStates.waiting_for_channel_join)
    
    await query.answer()


@router.callback_query(F.data == 'change_language')
async def change_language_handler(query: CallbackQuery, state: FSMContext):
    """Handle language change from main menu"""
    user_id = query.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    language_text = LanguageManager.get_text('language_selection', user_language)
    await query.message.edit_text(
        language_text,
        reply_markup=language_selection_keyboard()
    )
    await state.set_state(UserStates.selecting_language)
    await query.answer()