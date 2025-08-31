from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database.sqlite_manager import SQLiteManager
from database.supabase_manager import SupabaseManager
from keyboards.inline import admin_menu_keyboard, main_menu_keyboard, back_to_menu_keyboard
from utils.states import AdminStates
import asyncio
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    """Admin command handler"""
    if not await SQLiteManager.is_admin(message.from_user.id):
        await message.answer("❌ You don't have admin privileges.")
        return

    await message.answer(
        "👑 **Admin Panel**\n\n"
        "Welcome to the admin panel. What would you like to do?",
        reply_markup=admin_menu_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.admin_menu)


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery, state: FSMContext):
    """Admin panel access via callback"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ You don't have admin privileges.", show_alert=True)
        return

    await callback.message.edit_text(
        "👑 **Admin Panel**\n\n"
        "Welcome to the admin panel. What would you like to do?",
        reply_markup=admin_menu_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.admin_menu)
    await callback.answer()


# OLYMPIAD MANAGEMENT
@router.callback_query(F.data == "admin_create_olympiad")
async def start_create_olympiad(callback: CallbackQuery, state: FSMContext):
    """Start creating new olympiad"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access required", show_alert=True)
        return

    await callback.message.edit_text(
        "🏆 **Create New Olympiad**\n\n"
        "Please enter the UUID of the olympiad from Supabase.\n"
        "(Copy it from your Supabase olympiads table)",
        reply_markup=back_to_menu_keyboard()
    )
    await state.set_state(AdminStates.create_olympiad_id)
    await callback.answer()


@router.message(AdminStates.create_olympiad_id)
async def process_olympiad_id(message: Message, state: FSMContext):
    """Process olympiad UUID input"""
    olympiad_id = message.text.strip()

    # Check if olympiad already exists in SQLite
    existing = await SQLiteManager.get_olympiad_by_id(olympiad_id)
    if existing:
        await message.answer("❌ Olympiad with this ID already exists in the bot database.")
        return

    await state.update_data(olympiad_id=olympiad_id)
    await message.answer(
        "✅ Olympiad ID recorded.\n\n"
        "Please enter the olympiad title:"
    )
    await state.set_state(AdminStates.create_olympiad_title)


@router.message(AdminStates.create_olympiad_title)
async def process_olympiad_title(message: Message, state: FSMContext):
    """Process olympiad title input"""
    title = message.text.strip()

    if len(title) < 5 or len(title) > 100:
        await message.answer("❌ Title must be between 5-100 characters.")
        return

    await state.update_data(title=title)
    await message.answer(
        "✅ Title recorded.\n\n"
        "Please enter the subject (e.g., Mathematics, Physics, etc.):"
    )
    await state.set_state(AdminStates.create_olympiad_subject)


@router.message(AdminStates.create_olympiad_subject)
async def process_olympiad_subject(message: Message, state: FSMContext):
    """Process olympiad subject input"""
    subject = message.text.strip()

    if len(subject) < 2 or len(subject) > 50:
        await message.answer("❌ Subject must be between 2-50 characters.")
        return

    await state.update_data(subject=subject)
    await message.answer(
        "✅ Subject recorded.\n\n"
        "Please enter the date (YYYY-MM-DD format, e.g., 2025-12-25):"
    )
    await state.set_state(AdminStates.create_olympiad_date)


@router.message(AdminStates.create_olympiad_date)
async def process_olympiad_date(message: Message, state: FSMContext):
    """Process olympiad date input"""
    date_str = message.text.strip()

    # Basic date format validation
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-25)")
        return

    await state.update_data(date=date_str)
    await message.answer(
        "✅ Date recorded.\n\n"
        "Please enter the olympiad link (or send 'skip' if no link):"
    )
    await state.set_state(AdminStates.create_olympiad_link)


