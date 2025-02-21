from src.cls.deck import Deck
from src.cls.player import Player
from src.cls.dealer import Dealer

class BlackjackGame:
    def __init__(self, player_names, initial_money=1000):
        self.deck = Deck()
        self.players = [Player(name, money=initial_money) for name in player_names]

    def initial_deal(self):
        # deal two cards to each player's first hand
        for _ in range(2):
            for player in self.players:
                card = self.deck.deal()
                if card:
                    player.hit(card)

    def play_round(self):
        self.initial_deal()
        # additional game logic can be added here
        return {player.name: [str(hand) for hand in player.hands] for player in self.players}

# ...existing code or further enhancements...
