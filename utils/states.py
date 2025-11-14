from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    selecting_language = State()
    waiting_for_channel_join = State()
    main_menu = State()
    viewing_olympiads = State()
    olympiad_selected = State()

    # Registration states
    registration_email = State()
    registration_birth_year = State()
    registration_passport = State()
    registration_gender = State()
    registration_country = State()
    registration_city = State()
    registration_heard_about = State()
    registration_participated = State()
    registration_confirm = State()


class AdminStates(StatesGroup):
    admin_menu = State()
    broadcast_message = State()
    set_olympiad_price = State()
    set_olympiad_limit = State()

    # Olympiad management states
    create_olympiad_id = State()
    create_olympiad_title = State()
    create_olympiad_subject = State()
    create_olympiad_date = State()
    create_olympiad_link = State()
    create_olympiad_limit = State()
    create_olympiad_price = State()
    delete_olympiad = State()