@router.message(AdminStates.create_olympiad_link)
async def process_olympiad_link(message: Message, state: FSMContext):
    """Process olympiad link input"""
    link = message.text.strip()

    if link.lower() == 'skip':
        link = None
    elif link and not (link.startswith('http://') or link.startswith('https://')):
        await message.answer("❌ Please enter a valid URL starting with http:// or https://, or send 'skip'")
        return

    await state.update_data(link=link)
    await message.answer(
        "✅ Link recorded.\n\n"
        "Please enter the registration limit (number of participants, or send '0' for no limit):"
    )
    await state.set_state(AdminStates.create_olympiad_limit)


@router.message(AdminStates.create_olympiad_limit)
async def process_olympiad_limit(message: Message, state: FSMContext):
    """Process olympiad registration limit input"""
    try:
        limit = int(message.text.strip())
        if limit < 0:
            await message.answer("❌ Limit cannot be negative.")
            return

        limit_value = limit if limit > 0 else None
        await state.update_data(registration_limit=limit_value)

        await message.answer(
            "✅ Registration limit recorded.\n\n"
            "Please enter the price in points (or send '0' for free):"
        )
        await state.set_state(AdminStates.create_olympiad_price)

    except ValueError:
        await message.answer("❌ Please enter a valid number.")


@router.message(AdminStates.create_olympiad_price)
async def process_olympiad_price(message: Message, state: FSMContext):
    """Process olympiad price input and create the olympiad"""
    try:
        price = int(message.text.strip())
        if price < 0:
            await message.answer("❌ Price cannot be negative.")
            return

        # Get all stored data
        data = await state.get_data()

        # Create olympiad in SQLite
        success = await SQLiteManager.create_olympiad(
            olympiad_id=data['olympiad_id'],
            title=data['title'],
            subject=data['subject'],
            date=data['date'],
            link=data.get('link'),
            registration_limit=data.get('registration_limit'),
            price=price
        )

        if success:
            summary_text = f"🎉 **Olympiad Created Successfully!**\n\n"
            summary_text += f"🆔 **ID:** {data['olympiad_id']}\n"
            summary_text += f"🏆 **Title:** {data['title']}\n"
            summary_text += f"📚 **Subject:** {data['subject']}\n"
            summary_text += f"📅 **Date:** {data['date']}\n"
            summary_text += f"🔗 **Link:** {data.get('link') or 'None'}\n"
            summary_text += f"👥 **Limit:** {data.get('registration_limit') or 'No limit'}\n"
            summary_text += f"💰 **Price:** {price} points\n"

            await message.answer(
                summary_text,
                reply_markup=admin_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "❌ Failed to create olympiad. ID might already exist.",
                reply_markup=admin_menu_keyboard()
            )

    except ValueError:
        await message.answer("❌ Please enter a valid number for price.")
        return

    await state.set_state(AdminStates.admin_menu)


