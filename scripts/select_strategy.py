import matplotlib.pyplot as plt
import seaborn as sns

def score_strategy(strategy, sims):
    '''
    Need to come up with a score for a certain strategy. Would also be nice to represent the uncertainty somehow.

    Args:
        strategy (list): A list of (team, player) tuples representing the players chosen
        sims (list): A list of *n* Tournament objects representing *n* simulated tournaments
    
    Returns:
        scores (list): A list of scores for this strategy across the *n* simulations run
    '''
    scores = []
    for sim in sims:
        # extract score for strategy for the sim
        bk = sim.players_bookkeeping
        total = 0
        for team, player in strategy:
            player_simmed_pts = bk[team][player]['running_total_simulated']
            total += player_simmed_pts
        
        scores.append(total)

    return scores

def visualize_strategies(scores):
    # histograms and legend
    # maybe dots w/ sd and plot w different y values based on height
    # would be good to make hover yield players (interactive plot)
    pass