import pygame


def __font(name, size):
    return pygame.font.Font(f"resources/fonts/{name}.ttf", size)

def __themes():
    themes = [("ciri", "BLUE"), ("geralt", "ORANGE"), ("yennefer", "GOLD"), ("nithral", "SILVER")]
    theme_data = [
        (
            f"resources/gwent/backgrounds/{file}.png",
            (globals()[f"{color}_BUTTON_PATH"], globals()[f"{color}_BUTTON_PATH_HOVER"])
        )
        for file, color in themes
    ]

    return theme_data

# UI
DECK_CARD_SIZE = (83, 140)
SMALL_CARD_SIZE = (94, 127)
MEDIUM_CARD_SIZE = (210, 365)
LARGE_CARD_SIZE = (293, 512)

BUTTON_SIZE = (300, 100)
BUTTON_SIZE_WIDE = (400, 80)
BUTTON_SIZE_NARROW = (200, 60)

ARROW_SIZE = (54, 85)
TEXT_BOX_SIZE = (500, 74)

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (197, 152, 79)
COLOR_YELLOW = (212, 175, 55)
COLOR_GREEN = (15, 112, 47)
COLOR_RED = (237, 56, 24)
COLOR_LIGHTGRAY = (200, 200, 200)
COLOR_GRAY = (50, 50, 50)

COLOR_HIGHLIGHT = (255, 255, 0)
ALPHA_HIGHLIGHT = 50
COLOR_BUTTON = (139, 69, 19)
COLOR_BUTTON_HOVER = (160, 82, 45)

FRAMERATE = 60
MASON_20 = __font("mason", 20)
MASON_30 = __font("mason", 30)
MASON_40 = __font("mason", 40)
MASON_50 = __font("mason", 50)
CINZEL_15 = __font("Cinzel-Regular", 15)
CINZEL_25 = __font("Cinzel-Regular", 25)
CINZEL_30 = __font("Cinzel-Regular", 30)
CINZEL_40 = __font("Cinzel-Regular", 40)
CINZEL_20_BOLD = __font("Cinzel-SemiBold", 20)
CINZEL_25_BOLD = __font("Cinzel-SemiBold", 25)
CINZEL_30_BOLD = __font("Cinzel-SemiBold", 30)
CINZEL_40_BOLD = __font("Cinzel-SemiBold", 40)
CINZEL_50_BOLD = __font("Cinzel-SemiBold", 50)
DEFAULT_FONT = CINZEL_30
DEFAULT_FONT_BOLD = CINZEL_30_BOLD

LOGO_PATH = "resources/gwent/backgrounds/logo-solo.png"
ICON_PATH = "resources/gwent/icons/icon-transparent.png"

SCROLL_PATH = "resources/gwent/buttons/scroll.png"
BLUE_BUTTON_PATH = "resources/gwent/buttons/button-blue-big.png"
BLUE_BUTTON_PATH_HOVER = "resources/gwent/buttons/button-blue-big-hover.png"
COPPER_BUTTON_PATH = "resources/gwent/buttons/button-copper-big.png"
COPPER_BUTTON_PATH_HOVER = "resources/gwent/buttons/button-copper-big-hover.png"
GOLD_BUTTON_PATH = "resources/gwent/buttons/button-gold-big.png"
GOLD_BUTTON_PATH_HOVER = "resources/gwent/buttons/button-gold-big-hover.png"
ORANGE_BUTTON_PATH = "resources/gwent/buttons/button-orange-big.png"
ORANGE_BUTTON_PATH_HOVER = "resources/gwent/buttons/button-orange-big-hover.png"
SILVER_BUTTON_PATH = "resources/gwent/buttons/button-silver-big.png"
SILVER_BUTTON_PATH_HOVER = "resources/gwent/buttons/button-silver-big-hover.png"
DEFAULT_BUTTON_PATHS = (COPPER_BUTTON_PATH, COPPER_BUTTON_PATH_HOVER)

GOLD_LEFT_ARROW_PATH = "resources/gwent/arrows/arrow-left-gold.png"
GOLD_LEFT_ARROW_PATH_HOVER = "resources/gwent/arrows/arrow-left-gold-hover.png"
GOLD_RIGHT_ARROW_PATH = "resources/gwent/arrows/arrow-right-gold.png"
GOLD_RIGHT_ARROW_PATH_HOVER = "resources/gwent/arrows/arrow-right-gold-hover.png"
DEFAULT_LEFT_ARROW_PATHS = (GOLD_LEFT_ARROW_PATH, GOLD_LEFT_ARROW_PATH_HOVER)
DEFAULT_RIGHT_ARROW_PATHS = (GOLD_RIGHT_ARROW_PATH, GOLD_RIGHT_ARROW_PATH_HOVER)

# Menu
THEMES = __themes()
AUTHORS = [
    "Model, Frontend, Talia Toussaint:",
    "Maciej Kus",
    "Serwer, Frontend:",
    "Krzysztof Pieczka",
    "Talia Wiecznego Ognia, Optymalizacja Scoia'tael:",
    "Maciej Fraś"
]