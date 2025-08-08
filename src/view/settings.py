from src.view import loader, saver

user_settings = {}
observers = set()

def load_settings():
    data = loader.load_data("settings", is_userdata=True)
    user_settings.clear()
    user_settings.update(data)

def load_setting(setting_name):
    return user_settings[setting_name]

def save_setting(setting_name, value):
    user_settings[setting_name] = value
    saver.save_userdata("settings", user_settings)
    for observer in observers:
        observer.on_settings_update()

def register_observer(observer):
    observers.add(observer)

load_settings()