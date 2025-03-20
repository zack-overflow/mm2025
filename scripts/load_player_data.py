import time
import pickle
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

def get_tournament_games(player_gamelog_df):
    # Filter for tournament games (ROUND-64, ROUND-32,..., NATIONAL-SEMI, NATIONAL-FINAL)
    tournament_games = player_gamelog_df[player_gamelog_df['Type'].isin(['ROUND-64', 'ROUND-32', 'ROUND-16', 'ROUND-8', 'NATIONAL-SEMI', 'NATIONAL-FINAL'])]
    return tournament_games

def get_player_pts_gamelog(player_link, year):
    url = f'https://www.sports-reference.com{player_link[:-5]}/gamelog/{year}'
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with id 'player_game_log'
    table = soup.find('table', id='player_game_log')
    if not table:
        # throw error if table not found
        raise ValueError(f"Gamelog not found for player link: {player_link}")
    
    # Extract table to pandas DataFrame
    table_html = str(table)
    df = pd.read_html(StringIO(table_html))[0]

    # Clean up the DataFrame
    df = df[['Date', 'Opp', 'Type', 'PTS']]
    
    # Make sure the 'PTS' column is numeric
    df['PTS'] = pd.to_numeric(df['PTS'], errors='coerce')

    return df

def get_player_tournament_pts(player_link, year):
    """
    Get the total points scored by a player in tournament games from their gamelog.

    Args:
        player_link (str): The link to the player's SR page.
        year (str): The year of the tournament.

    Returns:
        total_pts (int): The total points scored in tournament games.
    """
    player_gamelog_df = get_player_pts_gamelog(player_link, year)
    tournament_games = get_tournament_games(player_gamelog_df)
    total_pts = tournament_games['PTS'].sum()
    
    return total_pts

def load_player_data_for_team(team_link, year):
    """
    Load the roster for a team from the link to the team's SR page.

    Args:
        team_link (str): The link to the team's SR page.

    Returns:
        player_ppg (dict): A dictionary mapping player names to their average points per game.
    """
    print(f"Loading player data for team link: {team_link}")
    url = "https://www.sports-reference.com" + team_link
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with id 'players_per_game'
    table = soup.find('table', id='players_per_game')

    # Extract player names and their links
    player_data = []
    for row in table.find('tbody').find_all('tr'):
        player_cell = row.find('td', {'data-stat': 'name_display'})
        if player_cell:
            player_name = player_cell.text.strip()
            player_link = None
            link_tag = player_cell.find('a')
            if link_tag:
                player_link = link_tag.get('href')
            player_data.append({'name': player_name, 'link': player_link})

    # Extract all data including stats
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        row_data = {}
        for td in tr.find_all(['th', 'td']):
            stat_name = td.get('data-stat')
            value = td.text.strip()
            row_data[stat_name] = value

            # Special handling for player links
            if stat_name == 'name_display' and td.find('a'):
                row_data['player_link'] = td.find('a').get('href')

        rows.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Clean up the data
    # Convert numeric columns to appropriate types
    numeric_columns = ['games', 'games_started', 'mp_per_g', 'fg_per_g', 'fga_per_g', 'fg_pct',
                    'fg3_per_g', 'fg3a_per_g', 'fg3_pct', 'fg2_per_g', 'fg2a_per_g', 'fg2_pct',
                    'efg_pct', 'ft_per_g', 'fta_per_g', 'ft_pct', 'orb_per_g', 'drb_per_g',
                    'trb_per_g', 'ast_per_g', 'stl_per_g', 'blk_per_g', 'tov_per_g', 'pf_per_g', 'pts_per_g']

    for col in numeric_columns:
        if col in df.columns:
            # Replace empty strings with NaN
            df[col] = df[col].replace('', float('nan'))
            # Remove any non-numeric characters (like % or *)
            df[col] = df[col].str.replace('[^0-9.-]', '', regex=True)
            # Convert to float
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Print the first few rows to verify
    # print(df[['name_display', 'player_link', 'pos', 'games', 'pts_per_g']].head())

    # Convert the DataFrame to a list of dictionaries
    raw_ppg = df.to_dict(orient='records')

    player_dict = {}
    for player in raw_ppg:
        player_dict[player['name_display']] = {'ppg': player['pts_per_g'], 'running_total_simulated': 0, 'link': player['player_link']}
        if year != '2025':
            player_dict['ground_truth_total'] = get_player_tournament_pts(player['player_link'], year)
        time.sleep(3.6) # Simulate a delay to avoid overwhelming the server

    return player_dict

def load_player_data(year, matchups_dict):
    # Load player ppg data if not already loaded
    try:
        with open(f'player_data_{year}_COMPLETE.pkl', 'rb') as f:
            player_data = pickle.load(f)
    except FileNotFoundError:
        player_data = {}
        for region in matchups_dict.values():
            for matchup in region:
                team1 = matchup['team_1']
                team2 = matchup['team_2']

                if team1['name'] not in player_data:
                    player_data[team1['name']] = load_player_data_for_team(team1['link'], year)
                if team2['name'] not in player_data:
                    player_data[team2['name']] = load_player_data_for_team(team2['link'], year)

                # Simulate a delay to avoid overwhelming the server
                time.sleep(3.6)
                print(f"Loaded player data for {team1['name']} and {team2['name']}")
                print(player_data[team1['name']])
                print(player_data[team2['name']])
                
                # Save the player data to a pickle file for future use
                with open(f'player_data_{year}.pkl', 'wb') as f:
                    pickle.dump(player_data, f)


        print("Player data loaded successfully.")
        print(player_data)

    return player_data