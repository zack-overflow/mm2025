import pandas as pd
from load_team_data import full_kenpom_pipeline, read_unplayed_tournament
from load_player_data import load_player_data
from simulate_tournament import simulate_n_tournaments


year = 2025
kenpom_ratings_df = full_kenpom_pipeline(year)
matchups_dict = read_unplayed_tournament(year)


play_ins_found = 0
for region, matchups in matchups_dict.items():
    # check where the team name is play-in
    print(matchups)
    for i, matchup in enumerate(matchups):
        t1 = matchup['team_1']['name']
        t2 = matchup['team_2']['name']
        if t2 == 'Play-In':
            if play_ins_found == 0:
                matchup['team_2'] = {
                    'name': 'Mount St. Mary\'s (MD)',
                    'seed': 16,
                    'link': '/cbb/schools/mount-st-marys/men/2025.html'
                }
            else:
                matchup['team_2'] = {
                    'name': 'Xavier',
                    'seed': 11,
                    'link': '/cbb/schools/xavier/men/2025.html'
                }
            play_ins_found += 1


print(matchups_dict)


import pickle

with open('player_data_2025.pkl', 'rb') as f:
    player = pickle.load(f)


# find instances where 'ground_truth_total' is in the player dict

for team in player:
    if 'ground_truth_total' in player[team]:
        print(f"Found ground_truth_total for {team}")

# remove the 'ground_truth_total' from the player dict
for team in player:
    if 'ground_truth_total' in player[team]:
        del player[team]['ground_truth_total']


from load_team_data import parse_silver_ratings

silver_path = '../data/silver.csv'
silver_df = parse_silver_ratings(silver_path)
print(silver_df)

probs, sims = simulate_n_tournaments(matchups_dict, player, silver_df, method='silver', N=20000)

# Convert the probabilities to a DataFrame for better readability
df = pd.DataFrame(probs.items(), columns=['Team', 'Probability'])
df = df.sort_values(by='Probability', ascending=False)
df.reset_index(drop=True, inplace=True)

# Save the DataFrame to a CSV file
df.to_csv('simulation_results_20k.csv', index=False)

# Pickle the simulation results
with open('simulation_results_20k.pkl', 'wb') as f:
    pickle.dump(sims, f)
