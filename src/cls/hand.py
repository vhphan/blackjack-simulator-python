
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total = sum(card.value() for card in self.cards)
        num_aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and num_aces:
            total -= 10
            num_aces -= 1
        return total

    def __repr__(self):
        return ', '.join(map(str, self.cards))
