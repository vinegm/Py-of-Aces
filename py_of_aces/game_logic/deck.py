import random


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
        self,
        shuffle: bool = True,
        num_decks: int = 1,
        num_cards_reshuffle: int = 15,
    ):
        self.cards = []
        self.on_table: list[Card] = []
        self.num_decks = max(num_decks, 1)
        self.num_cards_reshuffle = num_cards_reshuffle

        self.reset_deck(shuffle=shuffle)

    def __build_deck(self) -> None:
        """Create the deck with the given number of decks."""
        for _ in range(self.num_decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(rank, suit))

    def shuffle(self) -> None:
        """Shuffle the deck in place."""
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> list[Card]:
        """
        Deal n cards from the deck, reshuffling the
        cards not on the table if it runs out.
        """
        if n > len(self.cards):
            self.__reshuffle_around_table()

        if n > len(self.cards):
            raise ValueError("Too many cards requested to deal.")

        dealt, self.cards = self.cards[:n], self.cards[n:]
        self.on_table.extend(dealt)
        return dealt

    def clear_table(self) -> None:
        """Forget the cards dealt, as a round ended."""
        self.on_table = []

    def __reshuffle_around_table(self) -> None:
        """Rebuild the shoe without the cards still on the table."""
        self.cards = []
        self.__build_deck()
        for card in self.on_table:
            self.__remove_from_shoe(card)

        self.shuffle()

    def __remove_from_shoe(self, card: Card) -> None:
        """Take one copy of the card out of the shoe."""
        for shoe_card in self.cards:
            if (shoe_card.rank, shoe_card.suit) == (card.rank, card.suit):
                self.cards.remove(shoe_card)
                return

    def reset_deck(self, shuffle: bool = True) -> None:
        """Reset to a full deck again."""
        self.cards = []
        self.on_table = []
        self.__build_deck()
        if shuffle:
            self.shuffle()

    @property
    def needs_reshuffle(self) -> bool:
        """Check if the deck needs reshuffling."""
        return len(self.cards) < self.num_cards_reshuffle

    def __len__(self) -> int:
        return len(self.cards)
