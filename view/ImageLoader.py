import os

import pygame

image_cache = {}

def load_image(path, size=None):
    if (path, size) in image_cache:
        return image_cache[(path, size)]

    if not os.path.exists(path):
        print(path)
        placeholder = "resources/placeholder_large.png" if "large" in path else "resources/placeholder.png"
        return load_image(placeholder,size)

    image = pygame.image.load(path).convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)

    image_cache[(path, size)] = image
    return image