# Quick Start: Adding Translations to Handlers

## 5-Minute Setup for Any Handler

### Step 1: Add Imports
```python
from utils.language_manager import LanguageManager
from database.sqlite_manager import SQLiteManager
```

### Step 2: Get User Language
```python
user_id = message.from_user.id
user_language = await SQLiteManager.get_user_language(user_id)
```

### Step 3: Replace Hardcoded Text
```python
# Before
await message.answer("Welcome to the bot!")

# After
text = LanguageManager.get_text('welcome', user_language)
await message.answer(text)
```

### Step 4: Update Keyboards
```python
# Before
reply_markup=main_menu_keyboard(is_admin)

# After
reply_markup=main_menu_keyboard(is_admin, language=user_language)
```

## Common Translation Keys

### Messages
- `welcome` - New user welcome
- `welcome_back` - Returning user welcome
- `join_channel` - Channel join prompt

### Buttons
- `buttons.view_olympiads`
- `buttons.invite_friends`
- `buttons.my_stats`
- `buttons.back_to_menu`

### Olympiads
- `olympiads.title`
- `olympiads.no_olympiads`
- `olympiads.details`

### Registration
- `registration.enter_full_name`
- `registration.enter_email`
- `registration.enter_phone`

### Errors
- `errors.invalid_input`
- `errors.insufficient_points`

## Text with Variables

```python
# Single variable
text = LanguageManager.get_text('welcome_back', language, first_name='John')

# Multiple variables
text = LanguageManager.get_text('confirmation', language,
    name='John', email='john@example.com', phone='+1234567890')

# In JSON: "confirmation": "Name: {name}\nEmail: {email}\nPhone: {phone}"
```

## For Callback Handlers

```python
@router.callback_query(F.data == "my_action")
async def my_handler(query: CallbackQuery):
    user_id = query.from_user.id
    user_language = await SQLiteManager.get_user_language(user_id)
    
    text = LanguageManager.get_text('key_name', user_language)
    await query.message.edit_text(text)
```

## For Admin/Broadcast

```python
# Get all users and send in their language
all_users = await SQLiteManager.get_all_users()
for user_id in all_users:
    user_language = await SQLiteManager.get_user_language(user_id)
    text = LanguageManager.get_text('broadcast_message', user_language)
    await bot.send_message(user_id, text)
```

## Adding New Translation Keys

1. Add to all three JSON files:
   - `locales/en.json`
   - `locales/ru.json`
   - `locales/uz.json`

2. Use in code:
   ```python
   text = LanguageManager.get_text('new_key', user_language)
   ```

3. For nested keys:
   ```json
   {
     "buttons": {
       "my_new_button": "Button Text"
     }
   }
   ```
   
   Use as: `LanguageManager.get_text('buttons.my_new_button', language)`

## Testing

```bash
# Start bot
python main.py

# Test each language:
# 1. Send /start
# 2. Select language
# 3. Verify text appears in correct language
# 4. Test all buttons and interactions
```

## Troubleshooting

**Missing translation?**
- Check JSON syntax in locale files
- Verify key name matches exactly
- Will fallback to English automatically

**Wrong language showing?**
- Verify `user_language` is retrieved correctly
- Check database has language column
- Restart bot to reload translations

**Button text not translating?**
- Ensure `language` parameter passed to keyboard function
- Check keyboard function signature includes `language: str = 'en'`

## Files to Update Next

Priority order:
1. `handlers/olympiads.py` - View and select olympiads
2. `handlers/referral.py` - Referral system
3. `handlers/registration.py` - Registration form (most text)
4. `handlers/admin.py` - Admin panel

See `TRANSLATION_GUIDE.md` for detailed instructions.
