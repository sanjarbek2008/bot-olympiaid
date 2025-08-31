from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.supabase_manager import SupabaseManager
from database.sqlite_manager import SQLiteManager
from keyboards.inline import olympiads_keyboard, olympiad_detail_keyboard, main_menu_keyboard
from utils.states import UserStates
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "view_olympiads")
async def show_olympiads(callback: CallbackQuery, state: FSMContext):
    """Show list of all olympiads from SQLite"""
    olympiads = await SQLiteManager.get_all_olympiads()

    if not olympiads:
        is_admin = await SQLiteManager.is_admin(callback.from_user.id)
        await callback.message.edit_text(
            "📝 No olympiads available at the moment.\n\n"
            "Please check back later!",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await callback.answer()
        return

    text = "🏆 **Available Olympiads**\n\n"
    text += "Choose an olympiad to learn more about it:"

    await callback.message.edit_text(
        text,
        reply_markup=olympiads_keyboard(olympiads),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.viewing_olympiads)
    await callback.answer()


@router.callback_query(F.data.startswith("olympiad_"))
async def show_olympiad_details(callback: CallbackQuery, state: FSMContext):
    """Show details of selected olympiad"""
    olympiad_id = callback.data.split("_")[1]
    olympiad = await SQLiteManager.get_olympiad_by_id(olympiad_id)

    if not olympiad:
        await callback.answer("Olympiad not found!", show_alert=True)
        return

    # Get current registrations count from Supabase
    current_registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad_id)
    user = await SQLiteManager.get_user(callback.from_user.id)

    text = f"🏆 **{olympiad['title']}**\n\n"
    text += f"📚 **Subject:** {olympiad['subject']}\n"
    text += f"📅 **Date:** {olympiad['date']}\n"

    if olympiad['price'] > 0:
        text += f"💰 **Price:** {olympiad['price']} points\n"
        text += f"💳 **Your Points:** {user['points']}\n"
    else:
        text += f"💰 **Price:** Free\n"

    if olympiad['registration_limit']:
        text += f"👥 **Registrations:** {current_registrations}/{olympiad['registration_limit']}\n"
    else:
        text += f"👥 **Registrations:** {current_registrations}\n"

    text += "\nWhat would you like to do?"

    await callback.message.edit_text(
        text,
        reply_markup=olympiad_detail_keyboard(olympiad_id, olympiad['price'], user['points']),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.olympiad_selected)
    await state.update_data(selected_olympiad=olympiad_id)
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    is_admin = await SQLiteManager.is_admin(callback.from_user.id)
    await callback.message.edit_text(
        "🏠 **Main Menu**\n\nWhat would you like to do?",
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.main_menu)
    await callback.answer()