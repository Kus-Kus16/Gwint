import os

import pygame

image_cache = {}

def load_image(path):
    if path in image_cache:
        return image_cache[path]

    if not os.path.exists(path):
        placeholder = "resources/placeholder_large2.png" if "large" in path else "resources/placeholder.png"
        return load_image(placeholder)

    image = pygame.image.load(path).convert_alpha()
    if "large" in path:
        image = pygame.transform.scale(image, (image.get_width() // 2, image.get_height() // 2))

    image_cache[path] = image
    return image