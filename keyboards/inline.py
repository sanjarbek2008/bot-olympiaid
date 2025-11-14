from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any
from utils.language_manager import LanguageManager


def channel_join_keyboard(channel_link: str, language: str = 'en') -> InlineKeyboardMarkup:
    """Keyboard for joining channel"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('join_channel', language), url=channel_link)],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('i_joined', language), callback_data="check_joined")]
    ])


def main_menu_keyboard(is_admin: bool = False, language: str = 'en') -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(text=LanguageManager.get_button_text('view_olympiads', language), callback_data="view_olympiads")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('invite_friends', language), callback_data="invite_friends")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('my_stats', language), callback_data="my_stats")]
    ]

    if is_admin:
        keyboard.append([InlineKeyboardButton(text=LanguageManager.get_button_text('admin_panel', language), callback_data="admin_panel")])

    keyboard.append([InlineKeyboardButton(text=LanguageManager.get_button_text('change_language', language), callback_data="change_language")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_menu_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    """Admin menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('broadcast', language), callback_data="admin_broadcast")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('create_olympiad', language), callback_data="admin_create_olympiad")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('delete_olympiad', language), callback_data="admin_delete_olympiad")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('set_price', language), callback_data="admin_set_price")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('set_limit', language), callback_data="admin_set_limit")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('back_to_menu', language), callback_data="back_to_menu")]
    ])


def olympiads_keyboard(olympiads: List[Dict[str, Any]], language: str = 'en') -> InlineKeyboardMarkup:
    """Keyboard showing list of upcoming olympiads"""
    keyboard = []
    for olympiad in olympiads:
        button_text = f"🏆 {olympiad['title']} - {olympiad['subject']}"
        callback_data = f"olympiad_{olympiad['id']}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton(text=LanguageManager.get_button_text('back_to_menu', language), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def olympiad_detail_keyboard(olympiad_id: str, price: int = 0, user_points: int = 0, language: str = 'en') -> InlineKeyboardMarkup:
    """Keyboard for olympiad details"""
    keyboard = [
        [InlineKeyboardButton(text=LanguageManager.get_button_text('invite_friend', language), callback_data=f"invite_for_{olympiad_id}")],
    ]

    if price > 0:
        if user_points >= price:
            register_text = LanguageManager.get_text('buttons.register_points', language, price=price)
            keyboard.append([InlineKeyboardButton(text=register_text, callback_data=f"register_{olympiad_id}")])
        else:
            not_enough_text = LanguageManager.get_text('buttons.not_enough_points', language, price=price)
            keyboard.append([InlineKeyboardButton(text=not_enough_text, callback_data="insufficient_points")])
    else:
        keyboard.append([InlineKeyboardButton(text=LanguageManager.get_button_text('register_free', language), callback_data=f"register_{olympiad_id}")])

    keyboard.append([InlineKeyboardButton(text=LanguageManager.get_button_text('back_to_list', language), callback_data="view_olympiads")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def gender_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('male', language), callback_data="gender_male")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('female', language), callback_data="gender_female")]
    ])


def yes_no_keyboard(prefix: str, language: str = 'en') -> InlineKeyboardMarkup:
    """Yes/No keyboard for participation question"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('yes', language), callback_data=f"{prefix}_yes")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('no', language), callback_data=f"{prefix}_no")]
    ])


def confirmation_keyboard(olympiad_id: str, language: str = 'en') -> InlineKeyboardMarkup:
    """Registration confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('confirm_registration', language), callback_data=f"confirm_reg_{olympiad_id}")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('cancel', language), callback_data="cancel_registration")],
        [InlineKeyboardButton(text=LanguageManager.get_button_text('edit', language), callback_data="edit_registration")]
    ])


def back_to_menu_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    """Simple back to menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('back_to_menu', language), callback_data="back_to_menu")]
    ])


def cancel_registration_inline_keyboard(language: str = 'en') -> InlineKeyboardMarkup:
    """Inline keyboard for canceling registration during the process"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LanguageManager.get_button_text('cancel', language), callback_data="cancel_registration")]
    ])


def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for language selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ])
