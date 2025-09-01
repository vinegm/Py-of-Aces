from src.tui_handler import TuiHandler
from src.windows import MenuWindow, GameWindow


def run():
    tui = TuiHandler()

    tui.add_window("menu", MenuWindow, game_window="game")
    tui.add_window("game", GameWindow, menu_window="menu")

    tui.start("menu")
