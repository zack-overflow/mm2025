import numpy as np
from scipy.stats import norm
from load_team_data import full_kenpom_pipeline

sr_to_kenpom = {
    'Brigham Young': 'BYU',
    'Saint Mary\'s (CA)': 'Saint Mary\'s',
    'St. John\'s (NY)': 'St. John\'s',
    'Pittsburgh': 'Pittsburgh',
    'Mississippi State': 'Mississippi St.',
    'Central Florida': 'UCF',
    'Virginia Commonwealth': 'VCU',
    'Southern California': 'USC',
    'Ole Miss': 'Mississippi',
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
    'St. John\'s (NY)': 'St. John\'s',
    'Saint Mary\'s': 'Saint Mary\'s (CA)',
    'Mississippi State': 'Mississippi St.',
    'Norfolk State': 'Norfolk St.',
    'Colorado State': 'Colorado St.',
    'Alabama State': 'Alabama St.',
    'UC-San Diego': 'UC San Diego',
    'UNC': 'North Carolina',
    'Iowa State': 'Iowa St.',
    'Michigan State': 'Michigan St.',
    'SIU-Edwardsville': 'SIU Edwardsville',
    'McNeese State': 'McNeese St.',
    'Utah State': 'Utah St.',
    
}
sr_to_silver = {
    'St. John\'s (NY)': 'St. John\'s',
    'Saint Mary\'s': 'Saint Mary\'s (CA)',
    'Mississippi State': 'Mississippi St.',
    'Norfolk State': 'Norfolk St.',
    'Colorado State': 'Colorado St.',
    'Alabama State': 'Alabama St.',
    'UC-San Diego': 'UC San Diego',
    'UNC': 'North Carolina',
    'Iowa State': 'Iowa St.',
    'Michigan State': 'Michigan St.',
    'SIU-Edwardsville': 'SIU Edwardsville',
    'McNeese State': 'McNeese',
    'Utah State': 'Utah St.',
}
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
    # TODO: CHECK IF THIS IS THE RIGHT FORMULA FOR ESIMATING WP FROM KENPOM DIFFERENTIAL
    # ALTERNATIVE: https://www.kaggle.com/competitions/march-machine-learning-mania-2024/discussion/493793
    
    # From https://www.reddit.com/r/CollegeBasketball/comments/5xir8t/calculating_win_probability_and_margin_of_victory/
    prob_team1_wins = norm.cdf(rating_diff / sd)
    return prob_team1_wins

def wp_silver(team1, team2, ratings_df, sd=11):

    if team1.team_name not in ratings_df['Team'].values:
        team1_silver = sr_to_silver[team1.team_name]
    else:
        team1_silver = team1.team_name
    if team2.team_name not in ratings_df['Team'].values:
        team2_silver = sr_to_silver[team2.team_name]
    else:
        team2_silver = team2.team_name

    # Extract the ratings for each team
    # Get the 'Quasi-Sagarin' rating for each team
    team1_rating = ratings_df.loc[ratings_df['Team'] == team1_silver, 'Quasi-Sagarin'].values[0]
    team2_rating = ratings_df.loc[ratings_df['Team'] == team2_silver, 'Quasi-Sagarin'].values[0]
    
    rating_diff = team1_rating - team2_rating
    prob_team_1_wins = norm.cdf(rating_diff / sd)

    # FOR ELO:  wp = 1 / (1 + 10 ** (rating_diff / 400))
    
    return prob_team_1_wins

def simulate_game_kenpom(team1, team2, kenpom_ratings_df):
    # Calculate the probability of team1 winning
    prob_team1_wins = wp_kenpom(team1, team2, kenpom_ratings_df)

    # Simulate the game based on the probability
    if np.random.rand() < prob_team1_wins:
        return team1
    else:
        return team2
    
def simulate_game_silver(team1, team2, silver_ratings_df):
    # Calculate the probability of team1 winning
    prob_team1_wins = wp_silver(team1, team2, silver_ratings_df)

    # Simulate the game based on the probability
    if np.random.rand() < prob_team1_wins:
        return team1
    else:
        return team2
    
def simulate_game(team1, team2, ratings_df, method):
    """
    Simulate a game between two teams using either KenPom or Silver ratings.
    
    Args:
        team1 (Team): The first team.
        team2 (Team): The second team.
        kenpom_ratings_df (pd.DataFrame): DataFrame containing KenPom ratings.
        silver_ratings_df (pd.DataFrame): DataFrame containing Silver ratings.
        method (str): The method to use for simulation ('kenpom' or 'silver').
        
    Returns:
        Team: The winning team.
    """
    if method == 'kenpom':
        return simulate_game_kenpom(team1, team2, ratings_df)
    elif method == 'silver':
        return simulate_game_silver(team1, team2, ratings_df)
    else:
        raise ValueError("Method must be either 'kenpom' or 'silver'.")

# TODO: SHOULD MAKE THE SIMULATION DATA-BASED INSTEAD OF ASSUMING NORMAL
def simulate_player_pts(player_avg_pts, variance=None):
    """
    Simulate the points scored by a player in a game based on their average points and variance.
    
    Args:
        player_avg_pts (float): The average points scored by the player.
        variance (float): The variance in the player's scoring. Default is avg/5.
        
    Returns:
        float: The simulated points scored by the player.
    """
    if variance is None:
        variance = player_avg_pts / 5
    return max(0, np.random.normal(player_avg_pts, variance))

def handle_player_bookkeeping_for_team(player_bk_dict, winning_team_ref):
    winning_team_multiplier = winning_team_ref.get_multiplier()
    winning_team_dict = player_bk_dict[winning_team_ref.team_name]

    # sample from player pts and add to running total, including seed multiplier
    for player in winning_team_dict:
        player_stats = winning_team_dict[player]
        player_ppg = simulate_player_pts(player_stats['ppg'])
        increment = player_ppg * winning_team_multiplier
        player_stats['running_total_simulated'] += increment
