import numpy as np
from load_data import full_kenpom_pipeline

sr_to_kenpom = {
    'Brigham Young': 'BYU',
    'Saint Mary\'s (CA)': 'Saint Mary\'s',
    'St. John\'s (NY)': 'St. John\'s',
    'Pittsburgh': 'Pittsburgh',
    'Mississippi State': 'Mississippi St.',
    'Central Florida': 'UCF',
    'Virginia Commonwealth': 'VCU',
    'Southern California': 'USC',
    'Mississippi': 'Ole Miss',
    'Massachusetts': 'UMass',
    'Miami (FL)': 'Miami FL',
    'Nevada-Las Vegas': 'UNLV',
    'North Carolina State': 'N.C. State',
    'Louisiana State': 'LSU',
    'Connecticut': 'Connecticut',
    'North Carolina': 'North Carolina',
    'Pittsburgh': 'Pittsburgh',
    'St. John\'s (NY)': 'St. John\'s',
    'Louisiana State': 'LSU',
    'Central Florida': 'UCF',
    'Texas A&M-Corpus Christi': 'Texas A&M Corpus Chris',
    'Purdue Fort Wayne': 'Purdue Fort Wayne',
    'Loyola (IL)': 'Loyola Chicago',
    'College of Charleston': 'Charleston',
    'Loyola (IL)': 'Loyola Chicago',
    'Saint Joseph\'s': 'Saint Joseph\'s',
    'Saint Francis (PA)': 'Saint Francis',
    'Arkansas-Pine Bluff': 'Arkansas Pine Bluff',
    'SIU Edwardsville': 'SIU Edwardsville',
    'Maryland-Baltimore County': 'UMBC',
    'Maryland-Eastern Shore': 'Maryland Eastern Shore',
    'Massachusetts-Lowell': 'UMass Lowell',
    'Charleston Southern': 'Charleston Southern',
    'East Tennessee State': 'East Tennessee St.',
    'Florida International': 'FIU',
    'Loyola (IL)': 'Loyola Chicago',
    'Albany (NY)': 'Albany',
    'College of Charleston': 'Charleston',
    'Detroit Mercy': 'Detroit Mercy',
    'LIU': 'LIU',
    'North Carolina State': 'N.C. State',
    'Southeast Missouri State': 'Southeast Missouri St.',
    'Louisiana-Monroe': 'Louisiana Monroe',
    'Nicholls State': 'Nicholls St.',
    'Middle Tennessee': 'Middle Tennessee',
    'UMass Lowell': 'UMass Lowell',
    'UNC Asheville': 'UNC Asheville',
    'UNC Greensboro': 'UNC Greensboro',
    'UNC Wilmington': 'UNC Wilmington',
    'Texas-Rio Grande Valley': 'UT Rio Grande Valley',
    'Western Carolina': 'Western Carolina',
    'Northern Illinois': 'Northern Illinois',
    'Southern Illinois': 'Southern Illinois',
    'Fairleigh Dickinson': 'Fairleigh Dickinson',
    'Alcorn State': 'Alcorn St.',
    'Cal State Bakersfield': 'Cal St. Bakersfield',
    'Cal State Fullerton': 'Cal St. Fullerton',
    'Cal State Northridge': 'Cal St. Northridge',
    'Prairie View': 'Prairie View A&M',
    'Southern Methodist': 'SMU',
    'Southern Mississippi': 'Southern Miss',
    'East Tennessee State': 'East Tennessee St.',
    'Eastern Illinois': 'Eastern Illinois',
    'Eastern Kentucky': 'Eastern Kentucky',
    'Eastern Michigan': 'Eastern Michigan',
    'Eastern Washington': 'Eastern Washington',
    'Illinois-Chicago': 'Illinois Chicago',
    'Kansas City': 'UMKC',
    'Louisiana-Monroe': 'Louisiana Monroe',
    'Maryland-Eastern Shore': 'Maryland Eastern Shore',
    'Tennessee-Martin': 'Tennessee Martin',
    'Texas Southern': 'Texas Southern',
    'North Dakota State': 'North Dakota St.',
    'Southeast Missouri State': 'Southeast Missouri St.',
    'Virginia Commonwealth': 'VCU',
    'UConn': 'Connecticut',
    'San Diego State': 'San Diego St.',
    'Morehead State': 'Morehead St.',
    'Washington State': 'Washington St.',
    'Iowa State': 'Iowa St.',
    'South Dakota State': 'South Dakota St.',
    'UNC': 'North Carolina',
    'Michigan State': 'Michigan St.',
    'Long Beach State': 'Long Beach St.',
    'NC State': 'N.C. State',
    'Grambling': 'Grambling St.',
    'Utah State': 'Utah St.',
    'McNeese State': 'McNeese St.',
    'Colorado State': 'Colorado St.',
    'St. Peter\'s': 'Saint Peter\'s',
}

kenpom_ratings_df = full_kenpom_pipeline(year=2024)

def wp_kenpom(team1, team2, ratings_df, sd=11):
    # Extract ratings for each team in the matchup
    # First, check if team name is in the kenpom teams
    if team1.team_name not in ratings_df['Team'].values:
        team1_kp = sr_to_kenpom[team1.team_name]
    else:
        team1_kp = team1.team_name
    
    if team2.team_name not in ratings_df['Team'].values:
        team2_kp = sr_to_kenpom[team2.team_name]
    else:
        team2_kp = team2.team_name
        
    rating1 = ratings_df[ratings_df['Team'] == team1_kp]['NetRtg'].values[0]
    rating2 = ratings_df[ratings_df['Team'] == team2_kp]['NetRtg'].values[0]
    rating_diff = float(rating1) - float(rating2)

    # Calculate the probability of team1 winning
    prob_team1_wins = 1 / (1 + np.exp(-rating_diff / sd))

    return prob_team1_wins

def simulate_game_kenpom(team1, team2):
    # Calculate the probability of team1 winning
    prob_team1_wins = wp_kenpom(team1, team2, kenpom_ratings_df)

    # Simulate the game based on the probability
    if np.random.rand() < prob_team1_wins:
        return team1
    else:
        return team2

# TODO: SHOULD MAKE THE SIMULATION DATA-BASED INSTEAD OF ASSUMING NORMAL WITH VAR OF 5
def simulate_player_pts(player_avg_pts, variance=5):
    """
    Simulate the points scored by a player in a game based on their average points and variance.
    
    Args:
        player_avg_pts (float): The average points scored by the player.
        variance (float): The variance in the player's scoring. Default is 1.
        
    Returns:
        float: The simulated points scored by the player.
    """
    return max(0, np.random.normal(player_avg_pts, variance))

def handle_player_bookkeeping_for_team_win(player_bk_dict, winning_team_ref):
    winning_seed = winning_team_ref.seed
    winning_team_dict = player_bk_dict[winning_team_ref.team_name]

    # sample from player pts and add to running total, including seed multiplier
    