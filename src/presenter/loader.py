import json
import os

import pygame

image_cache = {}

def load_image(path, size=None):
    if (path, size) in image_cache:
        return image_cache[(path, size)]

    if not os.path.exists(path):
        print(f"Can't find {path}")
        placeholder = "resources/placeholder.png"
        return load_image(placeholder, size)

    image = pygame.image.load(path).convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)

    image_cache[(path, size)] = image
    return image

def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_data(filename, is_userdata=False):
    path = f"./userdata/{filename}.json" if is_userdata else f"./resources/data/{filename}.json"
    return load_json(path)