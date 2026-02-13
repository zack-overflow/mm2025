from collections import deque
from simulate_game import simulate_game, handle_player_bookkeeping_for_team
from matchup import Matchup

class Node:
    def __init__(self, matchup=None, left=None, right=None, parent=None):
        self.matchup = matchup
        self.left = left
        self.right = right
        self.parent = parent
        self.winner = None  # Winning team from this matchup

    def is_leaf(self):
        return self.left is None and self.right is None

class Region:
    def __init__(self, matchups):
        if len(matchups) > 0:
            self.matchup_q = deque(self.parse_matchups_into_nodes(matchups))
        else:
            self.matchup_q = deque()
        self.championship = None

    def parse_matchups_into_nodes(self, matchups_list):
        '''
        Takes a list of matchups and creates a tree of matchups.
        '''
        nodes = []
        for matchup in matchups_list:
            # Parse the matchup and create a Matchup object
            Matchup_obj = Matchup.parse_matchup(matchup)
            # Create a Node object for the matchup
            node = Node(matchup=Matchup_obj)
            nodes.append(node)
        
        return nodes

    def sim_region(self, ratings_df, player_bk_dict, method):
        '''
        Starting from initial matchups, sims a region of the tournament.
        '''
        # east plays west and south plays midwest in final four, so process east, west, south, midwest in that order
        # could start simulations in parallel when you add games to the queue
        while len(self.matchup_q) >= 2:
            game1 = self.matchup_q.popleft()  # pop the first game
            game2 = self.matchup_q.popleft()  # pop the second game

            # simulate those two games and do appropriate calculation and bookkeeping
            # uncertainty could be here in terms of player score (use reg. season to make distribution?)
            # simulation will lead to uncertainty in game outcomes
            
            game1winner = simulate_game(game1.matchup.team1, game1.matchup.team2, ratings_df, method)
            game1.winner = game1winner

            # Handle player bookkeeping for game 1; include seed multiplier
            handle_player_bookkeeping_for_team(player_bk_dict, game1.matchup.team1)
            handle_player_bookkeeping_for_team(player_bk_dict, game1.matchup.team2)
            
            game2winner = simulate_game(game2.matchup.team1, game2.matchup.team2, ratings_df, method)
            game2.winner = game2winner

            # Handle player bookkeeping for game 2; include seed multiplier
            handle_player_bookkeeping_for_team(player_bk_dict, game2.matchup.team1)
            handle_player_bookkeeping_for_team(player_bk_dict, game2.matchup.team2)

            # TODO: Update team ratings based on simulated game outcomes

            # create new Game object with the winner of those two games
            new_game = Node(matchup=Matchup(game1winner, game2winner))
            
            # set the left and right children of the new game
            new_game.left = game1
            new_game.right = game2
            
            # mark the game as the parent of the other two games
            game1.parent = new_game
            game2.parent = new_game

            # add the new game to queue
            self.matchup_q.append(new_game)
        
        # sim championship
        if len(self.matchup_q) == 1:
            final_game = self.matchup_q.popleft()
            champ = simulate_game(final_game.matchup.team1, final_game.matchup.team2, ratings_df, method)
            
            final_game.winner = champ
        
            self.championship = final_game
        else:
            raise Exception("Error: Region simulation did not end with a single championship game.")
    
    def print_region(self):
        '''
        Prints the bracket in a readable format.
        '''
        def print_node(node, indent=""):
            if node is None:
                return
            
            green_color = "\033[92m"
            reset_color = "\033[0m"
            
            # If the node has children, print them in a bracket-like structure.
            if node.is_leaf():
                if node.winner == node.matchup.team1:
                    print(indent + "├──" + f"{green_color}{node.matchup.team1}{reset_color}")
                    print(indent + "└──" + str(node.matchup.team2))
                else:
                    print(indent + "├──" + str(node.matchup.team1))
                    print(indent + "└──" + f"{green_color}{node.matchup.team2}{reset_color}")
           
            else:
                # find winner of the game
                if node.winner == node.matchup.team1:
                    print(indent + "├──" + f"{green_color}{node.matchup.team1}{reset_color}")
                    print_node(node.left, indent + "│   ")
                    print(indent + "└──" + str(node.matchup.team2))
                    print_node(node.right, indent + "    ")
                else:
                    print(indent + "├──" + str(node.matchup.team1))
                    print_node(node.left, indent + "│   ")
                    print(indent + "└──" + f"{green_color}{node.matchup.team2}{reset_color}")
                    print_node(node.right, indent + "    ")
                
        print(self.championship.winner)
        print_node(self.championship)

if __name__ == "__main__":
    # Example usage
    from load_team_data import read_unplayed_tournament, parse_silver_ratings, full_kenpom_pipeline
    year = 2025
    matchups = read_unplayed_tournament(year)["south"]
    for matchup in matchups:
        print(matchup)

    
    # Create a Region object with the matchups
    silver_path = '../data/silver.csv'  # Replace with actual path
    silver_ratings = parse_silver_ratings(silver_path)
    kenpom_ratings = full_kenpom_pipeline(2025)  # Load KenPom ratings for the year
    print(silver_ratings.head())  # Print the silver ratings for verification


    # Simulate the region with dummy ratings and player bookkeeping 1000 times
    probs_of_champ_silver = {}
    probs_of_champ_kenpom = {}
    n = 5000
    for _ in range(n):
        region = Region(matchups)
        region2 = Region(matchups)
        region.sim_region(silver_ratings, {}, method='silver')
        region2.sim_region(kenpom_ratings, {}, method='kenpom')
        champ1 = region.championship.winner.team_name
        champ2 = region2.championship.winner.team_name
        if champ1 not in probs_of_champ_silver:
            probs_of_champ_silver[champ1] = 1
        else:
            probs_of_champ_silver[champ1] += 1
        if champ2 not in probs_of_champ_kenpom:
            probs_of_champ_kenpom[champ2] = 1
        else:
            probs_of_champ_kenpom[champ2] += 1

    # Print the probabilities of each team winning the championship sorted by their chances
    sorted_probs = sorted(probs_of_champ_kenpom.items(), key=lambda x: x[1], reverse=True)
    print("Probabilities of each team winning the south region kenpom:")
    for team, prob in sorted_probs:
        # Print the team and its probability
        print(f"{team}: {prob / n:.2%}")

    sorted_probs = sorted(probs_of_champ_silver.items(), key=lambda x: x[1], reverse=True)
    print("Probabilities of each team winning the south region silver:")
    for team, prob in sorted_probs:
        # Print the team and its probability
        print(f"{team}: {prob / n:.2%}")
