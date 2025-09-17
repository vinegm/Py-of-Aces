from .tui_handler import TuiHandler
from .windows import MenuWindow, GameWindow, BettingWindow
from .game_logic.blackjack_game import BlackjackGame


def run():
    """Start Py of Aces"""
    tui = TuiHandler()
    game_instance = BlackjackGame()

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

    tui.start("menu")
