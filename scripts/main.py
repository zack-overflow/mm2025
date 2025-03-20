import pickle
import pandas as pd
from load_team_data import full_kenpom_pipeline, read_unplayed_tournament
from load_player_data import load_player_data
from simulate_tournament import simulate_n_tournaments

def main():
    year = 2025
    kenpom_ratings_df = full_kenpom_pipeline(year)
    matchups_dict = read_unplayed_tournament(year)
    player = load_player_data(year, matchups_dict)
    probs, sims = simulate_n_tournaments(matchups_dict, player, kenpom_ratings_df, N=1000)

    # Convert the probabilities to a DataFrame for better readability
    df = pd.DataFrame(probs.items(), columns=['Team', 'Probability'])
    df = df.sort_values(by='Probability', ascending=False)
    df.reset_index(drop=True, inplace=True)

    return df, sims
        

# print(main())
# convert_player_data('player_data_2024.pkl')
# print(load_player_data(2024, {}))
