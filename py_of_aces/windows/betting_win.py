from .utils import BaseWindow
from py_of_aces.game_logic import BlackjackGame, GameState, Modes


class BettingWindow(BaseWindow):
    message = ""

    def __init__(
        self,
        game: BlackjackGame,
        menu_window: str,
        game_window: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.bet_amount = self.config.game.default_bet
        self.bet_options = self.config.bet_options
        self.game = game
        self.menu_window = menu_window
        self.game_window = game_window

    def draw(self):
        if self.__is_game_ongoing():
            self.switch_win(self.game_window)
            return []

        lines: list[str] = []

        mode_text = ""
        is_practice_mode = self.game.mode == Modes.PRACTICE
        if is_practice_mode:
            mode_text = " (PRACTICE)"

        title = self.term.bold(
            f"{self.term.reverse}PY OF ACES{mode_text}{self.term.normal}",
        )
        lines.append(title)
        lines.append("")

        money_info = self.game.get_money_display
        lines.append(self.term.green(money_info))
        lines.append("")

        bet_display = f"Bet Amount: ${self.bet_amount}"
        lines.append(self.term.bold_yellow(bet_display))
        lines.append("")

        quick_bets = "  ".join(
            f"[{key}] ${amount}" for key, amount in self.bet_options.items()
        )
        lines.append(f"Quick bets: {quick_bets}")
        lines.append("")

        if is_practice_mode:
            lines.append(
                self.term.cyan("Practice Mode: No money lost, tracking total winnings"),
            )
            lines.append("")

        if self.message:
            styled_message = self.term.red(self.message)
            lines.append(styled_message)
            lines.append("")

        if self.game.will_reshuffle:
            styled_message = self.term.yellow("The deck will be reshuffled.")
            lines.append(styled_message)
            lines.append("")

        controls = "[q] Quit  [↑↓] Adjust bet  "
        option_keys = list(self.bet_options)
        if option_keys:
            controls += f"[{option_keys[0]}-{option_keys[-1]}] Quick bets  "
        controls += "[ENTER] Deal"
        lines.append(controls)

        return lines

    def __is_game_ongoing(self) -> bool:
        return self.game.state != GameState.BETTING

    def handle_input(self, key: str) -> None:
        self.message = ""
        key = key.lower()
        available_money = self.game.available_money

        if key in self.config.keys.quit:
            self.switch_win(self.menu_window)

        elif key in self.config.keys.enter:
            if not self.game.place_bet(self.bet_amount):
                self.message = "Invalid bet amount!"
                return

            self.game.deal_initial_cards()
            self.switch_win(self.game_window)

        elif key in self.config.keys.up:
            self.bet_amount = int(min(self.bet_amount + 5, available_money))

        elif key in self.config.keys.down:
            self.bet_amount = max(self.bet_amount - 5, 5)

        elif key in self.bet_options:
            self.bet_amount = int(min(self.bet_options[key], available_money))
