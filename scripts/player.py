class Player:
    def __init__(self, name, ppg, link, ground_truth_total=None):
        self.name = name
        self.ppg = ppg
        self.link = link
        self.ground_truth_total = ground_truth_total
        self.running_total_simulated = 0
