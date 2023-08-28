import os


# Data Loader

COUNTRIES = [
    'England',
    'Italy',
    # 'Scotland'
]

LEAGUES = [
    'Italian Serie A',
    'Italian Serie B',
    'Serie A',
    'Serie B',
    'Serie C, Girone A',
    'Serie C Grp. A',
    'Serie C, Girone B',
    'Serie C Grp. B',
    'Serie C, Girone C',
    'Serie C Grp. C',
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
    # 'Premiership',
    # 'Scottish Premiership',
    # 'Championship',
    # 'Scottish Championship',
    # 'League One',
    # 'Scottish League One',
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
    'Tottenham Hotspur',
    'West Ham United',
    'Wolverhampton Wanderers'
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
    'Wycombe Wanderers'
]

LEAGUE_TWO_TEAMS = [
    'Accrington Stanley',
    'AFC Wimbledon',
    'Barrow',
    'Bradford City',
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
    'Dagenham and Redbridge',
    'Dorking Wanderers',
    'Eastleigh',
    'Ebbsfleet United',
    'FC Halifax Town',
    'Gateshead',
    'Hartlepool United',
    'Kiddyminster Harriers',
    'Maidenhead United',
    'Oldham Athletic',
    'Oxford City',
    'Rochdale',
    'Solihull Moors',
    'Southend United',
    'Wealdstone',
    'Woking',
    'York City'
]

SERIE_A_TEAMS = [
    'AC Milan',
    'AS Roma',
    'Atalanta',
    'Bologna',
    'Cagliari',
    'Empoli',
    'Fiorentina',
    'Frosinone',
    'Genoa',
    'Hellas Verona',
    'Inter Milan',
    'Juventus',
    'Lazio',
    'Lecce',
    'Monza',
    'Napoli',
    'Salernitana',
    'Sassuolo',
    'Torino',
    'Udinese'
]

SERIE_B_TEAMS = [
    'Ascoli',
    'Bari',
    'Catanzaro',
    'Cittadella',
    'Como',
    'Cosenza',
    'Cremonese',
    'Feralpisalò',
    'Lecco',
    'Modena',
    'Palermo',
    'Parma',
    'Pisa',
    'Reggina',
    'Reggiana',
    'Sampdoria',
    'Spezia',
    'Sudtirol',
    'Ternana',
    'Venezia',
]

SERIE_C_GIRONE_A_TEAMS = [
    'Albinoleffe',
    'Arzignano Valchiampo',
    'Brescia',
    'Juventus U23',
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
    'Ancona',
    'Arezzo',
    'ASD Pineto Calcio',
    'Carrarese',
    'Cesena',
    'Fermana',
    'Gubbio',
    'Juventus U23',
    'Lucchese',
    'Olbia',
    'Perugia',
    'Pescara',
    'Pontedera',
    'Recanatese',
    'Rimini',
    'Sestri Levante',
    'SPAL',
    'Torres',
    'Virtus Entella',
    'Vis Pesaro'
]

