import code
import config
import log_in
import numpy as np
import pandas as pd


query = f' SELECT * FROM {config.TABLE_NAME_PAST} WHERE league IN {config.LEAGUES}'

data = log_in.get_session(query)
print(data.head())
print(data.shape)

data.to_csv('../data/football_matches.csv')

code.interact(local=locals())
