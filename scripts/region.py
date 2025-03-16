from collections import deque
from simulate_game import simulate_game_kenpom
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

    def sim_region(self):
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
            
            game1winner = simulate_game_kenpom(game1.matchup.team1, game1.matchup.team2)
            game1.winner = game1winner

            game2winner = simulate_game_kenpom(game2.matchup.team1, game2.matchup.team2)
            game2.winner = game2winner
                
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
            champ = simulate_game_kenpom(final_game.matchup.team1, final_game.matchup.team2)
            
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
                
            # Assume each node has a 'winner' attribute. Fall back to a placeholder if not.
            winner = getattr(node, "winner", "TBD")
            
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
