"""
Objective:
The purpose of this file is to get all of the different match combinations that are possible in a
season for a variety of different leagues. This will then be used to compare against the existing 
list of matches that has been scraped to ensure none are missed off as a result of needing to be 
rescheduled.

The output will be a table that has all of the possible match combinations as well as the
associated league.

Schema:
team | opponent | div

"""


from nis import match
import sys
sys.path.append("..")

import itertools
import pandas as pd


def get_all_matches(div, teams):
    matches = list(itertools.permutations(teams, 2))
    matches_df = pd.DataFrame(matches, columns=['home_team', 'away_team'])

    matches_df['league'] = div

    matches_df = duplicate_to_team_and_opponent(matches_df)

    return matches_df


def duplicate_to_team_and_opponent(df_matches):
    df_matches_copy = df_matches.copy()
    df_matches = df_matches.rename(columns={'home_team': 'team', 'away_team': 'opponent',
                                            })
    df_matches_copy = df_matches_copy.rename(columns={'away_team': 'team', 'home_team': 'opponent',
                                                    })
    df_matches_copy = df_matches_copy[['league', 'team', 'opponent' 
                                        ]]
    df_matches.loc[:, 'home'] = 1
    df_matches_copy.loc[:, 'home'] = 0
    df_matches = pd.concat([df_matches, df_matches_copy])

    return df_matches


# sa = [
#     'Arsenal',
#     'Aston Villa',
#     'Bournemouth',
#     'Brentford',
#     'Brighton',
#     'Chelsea',
#     'Crystal Palace',
#     'Everton',
#     'Fulham',
#     'Leeds',
#     'Leicester',
#     'Liverpool',
#     'Man City',
#     'Man United',
#     'Newcastle',
#     'Nott\'m Forest',
#     'Southampton',
#     'Tottenham',
#     'West Ham',
#     'Wolves',
#     ]

# sb = [
#     'Blackburn',
#     'Bristol City',
#     'Burnley',
#     'Cardiff',
#     'Luton',
#     'Preston',
#     'QPR',
#     'Stoke',
#     'Sheffield United',
#     'Coventry',
#     'Birmingham',
#     'Blackpool',
#     'Huddersfield',
#     'Hull',
#     'Middlesbrough',
#     'Millwall',
#     'Norwich',
#     'Reading',
#     'Rotherham',
#     'Sunderland',
#     'Watford',
#     'West Brom',
#     'Wigan',
#     'Swansea',
#     ]

sc = ['alessandria',
      'ancona',
      'aquila_montevarchi',
      'carrarese',
      'cesena',
      'fermana',
      'fiorenzuola',
      'gubbio',
      'imolese',
      'lucchese',
      'olbia',
      'pontedera',
      'recanatese',
      'reggiana',
      'rimini',
      'san_donato_tavarnelle',
      'sassari_torres',
      'siena',
      'virtus_entella',
      'vis_pesaro'
      ]

leagues = {
    # 'sa': sa,
    # 'sb': sb,
    'Serie C, Girone B': sc
    }

all_matches = pd.DataFrame(columns=['team', 'opponent', 'league', 'home'])
for league in leagues:
    single_league_all_matches = get_all_matches(league, leagues[league])
    all_matches = pd.concat([all_matches, single_league_all_matches])

all_matches.reset_index(inplace=True, drop=True)
all_matches.to_csv("../../data/all_match_combinations.csv")
print(all_matches.head())


