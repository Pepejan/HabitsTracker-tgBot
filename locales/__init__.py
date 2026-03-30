"""
locales/__init__.py

Usage:
    from locales import get_strings
    s = get_strings(lang)          # lang = "en" | "uk"
    text = s["start_greeting"].format(name="Alice", ...)
"""

from locales.en import STRINGS as _EN
from locales.uk import STRINGS as _UK

_LOCALES: dict[str, dict] = {
    "en": _EN,
    "uk": _UK,
}

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Українська",
}

DEFAULT_LANG = "en"


def get_strings(lang: str) -> dict:
    """Return the string dict for *lang*, falling back to English."""
    return _LOCALES.get(lang, _EN)