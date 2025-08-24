import json
import os
from abc import ABC
from src.presenter.loader import USERDATA_DIR

# noinspection PyTypeChecker
class Saver(ABC):
    @staticmethod
    def save_userdata(filename, obj):
        path = os.path.join(USERDATA_DIR, f"{filename}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)