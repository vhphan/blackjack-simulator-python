import os

class SimulationLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        # Clear file at start
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("Turn by Turn Simulation Log\n\n")

    def log(self, message):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            print(message)
            f.write(message + "\n")
