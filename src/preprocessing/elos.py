import numpy as np
import pandas as pd


def calculate_elo_ratings(df, elo_ratings):
  # Calculate the expected scores for each match
  rating_1 = np.array([elo_ratings[team] for team in df['pt1']])
  rating_2 = np.array([elo_ratings[team] for team in df['pt2']])
  expected_scores_1 = 1 / (1 + 10 ** ((rating_2 - rating_1) / 400))
  expected_scores_2 = 1 / (1 + 10 ** ((rating_1 - rating_2) / 400))
  
  # Calculate the actual scores for each match
  actual_scores_1 = np.where(df['score_1'] > df['score_2'], 1, 0)
  actual_scores_2 = np.where(df['score_1'] < df['score_2'], 1, 0)
  
  # Calculate the new Elo ratings for each team
  k = 32
  new_ratings_1 = rating_1 + k * (actual_scores_1 - expected_scores_1)
  new_ratings_2 = rating_2 + k * (actual_scores_2 - expected_scores_2)
  
  # Update the Elo ratings in the dataframe
  for i in range(df.shape[0]):
    team_1 = df.iloc[i]['pt1']
    team_2 = df.iloc[i]['pt2']
    elo_ratings[team_1] = new_ratings_1[i]
    elo_ratings[team_2] = new_ratings_2[i]
    
  return elo_ratings


def init_elos(df):
    # Get list of unique teams
    teams_list = df['pt1'].unique()
    teams_dict = dict.fromkeys(teams_list, 1500)

    return teams_dict



# Initialize the Elo ratings for each team
elo_ratings = {'Team A': 1500, 'Team B': 1500, 'Team C': 1500, 'Team D': 1500}

# Calculate the Elo ratings for each team
elo_ratings = calculate_elo_ratings(df, elo_ratings)
