from .utils import BaseWindow
from ..game_logic import BlackjackGame, GameState, Modes
from ..config import (
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
            return []

        lines: list[str] = []

        mode_text = ""
        is_practice_mode = self.game.mode == Modes.PRACTICE
        if is_practice_mode:
            mode_text = " (PRACTICE)"

        title = self.term.bold(
            f"{self.term.reverse}PY OF ACES{mode_text}{self.term.normal}"
        )
        lines.append(title)
        lines.append("")

        money_info = self.game.get_money_display
        lines.append(money_info)
        lines.append("")

        bet_display = f"Bet Amount: ${self.bet_amount}"
        lines.append(bet_display)
        lines.append("")

        lines.append("Quick bets: [1] $10  [2] $25  [3] $50  [4] $100")
        lines.append("")

        if is_practice_mode:
            lines.append("Practice Mode: No money lost, tracking total winnings")
            lines.append("")

        if self.message:
            styled_message = self.term.red(self.message)
            lines.append(styled_message)
            lines.append("")

        if self.game.will_reshuffle:
            styled_message = self.term.yellow("The deck will be reshuffled.")
            lines.append(styled_message)
            lines.append("")

        controls = "[q] Quit  [↑↓] Adjust bet  [1-4] Quick bets  [ENTER] Deal"
        lines.append(controls)

        return lines

    def __is_game_ongoing(self) -> bool:
        return self.game.state != GameState.BETTING

    def handle_input(self, key: str) -> None:
        self.message = ""
        key = key.lower()
        available_money = self.game.available_money

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
