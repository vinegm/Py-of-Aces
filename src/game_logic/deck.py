import random
from src.config import init_num_cards_reshuffle


class Card:
    """
    Represents a single playing card.
    """

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def value(self) -> int | list[int]:
        """Return Blackjack value of the card."""
        if self.rank in ["J", "Q", "K"]:
            return 10

        if self.rank == "A":
            return [1, 11]

        return int(self.rank)


class BlackjackDeck:
    """
    A deck of cards for Blackjack.
    - Supports shuffling
    - Dealing cards
    - Resetting to a new shuffled deck
    """

    suits = ["s", "h", "d", "c"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(
        self, shuffle: bool = True, num_cards_reshuffle: int = init_num_cards_reshuffle
    ):
        self.cards = []
        self.num_cards_reshuffle = num_cards_reshuffle

        self.reset_deck(shuffle=shuffle)

    def __build_deck(self) -> None:
        """Create the deck with the given number of decks."""
        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(Card(rank, suit))

    def shuffle(self) -> None:
        """Shuffle the deck in place."""
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> list[Card]:
        """
        Deal n cards from the deck.

        Returns:
            List of Card objects.
        """
        if n > len(self.cards):
            raise ValueError("Too many cards requested to deal.")

        dealt, self.cards = self.cards[:n], self.cards[n:]
        return dealt

    def reset_deck(self, shuffle: bool = True) -> None:
        """Reset to a full deck again."""
        self.__build_deck()
        if shuffle:
            self.shuffle()

    @property
    def needs_reshuffle(self) -> bool:
        """Check if the deck needs reshuffling."""
        return len(self.cards) < self.num_cards_reshuffle

    def __len__(self) -> int:
        return len(self.cards)
