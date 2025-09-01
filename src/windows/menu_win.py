from src.windows.utils import BaseWindow


class MenuWindow(BaseWindow):
    """
    Main menu window with selectable items.

    args:
        game_window: The name of the game window to switch to.
    """

    def __init__(self, game_window: str = None, **kwargs):
        super().__init__(**kwargs)
        self.game_window = game_window
        self.items = ["Start Game", "Quit"]
        self.item_count = len(self.items)
        self.selected_index = 0

    def draw(self):
        print(self.term.clear)
        print(self.term.center("Main Menu\n"))
        for i, item in enumerate(self.items):
            if i == self.selected_index:
                print(self.term.center(self.term.reverse(item)))
            else:
                print(self.term.center(item))

    def __handle_selection(self):
        selected_item = self.items[self.selected_index]
        match selected_item:
            case "Start Game":
                self.switch_win(self.game_window)
            case "Quit":
                raise SystemExit

    def handle_input(self, key):
        match key:
            case "KEY_UP" | "k":
                self.selected_index = (self.selected_index - 1) % self.item_count

            case "KEY_DOWN" | "j":
                self.selected_index = (self.selected_index + 1) % self.item_count

            case "KEY_ENTER" | " ":
                self.__handle_selection()

            case "q":
                raise SystemExit
