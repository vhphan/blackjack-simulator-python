from src.cls.deck import Deck
from src.cls.player import Player
from src.cls.dealer import Dealer
from src.helpers.simulation_logger import SimulationLogger
import os

class BlackjackGame:
    def __init__(self, player_names, initial_money=1000):
        self.deck = Deck()
        self.players = [Player(name, money=initial_money) for name in player_names]
        self.logger = SimulationLogger(os.path.join(os.getcwd(), "src/outputs/simulation_log.txt"))




