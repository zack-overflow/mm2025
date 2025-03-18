from team import Team

class Matchup:
    def __init__(self, team1, team2, location=None):
        self.team1 = team1
        self.team2 = team2
        self.location = location

    @classmethod
    def parse_matchup(cls, matchup_dict):
        """
        Parses a matchup string in the format "Team1 vs Team2" and returns a Matchup object.
        """
        t1 = Team(matchup_dict['team_1']['name'], matchup_dict['team_1']['seed'], matchup_dict['team_1']['link'])
        t2 = Team(matchup_dict['team_2']['name'], matchup_dict['team_2']['seed'], matchup_dict['team_2']['link'])
        
        return cls(t1, t2, matchup_dict['location'])
