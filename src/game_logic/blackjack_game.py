from enum import Enum
from src.game_logic.deck import BlackjackDeck, Card
from src.game_logic.hand import Hand
from src.game_logic.game_modes import BaseGameMode, NormalMode, PracticeMode
from src.config import default_starting_money


class GameState(Enum):
    BETTING = 0
    DEALING = 1
    PLAYER_TURN = 2
    DEALER_TURN = 3
    GAME_OVER = 4


class GameResult(Enum):
    PLAYER_WIN = 0
    DEALER_WIN = 1
    PUSH = 2
    PLAYER_BLACKJACK = 3
    DEALER_BLACKJACK = 4
    PLAYER_BUST = 5
    DEALER_BUST = 6

winnings_mult_map = {
    GameResult.PLAYER_WIN: 2,
    GameResult.DEALER_BUST: 2,
    GameResult.PLAYER_BLACKJACK: 2.5,
    GameResult.PUSH: 1,
}


class BlackjackGame:
    bets: list[int] = [0]
    state = GameState.BETTING
    result: list[GameResult] | None = None
    dealer_hidden_card = True
    current_hand_index = 0
    hands_finished = 0

    def __init__(self, starting_money: int = default_starting_money):
        self.starting_money = starting_money

        self.deck = BlackjackDeck()
        self.player_hands: list[Hand] = [Hand()]
        self.dealer_hand = Hand(hidden_card_default=True)
        self.mode: BaseGameMode | None = None

    def select_mode(self, selected_mode: str) -> None:
        """Select the game mode."""
        match selected_mode:
            case "normal":
                self.mode = NormalMode(self.starting_money)
            case "practice":
                self.mode = PracticeMode()

    def current_mode_name(self) -> str:
        """Get the name of the current game mode."""
        if isinstance(self.mode, NormalMode):
            return "Normal"
        
        if isinstance(self.mode, PracticeMode):
            return "Practice"

        return "Unknown"

    def start_new_round(self):
        """Start a new round."""
        if len(self.deck) < 15:
            self.deck.reset_deck()

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.player_hands = [Hand()]
        self.bets = [0]
        self.state = GameState.BETTING
        self.result = None
        self.dealer_hand.reset()
        self.dealer_hidden_card = True
        self.current_hand_index = 0
        self.hands_finished = 0

    def place_bet(self, amount: int) -> bool:
        """Place a bet for the current hand. Returns True if successful."""
        if not self.mode.place_bet(amount):
            return False

        self.bets[0] = amount
        return True

    def deal_initial_cards(self):
        """Deal initial cards to player and dealer."""
        self.state = GameState.DEALING

        initial_cards = self.deck.deal(4)

        # Deal to player and dealer (standard dealing order)
        for i, card in enumerate(initial_cards):
            if i % 2 == 0:
                self.player_hands[0].add_card(card)
                continue
            
            self.dealer_hand.add_card(card)

        is_player_blackjack = self.player_hands[0].is_blackjack
        is_dealer_blackjack = self.dealer_hand.is_blackjack

        self.dealer_hidden_card = False
        self.state = GameState.GAME_OVER
        match (is_player_blackjack, is_dealer_blackjack):
            case (True, True):
                self.result = [GameResult.PUSH]

            case (True, False):
                self.result = [GameResult.PLAYER_BLACKJACK]

            case (False, True):
                self.result = [GameResult.DEALER_BLACKJACK]

            case (False, False):
                self.dealer_hidden_card = True
                self.state = GameState.PLAYER_TURN

    def hit(self) -> bool:
        """Player hits. Returns True if successful."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False

        current_hand = self.player_hands[self.current_hand_index]
        current_hand.add_card(self.deck.deal(1)[0])

        if current_hand.is_bust:
            self.__finish_current_hand(GameResult.PLAYER_BUST)

        return True

    def stand(self) -> bool:
        """Player stands. Returns True if successful."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False

        self.__finish_current_hand()
        return True

    def double_down(self) -> bool:
        """Player doubles down. Returns True if successful."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False
        
        if not self.can_double_down():
            return False

        bet_amount = self.bets[self.current_hand_index]
        
        if not self.mode.double_down_bet(bet_amount):
            return False
            
        self.bets[self.current_hand_index] *= 2

        current_hand = self.player_hands[self.current_hand_index]
        current_hand.add_card(self.deck.deal(1)[0])

        if current_hand.is_bust:
            self.__finish_current_hand(GameResult.PLAYER_BUST)
        else:
            self.__finish_current_hand()

        return True

    def split(self) -> bool:
        """Player splits their hand. Returns True if successful."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False

        if not self.can_split():
            return False

        bet_amount = self.bets[0]
        
        if not self.mode.split_bet(bet_amount):
            return False

        original_hand = self.player_hands[0]
        new_hand = Hand()
        
        second_card = original_hand.cards.pop()
        new_hand.add_card(second_card)

        self.player_hands.append(new_hand)
        self.bets.append(bet_amount)

        self.player_hands[0].add_card(self.deck.deal(1)[0])
        self.player_hands[1].add_card(self.deck.deal(1)[0])

        return True

    def __finish_current_hand(self, result: GameResult = None):
        """Finish the current hand and move to next or dealer turn."""
        if result:
            if self.result is None:
                self.result = [None] * len(self.player_hands)
            self.result[self.current_hand_index] = result

        self.hands_finished += 1
        self.current_hand_index += 1

        if self.current_hand_index >= len(self.player_hands):
            self.state = GameState.DEALER_TURN
            self.dealer_hidden_card = False
            self.__dealer_play()

    def __dealer_play(self):
        """Automated dealer play."""
        has_non_busted_hands = False
        if self.result:
            has_non_busted_hands = any(
                result != GameResult.PLAYER_BUST for result in self.result if result
            )
        else:
            has_non_busted_hands = any(not hand.is_bust for hand in self.player_hands)

        if has_non_busted_hands:
            while self.dealer_hand.get_value() < 17:
                self.dealer_hand.add_card(self.deck.deal(1)[0])

        self.__determine_all_winners()
        self.state = GameState.GAME_OVER

    def __determine_all_winners(self):
        """Determine the winner for each hand and set results."""
        dealer_value = self.dealer_hand.get_value()
        dealer_busted = self.dealer_hand.is_bust

        if self.result is None:
            self.result = [None] * len(self.player_hands)

        for i, hand in enumerate(self.player_hands):
            if self.result[i] is not None:
                continue  

            player_value = hand.get_value()

            if dealer_busted:
                self.result[i] = GameResult.DEALER_BUST
                continue

            if player_value == dealer_value:
                self.result[i] = GameResult.PUSH
                continue

            if player_value > dealer_value:
                self.result[i] = GameResult.PLAYER_WIN
                continue

            self.result[i] = GameResult.DEALER_WIN

    def finish_round(self):
        """Finish the round."""
        winnings = self.get_winnings()
        total_bet = self.get_total_bet()
        self.mode.finish_round(winnings, total_bet)

    def get_winnings(self) -> int:
        """Calculate total winnings based on all hand results."""
        if self.result is None:
            return 0

        total_winnings = 0

        for i, result in enumerate(self.result):
            if result is None:
                continue

            bet = self.bets[i]
            mult = winnings_mult_map.get(result, 0)
            
            total_winnings += int(bet * mult)

        return total_winnings

    def get_total_bet(self) -> int:
        """Get total current bet across all hands."""
        return sum(self.bets)

    def get_dealer_hand(self) -> Hand:
        """Get dealer hand, shows only cards that should be visible to player."""
        return self.dealer_hand.get_showing_cards()

    def get_current_hand(self) -> Hand:
        """Get the currently active hand."""
        if self.current_hand_index < len(self.player_hands):
            return self.player_hands[self.current_hand_index]
        
        return self.player_hands[0]

    def can_double_down(self) -> bool:
        """Check if current hand can double down."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False

        if not self.player_hands[self.current_hand_index].can_double_down:
            return False

        bet_amount = self.bets[self.current_hand_index]
        return self.mode.can_afford_bet(bet_amount)

    def can_split(self) -> bool:
        """Check if current hand can be split."""
        if not self.__validate_game_state(GameState.PLAYER_TURN):
            return False

        if not self.player_hands[0].can_split:
            return False

        bet_amount = self.bets[0]
        return self.mode.can_afford_bet(bet_amount)
    
    def get_money_display(self) -> str:
        return self.mode.get_money_display()

    def get_available_money(self) -> int:
        return self.mode.get_available_money()

    def is_broke(self) -> bool:
        return self.mode.is_game_over()

    def __validate_game_state(self, required_state: GameState) -> bool:
        return self.state == required_state
