import sys


class SimulationLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_file_obj = open(self.log_file, 'w', encoding='utf-8')
        self.log_file_obj.write("Turn by Turn Simulation Log\n\n")

    def log(self, message):
        print(message)
        self.log_file_obj.write(message + "\n")

    def close(self):
        sys.stdout = sys.__stdout__
        self.log_file_obj.close()


logger = SimulationLogger("src/outputs/simulation_log.txt");
