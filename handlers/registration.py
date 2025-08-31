from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.supabase_manager import SupabaseManager
from database.sqlite_manager import SQLiteManager
from keyboards.inline import (
    gender_keyboard, yes_no_keyboard, confirmation_keyboard,
    back_to_menu_keyboard, main_menu_keyboard
)
from keyboards.reply import cancel_registration_keyboard
from utils.states import UserStates
import re
from aiogram.utils.markdown import hbold, hcode
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("register_"))
async def start_registration(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start the registration process"""
    olympiad_id = callback.data.split("_")[1]

    # Check if olympiad exists in SQLite
    olympiad = await SQLiteManager.get_olympiad_by_id(olympiad_id)
    if not olympiad:
        await callback.answer("Olympiad not found!", show_alert=True)
        return

    # Check registration limit
    current_registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad_id)

    if olympiad['registration_limit'] and current_registrations >= olympiad['registration_limit']:
        await callback.message.edit_text(
            "❌ **Registration Closed**\n\n"
            "This olympiad has reached its registration limit. "
            "Please check other available olympiads.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    # Store olympiad info in state
    await state.update_data(olympiad_id=olympiad_id, olympiad=olympiad)

    await callback.message.edit_text(
        f"📝 **Registration for {olympiad['title']}**\n\n"
        "Let's start with your email address.\n\n"
        "Please enter the email you used to sign up on our website:"
    )
    
    # Send the first input prompt with reply keyboard
    await bot.send_message(
        callback.from_user.id,
        "Please enter the email you used to sign up on our website:",
        reply_markup=cancel_registration_keyboard()
    )

    await state.set_state(UserStates.registration_email)
    await callback.answer()


@router.message(UserStates.registration_email)
async def process_email(message: Message, state: FSMContext):
    """Process email input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    email = message.text.strip().lower()

    # Basic email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await message.answer("❌ Please enter a valid email address.", reply_markup=cancel_registration_keyboard())
        return

    # Check if email exists in profiles
    profile = await SupabaseManager.check_email_exists(email)

    if not profile:
        await message.answer(
            "🤔 Hmmm. I don't think you signed up on our website.\n\n"
            "Please sign up here: https://olympiaid.net\n"
            "Or check your email spelling and try again.",
            reply_markup=cancel_registration_keyboard()
        )
        return

    # Store email and profile info
    await state.update_data(email=email, profile=profile)

    await message.answer(
        "✅ Great! Email verified.\n\n"
        "Now, please enter your year of birth (e.g., 1995):",
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_birth_year)


@router.message(UserStates.registration_birth_year)
async def process_birth_year(message: Message, state: FSMContext):
    """Process birth year input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    try:
        year = int(message.text.strip())
        if year < 1950 or year > 2010:
            await message.answer("❌ Please enter a valid birth year (1950-2010).", reply_markup=cancel_registration_keyboard())
            return

        # Convert year to date format (using January 1st)
        birth_date = f"{year}-01-01"
        await state.update_data(date_of_birth=birth_date)

        await message.answer(
            "✅ Birth year recorded.\n\n"
            "Please enter your Passport ID:",
            reply_markup=cancel_registration_keyboard()
        )
        await state.set_state(UserStates.registration_passport)

    except ValueError:
        await message.answer("❌ Please enter a valid year (numbers only).", reply_markup=cancel_registration_keyboard())


@router.message(UserStates.registration_passport)
async def process_passport(message: Message, state: FSMContext):
    """Process passport ID input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    passport_id = message.text.strip().upper()

    if len(passport_id) < 6 or len(passport_id) > 15:
        await message.answer("❌ Please enter a valid passport ID (6-15 characters).", reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(passport_id=passport_id)

    await message.answer(
        "✅ Passport ID recorded.\n\n"
        "Please select your gender:",
        reply_markup=gender_keyboard()
    )
    await state.set_state(UserStates.registration_gender)


@router.callback_query(F.data.startswith("gender_"), UserStates.registration_gender)
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender selection"""
    gender = callback.data.split("_")[1]
    await state.update_data(gender=gender)

    await callback.message.edit_text(
        f"✅ Gender: {'Male' if gender == 'male' else 'Female'}\n\n"
        "Please enter your country:"
    )
    await state.set_state(UserStates.registration_country)
    await callback.answer()


@router.message(UserStates.registration_country)
async def process_country(message: Message, state: FSMContext):
    """Process country input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    country = message.text.strip().title()

    if len(country) < 2 or len(country) > 50:
        await message.answer("❌ Please enter a valid country name.", reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(country=country)

    await message.answer(
        "✅ Country recorded.\n\n"
        "Please enter your city:",
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_city)


@router.message(UserStates.registration_city)
async def process_city(message: Message, state: FSMContext):
    """Process city input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    city = message.text.strip().title()

    if len(city) < 2 or len(city) > 50:
        await message.answer("❌ Please enter a valid city name.", reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(city=city)

    await message.answer(
        "✅ City recorded.\n\n"
        "How did you hear about us? Please describe briefly:",
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_heard_about)


@router.message(UserStates.registration_heard_about)
async def process_heard_about(message: Message, state: FSMContext):
    """Process 'heard about us' input"""
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(message.from_user.id)
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "You can start registration again anytime.",
            reply_markup=main_menu_keyboard(is_admin)
        )
        await state.clear()
        return

    heard_about = message.text.strip()

    if len(heard_about) < 5 or len(heard_about) > 200:
        await message.answer("❌ Please provide a brief description (5-200 characters).", reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(heard_about_us=heard_about)

    await message.answer(
        "✅ Thanks for sharing!\n\n"
        "Have you participated in our olympiads before?",
        reply_markup=yes_no_keyboard("participated")
    )
    await state.set_state(UserStates.registration_participated)


@router.callback_query(F.data.startswith("participated_"), UserStates.registration_participated)
async def process_participated(callback: CallbackQuery, state: FSMContext):
    """Process participation history"""
    participated = callback.data.split("_")[1] == "yes"
    await state.update_data(has_participated_before=participated)

    # Get all stored data
    data = await state.get_data()
    olympiad = data['olympiad']

    # Check if user already registered for this olympiad
    existing_registration = await SupabaseManager.check_existing_registration(
        data['profile']['id'], data['olympiad_id']
    )

    if existing_registration:
        await callback.message.edit_text(
            "❌ **Already Registered!**\n\n"
            f"You are already registered for {olympiad['title']}.\n\n"
            "You cannot register for the same olympiad twice.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        await state.clear()
        return

    # Show confirmation
    confirmation_text = (
        f"📋 <b>Registration Summary</b>\n\n"
        f"🏆 <b>Olympiad:</b> {olympiad['title']}\n"
        f"📚 <b>Subject:</b> {olympiad['subject']}\n"
        f"📅 <b>Date:</b> {olympiad['date']}\n\n"
        f"📧 <b>Email:</b> {data['email']}\n"
        f"🎂 <b>Birth Year:</b> {data['date_of_birth'][:4]}\n"
        f"🆔 <b>Passport:</b> {data['passport_id']}\n"
        f"👤 <b>Gender:</b> {data['gender'].title()}\n"
        f"🌍 <b>Country:</b> {data['country']}\n"
        f"🏙️ <b>City:</b> {data['city']}\n"
        f"📢 <b>Heard about us:</b> {data['heard_about_us'][:50]}...\n"
        f"🏆 <b>Previous participation:</b> {'Yes' if participated else 'No'}\n\n"
        "Is all information correct?"
    )

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=confirmation_keyboard(data['olympiad_id']),
        parse_mode="HTML"
    )

    await state.set_state(UserStates.registration_confirm)
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_reg_"))
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Confirm and complete registration"""
    data = await state.get_data()
    olympiad_id = data['olympiad_id']
    olympiad = data['olympiad']

    # Check if user needs to pay points
    price = await SupabaseManager.get_olympiad_price(olympiad_id)
    user = await SQLiteManager.get_user(callback.from_user.id)

    if price > 0:
        if user['points'] < price:
            await callback.message.edit_text(
                f"❌ <b>Insufficient Points</b>\n\n"
                f"You need {price} points to register for this olympiad.\n"
                f"You currently have {user['points']} points.\n\n"
                f"Invite more friends to earn points!",
                reply_markup=back_to_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            await state.clear()
            return

        # Deduct points and remove referrals
        success = await SQLiteManager.deduct_points_and_remove_referrals(
            callback.from_user.id, price
        )
        if not success:
            await callback.message.edit_text(
                "❌ <b>Payment Failed</b>\n\n"
                "Unable to process point payment. Please try again later.",
                reply_markup=back_to_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return

    # Register in Supabase
    registration_success = await SupabaseManager.register_for_olympiad(
        olympiad_id=olympiad_id,
        user_id=data['profile']['id'],
        passport_id=data['passport_id'],
        date_of_birth=data['date_of_birth'],
        gender=data['gender'],
        country=data['country'],
        city=data['city'],
        heard_about_us=data['heard_about_us'],
        has_participated_before=data['has_participated_before']
    )

    if registration_success:
        # 🗑 Delete the old summary message with inline keyboard
        try:
            await callback.message.delete()
        except Exception:
            pass  # ignore if already deleted

        # Build success text
        success_text = (
            f"🎉 <b>Registration Successful!</b>\n\n"
            f"You have been registered for:\n"
            f"🏆 {olympiad['title']}\n"
            f"📚 Subject: {olympiad['subject']}\n"
            f"📅 Date: {olympiad['date']}\n\n"
        )

        if price > 0:
            success_text += f"💰 Points deducted: {price}\n\n"

        if olympiad.get('link'):
            success_text += f"🔗 Olympiad Link:\n{olympiad['link']}\n\n"

        success_text += "Good luck with your olympiad! 🍀"

        # 1) Send final details (no keyboard)
        await callback.message.answer(success_text, parse_mode="HTML")

        # 2) Send separate menu message with inline keyboard
        is_admin = await SQLiteManager.is_admin(callback.from_user.id)
        await callback.message.answer(
            "⬅️ Back to menu",
            reply_markup=main_menu_keyboard(is_admin)
        )

        await callback.answer("Registration completed! ✅")

    else:
        await callback.message.edit_text(
            "❌ <b>Registration Failed</b>\n\n"
            "There was an error processing your registration. Please try again later.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Registration failed!")

    await state.clear()



@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Cancel registration process"""
    is_admin = await SQLiteManager.is_admin(callback.from_user.id)
    await callback.message.edit_text(
        "❌ Registration cancelled.\n\n"
        "You can start registration again anytime.",
        reply_markup=main_menu_keyboard(is_admin)
    )
    await callback.answer("Registration cancelled")
    await state.clear()


@router.callback_query(F.data == "edit_registration")
async def edit_registration(callback: CallbackQuery, state: FSMContext):
    """Allow user to edit registration information"""
    await callback.message.edit_text(
        "✏️ **Edit Registration**\n\n"
        "Please start over with your email address:",
        reply_markup=None
    )
    await state.set_state(UserStates.registration_email)
    await callback.answer()


@router.callback_query(F.data == "insufficient_points")
async def insufficient_points_info(callback: CallbackQuery, state: FSMContext):
    """Show info about insufficient points"""
    user = await SQLiteManager.get_user(callback.from_user.id)
    await callback.answer(
        f"You have {user['points']} points. Invite more friends to earn points!",
        show_alert=True
    )