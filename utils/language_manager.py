import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class LanguageManager:
    """Manages translations for the bot"""
    
    SUPPORTED_LANGUAGES = ['en', 'ru', 'uz']
    DEFAULT_LANGUAGE = 'en'
    
    _translations: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def load_translations(cls):
        """Load all translation files"""
        locales_dir = Path(__file__).parent.parent / 'locales'
        
        for lang in cls.SUPPORTED_LANGUAGES:
            lang_file = locales_dir / f'{lang}.json'
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    cls._translations[lang] = json.load(f)
    
    @classmethod
    def get_text(cls, key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """
        Get translated text by key
        
        Args:
            key: Translation key (supports nested keys with dots, e.g., 'buttons.join_channel')
            language: Language code ('en', 'ru', 'uz')
            **kwargs: Variables to format in the text (e.g., first_name='John')
        
        Returns:
            Translated text with formatted variables
        """
        if not cls._translations:
            cls.load_translations()
        
        # Validate language
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        # Get translation
        translation_dict = cls._translations.get(language, {})
        text = cls._get_nested_value(translation_dict, key)
        
        # Fallback to English if translation not found
        if text is None:
            translation_dict = cls._translations.get(cls.DEFAULT_LANGUAGE, {})
            text = cls._get_nested_value(translation_dict, key)
        
        # Return key if still not found
        if text is None:
            return key
        
        # Format text with provided variables
        try:
            if kwargs:
                text = text.format(**kwargs)
        except KeyError as e:
            # If formatting fails, return text as is
            pass
        
        return text
    
    @classmethod
    def _get_nested_value(cls, dictionary: Dict, key: str) -> Optional[str]:
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        value = dictionary
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    @classmethod
    def get_button_text(cls, button_key: str, language: str = DEFAULT_LANGUAGE) -> str:
        """Get button text translation"""
        return cls.get_text(f'buttons.{button_key}', language)
    
    @classmethod
    def is_valid_language(cls, language: str) -> bool:
        """Check if language is supported"""
        return language in cls.SUPPORTED_LANGUAGES


# Initialize translations on module load
LanguageManager.load_translations()
