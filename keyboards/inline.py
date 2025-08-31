from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def channel_join_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    """Keyboard for joining channel"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url=channel_link)],
        [InlineKeyboardButton(text="✅ I Joined", callback_data="check_joined")]
    ])


def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="🏆 View Olympiads", callback_data="view_olympiads")],
        [InlineKeyboardButton(text="👥 Invite Friends", callback_data="invite_friends")],
        [InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats")]
    ]

    if is_admin:
        keyboard.append([InlineKeyboardButton(text="👑 Admin Panel", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🏆 Create Olympiad", callback_data="admin_create_olympiad")],
        [InlineKeyboardButton(text="🗑️ Delete Olympiad", callback_data="admin_delete_olympiad")],
        [InlineKeyboardButton(text="💰 Set Olympiad Price", callback_data="admin_set_price")],
        [InlineKeyboardButton(text="🔢 Set Registration Limit", callback_data="admin_set_limit")],
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])


# def olympiads_keyboard(olympiads: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
#     """Keyboard showing list of upcoming olympiads"""
#     keyboard = []
#     for olympiad in olympiads:
#         button_text = f"🏆 {olympiad['title']} - {olympiad['subject']}"
#         callback_data = f"olympiad_{olympiad['id']}"
#         keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

#     keyboard.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")])
#     return InlineKeyboardMarkup(inline_keyboard=keyboard)


def olympiad_detail_keyboard(olympiad_id: str, price: int = 0, user_points: int = 0) -> InlineKeyboardMarkup:
    """Keyboard for olympiad details"""
    keyboard = [
        [InlineKeyboardButton(text="👥 Invite Friend", callback_data=f"invite_for_{olympiad_id}")],
    ]

    if price > 0:
        if user_points >= price:
            keyboard.append(
                [InlineKeyboardButton(text=f"📝 Register ({price} points)", callback_data=f"register_{olympiad_id}")])
        else:
            keyboard.append([InlineKeyboardButton(text=f"❌ Not enough points ({price} needed)",
                                                  callback_data="insufficient_points")])
    else:
        keyboard.append([InlineKeyboardButton(text="📝 Register (Free)", callback_data=f"register_{olympiad_id}")])

    keyboard.append([InlineKeyboardButton(text="🔙 Back to List", callback_data="view_olympiads")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Male", callback_data="gender_male")],
        [InlineKeyboardButton(text="👩 Female", callback_data="gender_female")]
    ])


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Yes/No keyboard for participation question"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes", callback_data=f"{prefix}_yes")],
        [InlineKeyboardButton(text="❌ No", callback_data=f"{prefix}_no")]
    ])


def confirmation_keyboard(olympiad_id: str) -> InlineKeyboardMarkup:
    """Registration confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm Registration", callback_data=f"confirm_reg_{olympiad_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_registration")],
        [InlineKeyboardButton(text="✏️ Edit Information", callback_data="edit_registration")]
    ])


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])

def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Yes/No keyboard for participation question"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes", callback_data=f"{prefix}_yes")],
        [InlineKeyboardButton(text="❌ No", callback_data=f"{prefix}_no")]
    ])


def confirmation_keyboard(olympiad_id: str) -> InlineKeyboardMarkup:
    """Registration confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm Registration", callback_data=f"confirm_reg_{olympiad_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_registration")],
        [InlineKeyboardButton(text="✏️ Edit Information", callback_data="edit_registration")]
    ])


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])



from typing import List, Dict, Any


def channel_join_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    """Keyboard for joining channel"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url=channel_link)],
        [InlineKeyboardButton(text="✅ I Joined", callback_data="check_joined")]
    ])


def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 View Olympiads", callback_data="view_olympiads")],
        [InlineKeyboardButton(text="👥 Invite Friends", callback_data="invite_friends")],
        [InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats")]
    ])



def olympiads_keyboard(olympiads: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Keyboard showing list of upcoming olympiads"""
    keyboard = []
    for olympiad in olympiads:
        button_text = f"🏆 {olympiad['title']} - {olympiad['subject']}"
        callback_data = f"olympiad_{olympiad['id']}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def olympiad_detail_keyboard(olympiad_id: str, price: int = 0, user_points: int = 0) -> InlineKeyboardMarkup:
    """Keyboard for olympiad details"""
    keyboard = [
        [InlineKeyboardButton(text="👥 Invite Friend", callback_data=f"invite_for_{olympiad_id}")],
    ]

    if price > 0:
        if user_points >= price:
            keyboard.append(
                [InlineKeyboardButton(text=f"📝 Register ({price} points)", callback_data=f"register_{olympiad_id}")])
        else:
            keyboard.append([InlineKeyboardButton(text=f"❌ Not enough points ({price} needed)",
                                                  callback_data="insufficient_points")])
    else:
        keyboard.append([InlineKeyboardButton(text="📝 Register (Free)", callback_data=f"register_{olympiad_id}")])

    keyboard.append([InlineKeyboardButton(text="🔙 Back to List", callback_data="view_olympiads")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Male", callback_data="gender_male")],
        [InlineKeyboardButton(text="👩 Female", callback_data="gender_female")]
    ])


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Yes/No keyboard for participation question"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes", callback_data=f"{prefix}_yes")],
        [InlineKeyboardButton(text="❌ No", callback_data=f"{prefix}_no")]
    ])


def confirmation_keyboard(olympiad_id: str) -> InlineKeyboardMarkup:
    """Registration confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm Registration", callback_data=f"confirm_reg_{olympiad_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_registration")],
        [InlineKeyboardButton(text="✏️ Edit Information", callback_data="edit_registration")]
    ])


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])


def cancel_registration_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for canceling registration during the process"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel Registration", callback_data="cancel_registration")]
    ])