from enum import Enum
from .deck import BlackjackDeck
from .hand import Hand
from .game_modes import Modes, BaseGameMode, NormalMode, PracticeMode
from ..config import init_starting_money, init_dealer_stand_value, init_max_splits


class GameState(Enum):
    BETTING = 0
    DEALING = 1
    PLAYER_TURN = 2
    DEALER_TURN = 3
    ROUND_FINISHED = 4


class GameResult(Enum):
    LOSE = 1
    PUSH = 2
    WIN = 3
    BLACKJACK = 4


winnings_mult_map = {
    GameResult.LOSE: 0,
    GameResult.PUSH: 1,
    GameResult.WIN: 2,
    GameResult.BLACKJACK: 2.5,
}


class BlackjackGame:
    def __init__(
        self,
        starting_money: int = init_starting_money,
        dealer_stand_value: int = init_dealer_stand_value,
        max_splits: int = init_max_splits,
    ):
        self.starting_money = starting_money
        self.max_splits = max_splits

        self.deck = BlackjackDeck()
        self.dealer_hand = Hand(hidden_card_default=True)
        self.dealer_stand_value = dealer_stand_value
        self.player_hands: list[Hand] = [Hand()]
        self.current_hand_index: int = 0

        self.bets: list[int] = [0]
        self.current_mode: BaseGameMode | None = BaseGameMode

        self.state: GameState = GameState.BETTING
        self.results: list[GameResult | None] = [None]

    @property
    def current_hand(self) -> Hand:
        """Get the currently active hand."""
        if self.current_hand_index < len(self.player_hands):
            return self.player_hands[self.current_hand_index]

        return self.player_hands[0]

    @property
    def has_more_hands(self) -> bool:
        """Check if there are more hands to play after the current one."""
        return self.current_hand_index < len(self.player_hands) - 1

    @property
    def is_game_over(self) -> bool:
        return self.current_mode.is_game_over

    @property
    def total_bet(self) -> int:
        return sum(self.bets)

    @property
    def can_double_down(self) -> bool:
        """Check if current hand can double down."""
        if self.state != GameState.PLAYER_TURN:
            return False

        if not self.current_hand.can_double_down:
            return False

        bet_amount = self.bets[self.current_hand_index]
        return self.current_mode.can_afford_bet(bet_amount)

    @property
    def can_split(self) -> bool:
        """Check if current hand can be split."""
        if self.state != GameState.PLAYER_TURN:
            return False

        # max hands = max splits + 1 original hand
        if len(self.player_hands) >= self.max_splits + 1:
            return False

        if not self.current_hand.can_split:
            return False

        bet_amount = self.bets[self.current_hand_index]
        return self.current_mode.can_afford_bet(bet_amount)

    @property
    def get_money_display(self) -> str:
        return self.current_mode.get_money_display()

    @property
    def available_money(self) -> int:
        return self.current_mode.get_available_money()

    @property
    def mode(self) -> Modes:
        return self.current_mode.mode_type

    @property
    def will_reshuffle(self) -> bool:
        return self.deck.needs_reshuffle

    def select_mode(self, selected_mode: Modes) -> None:
        """Select the game mode."""
        if selected_mode == self.mode:
            return

        match selected_mode:
            case Modes.NORMAL:
                self.current_mode = NormalMode(self.starting_money)
                self.__reset_game()
            case Modes.PRACTICE:
                self.current_mode = PracticeMode()
                self.__reset_game()

    def finish_round(self) -> None:
        """Finish the round."""
        winnings = self.get_winnings()
        total_bet = self.total_bet

        self.current_mode.finish_round(winnings, total_bet)

    def start_new_round(self):
        """Start a new round."""
        if self.deck.needs_reshuffle:
            self.deck.reset_deck()

        self.__reset_game()

    def __reset_game(self):
        """Reset the game to initial state."""
        self.dealer_hand.reset()
        self.player_hands = [Hand()]
        self.current_hand_index = 0

        self.bets = [0]

        self.state = GameState.BETTING
        self.results = [None]

    def reset_money(self):
        """Reset the current game mode."""
        self.current_mode.reset_money()

    def place_bet(self, amount: int) -> bool:
        """Place a bet for the current hand. Returns True if successful."""
        if not self.current_mode.place_bet(amount):
            return False

        self.bets[self.current_hand_index] = amount
        return True

    def deal_initial_cards(self):
        """Deal initial cards to player and dealer."""
        self.state = GameState.DEALING

        # Deal 2 cards to player, 2 to dealer (alternating)
        for _ in range(2):
            self.player_hands[0].add_card(self.deck.deal(1)[0])
            self.dealer_hand.add_card(self.deck.deal(1)[0])

        is_player_blackjack = self.player_hands[0].is_blackjack
        is_dealer_blackjack = self.dealer_hand.is_blackjack

        self.state = GameState.ROUND_FINISHED
        match (is_player_blackjack, is_dealer_blackjack):
            case (True, True):
                self.results = [GameResult.PUSH]

            case (True, False):
                self.results = [GameResult.BLACKJACK]

            case (False, True):
                self.results = [GameResult.LOSE]

            case (False, False):
                self.state = GameState.PLAYER_TURN

    def hit(self) -> bool:
        """Player hits. Returns True if successful."""
        if self.state != GameState.PLAYER_TURN:
            return False

        self.current_hand.add_card(self.deck.deal(1)[0])

        if self.current_hand.is_bust:
            self.__finish_current_hand(GameResult.LOSE)

        return True

    def stand(self) -> bool:
        """Player stands. Returns True if successful."""
        if self.state != GameState.PLAYER_TURN:
            return False

        self.__finish_current_hand()
        return True

    def double_down(self) -> bool:
        """Player doubles down. Returns True if successful."""
        if self.state != GameState.PLAYER_TURN or not self.can_double_down:
            return False

        bet_amount = self.bets[self.current_hand_index]

        if not self.current_mode.double_down_bet(bet_amount):
            return False

        self.bets[self.current_hand_index] *= 2

        self.current_hand.add_card(self.deck.deal(1)[0])

        if self.current_hand.is_bust:
            self.__finish_current_hand(GameResult.LOSE)
        else:
            self.__finish_current_hand()

        return True

    def split(self) -> bool:
        """Player splits their hand. Returns True if successful."""
        if self.state != GameState.PLAYER_TURN or not self.can_split:
            return False

        bet_amount = self.bets[self.current_hand_index]

        if not self.current_mode.split_bet(bet_amount):
            return False

        original_hand = self.current_hand
        new_hand = self.__create_new_hand(bet_amount)

        second_card = original_hand.cards.pop()
        new_hand.add_card(second_card)

        original_hand.add_card(self.deck.deal(1)[0])
        new_hand.add_card(self.deck.deal(1)[0])

        return True

    def __create_new_hand(self, bet: int) -> Hand:
        """Create a new hand for the player and return it."""
        new_hand = Hand()

        self.player_hands.append(new_hand)
        self.bets.append(bet)
        self.results.append(None)

        return new_hand

    def __finish_current_hand(self, result: GameResult = None) -> None:
        """Finish the current hand and move to next or dealer turn."""
        if result is not None:
            self.results[self.current_hand_index] = result

        if self.has_more_hands:
            self.current_hand_index += 1
            return

        self.state = GameState.DEALER_TURN
        self.__dealer_play()

    def __dealer_play(self) -> None:
        """Automated dealer play."""
        if self.__has_non_busted():
            while self.dealer_hand.get_value() < self.dealer_stand_value:
                self.dealer_hand.add_card(self.deck.deal(1)[0])

        self.__determine_winners()
        self.dealer_hand.has_hidden_card = False
        self.state = GameState.ROUND_FINISHED

    def __has_non_busted(self) -> bool:
        """Check if there is at least one non-busted player hand."""
        if None in self.results:
            return True

        return False

    def __determine_winners(self) -> None:
        """Determine the winner for each hand and set results."""
        dealer_value = self.dealer_hand.get_value()
        dealer_busted = self.dealer_hand.is_bust

        for i, hand in enumerate(self.player_hands):
            if self.results[i] is not None:
                continue

            player_value = hand.get_value()

            if dealer_busted:
                self.results[i] = GameResult.WIN
                continue

            if player_value == dealer_value:
                self.results[i] = GameResult.PUSH
                continue

            if player_value > dealer_value:
                self.results[i] = GameResult.WIN
                continue

            self.results[i] = GameResult.LOSE

    def get_winnings(self) -> int:
        """Calculate total winnings based on all hand results."""
        total_winnings = 0

        for i, result in enumerate(self.results):
            if result is None:
                continue

            bet = self.bets[i]
            mult = winnings_mult_map.get(result, 0)

            total_winnings += int(bet * mult)

        return total_winnings
