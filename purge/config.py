"""Some configuration values"""

LOG_FORMAT = "%(levelname)s [%(module)s.%(funcName)s]: %(message)s"
BASE_URL = "https://discord.com/api/v10/channels/"
BASE_PATH = "purge"


class I18n:
    "I18n configuration values"

    AVAILABLE_LOCALES = [
        "hu",
        "th",
        "ar",
        "he",
        "nl",
        "cs",
        "uk",
        "no",
        "de",
        "fr",
        "ja",
        "es-ES",
        "en-GB",
        "pl",
        "da",
        "pt-BR",
        "ru",
        "fi",
        "ko",
        "el",
        "tr",
        "ro",
        "it",
        "zh-CN",
        "en-US",
        "lt",
        "hr",
        "sv-SE",
        "vi",
        "hi",
        "zh-TW",
        "bg",
    ]
    FILENAME_FORMAT = "{locale}{format}"
    FALLBACK = "en-US"
