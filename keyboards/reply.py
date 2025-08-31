from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cancel_registration_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard for canceling registration during the process"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Cancel Registration")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
