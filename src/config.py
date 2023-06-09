import os


# Data Loader

COUNTRIES = [
    'England',
    'Italy',
    ''
]

LEAGUES = [
    # 'Coppa Italia',
    # 'Coppa Italia Serie C, Girone A',
    # 'Coppa Italia Serie C, Girone B',
    # 'Coppa Italia Serie C, Girone C',
    # 'Coppa Italia Serie C, Girone D',
    # 'Coppa Italia Serie C, Girone E',
    # 'Coppa Italia Serie C, Girone F',
    # 'Coppa Italia Serie C, Girone G',
    # 'Coppa Italia Serie C, Girone H',
    # 'Coppa Italia Serie C, Girone I',
    # 'Coppa Italia Serie C, Girone L',
    # 'Coppa Italia Serie C, Girone M',
    # 'Coppa Italia Serie C, Knockout stage',
    # 'Coppa Italia Serie D',
    # 'Italian Coppa Italia',
    'Italian Serie A',
    'Italian Serie B',
    # 'Italian Supercoppa',
    # 'Primavera Cup, Knockout stage',
    'Serie A',
    'Serie B',
    # 'Serie B, Promotion Playoffs',
    # 'Serie B, Relegation Playoffs',
    'Serie C, Girone A',
    'Serie C Grp. A',
    # 'Serie C, Girone A, Relegation Playoffs',
    'Serie C, Girone B',
    'Serie C Grp. B',
    # 'Serie C, Girone B, Relegation Playoffs',
    'Serie C, Girone C',
    'Serie C Grp. C',
    # 'Serie C, Girone C, Relegation Playoffs',
    # 'Serie C, Promotion Playoffs',
    # 'Serie C, Relegation Playoffs',
    # 'Serie D, Girone A',
    # 'Serie D, Girone A, Playoffs',
    # 'Serie D, Girone B',
    # 'Serie D, Girone B, Playoffs',
    # 'Serie D, Girone C',
    # 'Serie D, Girone C, Playoffs',
    # 'Serie D, Girone D',
    # 'Serie D, Girone D, Playoffs',
    # 'Serie D, Girone E',
    # 'Serie D, Girone E, Playoffs',
    # 'Serie D, Girone F',
    # 'Serie D, Girone F, Playoffs',
    # 'Serie D, Girone G',
    # 'Serie D, Girone G, Playoffs',
    # 'Serie D, Girone H',
    # 'Serie D, Girone H, Playoffs',
    # 'Serie D, Girone H, Playout',
    # 'Serie D, Girone I',
    # 'Serie D, Girone I, Playoffs',
    # 'Serie D, Girone I, Playout',
    # 'Serie D, Poule Scudetto, Group 2',
    # 'Serie D, Poule Scudetto, Group 3',
    # 'Serie D, Poule Scudetto, Knockout stage',
    # 'Supercoppa',
    # 'Supercoppa Serie',
    'Premier League',
    'English Premier League',
    'Championship',
    'English League Championship',
    'League One',
    'English League One',
    'League Two',
    'English League Two',
    'National League',
    'English National League',
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
    'Burnley',
    'Chelsea',
    'Crystal Palace',
    'Everton',
    'Fulham',
    'Liverpool',
    'Luton Town',
    'Manchester City',
    'Manchester United',
    'Newcastle United',
    'Nottingham Forest',
    'Sheffield United',
    'Tottenham',
    'West Ham United',
    'Wolves'
]

CHAMPIONSHIP_TEAMS = [
    'Birmingham City',
    'Blackburn Rovers',
    'Bristol City',
    'Cardiff City',
    'Coventry City',
    'Huddersfield Town',
    'Hull City',
    'Ipswich Town',
    'Leeds United',
    'Leicester City',
    'Middlesbrough',
    'Millwall',
    'Norwich City',
    'Plymouth Argyle',
    'Preston North End',
    'Queens Park Rangers',
    'Rotherham United',
    'Sheffield Wednesday',
    'Southampton',
    'Stoke City',
    'Sunderland',
    'Swansea City',
    'West Bromwich Albion',
    'Watford',
]

LEAGUE_ONE_TEAMS = [
    'Barnsley',
    'Blackpool',
    'Bolton Wanderers',
    'Bristol Rovers',
    'Burton Albion',
    'Cambridge United',
    'Carlisle United',
    'Charlton Athletic',
    'Cheltenham Town',
    'Derby County',
    'Exeter City',
    'Fleetwood Town',
    'Leyton Orient',
    'Lincoln City',
    'Northampton Town',
    'Oxford United',
    'Peterborough United',
    'Portsmouth',
    'Port Vale',
    'Reading',
    'Shrewsbury Town',
    'Stevenage',
    'Wigan Athletic',
    'Wycombe'
]

