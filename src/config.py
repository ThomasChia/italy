import os


# Data Loader

COUNTRIES = [
    'England',
    'Italy'
]

LEAGUES = [
    'Coppa Italia',
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
    'Supercoppa Serie',
    'Premier League',
    'English Premier League',
    'Championship',
    'English League Championship',
]

####################################################################################################
# TEAMS FOR FULL SEASON SIMULATION
####################################################################################################

PREMIER_LEAGUE_TEAMS = [
    'Arsenal',
    'Aston Villa',
    'Bournemouth',
    'Brentford',
    'Brighton',
    'Chelsea',
    'Crystal Palace',
    'Everton',
    'Fulham',
    'Leeds',
    'Leicester',
    'Liverpool',
    'Manchester City',
    'Manchester United',
    'Newcastle',
    'Nottingham Forest',
    'Southampton',
    'Tottenham',
    'West Ham',
    'Wolves'
]

CHAMPIONSHIP_TEAMS = [
    'Birmingham City',
    'Blackburn Rovers',
    'Blackpool',
    'Bristol City',
    'Burnley',
    'Cardiff City',
    'Coventry City',
    'Huddersfield Town',
    'Hull City',
    'Luton Town',
    'Middlesbrough',
    'Millwall',
    'Norwich City',
    'Preston North End',
    'Queens Park Rangers',
    'Reading',
    'Rotherham United',
    'Sheffield United',
    'Stoke City',
    'Sunderland',
    'Swansea City',
    'West Bromwich Albion',
    'Watford',
    'Wigan Athletic'
]

LEAGUE_ONE_TEAMS = [
    'Accrington',
    'Barnsley',
    'Bolton',
    'Bristol Rovers',
    'Burton',
    'Cambridge',
    'Charlton',
    'Cheltenham',
    'Derby',
    'Exeter',
    'Fleetwood Town',
    'Forest Green',
    'Ipswich',
    'Lincoln',
    'Milton Keynes Dons',
    'Morecambe',
    'Oxford',
    'Peterborough',
    'Plymouth',
    'Portsmouth',
    'Port Vale',
    'Sheffield Wednesday',
    'Shrewsbury',
    'Wycombe'
]

LEAGUE_TWO_TEAMS = [
    'AFC Wimbledon',
    'Barrow',
    'Bradford',
    'Carlisle',
    'Colchester',
    'Crawley',
    'Crewe',
    'Doncaster',
    'Gillingham',
    'Grimsby',
    'Harrogate',
    'Hartlepool',
    'Leyton Orient',
    'Mansfield',
    'Newport',
    'Northampton',
    'Rochdale',
    'Salford',
    'Stevenage',
    'Stockport',
    'Sutton',
    'Swindon',
    'Tranmere',
    'Walsall'
]

SERIE_A_TEAMS = [
    'AC Milan',
    'Atalanta',
    'Bologna',
    'Cremonese',
    'Empoli',
    'Fiorentina',
    'Hella Verona',
    'Inter Milan',
    'Juventus',
    'Lazio',
    'Lecce',
    'Monza',
    'Napoli',
    'Roma',
    'Salernitana',
    'Sampdoria',
    'Sassuolo',
    'Spezia',
    'Torino',
    'Udinese'
]

SERIE_B_TEAMS = [
    'Ascoli',
    'Bari',
    'Benevento',
    'Brescia',
    'Cagliari',
    'Cittadella',
    'Como',
    'Cosenza',
    'Frosinone',
    'Genoa',
    'Modena',
    'Palermo',
    'Parma',
    'Perugia',
    'Pisa',
    'Reggina',
    'SPAL',
    'Sudtirol',
    'Ternana',
    'Venezia',
]

SERIE_C_GIRONE_A_TEAMS = [
    'Albinoleffe',
    'Arzignano',
    'Feralpisalo',
    'Juventus U23',
    'Lecco',
    'Mantova',
    'Novara',
    'Padova',
    'Pergolettese',
    'Piacenza',
    'Pordenone',
    'Pro Patria',
    'Pro Sesto',
    'Pro Vercelli',
    'Renate',
    'Sangiuliano',
    'Trento',
    'Triestina',
    'Vicenza',
    'Virtus Verona'
]

SERIE_C_GIRONE_B_TEAMS = [
    'Alessandria',
    'Ancona',
    'Aquilla Montevarchi',
    'Carrarese',
    'Cesena',
    'Entella',
    'Fermana',
    'Fiorenzuola',
    'Gubbio',
    'Imolese',
    'Lucchese',
    'Olbia',
    'Pontedera',
    'Recanatese',
    'Reggiana',
    'Rimini',
    'San Donato',
    'Siena',
    'Torres',
    'Vis Pesaro'
]

