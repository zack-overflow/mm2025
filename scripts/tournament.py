from region import Region, Matchup
from collections import defaultdict

class Tournament:        
    def __init__(self, east_matchups, west_matchups, south_matchups, midwest_matchups):
        self.east = east_matchups
        self.west = west_matchups
        self.south = south_matchups
        self.midwest = midwest_matchups
        self.players_bookkeeping = None

    def simulate_tournament(self):
        for region in [self.east, self.west, self.south, self.midwest]:
            region.sim_region()
            region.print_region()

        # final four matchups
        ew_matchup = Matchup(self.east.championship.winner, self.west.championship.winner)
        sm_matchup = Matchup(self.south.championship.winner, self.midwest.championship.winner)
        final_four = Region()
        final_four.matchup_q.append(ew_matchup, sm_matchup)
        final_four.sim_region()
        final_four.print_region()
        overall_champ = final_four.championship.winner
        print(f"---\n---\nOverall Champion: {overall_champ}")

    def bracket_distance(team1, team2):
        '''
        How many games it will take before team1 plays team2 if they keep winning.
        '''
        pass
