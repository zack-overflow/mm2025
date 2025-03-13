import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_kenpom_to_df(year=2024):
    """
    Scrape KenPom data and return it as a pandas DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame containing KenPom data.
    """
    url = f"https://kenpom.com/index.php?y={year}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(response)
        raise Exception(f"Failed to fetch data from {url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Parse the HTML content using BeautifulSoup
    table = soup.find("table", id ="ratings-table")

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

def read_unplayed_tournament(year, region):
    BASE_URL = "https://www.sports-reference.com/cbb/postseason/men/{}-ncaa.html"
    url = BASE_URL.format(year)
    
    # Use requests to get the content of the webpage
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the container for the east region
    east_round_64 = soup.find(id=region).find(class_='team16').find(class_='round', recursive=False)
    matchups = []

    games = east_round_64.find_all('div', recursive=False)  # Each game is contained in a div directly under the round div
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