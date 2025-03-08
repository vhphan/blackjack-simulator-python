from src.cls.card import Card


class Hand:
    def __init__(self):
        self.cards = []
        self._value = None

    @property
    def value(self) -> int:
        if self._value is None:
            self._value = self._calculate_value()
        return self._value

    def add_card(self, card: Card) -> None:
        self.cards.append(card)
        self._value = None  # Invalidate cached value

    def _calculate_value(self) -> int:
        """
        Calculate the total value of the hand, adjusting for Aces to prevent exceeding 21.
    
        Returns:
            int: The total value of the hand.
        """
        total = sum(card.value() for card in self.cards)
        num_aces = sum(card.rank == 'A' for card in self.cards)

        while total > 21 and num_aces:
            total -= 10
            num_aces -= 1
        return total

    def get_winnings(self, dealer_value: int) -> int:
        """
        Determine the outcome (win, loss, draw) based on the hand's value and the dealer's hand value.
    
        Args:
            dealer_value (int): The value of the dealer's hand.
    
        Returns:
            int: -1 for loss, 1 for win, 0 for draw.
        """
        if self.value > 21:
            print(f'Player bust: Player value: {self.value}, Dealer value: {dealer_value}')
            return -1  # Loss
        elif self.value > dealer_value or dealer_value > 21:
            return 1  # Win
        elif self.value == dealer_value:
            return 0  # Draw
        else:
            print(f'Player loses: Player value: {self.value}, Dealer value: {dealer_value}')
            return -1  # Loss

    def __repr__(self) -> str:
        return ', '.join(map(str, self.cards))
