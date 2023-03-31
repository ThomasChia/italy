import code
import config
import log_in
import numpy as np
import pandas as pd


query = f' SELECT * FROM {config.TABLE_NAME_PAST} WHERE league IN {config.LEAGUES}'

data = log_in.get_session(query)
print(data.head())
print(data.shape)
print(data[data['pt1']=='cesena'].sort_values(by='date', ascending=False).head())
print(data[data['pt2']=='cesena'].sort_values(by='date', ascending=False).head())

data.to_csv('../data/football_matches.csv')

# code.interact(local=locals())
