import pickle
import pandas as pd
from simulate_tournament import simulate_n_tournaments
# from load_data import read_unplayed_tournament, load_player_data_for_team, load_player_data

def main():
    year = 2024
    kenpom_ratings_df = full_kenpom_pipeline(year)
    matchups_dict = read_unplayed_tournament(year)
    player = load_player_data(year, matchups_dict)
    probs, sims = simulate_n_tournaments(matchups_dict, player, kenpom_ratings_df, N=1000)

    # Convert the probabilities to a DataFrame for better readability
    df = pd.DataFrame(probs.items(), columns=['Team', 'Probability'])
    df = df.sort_values(by='Probability', ascending=False)
    df.reset_index(drop=True, inplace=True)

    return df

def convert_player_data(old_file):
    with open(old_file, 'rb') as f:
            player_data = pickle.load(f)

    new = {}
    for team in player_data:
        new[team] = {}
        for player in player_data[team]:
            new[team][player] = {'avg': player_data[team][player], 'running_total': 0}

    with open(f'NEW_player_data_2024.pkl', 'wb') as f:
            pickle.dump(new, f)
        

print(main())
# convert_player_data('player_data_2024.pkl')
# print(load_player_data(2024, {}))
