from src.windows.utils import BaseWindow
from src.utils import get_card_ascii, join_cards


class GameWindow(BaseWindow):
    def __init__(self, menu_window: str = None, **kwargs):
        super().__init__(**kwargs)
        self.menu_window = menu_window

    def draw(self):
        print(self.term.clear)
        print(self.term.center("Game Win\n"))

        card1_art = get_card_ascii("10", "♠")
        card2_art = get_card_ascii("A", "♠", face_down_text="???")
        card_art = join_cards(card1_art, card2_art)

        for line in card_art.splitlines():
            print(self.term.center(line))

        print(self.term.center("\nPress 'q' to return to menu."))

    def handle_input(self, key):
        match key:
            case "q":
                self.switch_win(self.menu_window)