@router.callback_query(F.data == "admin_delete_olympiad")
async def start_delete_olympiad(callback: CallbackQuery, state: FSMContext):
    """Start delete olympiad process"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access required", show_alert=True)
        return

    olympiads = await SQLiteManager.get_all_olympiads()

    if not olympiads:
        await callback.message.edit_text(
            "❌ No olympiads found to delete.",
            reply_markup=admin_menu_keyboard()
        )
        await callback.answer()
        return

    text = "🗑️ **Delete Olympiad**\n\n"
    text += "Available olympiads:\n\n"

    for i, olympiad in enumerate(olympiads, 1):
        registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad['id'])
        text += f"{i}. {olympiad['title']} ({olympiad['subject']})\n"
        text += f"   📅 {olympiad['date']} | 👥 {registrations} registrations\n\n"

    text += "Please send the number of the olympiad to delete:\n"
    text += "⚠️ **Warning:** This action cannot be undone!"

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )

    await state.update_data(olympiads=olympiads)
    await state.set_state(AdminStates.delete_olympiad)
    await callback.answer()


@router.message(AdminStates.delete_olympiad)
async def process_delete_olympiad(message: Message, state: FSMContext):
    """Process olympiad deletion"""
    try:
        olympiad_index = int(message.text.strip()) - 1

        data = await state.get_data()
        olympiads = data['olympiads']

        if olympiad_index < 0 or olympiad_index >= len(olympiads):
            await message.answer("❌ Invalid olympiad number.")
            return

        olympiad = olympiads[olympiad_index]

        # Delete olympiad from SQLite
        success = await SQLiteManager.delete_olympiad(olympiad['id'])

        if success:
            await message.answer(
                f"✅ **Olympiad Deleted**\n\n"
                f"🏆 {olympiad['title']} has been deleted from the bot.\n\n"
                f"⚠️ Note: Existing registrations in Supabase are not affected.",
                reply_markup=admin_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "❌ Failed to delete olympiad.",
                reply_markup=admin_menu_keyboard()
            )

    except ValueError:
        await message.answer("❌ Please enter a valid number.")
        return

    await state.set_state(AdminStates.admin_menu)


async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start broadcast message process"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access required", show_alert=True)
        return

    await callback.message.edit_text(
        "📢 **Broadcast Message**\n\n"
        "Please send the message you want to broadcast to all users.\n\n"
        "You can send text, photos, videos, or any other content.",
        reply_markup=back_to_menu_keyboard()
    )
    await state.set_state(AdminStates.broadcast_message)
    await callback.answer()


@router.message(AdminStates.broadcast_message)
async def process_broadcast(message: Message, state: FSMContext):
    """Process and send broadcast message"""
    users = await SQLiteManager.get_all_users()

    if not users:
        await message.answer("❌ No users found to broadcast to.")
        return

    await message.answer(f"📤 Broadcasting message to {len(users)} users...")

    success_count = 0
    failed_count = 0

    for user_id in users:
        try:
            if message.text:
                await message.bot.send_message(user_id, message.text)
            elif message.photo:
                await message.bot.send_photo(
                    user_id,
                    message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.video:
                await message.bot.send_video(
                    user_id,
                    message.video.file_id,
                    caption=message.caption
                )
            elif message.document:
                await message.bot.send_document(
                    user_id,
                    message.document.file_id,
                    caption=message.caption
                )
            elif message.audio:
                await message.bot.send_audio(
                    user_id,
                    message.audio.file_id,
                    caption=message.caption
                )
            elif message.voice:
                await message.bot.send_voice(
                    user_id,
                    message.voice.file_id
                )
            elif message.sticker:
                await message.bot.send_sticker(
                    user_id,
                    message.sticker.file_id
                )

            success_count += 1

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)

        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

    await message.answer(
        f"📊 **Broadcast Complete**\n\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed to send: {failed_count}\n"
        f"📱 Total users: {len(users)}",
        reply_markup=admin_menu_keyboard(),
        parse_mode="Markdown"
    )

    await state.set_state(AdminStates.admin_menu)


@router.callback_query(F.data == "admin_set_price")
async def start_set_price(callback: CallbackQuery, state: FSMContext):
    """Start set olympiad price process"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access required", show_alert=True)
        return

    olympiads = await SupabaseManager.get_upcoming_olympiads()

    if not olympiads:
        await callback.message.edit_text(
            "❌ No upcoming olympiads found.",
            reply_markup=admin_menu_keyboard()
        )
        await callback.answer()
        return

    text = "💰 **Set Olympiad Price**\n\n"
    text += "Available olympiads:\n\n"

    for i, olympiad in enumerate(olympiads, 1):
        current_price = await SupabaseManager.get_olympiad_price(olympiad['id'])
        text += f"{i}. {olympiad['title']} - Current price: {current_price} points\n"

    text += "\nPlease send the olympiad number and new price in format:\n"
    text += "Example: `1 50` (sets olympiad 1 price to 50 points)"

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )

    await state.update_data(olympiads=olympiads)
    await state.set_state(AdminStates.set_olympiad_price)
    await callback.answer()


