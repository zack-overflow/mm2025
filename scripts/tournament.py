from region import Region, Matchup, Node
from collections import defaultdict
from copy import deepcopy

class Tournament:        
    def __init__(self, east_matchups, west_matchups, south_matchups, midwest_matchups, player_dict):
        self.east = east_matchups
        self.west = west_matchups
        self.south = south_matchups
        self.midwest = midwest_matchups
        self.players_bookkeeping = deepcopy(player_dict) # dict of dicts (team_name -> player_name -> total points scored)
        self.championship = None

    def simulate_tournament(self, ratings_df, method, player_bk_used=True):
        for region in [self.east, self.west, self.south, self.midwest]:
            region.sim_region(ratings_df, self.players_bookkeeping, method, player_bk_used=player_bk_used)
            # region.print_region()

        # final four matchups
        sw_matchup = Matchup(self.south.championship.winner, self.west.championship.winner)
        sw_node = Node(matchup=sw_matchup)
        emw_matchup = Matchup(self.east.championship.winner, self.midwest.championship.winner)
        emw_node = Node(matchup=emw_matchup)
        
        final_four = Region([])
        final_four.matchup_q.append(sw_node)
        final_four.matchup_q.append(emw_node)
        final_four.sim_region(ratings_df, self.players_bookkeeping, method, player_bk_used=player_bk_used)
        self.championship = final_four.championship

    def bracket_distance(team1, team2):
        '''
        How many games it will take before team1 plays team2 if they keep winning.
        '''
        pass
