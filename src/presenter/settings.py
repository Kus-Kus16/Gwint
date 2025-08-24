import gettext
import random
from abc import ABC

from src.presenter.saver import Saver
from src.presenter.loader import Loader
from src.view.constants import ui_constants as u

class Settings(ABC):
    __user_settings = Loader.load_userdata("settings")
    __observers = {}
    __theme_index = None
    __lang_provider = None

    LANGUAGES = ["EN", "PL"]
    THEMES = ["Ciri", "Gerald", "Yennefer", "Nithral", "Random"]
    OFFON = ["OFF", "ON"]

    @classmethod
    def get_setting(cls, setting_name):
        return cls.__user_settings[setting_name]

    @classmethod
    def save_setting(cls, setting_name, value):
        cls.__user_settings[setting_name] = value
        Saver.save_userdata("settings", cls.__user_settings)
        cls.__notify_observers(setting_name)

    @classmethod
    def register_observer(cls, observer, setting_name):
        if setting_name not in cls.__observers:
            cls.__observers[setting_name] = set()
        cls.__observers[setting_name].add(observer)

    @classmethod
    def __notify_observers(cls, setting_name):
        for observer in cls.__observers.get(setting_name, []):
            observer.on_setting_update()

    @classmethod
    def get_random_theme(cls):
        if cls.__theme_index is None:
            cls.__theme_index = random.randrange(len(u.THEMES))
        return cls.__theme_index

    @classmethod
    def reload_language(cls, new_index):
        language_id = cls.LANGUAGES[new_index]
        locale_path = Loader.get_resource_path("locales")
        lang = gettext.translation("base", localedir=locale_path, fallback=True, languages=[language_id])
        cls.__lang_provider = lang.gettext

    @classmethod
    def gettext(cls, text):
        if cls.__lang_provider is None:
            cls.reload_language(cls.get_setting("language"))
        return cls.__lang_provider(text)

Settings.register_observer(Loader, "language")