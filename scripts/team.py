class Team:
    def __init__(self, team_name, seed, link):
        self.team_name = team_name
        self.seed = seed
        self.link = link
        # self.roster = load_team_roster(link)
    
    def __str__(self):
        return f"{self.team_name} ({self.seed})"