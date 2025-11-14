from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.sqlite_manager import SQLiteManager
from keyboards.inline import back_to_menu_keyboard, main_menu_keyboard
from utils.helpers import create_referral_link
from utils.language_manager import LanguageManager
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "invite_friends")
async def show_referral_info(callback: CallbackQuery, state: FSMContext):
    """Show referral link and statistics"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    bot_info = await callback.bot.get_me()

    # Get user's referral statistics
    user = await SQLiteManager.get_user(user_id)
    referrals = await SQLiteManager.get_user_referrals(user_id)

    # Generate referral link
    referral_link = create_referral_link(user_id, bot_info.username)

    text = LanguageManager.get_text('referral.title', user_language) + "\n\n"
    text += f"🎯 {LanguageManager.get_text('referral.points', user_language, points=user['points'])}\n"
    text += f"👥 {LanguageManager.get_text('referral.referrals_count', user_language, count=len(referrals))}\n\n"
    text += f"🔗 {LanguageManager.get_text('referral.your_link', user_language)}:\n`{referral_link}`\n\n"
    text += LanguageManager.get_text('referral.copy_link', user_language)

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(language=user_language),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("invite_for_"))
async def invite_for_olympiad(callback: CallbackQuery, state: FSMContext):
    """Generate referral link specifically for an olympiad"""
    olympiad_id = callback.data.split("_")[2]
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    bot_info = await callback.bot.get_me()

    # Get user's referral statistics
    user = await SQLiteManager.get_user(user_id)
    referrals = await SQLiteManager.get_user_referrals(user_id)

    # Generate referral link
    referral_link = create_referral_link(user_id, bot_info.username)

    text = "👥 " + LanguageManager.get_text('referral.title', user_language) + "\n\n"
    text += f"📊 {LanguageManager.get_text('referral.stats', user_language)}:\n"
    text += f"• {LanguageManager.get_text('referral.points', user_language, points=user['points'])}\n"
    text += f"• {LanguageManager.get_text('referral.referrals_count', user_language, count=len(referrals))}\n\n"
    text += f"🔗 {LanguageManager.get_text('referral.your_link', user_language)}:\n`{referral_link}`\n\n"
    text += LanguageManager.get_text('referral.copy_link', user_language)

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(language=user_language),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def show_user_stats(callback: CallbackQuery, state: FSMContext):
    """Show user's referral statistics"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)

    user = await SQLiteManager.get_user(user_id)
    referrals = await SQLiteManager.get_user_referrals(user_id)

    # Count successful referrals (those who joined the channel)
    successful_referrals = [r for r in referrals if r['joined_channel']]

    text = LanguageManager.get_text('referral.stats', user_language) + "\n\n"
    text += f"🎯 {LanguageManager.get_text('referral.points', user_language, points=user['points'])}\n"
    text += f"👥 {LanguageManager.get_text('referral.referrals_count', user_language, count=len(referrals))}\n"
    text += f"✅ Successful Referrals: {len(successful_referrals)}\n"
    text += f"📅 Member Since: {user['created_at'][:10]}\n\n"

    if successful_referrals:
        text += "🏆 Your Successful Referrals:\n"
        for ref in successful_referrals[:5]:  # Show first 5
            name = ref['first_name'] or ref['username'] or "Unknown"
            text += f"• {name}\n"

        if len(successful_referrals) > 5:
            text += f"... and {len(successful_referrals) - 5} more!\n"

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(language=user_language),
        parse_mode="Markdown"
    )
    await callback.answer()