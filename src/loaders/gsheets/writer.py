import gspread
from gspread_dataframe import set_with_dataframe
from loaders.gsheets.config import GSHEET_NAME, ELOS_NAME, GSHEETSCREDS, TABS, ELO_TABS
from loaders.writer import Writer
import logging


class GsheetsWriter(Writer):
    def __init__(self, data, elos=False):
        self.gsheet_name = GSHEET_NAME if not elos else ELOS_NAME
        self.tabs = TABS if not elos else ELO_TABS
        self.data = data

    def write_all_to_gsheets(self):
        for i in range(len(self.data)):
            self.write_df_to_gsheets(self.tabs[i], self.data[i])

    def write_df_to_gsheets(self, tab_name, df):
        upload_data = df.copy(deep=True)
        upload_data = upload_data.apply(lambda x: x.astype(str).str.replace('Nan', ''))
        gc = gspread.service_account(filename=GSHEETSCREDS)
        sh = gc.open(self.gsheet_name) 
        worksheet = sh.worksheet(tab_name)
        set_with_dataframe(worksheet, upload_data)