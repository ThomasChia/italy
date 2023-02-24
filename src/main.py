import code
import time

import db_pull
from scrapers import future_fixture_scraper

time.sleep(30)

from preprocessing import clean_team_names

time.sleep(15)

from preprocessing import add_next_match
time.sleep(5)
from preprocessing import elos_calc
time.sleep(5)
from preprocessing import goals
time.sleep(5)
from preprocessing import streaks
time.sleep(5)
from preprocessing import build_wavenet_data
time.sleep(5)
from model import run_model
time.sleep(5)
from post_processing import monte_carlo, past_predictions, home_and_away
time.sleep(5)
from post_processing import dashboard_output


# code.interact(local=locals())