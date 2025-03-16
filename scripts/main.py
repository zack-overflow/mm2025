import pandas as pd
from collections import defaultdict
from region import Region
from tournament import Tournament
from load_data import read_unplayed_tournament, load_player_data

def score_strategy(strategy):
    '''
    Need to come up with a score for a certain strategy. Would also be nice to represent the uncertainty somehow.

    Input: a dict representing the players chosen
    '''
    pass

def simulate_n_tournaments(matchups_dict, N=100):
    champions = defaultdict(int)

    for _ in range(N):
        east = Region(matchups_dict["east"])
        west = Region(matchups_dict["west"])
        south = Region(matchups_dict["south"])
        midwest = Region(matchups_dict["midwest"])

        tourney = Tournament(east, west, south, midwest)
        tourney.simulate_tournament()
        champ = tourney.championship.winner

        champions[str(champ)] += 1
        print(f"---\n---\nOverall Champion: {champ}")

    # Convert to probabilities
    champion_probs = {team: count / N for team, count in champions.items()}
    return champion_probs

def main():
    matchups_dict = read_unplayed_tournament(year=2024)
    
    # Load player ppg data
    player_data = {}
    for region in matchups_dict.values():
        for matchup in region:
            team1 = matchup['team_1']['link']
            team2 = matchup['team_2']['link']
            if team1 not in player_data:
                player_data[team1] = load_player_data(team1)
            if team2 not in player_data:
                player_data[team2] = load_player_data(team2)
    
    print("Player data loaded successfully.")
    print(player_data)
    

    probs = simulate_n_tournaments(matchups_dict, N=1000)

    # Convert the probabilities to a DataFrame for better readability
    df = pd.DataFrame(probs.items(), columns=['Team', 'Probability'])
    df = df.sort_values(by='Probability', ascending=False)
    df.reset_index(drop=True, inplace=True)

    return df

print(main())
