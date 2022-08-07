# pylint: disable=too-few-public-methods
"""Some configuration values"""
LOG_FORMAT = "%(levelname)s [%(module)s.%(funcName)s]: %(message)s"
BASE_URL = "https://discord.com/api/v10/channels/"


class I18n:
    "I18n configuration values"
    AVAILABLE_LOCALES = ["en-US", "de", "fr"]
    FILENAME_FORMAT = "{locale}{format}"
    FALLBACK = "en-US"
