import pygame

image_cache = {}

def load_image(path):
    if path in image_cache:
        return image_cache[path]

    image = pygame.image.load(path).convert_alpha()
    image_cache[path] = image
    return image