import pygame

from model.enums.cards_area import CardsArea
from model.enums.row_type import RowType


def __row(row_y, text_y_center):
    return {
        "UNIT_RECT": __rect((UNIT_X, row_y), UNIT_ROW_SIZE),
        "BOOST_RECT": __rect((BOOST_X, row_y), BOOST_ROW_SIZE),
        "TEXT_CENTER": (TEXT_X_CENTER, text_y_center)
    }

def __rect(pos, size):
    return pygame.Rect(*pos, *size)

def __font(name, size):
    return pygame.font.Font(f"resources/fonts/{name}.ttf", size)

def __theme():
    themes = [("ciri", "BLUE"), ("geralt", "ORANGE"), ("yennefer", "GOLD"), ("nithral", "SILVER")]
    # file, color = random.choice(themes)
    file, color = themes[0]

    bck = f"resources/gwent/backgrounds/{file}.png"
    but = (globals()[f"{color}_BUTTON_PATH"], globals()[f"{color}_BUTTON_PATH_HOVER"])

    return bck, but


UNIT_X = 707
BOOST_X = 570
TEXT_X_CENTER = 536
UNIT_ROW_SIZE = (812, 119)
BOOST_ROW_SIZE = (130, 119)

WEATHER_POS = (140, 448)
WEATHER_SIZE = (281, 140)

HAND_POS = (577, 842)
HAND_SIZE = (936, 125)

BOARD_POS = (570, 17)
BOARD_SIZE = (949, 807)

DECK_SIZE = (112, 147)
GRAVE_OPP_POS = (1544, 69)
GRAVE_POS = (1544, 827)
DECK_OPP_POS = (1725, 69)
DECK_POS = (1724, 827)

COMM_SIZE = (101, 134)
COMM_OPP_POS = (138, 80)
COMM_POS = (138, 833)

POINTS_OPP_POS = (453, 332)
POINTS_POS = (453, 734)

SELF_ROW_TYPES = [RowType.CLOSE, RowType.RANGED, RowType.SIEGE]
ROW_TYPES = [RowType.SIEGE_OPP, RowType.RANGED_OPP, RowType.CLOSE_OPP] + SELF_ROW_TYPES
SIEGE_OPP = __row(17, 74)
RANGED_OPP = __row(149, 205)
CLOSE_OPP = __row(286, 343)
CLOSE = __row(435, 492)
RANGED = __row(567, 625)
SIEGE = __row(705, 763)

WEATHER_RECT = __rect(WEATHER_POS, WEATHER_SIZE)
HAND_RECT = __rect(HAND_POS, HAND_SIZE)
BOARD_RECT = __rect(BOARD_POS, BOARD_SIZE)

GRAVE_RECT = __rect(GRAVE_POS, DECK_SIZE)
GRAVE_OPP_RECT = __rect(GRAVE_OPP_POS, DECK_SIZE)
GRAVES = [(CardsArea.GRAVE, GRAVE_RECT), (CardsArea.GRAVE_OPP, GRAVE_OPP_RECT)]

DECK_RECT = __rect(DECK_POS, DECK_SIZE)
DECK_OPP_RECT = __rect(DECK_OPP_POS, DECK_SIZE)
DECKS = [(CardsArea.DECK, DECK_RECT), (CardsArea.DECK_OPP, DECK_OPP_RECT)]

COMM_RECT = __rect(COMM_POS, COMM_SIZE)
COMM_OPP_RECT = __rect(COMM_OPP_POS, COMM_SIZE)
COMMANDERS = [(CardsArea.COMMANDER, COMM_RECT), (CardsArea.COMMANDER_OPP, COMM_OPP_RECT)]

INFO_SIZE = (451, 145)
INFO_POS = (0, 662)
INFO_OPP_POS = (0, 260)
INFO_RECT = __rect(INFO_POS, INFO_SIZE)
INFO_OPP_RECT = __rect(INFO_OPP_POS, INFO_SIZE)

BUTTON_SIZE = (300, 100)
BUTTON_SIZE_WIDE = (400, 80)
BUTTON_SIZE_NARROW = (200, 60)

DECK_CARD_SIZE = (83, 140)
SMALL_CARD_SIZE = (94, 123)
MEDIUM_CARD_SIZE = (210, 365)
LARGE_CARD_SIZE = (293, 512)
SELECTED_CARD_POS = (1544, 265)

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
MASON_50 = __font("mason", 50)
CINZEL_15 = __font("Cinzel-Regular", 15)
CINZEL_30 = __font("Cinzel-Regular", 30)
CINZEL_40 = __font("Cinzel-Regular", 40)
CINZEL_20_BOLD = __font("Cinzel-SemiBold", 20)
CINZEL_25_BOLD = __font("Cinzel-SemiBold", 25)
CINZEL_30_BOLD = __font("Cinzel-SemiBold", 30)
CINZEL_50_BOLD = __font("Cinzel-SemiBold", 50)
DEFAULT_FONT = CINZEL_30
DEFAULT_FONT_BOLD = CINZEL_30_BOLD

LOGO_PATH = "resources/gwent/backgrounds/logo-solo.png"
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
DEFAULT_BUTTON_PATHS = (COPPER_BUTTON_PATH, COPPER_BUTTON_PATH_HOVER, GOLD_BUTTON_PATH)

BACKGROUND_PATH, THEME_BUTTON_PATHS = __theme()

AUTHORS = ["Autorzy:", "Krzysztof Pieczka", "Maciej Kus"]