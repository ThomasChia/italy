"""
This file is to pull the past predictions that have been made and save them as a record. This will then be
used to combine with future predictions.
"""

from datetime import datetime
import gspread
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


def read_df_from_gsheets(gsheet_name, tab_name):
    gc = gspread.service_account(filename='../../tools/gsheet_s4c_creds/italy-football-373515-95398f188c18.json')
    sh = gc.open(gsheet_name) 
    worksheet = sh.worksheet(tab_name)
    df = pd.DataFrame(worksheet.get_all_records())
    return df


def limit_to_past(df):
    today = datetime.today().strftime('%Y-%m-%d')
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date']<=today]
    return df


def cut_to_preds(df):
    df_cut = df[['league', 'date', 'team', 'opponent', 'result', 'home', 'loss', 'draw', 'win']]
    df_cut.rename(columns={'loss': '0', 'draw': '1', 'win': '2'}, inplace=True)
    return df_cut


def update_result(df):
    result_num = []
    for home, result in zip(df['home'], df['result']):
        if home == 1:
            if result == 'H':
                result_num.append(1)
            elif result == 'A':
                result_num.append(0)
            else:
                result_num.append(0.5)
        elif home == 0:
            if result == 'H':
                result_num.append(0)
            elif result == 'A':
                result_num.append(1)
            else:
                result_num.append(0.5)
    df.drop(['result'], axis=1, inplace=True)
    df['result'] = result_num
    return df


predictions = read_df_from_gsheets('serie_c_data', 'preds_team_opp')
past_predictions = limit_to_past(predictions)
past_predictions = cut_to_preds(past_predictions)
past_predictions = update_result(past_predictions)
past_predictions.to_csv("../../data/past_predictions.csv")