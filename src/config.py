import os


# Data Loader

LEAGUES = '''
    ('Coppa Italia',
    'Coppa Italia Serie C, Girone A',
    'Coppa Italia Serie C, Girone B',
    'Coppa Italia Serie C, Girone C',
    'Coppa Italia Serie C, Girone D',
    'Coppa Italia Serie C, Girone E',
    'Coppa Italia Serie C, Girone F',
    'Coppa Italia Serie C, Girone G',
    'Coppa Italia Serie C, Girone H',
    'Coppa Italia Serie C, Girone I',
    'Coppa Italia Serie C, Girone L',
    'Coppa Italia Serie C, Girone M',
    'Coppa Italia Serie C, Knockout stage',
    'Coppa Italia Serie D',
    'Italian Coppa Italia',
    'Italian Serie A',
    'Italian Serie B',
    'Italian Supercoppa',
    'Primavera Cup, Knockout stage',
    'Serie A',
    'Serie B',
    'Serie B, Promotion Playoffs',
    'Serie B, Relegation Playoffs',
    'Serie C, Girone A',
    'Serie C Grp. A',
    'Serie C, Girone A, Relegation Playoffs',
    'Serie C, Girone B',
    'Serie C Grp. B',
    'Serie C, Girone B, Relegation Playoffs',
    'Serie C, Girone C',
    'Serie C Grp. C',
    'Serie C, Girone C, Relegation Playoffs',
    'Serie C, Promotion Playoffs',
    'Serie C, Relegation Playoffs',
    'Serie D, Girone A',
    'Serie D, Girone A, Playoffs',
    'Serie D, Girone B',
    'Serie D, Girone B, Playoffs',
    'Serie D, Girone C',
    'Serie D, Girone C, Playoffs',
    'Serie D, Girone D',
    'Serie D, Girone D, Playoffs',
    'Serie D, Girone E',
    'Serie D, Girone E, Playoffs',
    'Serie D, Girone F',
    'Serie D, Girone F, Playoffs',
    'Serie D, Girone G',
    'Serie D, Girone G, Playoffs',
    'Serie D, Girone H',
    'Serie D, Girone H, Playoffs',
    'Serie D, Girone H, Playout',
    'Serie D, Girone I',
    'Serie D, Girone I, Playoffs',
    'Serie D, Girone I, Playout',
    'Serie D, Poule Scudetto, Group 2',
    'Serie D, Poule Scudetto, Group 3',
    'Serie D, Poule Scudetto, Knockout stage',
    'Supercoppa',
    'Supercoppa Serie')
'''

TABLE_NAME_PAST = "football_matches"

os.environ["API_DB_USER"] = "postgres"
os.environ["API_DB_PASSWORD"] = "ywngtpwyBH0922"
os.environ["API_DB_HOST"] = "localhost"
os.environ["API_DB_PORT"] = "5431"
os.environ["API_DB_DB"] = "rugby4cast"


# ELO settings
STARTING_ELO = 1500
KFACTOR_QUICK = 40
KFACTOR_SLOW = 30
HOME_AD = 50
new_team_rating = 1500