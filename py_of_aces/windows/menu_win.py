from .utils import BaseWindow
from ..utils import get_title_ascii
from ..game_logic import BlackjackGame, Modes
from ..config import enter_keys, up_keys, down_keys, quit_keys


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
            lines.append(line)
        lines.append("")

        for i, item in enumerate(self.items):
            if i == self.selected_index:
                lines.append(self.term.reverse(item))
                continue
            lines.append(item)

        return lines

    def handle_input(self, key: str) -> None:
        key = key.lower()

        if key in up_keys:
            self.selected_index = (self.selected_index - 1) % self.item_count

        elif key in down_keys:
            self.selected_index = (self.selected_index + 1) % self.item_count

        elif key in enter_keys:
            self.__handle_selection()

        elif key in quit_keys:
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
