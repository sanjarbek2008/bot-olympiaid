import base64
import hashlib
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config.settings import settings

def generate_referral_code(telegram_id: int) -> str:
    """Generate a unique referral code for user"""
    # Create a unique code based on telegram_id
    raw_data = f"{telegram_id}_{settings.bot_token[:10]}"
    encoded = base64.b64encode(hashlib.md5(raw_data.encode()).digest()).decode()
    return encoded[:8]

def decode_referral_code(code: str) -> Optional[int]:
    """Decode referral code to get telegram_id (simplified approach)"""
    # This is a simplified approach - in production, you might want to store
    # referral codes in database for better security
    # For now, we'll handle this in the start handler
    return None

async def check_user_in_channel(bot: Bot, user_id: int) -> bool:
    """Check if user has joined the required channel"""
    try:
        member = await bot.get_chat_member(chat_id=settings.channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False

def create_referral_link(telegram_id: int, bot_username: str) -> str:
    """Create referral link for user"""
    referral_code = generate_referral_code(telegram_id)
    return f"https://t.me/{bot_username}?start=ref_{referral_code}_{telegram_id}"

def extract_referrer_id(start_param: str) -> Optional[int]:
    """Extract referrer telegram_id from start parameter"""
    if start_param and start_param.startswith("ref_"):
        parts = start_param.split("_")
        if len(parts) >= 3:
            try:
                return int(parts[2])  # ref_code_telegram_id
            except ValueError:
                pass
    return None