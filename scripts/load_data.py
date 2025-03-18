import requests
import pickle
import time
import os
import pandas as pd
from bs4 import BeautifulSoup
# from kenpompy.misc import get_pomeroy_ratings
import cloudscraper
from io import StringIO

def scrape_kenpom_to_df(year=2024):
    """
    Scrape KenPom data and return it as a pandas DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame containing KenPom data.
    """
    # Use cloudscraper to bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()
    # print(get_pomeroy_ratings(browser=scraper, season='2024'))
    
    url = f"https://kenpom.com/index.php?y={year}"
    response = scraper.get(url)
    
    if response.status_code != 200:
        print(f"Error: {response.status}")
        print(response)
        raise Exception(f"Failed to fetch data from {url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Parse the HTML content using BeautifulSoup
    table = soup.find("table", id="ratings-table")

    if table is None:
        raise Exception("Failed to find the ratings table on the page.")
    
    kenpom_df = pd.read_html(str(table))[0]
    
    return kenpom_df

def clean_kenpom_df(kenpom_df):
    """
    Clean the KenPom DataFrame by renaming columns and dropping unnecessary ones.
    
    Args:
        kenpom_df (pd.DataFrame): The KenPom DataFrame to clean.
    
    Returns:
        pd.DataFrame: The cleaned KenPom DataFrame.
    """
    kenpom_df.columns = kenpom_df.columns.get_level_values(1)
    # select only the relevant columns
    kenpom_df = kenpom_df.iloc[:, :5]

    # get rid of duplicate rows of header
    kenpom_df = kenpom_df.drop_duplicates()

    # drop extra row with header
    kenpom_df.dropna(subset=['Team'], inplace=True)

    # reset index after drops
    kenpom_df.reset_index(drop=True, inplace=True)

    # drop extra copy of column labels
    kenpom_df.drop(kenpom_df[kenpom_df['Team'] == 'Team'].index, inplace=True)

    # remove seed numbers
    kenpom_df['Team'] = kenpom_df['Team'].str.replace(r' \d{1,2}', '', regex=True)

    return kenpom_df

def full_kenpom_pipeline(year=2024):
    """
    Full pipeline to scrape, clean, and return KenPom data as a DataFrame.
    
    Args:
        year (int): The year for which to scrape KenPom data.
    
    Returns:
        pd.DataFrame: The cleaned KenPom DataFrame.
    """
    print(f"Scraping KenPom data for {year}...")

    kenpom_df = scrape_kenpom_to_df(year)
    kenpom_df = clean_kenpom_df(kenpom_df)
    
    # Convert columns to appropriate types
    kenpom_df['NetRtg'] = pd.to_numeric(kenpom_df['NetRtg'], errors='coerce')
    
    return kenpom_df

def read_unplayed_region(year, region):
    BASE_URL = "https://www.sports-reference.com/cbb/postseason/men/{}-ncaa.html"
    url = BASE_URL.format(year)
    
    # Use requests to get the content of the webpage
    response = requests.get(url)
    html_content = response.text
    if response.status_code != 200:
        print(response)
        raise Exception(f"Failed to fetch data from {url}")

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the container for the east region
    round_64 = soup.find(id=region).find(class_='team16').find(class_='round', recursive=False)
    matchups = []

    games = round_64.find_all('div', recursive=False)  # Each game is contained in a div directly under the round div
    for game in games:
        teams = game.find_all('div', recursive=False)
        if teams[0].find('span', recursive=False) is not None:
            if game.find('span', recursive=False) is not None: # regular games
                location = game.find('span', recursive=False).text.strip()[3:]
                team1_seed, team1_name, team1_link = teams[0].find('span').text, teams[0].find('a').text, teams[0].find('a')['href']
                team2_seed, team2_name, team2_link = teams[1].find('span').text, teams[1].find('a').text, teams[1].find('a')['href']
            else: # play-in games
                location = "TBD"
                team1_seed, team1_name, team1_link = teams[0].find('span').text, teams[0].find('a').text, teams[0].find('a')['href']
                team2_seed = 16 - (int(team1_seed) - 1)
                team2_name = "Play-In"
                team2_link = None

            matchups.append({
                'team_1': {'seed': team1_seed, 'name': team1_name, 'link': team1_link},
                'team_2': {'seed': team2_seed, 'name': team2_name, 'link': team2_link},
                'location': location
            })

    return matchups

def read_unplayed_tournament(year):
    """
    Read the unplayed tournament matchups for a given year and region.
    
    Args:
        year (int): The year of the tournament.
    
    Returns:
        list: A list of dictionaries containing matchups.
    """
    east_2024_list = read_unplayed_region(year, "east")
    west_2024_list = read_unplayed_region(year, "west")
    south_2024_list = read_unplayed_region(year, "south")
    midwest_2024_list = read_unplayed_region(year, "midwest")

    matchups_dict = {
        "east": east_2024_list,
        "west": west_2024_list,
        "south": south_2024_list,
        "midwest": midwest_2024_list
    }

    return matchups_dict

# TODO: USE LINKS TO PLAYER PROFILES IN ROSTER FOR REG SEASON STATS ONLY & EMPERICAL DISTRIBUTION
def load_player_data_for_team(team_link):
    """
    Load the roster for a team from the link to the team's SR page.
    
    Args:
        team_link (str): The link to the team's SR page.
    
    Returns:
        player_ppg (dict): A dictionary mapping player names to their average points per game.
    """
    # Use requests to get the content of the webpage
    url = "https://www.sports-reference.com" + team_link
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the roster
    table = soup.find('table', id='players_per_game')
    
    if table is None:
        print(f"Failed to find the roster table for {team_link}.")
        raise Exception("Failed to find the roster table on the page.")
    
    # Parse the table into a DataFrame
    df = pd.read_html(StringIO(str(table)))[0]
    df = df[['Player', 'PTS']]
    df = df.dropna()

    # Remove the 'Player' column if it contains 'Team Totals'
    df = df[~df['Player'].str.contains('Team Totals', na=False)]

    # Convert the 'PTS' column to numeric
    df['PTS'] = pd.to_numeric(df['PTS'], errors='coerce')
    df = df.dropna()

    # Rename PTS col to AVG PTS
    df = df.rename(columns={'PTS': 'AVG PTS'})

    # Convert the DataFrame to a list of dictionaries
    raw_ppg = df.to_dict(orient='records')
    player_ppg = {player['Player']: {'avg': player['AVG PTS'], 'running_total': 0} for player in raw_ppg}

    return player_ppg

def load_player_data(year, matchups_dict):
    # Load player ppg data if not already loaded
    try:
        print(os.getcwd())
        with open(f'./scripts/NEW_player_data_{year}.pkl', 'rb') as f:
            player_data = pickle.load(f)
    except FileNotFoundError:
        player_data = {}
        for region in matchups_dict.values():
            for matchup in region:
                team1 = matchup['team_1']
                team2 = matchup['team_2']

                if team1['name'] not in player_data:
                    player_data[team1['name']] = load_player_data_for_team(team1['link'])
                if team2['name'] not in player_data:
                    player_data[team2['name']] = load_player_data_for_team(team2['link'])
                
                # Simulate a delay to avoid overwhelming the server
                time.sleep(3.6)
        
        print("Player data loaded successfully.")
        print(player_data)

        # Save player data dictionary to a file
        with open(f'player_data_{year}.pkl', 'wb') as f:
            pickle.dump(player_data, f)

    return player_data

if __name__ == "__main__":
    # Example of loading a team's roster
    team_link = "/cbb/schools/connecticut/men/2024.html"
    ppgs = load_player_data_for_team(team_link)
    print(ppgs)
    for player, ppg in ppgs.items():
        print(f"{player}: {ppg}")
