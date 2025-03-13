from collections import defaultdict
from region import Region
from tournament import Tournament
from load_data import read_unplayed_tournament

def score_strategy(strategy):
    '''
    Need to come up with a score for a certain strategy. Would also be nice to represent the uncertainty somehow.

    Input: a dict representing the players chosen
    '''

    

def parse_round():
    pass


def simulate_n_tournaments(matchups_dict, N=100):
    champions = defaultdict(int)

    # for _ in range(N):
    #     east = Region(matchups_dict["east"])
    #     east.sim_region()
    #     champ = east.championship.winner
    #     champions[str(champ)] += 1

    for _ in range(N):
        east = Region(matchups_dict["east"])
        west = Region(matchups_dict["west"])
        south = Region(matchups_dict["south"])
        midwest = Region(matchups_dict["midwest"])

        tourney = Tournament(east, west, south, midwest)
        tourney.simulate_tournament()
        champ = tourney.east.championship.winner

        champions[str(champ)] += 1

    # Convert to probabilities
    champion_probs = {team: count / N for team, count in champions.items()}
    return champion_probs

def main():
    east_2024_list = read_unplayed_tournament(2024, "east")
    west_2024_list = read_unplayed_tournament(2024, "west")
    south_2024_list = read_unplayed_tournament(2024, "south")
    midwest_2024_list = read_unplayed_tournament(2024, "midwest")

    matchups_dict = {
        "east": east_2024_list,
        "west": west_2024_list,
        "south": south_2024_list,
        "midwest": midwest_2024_list
    }

    print(simulate_n_tournaments(matchups_dict, N=1000))

print(main())
