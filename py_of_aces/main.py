from .config import load_config
from .tui_handler import TuiHandler
from .windows import MenuWindow, GameWindow, BettingWindow, SizeWarningWindow
from .game_logic.blackjack_game import BlackjackGame


def run():
    """Start Py of Aces"""
    MIN_HEIGHT = 30
    MIN_WIDTH = 25

    config = load_config()
    tui = TuiHandler(config, min_height=MIN_HEIGHT, min_width=MIN_WIDTH)
    game_instance = BlackjackGame(config)

    tui.add_window("menu", MenuWindow, betting_window="betting", game=game_instance)
    tui.add_window(
        "betting",
        BettingWindow,
        menu_window="menu",
        game_window="game",
        game=game_instance,
    )
    tui.add_window(
        "game",
        GameWindow,
        menu_window="menu",
        betting_window="betting",
        game=game_instance,
    )
    tui.add_window(
        "size_warning", SizeWarningWindow, min_width=MIN_WIDTH, min_height=MIN_HEIGHT
    )

    tui.start("menu")
