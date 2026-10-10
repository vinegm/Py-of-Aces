from .utils import BaseWindow
from py_of_aces.game_logic import BlackjackGame, Modes
from py_of_aces.utils import get_title_ascii


class MenuWindow(BaseWindow):
    """
    Main menu window with selectable items.

    args:
        game: The BlackjackGame instance to manage game state.
        betting_window: The name of the betting window to switch to.
    """

    items = ["Play", "Practice", "Quit"]
    item_count = len(items)
    selected_index = 0

    def __init__(self, game: BlackjackGame, betting_window: str, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.betting_window = betting_window

    def draw(self) -> list[str]:
        lines: list[str] = []

        title_art = get_title_ascii()
        for line in title_art.splitlines():
            lines.append(self.term.red(line))
        lines.append("")

        lines.append(f"♠ {self.term.red('♥')} {self.term.red('♦')} ♣")
        lines.append("")

        for i, item in enumerate(self.items):
            if i == self.selected_index:
                lines.append(self.term.bold_reverse(item))
                continue
            lines.append(item)

        return lines

    def handle_input(self, key: str) -> None:
        key = key.lower()

        if key in self.config.keys.up:
            self.selected_index = (self.selected_index - 1) % self.item_count

        elif key in self.config.keys.down:
            self.selected_index = (self.selected_index + 1) % self.item_count

        elif key in self.config.keys.enter:
            self.__handle_selection()

        elif key in self.config.keys.quit:
            self.stop_process()

    def __handle_selection(self) -> None:
        selected_item = self.items[self.selected_index]
        match selected_item:
            case "Play":
                self.game.select_mode(Modes.NORMAL)
                self.switch_win(self.betting_window)

            case "Practice":
                self.game.select_mode(Modes.PRACTICE)
                self.switch_win(self.betting_window)

            case "Quit":
                self.stop_process()
