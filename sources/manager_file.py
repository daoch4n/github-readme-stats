from os.path import join, isfile, dirname
from pickle import load as load_pickle, dump as dump_pickle
from json import load as load_json
from typing import Dict, Optional, Any

from manager_environment import EnvironmentManager as EM


def init_localization_manager():
    """
    Initialize localization manager.
    Load GUI translations JSON file.
    """
    # Assuming EM.LOCALE is set before this is called
    FileManager.load_localization(EM.LOCALE)


class FileManager:
    """
    Class for handling localization (and maybe other file IO in future).
    Stores localization in dictionary.
    """

    ASSETS_DIR = "assets"
    _LOCALIZATION: Dict[str, str] = dict()
    TRANSLATION_FILE_PATH = join(dirname(__file__), "translation.json")

    @staticmethod
    def load_localization(locale_name: str):
        """
        Loads localization data for the given locale.
        If a base language (e.g., 'ja') is requested, it will also load and merge
        any more specific regional variants (e.g., 'ja_JP'), with regional variants
        taking precedence.
        """
        try:
            with open(FileManager.TRANSLATION_FILE_PATH, 'r', encoding='utf-8') as f:
                all_translations = load_json(f)
        except FileNotFoundError:
            print(f"Error: translation.json not found at {FileManager.TRANSLATION_FILE_PATH}")
            FileManager._LOCALIZATION = {}
            return
        except load_json.JSONDecodeError: # Use load_json.JSONDecodeError for clarity
            print(f"Error: Could not decode translation.json at {FileManager.TRANSLATION_FILE_PATH}")
            FileManager._LOCALIZATION = {}
            return

        # Start with an empty dictionary for the current session's translations
        current_translations: Dict[str, str] = {}

        # Split the locale name to get the base language (e.g., 'ja' from 'ja_JP')
        parts = locale_name.split('_')
        base_language = parts[0]

        # 1. Load the base language translations first
        if base_language in all_translations:
            current_translations.update(all_translations[base_language])

        # 2. If a specific regional locale was requested (e.g., 'ja_JP'), load and merge it
        # This handles cases where the user explicitly sets locale to 'ja_JP'
        if locale_name != base_language and locale_name in all_translations:
            current_translations.update(all_translations[locale_name])
        elif locale_name == base_language:
            # If only the base language was requested (e.g., 'ja'),
            # iterate through all available locales to find and merge any regional variants
            # that start with this base language (e.g., 'ja_JP', 'ja_KR')
            for key, value in all_translations.items():
                if key.startswith(f"{base_language}_") and key != base_language:
                    current_translations.update(value)
        
        FileManager._LOCALIZATION = current_translations

    @staticmethod
    def t(key: str) -> str:
        """
        Translate string to current localization.
        Falls back to the key itself if no translation is found.

        :param key: Localization key.
        :returns: Translation string.
        """
        return FileManager._LOCALIZATION.get(key, key)

    @staticmethod
    def write_file(name: str, content: str, append: bool = False, assets: bool = False):
        """
        Save output file.

        :param name: File name.
        :param content: File content (utf-8 string).
        :param append: True for appending to file, false for rewriting.
        :param assets: True for saving to 'assets' directory, false otherwise.
        """
        name = join(FileManager.ASSETS_DIR, name) if assets else name
        with open(name, "a" if append else "w", encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    def cache_binary(name: str, content: Optional[Any] = None, assets: bool = False) -> Optional[Any]:
        """
        Save binary output file if provided or read if content is None.

        :param name: File name.
        :param content: File content (utf-8 string) or None.
        :param assets: True for saving to 'assets' directory, false otherwise.
        :returns: File cache contents if content is None, None otherwise.
        """
        name = join(FileManager.ASSETS_DIR, name) if assets else name
        if content is None and not isfile(name):
            return None

        with open(name, "rb" if content is None else "wb") as file:
            if content is None:
                try:
                    return load_pickle(file)
                except Exception: # Catching a general Exception for pickle errors
                    return None
            else:
                dump_pickle(content, file)
                return None