LEAGUE_TWO_TEAMS = [
    'Accrington Stanley',
    'AFC Wimbledon',
    'Barrow',
    'Bradford United',
    'Colchester United',
    'Crawley Town',
    'Crewe Alexandra',
    'Doncaster Rovers',
    'Forest Green Rovers',
    'Gillingham',
    'Grimsby Town',
    'Harrogate Town',
    'Mansfield Town',
    'Milton Keynes Dons',
    'Morecambe',
    'Newport County',
    'Notts County',
    'Salford City',
    'Stockport County',
    'Sutton United',
    'Swindon Town',
    'Tranmere Rovers',
    'Walsall',
    'Wrexham'
]

NATIONAL_LEAGUE_TEAMS = [
    'AFC Fylde',
    'Aldershot Town',
    'Altrincham',
    'Barnet',
    'Boreham Wood',
    'Bromley',
    'Chesterfield',
    'Dagenham & Redbridge',
    'Dorking Wanderers',
    'Eastleigh',
    'Ebbsfleet United',
    'FC Halifax Town',
    'Gateshead',
    'Hartlepool United',
    'Kiddyminster Harriers',
    'Maidehead United',
    'Oldham Athletic',
    'Oxford City',
    'Solihull Moors',
    'Southend United',
    'Wealdstone',
    'Woking',
    'York City'
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
    'Arzignano Valchiampo',
    'Feralpisalò',
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
    'Sangiuliano City',
    'Trento',
    'Triestina',
    'Vicenza',
    'Virtus Verona'
]

SERIE_C_GIRONE_B_TEAMS = [
    'Alessandria',
    'Ancona',
    'Aquila Montevarchi',
    'Carrarese',
    'Cesena',
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
    'Virtus Entella',
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
    'League One': LEAGUE_ONE_TEAMS,
    'League Two': LEAGUE_TWO_TEAMS,
    'National League': NATIONAL_LEAGUE_TEAMS,
    # 'Serie A': SERIE_A_TEAMS,
    # 'Serie B': SERIE_B_TEAMS,
    # 'Serie C, Girone A': SERIE_C_GIRONE_A_TEAMS,
    # 'Serie C, Girone B': SERIE_C_GIRONE_B_TEAMS,
    # 'Serie C, Girone C': SERIE_C_GIRONE_C_TEAMS
}

PROMOTED_TEAMS = [
    'Burnley',
    'Carlisle United',
    'Ipswich Town',
    'Leyton Orient',
    'Luton Town',
    'Northampton Town',
    'Notts County',
    'Plymouth Argyle',
    'Sheffield United',
    'Sheffield Wednesday',
    'Stevenage',
    'Wrexham'
]
    
RELEGATED_TEAMS = [
    'Accringhton Stanley',
    'Blackpool',
    'Forest Green Rovers',
    'Hartlepool United',
    'Leeds United',
    'Leicester City',
    'Milton Keynes Dons',
    'Morecambe',
    'Reading',
    'Rochdale',
    'Southampton',
    'Wigan Athletic',
]

MANUAL_TEAM_ADJUSTMENT = [
    'Chelsea',
    'Leciester City',
    'Southampton'
]

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
    'leeds': 'leeds_united',
    'leicester': 'leicester_city',
    'manchester_utd': 'manchester_united',
    'newcastle_utd': 'newcastle_united',
    'nottingham': 'nottingham_forest',
    'san_donato': 'san_donato_tavarnelle',
    'sassari_torres': 'torres',
    'suditrol': 'sudtirol',
    'südtirol': 'sudtirol',
    'us_ancona': 'ancona',
    'verona': 'hellas_verona',
    'west_ham': 'west_ham_united',
    'wolverhampton': 'wolves',
}

LEAGUE_NAMES_MAPPING = {
    'Italian Serie A': 'Serie A',
    'Italian Serie B': 'Serie B',
    'Serie C Grp. A': 'Serie C, Girone A',
    'Serie C Grp. B': 'Serie C, Girone B',
    'Serie C Grp. C': 'Serie C, Girone C',
    'English Premier League': 'Premier League',
    'English Championship': 'Championship',
    'English League One': 'League One',
    'English League Two': 'League Two',
    'English National League': 'National League',
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
PROMOTION_ELO_ADJUSTMENT = -600
RELEGATION_ELO_ADJUSTMENT = 500
MANUAL_TEAM_ELO_ADJUSTMENT = 600
KFACTOR_QUICK = 40
KFACTOR_SLOW = 30
HOME_AD = 50
new_team_rating = 1500

# Poisson settings
PROMOTION_GOAL_ADJUSTMENT = 0.5
RELEGATION_GOAL_ADJUSTMENT = 1.5
MANUAL_TEAM_GOAL_ADJUSTMENT = 1.5

# Simulation settings
NUM_SIMULATIONS = 10000