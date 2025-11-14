from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.supabase_manager import SupabaseManager
from database.sqlite_manager import SQLiteManager
from keyboards.inline import olympiads_keyboard, olympiad_detail_keyboard, main_menu_keyboard
from utils.states import UserStates
from utils.language_manager import LanguageManager
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "view_olympiads")
async def show_olympiads(callback: CallbackQuery, state: FSMContext):
    """Show list of all olympiads from SQLite"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    olympiads = await SQLiteManager.get_all_olympiads()

    if not olympiads:
        is_admin = await SQLiteManager.is_admin(user_id)
        no_olympiads_text = LanguageManager.get_text('olympiads.no_olympiads', user_language)
        await callback.message.edit_text(
            no_olympiads_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await callback.answer()
        return

    text = "🏆 " + LanguageManager.get_text('olympiads.title', user_language) + "\n\n"
    text += LanguageManager.get_text('olympiads.details', user_language)

    await callback.message.edit_text(
        text,
        reply_markup=olympiads_keyboard(olympiads, language=user_language),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.viewing_olympiads)
    await callback.answer()


@router.callback_query(F.data.startswith("olympiad_"))
async def show_olympiad_details(callback: CallbackQuery, state: FSMContext):
    """Show details of selected olympiad"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    olympiad_id = callback.data.split("_")[1]
    olympiad = await SQLiteManager.get_olympiad_by_id(olympiad_id)

    if not olympiad:
        error_text = LanguageManager.get_text('errors.invalid_input', user_language)
        await callback.answer(error_text, show_alert=True)
        return

    # Get current registrations count from Supabase
    current_registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad_id)
    user = await SQLiteManager.get_user(user_id)

    text = f"🏆 **{olympiad['title']}**\n\n"
    text += f"📚 {LanguageManager.get_text('olympiads.subject', user_language)}: {olympiad['subject']}\n"
    text += f"📅 {LanguageManager.get_text('olympiads.date', user_language)}: {olympiad['date']}\n"

    if olympiad['price'] > 0:
        text += f"💰 {LanguageManager.get_text('olympiads.price', user_language)}: {olympiad['price']} points\n"
        text += f"💳 Your Points: {user['points']}\n"
    else:
        text += f"💰 {LanguageManager.get_text('olympiads.price', user_language)}: {LanguageManager.get_text('olympiads.free', user_language)}\n"

    if olympiad['registration_limit']:
        text += f"👥 {LanguageManager.get_text('olympiads.registration_limit', user_language)}: {current_registrations}/{olympiad['registration_limit']}\n"
    else:
        text += f"👥 {LanguageManager.get_text('olympiads.registration_limit', user_language)}: {current_registrations}\n"

    text += "\n" + LanguageManager.get_text('olympiads.details', user_language)

    await callback.message.edit_text(
        text,
        reply_markup=olympiad_detail_keyboard(olympiad_id, olympiad['price'], user['points'], language=user_language),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.olympiad_selected)
    await state.update_data(selected_olympiad=olympiad_id)
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    is_admin = await SQLiteManager.is_admin(user_id)
    await callback.message.edit_text(
        "🏠 Main Menu\n\n" + LanguageManager.get_text('welcome_back', user_language, first_name=''),
        reply_markup=main_menu_keyboard(is_admin, language=user_language),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.main_menu)
    await callback.answer()