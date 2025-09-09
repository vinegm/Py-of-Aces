from src.windows.utils import BaseWindow
from src.game_logic import BlackjackGame, GameState
from src.config import (
    init_default_bet,
    init_bet_options,
    quit_keys,
    enter_keys,
    up_keys,
    down_keys,
)


class BettingWindow(BaseWindow):
    message = ""
    bet_amount = init_default_bet
    bet_options = init_bet_options

    def __init__(
        self, game: BlackjackGame, menu_window: str, game_window: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.game = game
        self.menu_window = menu_window
        self.game_window = game_window

    def draw(self) -> None:
        if self.__is_game_ongoing():
            self.switch_win(self.game_window)
            return

        print(self.term.clear)

        mode_text = ""
        is_practice_mode = self.game.current_mode_name() == "practice"
        if is_practice_mode:
            mode_text = " (PRACTICE)"

        title = self.term.bold("PY OF ACES - BLACKJACK" + mode_text)
        print(self.term.center(title))
        print()

        money_info = self.game.get_money_display()
        print(self.term.center(money_info))
        print()

        bet_display = f"Bet Amount: ${self.bet_amount}"
        print(self.term.center(bet_display))
        print()

        print(self.term.center("Quick bets: [1] $10  [2] $25  [3] $50  [4] $100"))
        print()

        if is_practice_mode:
            print(
                self.term.center(
                    "Practice Mode: No money lost, tracking total winnings"
                )
            )
            print()

        if self.message:
            styled_message = self.term.yellow(self.message)
            print(self.term.center(styled_message))
            print()

        controls = "[q] Quit  [↑↓] Adjust bet  [1-4] Quick bets  [ENTER] Deal"
        print(self.term.center(controls))

    def __is_game_ongoing(self) -> bool:
        return self.game.state != GameState.BETTING

    def handle_input(self, key: str) -> None:
        self.message = ""
        key = key.lower()
        available_money = self.game.get_available_money()

        if key in quit_keys:
            self.switch_win(self.menu_window)

        elif key in enter_keys:
            if not self.game.place_bet(self.bet_amount):
                self.message = "Invalid bet amount!"
                return

            self.game.deal_initial_cards()
            self.switch_win(self.game_window)

        elif key in up_keys:
            self.bet_amount = min(self.bet_amount + 5, available_money)

        elif key in down_keys:
            self.bet_amount = max(self.bet_amount - 5, 5)

        elif key in self.bet_options:
            self.bet_amount = min(self.bet_options[key], available_money)
