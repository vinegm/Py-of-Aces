from .utils import BaseWindow
from ..utils import get_card_ascii, join_cards
from ..game_logic import BlackjackGame, GameResult, GameState, Hand, Modes
from ..config import enter_keys, quit_keys

result_text_mapping = {
    GameResult.WIN: "YOU WIN",
    GameResult.BLACKJACK: "BLACKJACK! You win",
    GameResult.LOSE: "Dealer wins. You lose",
    GameResult.PUSH: "PUSH! Bet returned",
}


class GameWindow(BaseWindow):
    def __init__(
        self, game: BlackjackGame, menu_window: str, betting_window: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.game = game
        self.message = ""
        self.menu_window = menu_window
        self.betting_window = betting_window

    def draw(self):
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
        money_info += f" | Total Bet: ${self.game.total_bet}"
        lines.append(money_info)
        lines.append("")

        lines.extend(self.__draw_hands())
        lines.append("")

        if self.game.state == GameState.ROUND_FINISHED:
            lines.extend(self.__draw_game_result())
            lines.append("")

        if self.message:
            styled_message = self.term.red(self.message)
            lines.append(styled_message)
            lines.append("")

        if self.game.will_reshuffle:
            styled_message = self.term.yellow(
                "After this round, the deck will be reshuffled."
            )
            lines.append(styled_message)
            lines.append("")

        lines.extend(self.__draw_controls())

        return lines

    def __draw_hands(self) -> list[str]:
        lines: list[str] = []
        lines.append("DEALER")

        dealer_hand = self.game.dealer_hand
        lines.extend(self.__draw_cards(dealer_hand))
        lines.append("")

        lines.append("PLAYER")

        has_multiple_hands = len(self.game.player_hands) > 1
        for hand_index, hand in enumerate(self.game.player_hands):
            if has_multiple_hands:
                hand_title = f"Hand {hand_index + 1} ({self.game.bets[hand_index]}$)"
                if hand_index == self.game.current_hand_index:
                    hand_title += " (ACTIVE)"

                lines.append(hand_title)

            lines.extend(self.__draw_cards(hand))

        return lines

    def __draw_cards(self, hand: Hand) -> list[str]:
        lines: list[str] = []
        card_arts = []
        has_hidden = hand.has_hidden_card

        for card in hand.get_showing_cards():
            card_art = get_card_ascii(card.rank, card.suit)
            card_arts.append(card_art)

        if has_hidden:
            hidden_art = get_card_ascii("?", "?", face_down_text="HIDDEN")
            card_arts.append(hidden_art)

        combined_cards = join_cards(*card_arts)
        for line in combined_cards.splitlines():
            lines.append(line)

        hand_info = ""
        if has_hidden:
            hand_info += f"Showing: {hand.get_showing_value()}"
            lines.append(hand_info)
            return lines

        hand_info += f"Total: {hand.get_showing_value()}"
        if hand.is_blackjack:
            hand_info += " (BLACKJACK!)"

        elif hand.is_bust:
            hand_info += " (BUST!)"

        lines.append(hand_info)
        return lines

    def __draw_game_result(self) -> list[str]:
        lines: list[str] = []
        total_winnings = self.game.get_winnings()

        summary_text = ""
        if total_winnings > 0:
            summary_text += f"Result: +{total_winnings}$"
        else:
            total_bet = self.game.total_bet
            summary_text += f"Result: -{total_bet}$"

        styled_result = self.term.bold_green(summary_text)
        lines.append(styled_result)
        return lines

    def __draw_controls(self) -> list[str]:
        controls = ""
        match self.game.state:
            case GameState.PLAYER_TURN:
                controls += "[h] Hit  [SPACE] Stand"

                if self.game.can_double_down:
                    controls += "  [d] Double Down"

                if self.game.can_split:
                    controls += "  [p] Split"

                controls += "  [q] Quit"

            case GameState.ROUND_FINISHED:
                if self.game.available_money > 0:
                    controls += "[ENTER] New Round  "
                controls += "[r] Restart money  "
                controls += "[q] Quit"

        return [controls]

    def handle_input(self, key: str) -> None:
        """Handle user input based on the current game state."""
        self.message = ""
        self.info = ""
        key = key.lower()

        if key in quit_keys:
            self.switch_win(self.menu_window)
            return

        if self.game.state == GameState.PLAYER_TURN:
            self.__handle_player_turn_input(key)
            return

        if self.game.state != GameState.ROUND_FINISHED:
            return

        if key == "r":
            self.game.reset_money()

        if key in enter_keys:
            self.game.finish_round()
            if self.game.is_game_over:
                self.message = "Game Over! No money left."
                return

        self.game.start_new_round()
        self.switch_win(self.betting_window)

    def __handle_player_turn_input(self, key: str):
        """Handle input during the player's turn."""
        match key:
            case "h":
                if not self.game.hit():
                    self.message = "Cannot hit right now!"

            case " ":
                if not self.game.stand():
                    self.message = "Cannot stand right now!"

            case "d":
                if not self.game.double_down():
                    self.message = "Cannot double down!"

            case "s":
                if not self.game.split():
                    self.message = "Cannot split without a pair!"