SERIE_C_GIRONE_C_TEAMS = [
    'Audace Cerignola',
    'Avellino',
    'AZ Picerno',
    'Catanzaro',
    'Crotone',
    'Fidelis Andria',
    'Foggia',
    'Gelbison',
    'Giugliano',
    'Juve Stabia',
    'Latina',
    'Messina',
    'Monopoli',
    'Monterosi',
    'Pescara',
    'Potenza',
    'Taranto',
    'Turris',
    'Virtus Francavilla',
    'Viterbese'
]

LEAGUE_TEAMS_MAPPING = {
    'Premier League': PREMIER_LEAGUE_TEAMS,
    'Championship': CHAMPIONSHIP_TEAMS,
    # 'League One': LEAGUE_ONE_TEAMS,
    # 'League Two': LEAGUE_TWO_TEAMS,
    # 'Serie A': SERIE_A_TEAMS,
    'Serie B': SERIE_B_TEAMS,
    # 'Serie C, Girone A': SERIE_C_GIRONE_A_TEAMS,
    # 'Serie C, Girone B': SERIE_C_GIRONE_B_TEAMS,
    # 'Serie C, Girone C': SERIE_C_GIRONE_C_TEAMS
}

########################################################################################################################

DASHBOARD_LEAGUES = [LEAGUE for LEAGUE in LEAGUE_TEAMS_MAPPING.keys()]

SCRAPED_LEAGUES_MAPPING = {
    'serie-a': 'Serie A',
    'serie-b': 'Serie B',
    'serie-c-girone-a': 'Serie C, Girone A',
    'serie-c-girone-b': 'Serie C, Girone B',
    'serie-c-girone-c': 'Serie C, Girone C',
    'premier-league': 'Premier League',
    'championship': 'Championship',
    'league-one': 'League One',
    'league-two': 'League Two'
}

TABLE_NAME_PAST = "football_matches"

os.environ["API_DB_USER"] = "postgres"
os.environ["API_DB_PASSWORD"] = "ywngtpwyBH0922"
os.environ["API_DB_HOST"] = "localhost"
os.environ["API_DB_PORT"] = "5431"
os.environ["API_DB_DB"] = "rugby4cast"

# Cleaning
TEAM_NAMES_DICT = {
    'afc_bournemouth': 'bournemouth',
    'brighton_and_hove_albion': 'brighton',
    'Inter Milan': 'inter_milan',
    'internazionale': 'inter_milan',
    'inter': 'inter_milan',
    'internazionale': 'inter_milan',
    'leeds_united': 'leeds',
    'leicester_city': 'leicester',
    'manchester_united': 'manchester_utd',
    'newcastle_united': 'newcastle',
    'nottingham_forest': 'nottingham',
    'san_donato': 'san_donato_tavarnelle',
    'sassari_torres': 'torres',
    'suditrol': 'sudtirol',
    'südtirol': 'sudtirol',
    'us_ancona': 'ancona',
    'verona': 'hellas_verona',
    'west_ham_united': 'west_ham',
    'wolverhampton': 'wolves',
}

LEAGUE_NAMES_MAPPING = {
    'Italian Serie A': 'Serie A',
    'Italian Serie B': 'Serie B',
    'Serie C Grp. A': 'Serie C, Girone A',
    'Serie C Grp. B': 'Serie C, Girone B',
    'Serie C Grp. C': 'Serie C, Girone C',
    'English Premier League': 'Premier League'
}

DEPENDENT_FEATURE = [
    'result'
]

ID_FEATURES = [
    'match_id',
    'league',
    'date',
    'team',
    'opponent'
]

FEATURES = [
    'elo_team',
    'elo_opponent',
    'elo_diff',
    'home',
    # 'team_goals_scored',
    # 'team_goals_conceded',
    'team_goals_scored_avg',
    'team_goals_conceded_avg',
    'team_goals_scored_avg_home',
    'team_goals_conceded_avg_home', 
    'team_goals_scored_avg_away',
    'team_goals_conceded_avg_away',
    # 'opponent_goals_scored',
    # 'opponent_goals_conceded',
    'opponent_goals_scored_avg',
    'opponent_goals_conceded_avg',
    'opponent_goals_scored_avg_home',
    'opponent_goals_conceded_avg_home',
    'opponent_goals_scored_avg_away',
    'opponent_goals_conceded_avg_away',
    'league_home_goals_scored',
    'league_away_goals_scored',
    'league_home_goals_scored_avg',
    'league_away_goals_scored_avg',
    'league_home_goals_conceded',
    'league_away_goals_conceded',
    'league_home_goals_conceded_avg',
    'league_away_goals_conceded_avg',
    'team_attack_strength',
    'team_defense_strength',
    'opponent_attack_strength',
    'opponent_defense_strength',
    # 'team_lambda',
    # 'opponent_lambda'
]

SEASON_START = '2022-07-20'

# ELO settings
STARTING_ELO = 1500
KFACTOR_QUICK = 40
KFACTOR_SLOW = 30
HOME_AD = 50
new_team_rating = 1500

# Simulation settings
NUM_SIMULATIONS = 1000