SERIE_C_GIRONE_C_TEAMS = [
    'Audace Cerignola',
    'Avellino',
    'AZ Picerno',
    'Benevento Calcio',
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

SCOTTISH_PREMIERSHIP_TEAMS = [
    'Aberdeen',
    'Celtic',
    'Dundee',
    'Hearts',
    'Hibernian',
    'Kilmarnock',
    'Livingston',
    'Motherwell',
    'Rangers',
    'Ross County',
    'St Johnstone',
    'St Mirren'
]

SCOTTISH_CHAMPIONSHIP_TEAMS = [
    'Airdrieonians',
    'Arbroath',
    'Ayr United',
    'Dundee United',
    'Dunfermline Athletic',
    'Morton',
    'Inverness Caledonian Thistle',
    'Partick Thistle',
    'Queen\'s Park',
    'Raith Rovers',
]

SCOTTISH_LEAGUE_ONE_TEAMS = [
    'Alloa Athletic',
    'Annan Athletic',
    'Cove Rangers',
    'Edinburgh City',
    'Falkirk',
    'Hamilton Academical',
    'Kelty Hearts',
    'Montrose',
    'Queen of the South',
    'Stirling Albion',
]

LEAGUE_TEAMS_MAPPING = {
    'Premier League': PREMIER_LEAGUE_TEAMS,
    'Championship': CHAMPIONSHIP_TEAMS,
    'League One': LEAGUE_ONE_TEAMS,
    'League Two': LEAGUE_TWO_TEAMS,
    'National League': NATIONAL_LEAGUE_TEAMS,
    'Serie A': SERIE_A_TEAMS,
    # 'Serie B': SERIE_B_TEAMS,
    # 'Serie C, Girone A': SERIE_C_GIRONE_A_TEAMS,
    'Serie C, Girone B': SERIE_C_GIRONE_B_TEAMS,
    # 'Serie C, Girone C': SERIE_C_GIRONE_C_TEAMS,
    # 'Scottish Premiership': SCOTTISH_PREMIERSHIP_TEAMS,
    # 'Scottish Championship': SCOTTISH_CHAMPIONSHIP_TEAMS,
    # 'Scottish League One': SCOTTISH_LEAGUE_ONE_TEAMS
}

LEAGUE_TEAMS_COUNT = {
    'Premier League': 20,
    'Championship': 24,
    'League One': 24,
    'League Two': 24,
    'National League': 24,
    'Serie A': 20,
    # 'Serie B': 20,
    # 'Serie C, Girone A': 20,
    'Serie C, Girone B': 20,
    # 'Serie C, Girone C': 20,
    # 'Scottish Premiership': 12,
    # 'Scottish Championship': 10,
    # 'Scottish League One': 10
}

LEAGUE_COUNTRY_MAPPING = {
    'Premier League': 'England',
    'Championship': 'England',
    'League One': 'England',
    'League Two': 'England',
    'National League': 'England',
    'Serie A': 'Italy',
    # 'Serie B': 'Italy',
    # 'Serie C, Girone A': 'Italy',
    'Serie C, Girone B': 'Italy',
    # 'Serie C, Girone C': 'Italy',
    # 'Scottish Premiership': 'Scotland',
    # 'Scottish Championship': 'Scotland',
    # 'Scottish League One': 'Scotland'
}

LEAGUE_SCALING_MAPPING = {
    'Premier League': 2050,
    'Championship': 1750,
    'League One': 1500,
    'League Two': 1250,
    'National League': 1000,
    'Serie A': 1750,
    'Serie B': 1500,
    'Serie C, Girone A': 1000,
    'Serie C, Girone B': 1000,
    'Serie C, Girone C': 1000,
    'Scottish Premiership': 1500,
    'Scottish Championship': 1000,
    'Scottish League One': 1000,
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

DASHBOARD_TEAMS = [team for league in list(LEAGUE_TEAMS_MAPPING.values()) for team in league]

SCRAPED_LEAGUES_MAPPING = {
    'serie-a': 'Serie A',
    'serie-b': 'Serie B',
    'serie-c-girone-a': 'Serie C, Girone A',
    'serie-c-girone-b': 'Serie C, Girone B',
    'serie-c-group-b': 'Serie C, Girone B',
    'serie-c-girone-c': 'Serie C, Girone C',
    'premier-league': 'Premier League',
    'championship': 'Championship',
    'league-one': 'League One',
    'league-two': 'League Two',
    'national-league': 'National League',
    # 'premiership': 'Scottish Premiership',
    # 'championship': 'Scottish Championship',
    # 'league-one': 'Scottish League One'
}

TABLE_NAME_PAST = "football_matches"

os.environ["API_DB_USER"] = "postgres"
os.environ["API_DB_PASSWORD"] = "ywngtpwyBH0922"
os.environ["API_DB_HOST"] = "localhost"
os.environ["API_DB_PORT"] = "5431"
os.environ["API_DB_DB"] = "rugby4cast"

# Cleaning
TEAM_NAMES_DICT = {
    'accrington': 'accrington_stanley',
    'afc_bournemouth': 'bournemouth',
    'aldershot': 'aldershot_town',
    'alloa': 'alloa_athletic',
    'annan': 'annan_athletic',
    'ayr': 'ayr_united',
    'birmingham': 'birmingham_city',
    'bolton': 'bolton_wanderers',
    'blackburn': 'blackburn_rovers',
    'brighton_and_hove_albion': 'brighton',
    'burton': 'burton_albion',
    'cambridge': 'cambridge_united',
    'cambridge_utd': 'cambridge_united',
    'cardiff': 'cardiff_city',
    'carlisle': 'carlisle_united',
    'charlton': 'charlton_athletic',
    'cheltenham': 'cheltenham_town',
    'colchester': 'colchester_united',
    'coventry': 'coventry_city',
    'crawley': 'crawley_town',
    'crewe': 'crewe_alexandra',
    'dag_&_red': 'dagenham_and_redbridge',
    'dagenham_&_redbridge': 'dagenham_and_redbridge',
    'derby': 'derby_county',
    'doncaster': 'doncaster_rovers',
    'dorking': 'dorking_wanderers',
    'dundee_fc': 'dundee',
    'dundee_utd': 'dundee_united',
    'dunfermline': 'dunfermline_athletic',
    'ebbsfleet': 'ebbsfleet_united',
    'entella': 'virtus_entella',
    'exeter': 'exeter_city',
    'fc_halifax': 'fc_halifax_town',
    'fleetwood': 'fleetwood_town',
    'forest_green': 'forest_green_rovers',
    'grimsby': 'grimsby_town',
    'hamilton': 'hamilton_academical',
    'harrogate': 'harrogate_town',
    'hartlepool': 'hartlepool_united',
    'huddersfield': 'huddersfield_town',
    'hull': 'hull_city',
    'ipswich': 'ipswich_town',
    'Inter Milan': 'inter_milan',
    'internazionale': 'inter_milan',
    'inter': 'inter_milan',
    'internazionale': 'inter_milan',
    'inverness': 'inverness_caledonian_thistle',
    'kidderminster': 'kiddyminster_harriers',
    'kidderminster_harriers': 'kiddyminster_harriers',
    'leeds': 'leeds_united',
    'leicester': 'leicester_city',
    'lincoln': 'lincoln_city',
    'luton': 'luton_town',
    'maidenhead': 'maidenhead_united',
    'manchester_utd': 'manchester_united',
    'mansfield': 'mansfield_town',
    'mk_dons': 'milton_keynes_dons',
    'newcastle': 'newcastle_united',
    'newcastle_utd': 'newcastle_united',
    'newport': 'newport_county',
    'northampton': 'northampton_town',
    'norwich': 'norwich_city',
    'notts_co': 'notts_county',
    'nottingham': 'nottingham_forest',
    'oldham': 'oldham_athletic',
    'oxford': 'oxford_united',
    'oxford_utd': 'oxford_united',
    'peterborough': 'peterborough_united',
    'plymouth': 'plymouth_argyle',
    'preston': 'preston_north_end',
    'qpr': 'queens_park_rangers',
    'queen_of_south': 'queen_of_the_south',
    'queens_park': 'queens_park_rangers',
    'raith': 'raith_rovers',
    'rotherham': 'rotherham_united',
    'salford': 'salford_city',
    'san_donato': 'san_donato_tavarnelle',
    'sassari_torres': 'torres',
    'sheffield_utd': 'sheffield_united',
    'sheffield_wed': 'sheffield_wednesday',
    'sheffield_weds': 'sheffield_wednesday',
    'shrewsbury': 'shrewsbury_town',
    'southend': 'southend_united',
    'stirling': 'stirling_albion',
    'stoke': 'stoke_city',
    'st._mirren': 'st_mirren',
    'suditrol': 'sudtirol',
    'südtirol': 'sudtirol',
    'sutton': 'sutton_united',
    'swansea': 'swansea_city',
    'swindon': 'swindon_town',
    'tottenham': 'tottenham_hotspur',
    'tranmere': 'tranmere_rovers',
    'us_ancona': 'ancona',
    'verona': 'hellas_verona',
    'west_brom': 'west_bromwich_albion',
    'west_ham': 'west_ham_united',
    'wigan': 'wigan_athletic',
    'wolves': 'wolverhampton_wanderers',
    'wolverhampton': 'wolverhampton_wanderers',
    'wycombe': 'wycombe_wanderers',
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
    'English League Championship': 'Championship',
    'Premiership': 'Scottish Premiership',
    # 'Championship': 'Scottish Championship',
    # 'League One': 'Scottish League One'
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
    # 'league_home_goals_scored',
    # 'league_away_goals_scored',
    # 'league_home_goals_scored_avg',
    # 'league_away_goals_scored_avg',
    # 'league_home_goals_conceded',
    # 'league_away_goals_conceded',
    # 'league_home_goals_conceded_avg',
    # 'league_away_goals_conceded_avg',
    'team_attack_strength',
    'team_defense_strength',
    'opponent_attack_strength',
    'opponent_defense_strength',
    # 'team_lambda',
    # 'opponent_lambda'
]

SEASON_START = '2023-07-20'
SEASON_END = '2024-05-31'

# ELO settings
STARTING_ELO = 1500
PROMOTION_ELO_ADJUSTMENT = -350
RELEGATION_ELO_ADJUSTMENT = 500
MANUAL_TEAM_ELO_ADJUSTMENT = 400
KFACTOR_QUICK = 40
KFACTOR_SLOW = 30
HOME_AD = 50
new_team_rating = 1500

# Poisson settings
PROMOTION_GOAL_ADJUSTMENT = 0.8
RELEGATION_GOAL_ADJUSTMENT = 1.5
MANUAL_TEAM_GOAL_ADJUSTMENT = 1.5

# Simulation settings
NUM_SIMULATIONS = 10000

# Assertions
assert len(PREMIER_LEAGUE_TEAMS) == 20
assert len(CHAMPIONSHIP_TEAMS) == 24
assert len(LEAGUE_ONE_TEAMS) == 24
assert len(LEAGUE_TWO_TEAMS) == 24
assert len(NATIONAL_LEAGUE_TEAMS) == 24