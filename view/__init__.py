import ctypes
import pygame

ctypes.windll.user32.SetProcessDPIAware()
pygame.init()
pygame.mouse.set_visible(False)