@router.message(AdminStates.set_olympiad_price)
async def process_set_price(message: Message, state: FSMContext):
    """Process olympiad price setting"""
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            await message.answer("❌ Invalid format. Use: `olympiad_number new_price`", parse_mode="Markdown")
            return

        olympiad_index = int(parts[0]) - 1
        new_price = int(parts[1])

        data = await state.get_data()
        olympiads = data['olympiads']

        if olympiad_index < 0 or olympiad_index >= len(olympiads):
            await message.answer("❌ Invalid olympiad number.")
            return

        if new_price < 0:
            await message.answer("❌ Price cannot be negative.")
            return

        olympiad = olympiads[olympiad_index]

        # Update price in Supabase
        try:
            supabase = SupabaseManager.get_supabase_client()
            supabase.table("olympiads").update({"price": new_price}).eq("id", olympiad['id']).execute()

            await message.answer(
                f"✅ **Price Updated**\n\n"
                f"Olympiad: {olympiad['title']}\n"
                f"New price: {new_price} points",
                reply_markup=admin_menu_keyboard(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error updating olympiad price: {e}")
            await message.answer("❌ Failed to update price. Please try again.")

    except ValueError:
        await message.answer("❌ Please enter valid numbers.")

    await state.set_state(AdminStates.admin_menu)


@router.callback_query(F.data == "admin_set_limit")
async def start_set_limit(callback: CallbackQuery, state: FSMContext):
    """Start set registration limit process"""
    if not await SQLiteManager.is_admin(callback.from_user.id):
        await callback.answer("❌ Admin access required", show_alert=True)
        return

    olympiads = await SupabaseManager.get_upcoming_olympiads()

    if not olympiads:
        await callback.message.edit_text(
            "❌ No upcoming olympiads found.",
            reply_markup=admin_menu_keyboard()
        )
        await callback.answer()
        return

    text = "🔢 **Set Registration Limit**\n\n"
    text += "Available olympiads:\n\n"

    for i, olympiad in enumerate(olympiads, 1):
        current_limit = await SupabaseManager.get_olympiad_limit(olympiad['id'])
        current_registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad['id'])
        text += f"{i}. {olympiad['title']}\n"
        text += f"   Current limit: {current_limit or 'No limit'}\n"
        text += f"   Current registrations: {current_registrations}\n\n"

    text += "Please send the olympiad number and new limit in format:\n"
    text += "Example: `1 100` (sets olympiad 1 limit to 100 registrations)\n"
    text += "Use `1 0` to remove limit"

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )

    await state.update_data(olympiads=olympiads)
    await state.set_state(AdminStates.set_olympiad_limit)
    await callback.answer()


@router.message(AdminStates.set_olympiad_limit)
async def process_set_limit(message: Message, state: FSMContext):
    """Process registration limit setting"""
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            await message.answer("❌ Invalid format. Use: `olympiad_number new_limit`", parse_mode="Markdown")
            return

        olympiad_index = int(parts[0]) - 1
        new_limit = int(parts[1])

        data = await state.get_data()
        olympiads = data['olympiads']

        if olympiad_index < 0 or olympiad_index >= len(olympiads):
            await message.answer("❌ Invalid olympiad number.")
            return

        if new_limit < 0:
            await message.answer("❌ Limit cannot be negative.")
            return

        olympiad = olympiads[olympiad_index]
        limit_value = new_limit if new_limit > 0 else None

        # Update limit in Supabase
        try:
            supabase = SupabaseManager.get_supabase_client()
            supabase.table("olympiads").update({"registration_limit": limit_value}).eq("id", olympiad['id']).execute()

            limit_text = f"{new_limit} registrations" if new_limit > 0 else "No limit"
            await message.answer(
                f"✅ **Registration Limit Updated**\n\n"
                f"Olympiad: {olympiad['title']}\n"
                f"New limit: {limit_text}",
                reply_markup=admin_menu_keyboard(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error updating olympiad limit: {e}")
            await message.answer("❌ Failed to update limit. Please try again.")

    except ValueError:
        await message.answer("❌ Please enter valid numbers.")

    await state.set_state(AdminStates.admin_menu)