from src.presenter import loader, saver

user_settings = {}
observers = {}

def load_settings():
    data = loader.load_data("settings", is_userdata=True)
    user_settings.clear()
    user_settings.update(data)

def load_setting(setting_name):
    return user_settings[setting_name]

def save_setting(setting_name, value):
    user_settings[setting_name] = value
    saver.save_userdata("settings", user_settings)
    notify_observers(setting_name)

def register_observer(observer, setting_name):
    if setting_name not in observers:
        observers[setting_name] = set()
    observers[setting_name].add(observer)

def notify_observers(setting_name):
    for observer in observers[setting_name]:
        observer.on_setting_update()

load_settings()