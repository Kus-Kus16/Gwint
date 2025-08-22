import json
import logging
import os
from abc import ABC

import pygame

class Loader(ABC):
    __image_cache = {}

    @classmethod
    def load_image(cls, path, size=None):
        if (path, size) in cls.__image_cache:
            return cls.__image_cache[(path, size)]

        if not os.path.exists(path):
            logging.info(f"Can't find image path: {path}")
            placeholder = "resources/placeholder.png"
            return cls.load_image(placeholder, size)

        image = pygame.image.load(path).convert_alpha()
        if size is not None:
            image = pygame.transform.scale(image, size)

        cls.__image_cache[(path, size)] = image
        return image

    @staticmethod
    def load_data(filename):
        path = f"./resources/data/{filename}.json"
        return Loader.load_json(path)

    @staticmethod
    def load_userdata(filename):
        path = f"./userdata/{filename}.json"
        return Loader.load_json(path)

    @staticmethod
    def load_json(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)