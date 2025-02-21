from src.cls.card import Card, Suit
from src.settings import NUM_DECKS  # import number of decks from settings
import random

class Deck:
    def __init__(self):
        self.cards = []
        for _ in range(NUM_DECKS):
            self.cards.extend([Card(suit, rank)
                               for suit in [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
                               for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']])
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop() if self.cards else None
