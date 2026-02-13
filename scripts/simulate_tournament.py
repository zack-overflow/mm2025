from tqdm import tqdm
from collections import defaultdict
from region import Region
from tournament import Tournament

def simulate_n_tournaments(matchups_dict, players_dict, ratings_df, method, N=100, player_bk_used=True):
    champions = defaultdict(int)
    sims = []

    for i in tqdm(range(N)):
        east = Region(matchups_dict["east"])
        west = Region(matchups_dict["west"])
        south = Region(matchups_dict["south"])
        midwest = Region(matchups_dict["midwest"])

        tourney = Tournament(east, west, south, midwest, players_dict)
        tourney.simulate_tournament(ratings_df, method, player_bk_used=player_bk_used)
        champ = tourney.championship.winner
        sims.append(tourney)

        champions[str(champ)] += 1
        # print(f"---\n---\n Sim {i}, Overall Champion: {champ}")

    # Convert to probabilities
    champion_probs = {team: count / N for team, count in champions.items()}
    return champion_probs, sims
