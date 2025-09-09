from src.windows.utils import BaseWindow
from src.utils import get_card_ascii, join_cards
from src.game_logic import BlackjackGame, GameState, GameResult, Hand
from src.config import *

result_text_mapping = {
    GameResult.PLAYER_WIN: "YOU WIN",
    GameResult.PLAYER_BLACKJACK: "BLACKJACK! You win",
    GameResult.DEALER_BUST: "DEALER BUSTS! You win",
    GameResult.DEALER_WIN: "Dealer wins. You lose",
    GameResult.DEALER_BLACKJACK: "Dealer blackjack. You lose",
    GameResult.PLAYER_BUST: "BUST! You lose",
    GameResult.PUSH: "PUSH! Bet returned"
}


class GameWindow(BaseWindow):
    message = ""
    def __init__(self, game: BlackjackGame, menu_window: str, betting_window: str, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.menu_window = menu_window
        self.betting_window = betting_window

    def draw(self):
        print(self.term.clear)

        mode_text = ""
        if self.game.current_mode_name() == "Practice":
            mode_text = " (PRACTICE)"
        
        title = self.term.bold("PY OF ACES - BLACKJACK" + mode_text)
        print(self.term.center(title))
        print()

        money_info = self.game.get_money_display()
        money_info += f" | Total Bet: ${self.game.get_total_bet()}"
        print(self.term.center(money_info))
        print()

        self.__draw_hands()
        print()
        if self.game.state == GameState.GAME_OVER:
            self.__draw_game_result()
            print()

        if self.message:
            styled_message = self.term.yellow(self.message)
            print(self.term.center(styled_message))
            print()

        self.__draw_controls()

    def __draw_hands(self):
        print(self.term.center("DEALER"))

        dealer_hand = self.game.get_dealer_visible_hand()
        dealer_hidden = self.game.state != GameState.GAME_OVER
        self.__draw_cards(dealer_hand, append_hidden=dealer_hidden)
        print()

        print(self.term.center("PLAYER"))

        has_multiple_hands = len(self.game.player_hands) > 1
        for hand_index, hand in enumerate(self.game.player_hands):
            if has_multiple_hands:
                hand_title = f"Hand {hand_index + 1} ({self.game.bets[hand_index]}$)"
                if hand_index == self.game.current_hand_index:
                    hand_title += " (ACTIVE)"

                print(self.term.center(hand_title))

            self.__draw_cards(hand)

    def __draw_cards(self, hand: Hand, append_hidden: bool = False) -> None:
        card_arts = []

        for card in hand.cards:
            card_art = get_card_ascii(card.rank, card.suit)
            card_arts.append(card_art)

        if append_hidden:
            hidden_art = get_card_ascii("?", "?", face_down_text="HIDDEN")
            card_arts.append(hidden_art)

        combined_cards = join_cards(*card_arts)
        for line in combined_cards.splitlines():
            print(self.term.center(line))

        hand_info = ""
        if append_hidden:
            hand_info += f"Showing: {hand.get_value()}"
            print(self.term.center(hand_info))
            return

        hand_info += f"Total: {hand.get_value()}"        
        if hand.is_blackjack():
            hand_info += " (BLACKJACK!)"
        
        elif hand.is_bust:
            hand_info += " (BUST!)"

        print(self.term.center(hand_info))

    def __draw_game_result(self) -> None:
        total_winnings = self.game.get_winnings()

        summary_text = ""
        if total_winnings > 0:
            summary_text += f"Result: +{total_winnings}$"
        else:
            total_bet = self.game.get_total_bet()
            summary_text += f"Result: -{total_bet}$"
        
        styled_result = self.term.bold_green(summary_text)
        print(self.term.center(styled_result))

    def __draw_controls(self):
        controls = ""
        match self.game.state:
            case GameState.PLAYER_TURN:
                controls += "[h] Hit  [s] Stand"

                if self.game.can_double_down():
                    controls += "  [d] Double Down"

                if self.game.can_split():
                    controls += "  [p] Split"

                controls += "  [q] Quit"

            case GameState.GAME_OVER:
                controls += "[SPACE] New Round [q] Quit"

        print(self.term.center(controls))

    def handle_input(self, key: str) -> None:
        """Handle user input based on the current game state."""
        self.message = ""
        key = key.lower()

        if key in quit_keys:
            self.switch_win(self.menu_window)
            return

        match self.game.state:
            case GameState.PLAYER_TURN:
                self.__handle_player_turn_input(key)
            
            case GameState.GAME_OVER:
                self.__handle_game_over_input(key)

    def __handle_player_turn_input(self, key: str):
        """Handle input during the player's turn."""
        match key:
            case "h":
                if not self.game.hit():
                    self.message = "Cannot hit right now!"

            case "s":
                if not self.game.stand():
                    self.message = "Cannot stand right now!"

            case "d":
                if not self.game.double_down():
                    self.message = "Cannot double down!"

            case "p":
                if not self.game.split():
                    self.message = "Cannot split!"

    def __handle_game_over_input(self, key: str) -> None:
        """Handle input when the game is over."""
        if key in enter_keys:
            self.game.finish_round()
            if self.game.is_broke():
                self.message = "Game Over! No money left."
                return
            
            self.game.start_new_round()
            self.switch_win(self.betting_window)
