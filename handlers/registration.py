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
from utils.language_manager import LanguageManager
import re
from aiogram.utils.markdown import hbold, hcode
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("register_"))
async def start_registration(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start the registration process"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    olympiad_id = callback.data.split("_")[1]

    # Check if olympiad exists in SQLite
    olympiad = await SQLiteManager.get_olympiad_by_id(olympiad_id)
    if not olympiad:
        error_text = LanguageManager.get_text('errors.invalid_input', user_language)
        await callback.answer(error_text, show_alert=True)
        return

    # Check registration limit
    current_registrations = await SupabaseManager.get_olympiad_registrations_count(olympiad_id)

    if olympiad['registration_limit'] and current_registrations >= olympiad['registration_limit']:
        closed_text = LanguageManager.get_text('registration.closed', user_language)
        await callback.message.edit_text(
            closed_text,
            reply_markup=back_to_menu_keyboard(language=user_language),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    # Store olympiad info in state
    await state.update_data(olympiad_id=olympiad_id, olympiad=olympiad)

    reg_title = LanguageManager.get_text('registration.title', user_language, olympiad_title=olympiad['title'])
    email_prompt = LanguageManager.get_text('registration.email_prompt', user_language)
    
    await callback.message.edit_text(reg_title)
    
    # Send the first input prompt with reply keyboard
    await bot.send_message(
        user_id,
        email_prompt,
        reply_markup=cancel_registration_keyboard()
    )

    await state.set_state(UserStates.registration_email)
    await callback.answer()


@router.message(UserStates.registration_email)
async def process_email(message: Message, state: FSMContext):
    """Process email input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    email = message.text.strip().lower()

    # Basic email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        invalid_email = LanguageManager.get_text('registration.invalid_email', user_language)
        await message.answer(invalid_email, reply_markup=cancel_registration_keyboard())
        return

    # Check if email exists in profiles
    profile = await SupabaseManager.check_email_exists(email)

    if not profile:
        email_not_found = LanguageManager.get_text('registration.email_not_found', user_language)
        await message.answer(
            email_not_found,
            reply_markup=cancel_registration_keyboard()
        )
        return

    # Store email and profile info
    await state.update_data(email=email, profile=profile)

    birth_year_prompt = LanguageManager.get_text('registration.birth_year_prompt', user_language)
    await message.answer(
        birth_year_prompt,
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_birth_year)


@router.message(UserStates.registration_birth_year)
async def process_birth_year(message: Message, state: FSMContext):
    """Process birth year input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    try:
        year = int(message.text.strip())
        if year < 1950 or year > 2010:
            invalid_year = LanguageManager.get_text('registration.invalid_birth_year', user_language)
            await message.answer(invalid_year, reply_markup=cancel_registration_keyboard())
            return

        # Convert year to date format (using January 1st)
        birth_date = f"{year}-01-01"
        await state.update_data(date_of_birth=birth_date)

        passport_prompt = LanguageManager.get_text('registration.passport_prompt', user_language)
        await message.answer(
            passport_prompt,
            reply_markup=cancel_registration_keyboard()
        )
        await state.set_state(UserStates.registration_passport)

    except ValueError:
        invalid_year_format = LanguageManager.get_text('registration.invalid_year_format', user_language)
        await message.answer(invalid_year_format, reply_markup=cancel_registration_keyboard())


@router.message(UserStates.registration_passport)
async def process_passport(message: Message, state: FSMContext):
    """Process passport ID input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    passport_id = message.text.strip().upper()

    if len(passport_id) < 6 or len(passport_id) > 15:
        invalid_passport = LanguageManager.get_text('registration.invalid_passport', user_language)
        await message.answer(invalid_passport, reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(passport_id=passport_id)

    gender_prompt = LanguageManager.get_text('registration.gender_prompt', user_language)
    await message.answer(
        gender_prompt,
        reply_markup=gender_keyboard(language=user_language)
    )
    await state.set_state(UserStates.registration_gender)


@router.callback_query(F.data.startswith("gender_"), UserStates.registration_gender)
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender selection"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    gender = callback.data.split("_")[1]
    await state.update_data(gender=gender)

    gender_text = LanguageManager.get_text('registration.gender_selected', user_language, gender=gender.title())
    country_prompt = LanguageManager.get_text('registration.country_prompt', user_language)
    await callback.message.edit_text(
        f"✅ {gender_text}\n\n{country_prompt}"
    )
    await state.set_state(UserStates.registration_country)
    await callback.answer()


@router.message(UserStates.registration_country)
async def process_country(message: Message, state: FSMContext):
    """Process country input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    country = message.text.strip().title()

    if len(country) < 2 or len(country) > 50:
        invalid_country = LanguageManager.get_text('registration.invalid_country', user_language)
        await message.answer(invalid_country, reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(country=country)

    city_prompt = LanguageManager.get_text('registration.city_prompt', user_language)
    await message.answer(
        city_prompt,
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_city)


@router.message(UserStates.registration_city)
async def process_city(message: Message, state: FSMContext):
    """Process city input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    city = message.text.strip().title()

    if len(city) < 2 or len(city) > 50:
        invalid_city = LanguageManager.get_text('registration.invalid_city', user_language)
        await message.answer(invalid_city, reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(city=city)

    heard_about_prompt = LanguageManager.get_text('registration.heard_about_prompt', user_language)
    await message.answer(
        heard_about_prompt,
        reply_markup=cancel_registration_keyboard()
    )
    await state.set_state(UserStates.registration_heard_about)


@router.message(UserStates.registration_heard_about)
async def process_heard_about(message: Message, state: FSMContext):
    """Process 'heard about us' input"""
    user_id = message.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    # Check if user wants to cancel
    if message.text == "❌ Cancel Registration":
        is_admin = await SQLiteManager.is_admin(user_id)
        cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
        await message.answer(
            cancelled_text,
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )
        await state.clear()
        return

    heard_about = message.text.strip()

    if len(heard_about) < 5 or len(heard_about) > 200:
        invalid_description = LanguageManager.get_text('registration.invalid_description', user_language)
        await message.answer(invalid_description, reply_markup=cancel_registration_keyboard())
        return

    await state.update_data(heard_about_us=heard_about)

    participated_prompt = LanguageManager.get_text('registration.participated_prompt', user_language)
    await message.answer(
        participated_prompt,
        reply_markup=yes_no_keyboard("participated", language=user_language)
    )
    await state.set_state(UserStates.registration_participated)


@router.callback_query(F.data.startswith("participated_"), UserStates.registration_participated)
async def process_participated(callback: CallbackQuery, state: FSMContext):
    """Process participation history"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
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
        already_registered = LanguageManager.get_text('registration.already_registered', user_language, olympiad_title=olympiad['title'])
        await callback.message.edit_text(
            already_registered,
            reply_markup=back_to_menu_keyboard(language=user_language),
            parse_mode="Markdown"
        )
        await callback.answer()
        await state.clear()
        return

    # Show confirmation
    confirmation_title = LanguageManager.get_text('registration.confirmation_title', user_language)
    confirmation_text = (
        f"📋 <b>{confirmation_title}</b>\n\n"
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
        + LanguageManager.get_text('registration.confirm_prompt', user_language)
    )

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=confirmation_keyboard(data['olympiad_id'], language=user_language),
        parse_mode="HTML"
    )

    await state.set_state(UserStates.registration_confirm)
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_reg_"))
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Confirm and complete registration"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    data = await state.get_data()
    olympiad_id = data['olympiad_id']
    olympiad = data['olympiad']

    # Check if user needs to pay points
    price = await SupabaseManager.get_olympiad_price(olympiad_id)
    user = await SQLiteManager.get_user(user_id)

    if price > 0:
        if user['points'] < price:
            insufficient_points = LanguageManager.get_text('registration.insufficient_points', user_language, price=price, current_points=user['points'])
            await callback.message.edit_text(
                insufficient_points,
                reply_markup=back_to_menu_keyboard(language=user_language),
                parse_mode="HTML"
            )
            await callback.answer()
            await state.clear()
            return

        # Deduct points and remove referrals
        success = await SQLiteManager.deduct_points_and_remove_referrals(
            user_id, price
        )
        if not success:
            payment_failed = LanguageManager.get_text('registration.payment_failed', user_language)
            await callback.message.edit_text(
                payment_failed,
                reply_markup=back_to_menu_keyboard(language=user_language),
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
        success_title = LanguageManager.get_text('registration.success_title', user_language)
        success_text = (
            f"🎉 <b>{success_title}</b>\n\n"
            f"You have been registered for:\n"
            f"🏆 {olympiad['title']}\n"
            f"📚 Subject: {olympiad['subject']}\n"
            f"📅 Date: {olympiad['date']}\n\n"
        )

        if price > 0:
            points_deducted = LanguageManager.get_text('registration.points_deducted', user_language, points=price)
            success_text += f"💰 {points_deducted}\n\n"

        if olympiad.get('link'):
            success_text += f"🔗 Olympiad Link:\n{olympiad['link']}\n\n"

        success_text += LanguageManager.get_text('registration.good_luck', user_language)

        # 1) Send final details (no keyboard)
        await callback.message.answer(success_text, parse_mode="HTML")

        # 2) Send separate menu message with inline keyboard
        is_admin = await SQLiteManager.is_admin(user_id)
        await callback.message.answer(
            "⬅️ Back to menu",
            reply_markup=main_menu_keyboard(is_admin, language=user_language)
        )

        await callback.answer("Registration completed! ✅")

    else:
        registration_failed = LanguageManager.get_text('registration.failed', user_language)
        await callback.message.edit_text(
            registration_failed,
            reply_markup=back_to_menu_keyboard(language=user_language),
            parse_mode="HTML"
        )
        await callback.answer("Registration failed!")

    await state.clear()



@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Cancel registration process"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    is_admin = await SQLiteManager.is_admin(user_id)
    cancelled_text = LanguageManager.get_text('registration.cancelled', user_language)
    await callback.message.edit_text(
        cancelled_text,
        reply_markup=main_menu_keyboard(is_admin, language=user_language)
    )
    await callback.answer("Registration cancelled")
    await state.clear()


@router.callback_query(F.data == "edit_registration")
async def edit_registration(callback: CallbackQuery, state: FSMContext):
    """Allow user to edit registration information"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    edit_text = LanguageManager.get_text('registration.edit', user_language)
    await callback.message.edit_text(
        edit_text,
        reply_markup=None
    )
    await state.set_state(UserStates.registration_email)
    await callback.answer()


@router.callback_query(F.data == "insufficient_points")
async def insufficient_points_info(callback: CallbackQuery, state: FSMContext):
    """Show info about insufficient points"""
    user_id = callback.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    user = await SQLiteManager.get_user(user_id)
    insufficient_msg = LanguageManager.get_text('registration.insufficient_points_info', user_language, points=user['points'])
    await callback.answer(
        insufficient_msg,
        show_alert=True
    )