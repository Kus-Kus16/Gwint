import gettext
import random
from src.presenter import loader, saver
from src.view.constants import ui_constants as u

lang = gettext.translation("base", localedir="locales", languages=["PL"])
lang.install()
locale = lang.gettext

_user_settings = {}
_observers = {}
_theme_index = None

def load_settings():
    data = loader.load_data("settings", is_userdata=True)
    _user_settings.clear()
    _user_settings.update(data)

def load_setting(setting_name):
    return _user_settings[setting_name]

def save_setting(setting_name, value):
    _user_settings[setting_name] = value
    saver.save_userdata("settings", _user_settings)
    _notify_observers(setting_name)

def register_observer(observer, setting_name):
    if setting_name not in _observers:
        _observers[setting_name] = set()
    _observers[setting_name].add(observer)

def _notify_observers(setting_name):
    for observer in _observers.get(setting_name, []):
        observer.on_setting_update()

def get_random_theme():
    global _theme_index
    if _theme_index is None:
        _theme_index = random.randrange(len(u.THEMES))
    return _theme_index

load_settings()
