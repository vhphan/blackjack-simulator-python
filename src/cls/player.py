from src.cls.hand import Hand

class Player:
    def __init__(self, name, money=1000):
        self.name = name
        self.money = money
        self.hands = [Hand()]  # start with one hand
        self.hands_bets = [0]  # total bet per corresponding hand

    def hit(self, card, hand_index=0):
        # add card to specified hand
        if hand_index < len(self.hands):
            self.hands[hand_index].add_card(card)
        else:
            raise IndexError("Hand index out of range.")

    def set_bet(self, bet, hand_index=0):
        if hand_index < len(self.hands_bets):
            self.hands_bets[hand_index] = bet
        else:
            raise IndexError("Hand index out of range.")

    def add_hand(self, hand=None, bet=0):
        # add a new hand or an empty one if not provided
        self.hands.append(hand if hand is not None else Hand())
        self.hands_bets.append(bet)
