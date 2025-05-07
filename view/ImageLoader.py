import os

import pygame

image_cache = {}

def load_image(path):
    if path in image_cache:
        return image_cache[path]

    if not os.path.exists(path):
        print(f"[WARN] Brak pliku: {path}")
        return load_image("resources/placeholder.png")

    image = pygame.image.load(path).convert_alpha()
    image_cache[path] = image
    return image