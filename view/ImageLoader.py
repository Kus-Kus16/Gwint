import os

import pygame
from view import Constants as C

image_cache = {}

def load_image(path):
    if path in image_cache:
        return image_cache[path]

    if not os.path.exists(path):
        placeholder = "resources/placeholder_large2.png" if "large" in path else "resources/placeholder.png"
        return load_image(placeholder)

    image = pygame.image.load(path).convert_alpha()
    if "large" in path:
        image = pygame.transform.scale(image, C.LARGE_CARD_SIZE)

    image_cache[path] = image
    return image