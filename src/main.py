import code
import time

import db_pull
from scrapers import future_fixture_scraper

time.sleep(60)

from preprocessing import clean_team_names

time.sleep(15)


from preprocessing import add_next_match
from preprocessing import elos_calc, goals, streaks
from preprocessing import build_wavenet_data

from model import run_model

from post_processing import monte_carlo, past_predictions, home_and_away
from post_processing import dashboard_output


# code.interact(local=locals())