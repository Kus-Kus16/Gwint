import json
import logging
import os
import sys
from abc import ABC
import pygame
import shutil
from appdirs import user_data_dir

USERDATA_DIR = user_data_dir("Gwent", "KusKus")
os.makedirs(USERDATA_DIR, exist_ok=True)

class Loader(ABC):
    __image_cache = {}
    __text_cache = {}

    @classmethod
    def load_text(cls, text_id, font, color, **kwargs):
        from src.presenter.settings import Settings

        translated = Settings.gettext(text_id)
        text = translated.format(**kwargs)

        key = (text, font, color)
        if key in cls.__text_cache:
            text_surface = cls.__text_cache[key]
        else:
            text_surface = font.render(text, True, color)
            cls.__text_cache[key] = text_surface

        return text_surface

    @classmethod
    def load_image(cls, path, size=None):
        key = (path, size)
        if key in cls.__image_cache:
            return cls.__image_cache[key]

        actual_path = cls.get_resource_path(path)
        if not os.path.exists(actual_path):
            logging.info(f"Can't find image path: {path}")
            placeholder = "resources/placeholder.png"
            return cls.load_image(placeholder, size)

        image = pygame.image.load(actual_path).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)

        cls.__image_cache[key] = image
        return image

    @staticmethod
    def load_data(filename):
        path = f"./resources/data/{filename}.json"
        actual_path = Loader.get_resource_path(path)
        return Loader.load_json(actual_path)

    @staticmethod
    def load_userdata(filename):
        path = str(os.path.join(USERDATA_DIR, f"{filename}.json"))

        if not os.path.exists(path):
            default_path = str(Loader.get_resource_path(f"resources/default_userdata/{filename}.json"))
            shutil.copy(default_path, path)

        return Loader.load_json(path)

    @staticmethod
    def load_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def on_setting_update(cls):
        cls.__text_cache.clear()

    @staticmethod
    def get_resource_path(relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base_path, relative_path)