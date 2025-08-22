import json
from abc import ABC


# noinspection PyTypeChecker
class Saver(ABC):
    @staticmethod
    def save_userdata(filename, obj):
        with open(f"./userdata/{filename}.json", "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)