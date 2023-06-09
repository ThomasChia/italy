LEAGUE_TARGETS_COLUMNS = [
    'league',
    'position',
    'points',
    'rounded'
]

RESULTS_COLUMNS = []

PAST_PREDICTIONS_COLUMNS = [
    'match_id',
    'date',
    'team',
    'opponent',
    'league',
    'home',
    'rest_days',
    'win',
    'draw',
    'loss'
]

FUTURE_PREDICTIONS_COLUMNS = [
    'match_id',
    'date',
    'team',
    'opponent',
    'league',
    'home',
    'rest_days',
    'win',
    'draw',
    'loss'
]

MATCH_IMPORTANCE_COLUMNS = [
    'league',
    'team'
] + ['{}_{}'.format(i, j) for i in range(1, 25) for j in [0, 1, 3]] 

FINISHING_POSITIONS_COLUMNS = [
    'team'
] + [str(i) for i in range(1, 25)] + ['league']

OPPONENT_ANALYSIS_COLUMNS = []

ELO_TRACKER_COLUMNS = [
    'team',
    'pts',
    'last_played',
    'league'
]

ELO_OVER_TIME_COLUMNS = [
    'team',
    'date',
    'elo',
    'league'
]