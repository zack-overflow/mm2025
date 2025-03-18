class Team:
    def __init__(self, team_name, seed, link):
        self.team_name = team_name
        self.seed = int(seed)
        self.link = link
        # self.roster = load_team_roster(link)

    def get_multiplier(self):
        if self.seed < 6:
            return 1
        elif self.seed < 13:
            return 2
        else:
            return 3
    
    def __str__(self):
        return f"{self.team_name} ({self.seed})"