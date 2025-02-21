from src.cls.card import Card
from src.cls.deck import Deck
from src.cls.hand import Hand
from src.settings import DEALER_STANDS_ON_SOFT_17

class Dealer:
    def __init__(self):
        self.hand = Hand()

    def reset_hand(self):
        self.hand.cards = []

    def add_card(self, card: Card):
        self.hand.add_card(card)

    def is_soft(self):
        # Compute base total counting aces as 1
        base_total = 0
        ace_count = 0
        for card in self.hand.cards:
            if card.rank == 'A':
                base_total += 1
                ace_count += 1
            else:
                base_total += card.value()
        # If an Ace is being counted as 11 then hand.get_value() > base_total.
        return ace_count > 0 and self.hand.get_value() > base_total

    def play_turn(self, deck: Deck):
        # Dealer hits until total reaches 17 (or 17 soft based on settings)
        while True:
            total = self.hand.get_value()
            soft = self.is_soft()
            if total < 17:
                card = deck.deal()
                if not card:
                    raise ValueError("Deck is empty")
                self.add_card(card)
            elif total == 17 and soft and not DEALER_STANDS_ON_SOFT_17:
                # Hit on soft 17 if rule is disabled.
                card = deck.deal()
                if not card:
                    break
                self.add_card(card)
            else:
                break
