# Multi-Language Support Implementation Guide

## Overview
Your bot now supports three languages: English (en), Russian (ru), and Uzbek (uz). This guide explains how to use translations throughout your handlers.

## Quick Start

### 1. Import the Language Manager
```python
from utils.language_manager import LanguageManager
```

### 2. Get User's Language
```python
from database.sqlite_manager import SQLiteManager

user_language = await SQLiteManager.get_user_language(user_id)
```

### 3. Use Translations
```python
# Simple text
text = LanguageManager.get_text('welcome', user_language)

# Text with variables
text = LanguageManager.get_text('welcome_back', user_language, first_name='John')

# Nested keys (buttons)
button_text = LanguageManager.get_text('buttons.join_channel', user_language)
```

## Translation Key Structure

### Available Keys in locales/*.json:

#### Top-level keys:
- `welcome` - Welcome message for new users
- `welcome_back` - Welcome message for returning users
- `join_channel` - Channel join prompt
- `language_selection` - Language selection prompt
- `language_selected` - Language confirmation

#### Nested keys:
- `buttons.*` - All button texts
- `olympiads.*` - Olympiad-related texts
- `registration.*` - Registration form texts
- `referral.*` - Referral system texts
- `admin.*` - Admin panel texts
- `errors.*` - Error messages

## Implementation Pattern

### Before (Hardcoded):
```python
await message.answer("Welcome to the bot!")
```

### After (Translated):
```python
user_language = await SQLiteManager.get_user_language(user_id)
text = LanguageManager.get_text('welcome', user_language, first_name=first_name)
await message.answer(text)
```

## Updating Keyboards with Translations

### Before:
```python
def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🏆 View Olympiads", callback_data="view_olympiads")],
    ]
```

### After:
```python
def main_menu_keyboard(is_admin: bool = False, language: str = 'en') -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text=LanguageManager.get_button_text('view_olympiads', language),
            callback_data="view_olympiads"
        )],
    ]
```

## Handler Update Checklist

### For each handler file, update:

1. **Imports**
   - Add: `from utils.language_manager import LanguageManager`
   - Add: `from database.sqlite_manager import SQLiteManager`

2. **Get user language at start of handler**
   ```python
   user_language = await SQLiteManager.get_user_language(user_id)
   ```

3. **Replace all hardcoded strings**
   ```python
   # Find: await message.answer("Some text")
   # Replace: 
   text = LanguageManager.get_text('key_name', user_language)
   await message.answer(text)
   ```

4. **Update keyboard functions**
   - Add `language: str = 'en'` parameter
   - Use `LanguageManager.get_button_text()` for button texts

5. **Pass language to keyboard functions**
   ```python
   reply_markup=main_menu_keyboard(is_admin, user_language)
   ```

## Files to Update

### Priority 1 (Core):
- [ ] `handlers/channel.py` - Channel join verification
- [ ] `handlers/olympiads.py` - Olympiad viewing
- [ ] `handlers/referral.py` - Referral system

### Priority 2 (Registration):
- [ ] `handlers/registration.py` - Registration form (most text-heavy)

### Priority 3 (Admin):
- [ ] `handlers/admin.py` - Admin panel

## Adding New Translations

1. Add the key to all three JSON files:
   - `locales/en.json`
   - `locales/ru.json`
   - `locales/uz.json`

2. Use in code:
   ```python
   text = LanguageManager.get_text('new_key', user_language)
   ```

## Fallback Behavior

- If a translation key is missing in the user's language, it falls back to English
- If the key doesn't exist in English either, the key name is returned
- This prevents the bot from crashing due to missing translations

## Testing

Test each language by:
1. Starting the bot with `/start`
2. Selecting a language
3. Verifying all text appears in the correct language
4. Testing all buttons and interactions

## Common Patterns

### Format with variables:
```python
text = LanguageManager.get_text('referrals_count', language, count=42)
# Output: "Total Referrals: 42"
```

### Multiple variables:
```python
text = LanguageManager.get_text('confirmation', language, 
    name='John', email='john@example.com', phone='+1234567890')
```

### Conditional text:
```python
if price > 0:
    text = LanguageManager.get_text('buttons.register_points', language, price=price)
else:
    text = LanguageManager.get_text('buttons.register_free', language)
```

## Notes

- Always get user language from database before using translations
- Pass language to all keyboard functions
- Keep translation keys consistent across all files
- Test thoroughly with all three languages
- For RTL languages (future), add to LanguageManager if needed
