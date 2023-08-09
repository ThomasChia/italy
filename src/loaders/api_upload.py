import sys
sys.path.append("..")

import datetime as dt
from datetime import datetime
from connector import Connector
from loader import DBConnector
import os
import pandas as pd
import logging
from query import Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.types import JSON


def get_connection() -> Engine:
        if "API_DB_USER" in os.environ:
            user = os.getenv("API_DB_USER")
            password = os.getenv("API_DB_PASSWORD")
            host = os.getenv("API_DB_HOST")
            port = os.getenv("API_DB_PORT")
            database = os.getenv("API_DB_DB")
        else:
            raise EnvironmentError("No Env Vars Supplied to Access DB")

        connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        return create_engine(
            connection_str, pool_pre_ping=True, pool_recycle=600
        )

def create_date_cols(df: pd.DataFrame):
    df["game_week"] = (
        pd.to_datetime(df.gw - dt.timedelta(days=1)).dt.strftime("%a %d %b %Y")
        + " - "
        + pd.to_datetime(df.gw + dt.timedelta(days=5)).dt.strftime("%a %d %b %Y")
    )
    # df = df.sort_values("date").reset_index().rename(columns={"index": "match_order"})
    df["disp_date"] = pd.to_datetime(df.date).dt.strftime("%a %d %b %Y")
    df["raw_date"] = pd.to_datetime(df.date).dt.date
    df["date"] = pd.to_datetime(df.date).dt.strftime("%d/%m")
    return (
        df[df.listed_pt1 == 1]
        .sort_values("raw_date")
        .reset_index(drop=True)
        .reset_index()
        .rename(columns={"index": "match_order"})
    )


def create_and_upload_matches_meta_table(df, sport):
    TABLE_NAME = "matches_meta"
    logging.info("Creating and uploading %s", "matches_meta")
    df = create_date_cols(df)

    if "round" not in df.columns:
        df["round"] = 1
    if "location" not in df.columns:
        df["location"] = "none"
    if "nationality" not in df.columns:
        df["nationality"] = "none"
    if "nationality_opp" not in df.columns:
        df["nationality_opp"] = "none"
    if "event_type" not in df.columns:
        df["event_type"] = df.model_name.copy()

    cols = [
        "match_id",
        "team",
        "opp",
        "model_name",
        "league",
        "game_week",
        "date",
        "played",
        "disp_date",
        "raw_date",
        "match_order",
        "nationality",
        "nationality_opp",
        "round",
        "location",
        "score",
        "score_opp",
        "event_type"
    ]
    delete_sport_rows(TABLE_NAME, sport)
    add_sport_rows(TABLE_NAME, sport, df[cols])

def delete_sport_rows(table_name, sport, df=None):

    engine = get_connection()
    session_made = sessionmaker(bind=engine)
    session = session_made()

    query = f"DELETE FROM {table_name} WHERE sport = '{sport}'"
    if df is not None:
        query += f""" AND match_id in ({",".join([f"'{mid}'" for mid in df.match_id.unique()])}) """
    session.execute(text(query))
    session.commit()
    session.close()

def create_json_columns(js_cols: iter) -> dict:
    """
    Cast columns to json to upload to db.

    Parameters
    ----------
    js_cols : iter
        list of names of any JSON columns

    Returns
    -------
    dict
        dict of json cols
    """
    return {k: JSON for k in js_cols}


def add_sport_rows(table_name, sport, df, js_cols=None):
    df["sport"] = sport
    logging.info("Adding %s Rows to table %s", len(df), table_name)

    if js_cols is None:
        js_cols = create_json_columns(
            [c for c in ["all_bookies", "players"] if c in df.columns]
        )
    else:
        js_cols = create_json_columns(js_cols)

    engine = get_connection()
    conn = engine.connect()

    df.reset_index(drop=True).to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000,
        method="multi",
        dtype=js_cols,
    )
    conn.invalidate()
    engine.dispose()

def sort_future(df):
    df_future = df.dropna(subset=['loss', 'draw', 'win'], axis=0)
    df_future.sort_values('date', inplace=True)
    df_future.reset_index(inplace=True, drop=True)

    return df_future


def output_predhub_table(df, columns):
    df = sort_future(df)
    df_table = get_match_id(df)

    # df_table = get_match_id(df_table)

    df_table['pred_perc'] = round(df_table['win'] * 100, 0)
    df_table['pred_score'] = 0

    df_table = df_table[columns]

    # df_table.drop_duplicates(subset='match_id', inplace=True)

    return df_table


def get_match_id(df):
    """
    Make new column as a list of home_team, away_team, and date. This is then sorted alphabetically and joined.
    """

    df['match_id'] = df['team'] + ' ' + df['opponent']
    df['match_id'] = df['match_id'].apply(lambda x : sort_words(x))
    df['match_id'] = df['match_id'] + '_' + df['date'].astype(str)

    return df


def sort_words(my_str):
    words = [word.lower() for word in my_str.split()]
    words.sort()
    return '_'.join(words)


def output_matches_meta_table(df, columns):
    df = sort_future(df)
    df_table = get_match_id(df)
    df_table['date'] = pd.to_datetime(df_table['date'])
    df_table['league'] = df_table['league'].str.lower().str.replace(' ', '_')
    df_table['location'] = df_table.apply(lambda x: get_location(x), axis=1)
    df_table = change_division(df_table)
    df_table['played'] = 0
    df_table['nationality_opp'] = 'eng'
    df_table['model_name'] = df_table['league']
    df_table['gw'] = df_table['date']
    df_table['opp'] = df_table['opponent']
    df_table['nationality'] = 'eng'
    df_table['round'] = 'n/a'
    df_table['location'] = 'eng'
    df_table['score'] = 0
    df_table['score_opp'] = 0
    df_table['listed_pt1'] = 1
    df_table['event_logo'] = 'https://sports4castdocs.b-cdn.net/website/logos/football/World_Cup_2022.png'

    df_table = df_table[columns]

    df_table.drop_duplicates(subset='match_id', inplace=True)

    return df_table


def change_division(df):
    # df['league'] = df['league'] + '_english_domestic'
    return df


def get_league(row):
    if row == 'e0':
        return 'premier_league'
    elif row == 'e1':
        return 'championship'
    elif row == 'e2':
        return 'league_one'
    elif row == 'world_cup':
        return 'world_cup'


def get_location(row):
    if row['home'] == 1:
        return row['team']
    else:
        return row['opponent']


def transform_international_preds(df):
    df.rename(columns={'home_team':'team', 'away_team':'opponent', 'league':'div', '0': 'loss', '1':'win'}, inplace=True)
    df['draw'] = 0
    df = df[pd.to_datetime(df['date']) >= datetime.today()]

    return df


def update_team_name(df: pd.DataFrame):
    names_dict = {"Accrington": "accrington_stanley",
                  "Accrington Stanley": "accrington_stanley",
                    "Bournemouth": "afc_bournemouth",
                    "Afc Fylde": "afc_fylde",
                    "AFC Wimbledon": "afc_wimbledon",
                    "Afc Wimbledon": "afc_wimbledon",
                    "Aldershot": "aldershot_town",
                    "Aldershot Town": "aldershot_town",
                    "Altrincham": "altrincham",
                    "Arsenal": "arsenal",
                    "Aston Villa": "aston_villa",
                    "Barnet": "barnet",
                    "Barnsley": "barnsley",
                    "Barrow": "barrow",
                    "Bath City": "bath",
                    "Berwick": "berwick_rangers",
                    "Birmingham": "birmingham_city",
                    "Birmingham City": "birmingham_city",
                    "Blackburn": "blackburn_rovers",
                    "Blackburn Rovers": "blackburn_rovers",
                    "Blackpool": "blackpool",
                    "Bolton": "bolton_wanderers",
                    "Boreham Wood": "boreham_wood",
                    "Boston": "boston_united",
                    "Bradford": "bradford_city",
                    "Bradford City": "bradford_city",
                    "Brentford": "brentford",
                    "Brighton": "brighton_and_hove_albion",
                    "Bristol City": "bristol_city",
                    "Bristol Rvs": "bristol_rovers",
                    "Bristol Rovers": "bristol_rovers",
                    "Bromley": "bromley",
                    "Burnley": "burnley",
                    "Burton": "burton_albion",
                    "Burton Albion": "burton_albion",
                    "Bury": "bury",
                    "Cardiff City": "cardiff_city",
                    "Cambridge": "cambridge_united",
                    "Cambridge United": "cambridge_united",
                    "Canvey Island": "canvey_island",
                    "Carlisle": "carlisle_united",
                    "Charlton": "charlton_athletic",
                    "Charlton Athletic": "charlton_athletic",
                    "Chelsea": "chelsea",
                    "Cheltenham": "cheltenham_town",
                    "Cheltenham Town": "cheltenham_town",
                    "Chester": "chester",
                    "Chesterfield": "chesterfield",
                    "Chorley": "chorley",
                    "Colchester": "colchester_united",
                    "Colchester United": "colchester_united",
                    "Coventry": "coventry_city",
                    "Crawley Town": "crawley_town",
                    "Crewe": "crewe_alexandra",
                    "Crystal Palace": "crystal_palace",
                    "Dag and Red": "dagenham_and_redbridge",
                    "Darlington": "darlington",
                    "Derby": "derby_county",
                    "Doncaster": "doncaster_rovers",
                    "Dorking": "dorking_wanderers",
                    "Dover Athletic": "dover_athletic",
                    "Droylsden": "droylsden",
                    "Eastbourne Borough": "eastbourne_borough",
                    "Eastleigh": "eastleigh",
                    "Ebbsfleet": "ebbsfleet_united",
                    "Everton": "everton",
                    "Exeter": "exeter_city",
                    "Farnborough": "farnborough",
                    "Farsley": "farsley_celtic",
                    "Halifax": "fc_halifax_town",
                    "Fleetwood Town": "fleetwood_town",
                    "Forest Green": "forest_green_rovers",
                    "Fulham": "fulham",
                    "Gateshead": "gateshead",
                    "Gillingham": "gillingham",
                    "Grays": "grays_athletic",
                    "Grimsby": "grimsby_town",
                    "Harrogate": "harrogate_town",
                    "Hartlepool": "hartlepool_united",
                    "Havant & Waterlooville": "havant_and_waterlooville",
                    "Hayes & Yeading": "hayes_and_yeading",
                    "Hereford": "hereford_united",
                    "Histon": "histon",
                    "Huddersfield": "huddersfield_town",
                    "Hull": "hull_city",
                    "Ipswich": "ipswich_town",
                    "Kettering Town": "kettering_town",
                    "Kidderminster": "kidderminster_harriers",
                    "King's Lynn": "kings_lynn_town",
                    "Leeds": "leeds_united",
                    "Leicester": "leicester_city",
                    "Leigh": "leigh_rmi",
                    "Lewes": "lewes",
                    "Leyton Orient": "leyton_orient",
                    "Lincoln": "lincoln_city",
                    "Liverpool": "liverpool",
                    "Luton": "luton_town",
                    "Macclesfield": "macclesfield_town",
                    "Maidenhead": "maidenhead_united",
                    "Man City": "manchester_city",
                    "Manchester City": "manchester_city",
                    "Man United": "manchester_united",
                    "Manchester United": "manchester_united",
                    "Mansfield": "mansfield_town",
                    "Margate": "margate",
                    "Middlesbrough": "middlesbrough",
                    "Millwall": "millwall",
                    "Milton Keynes Dons": "mk_dons",
                    "Morecambe": "morecambe",
                    "Newcastle": "newcastle_united",
                    "Newport County": "newport_county",
                    "Northampton": "northampton_town",
                    "Northwich": "northwich_victoria",
                    "Norwich": "norwich_city",
                    "Nott'm Forest": "nottingham_forest",
                    "Nottingham Forest": "nottingham_forest",
                    "Notts County": "notts_county",
                    "Nuneaton Town": "nuneaton_town",
                    "Oldham": "oldham_athletic",
                    "Oxford": "oxford_united",
                    "Peterboro": "peterborough_united",
                    "Plymouth": "plymouth_argyle",
                    "Portsmouth": "portsmouth",
                    "Port Vale": "port_vale",
                    "Preston": "preston_north_end",
                    "QPR": "queens_park_rangers",
                    "Reading": "reading",
                    "Rochdale": "rochdale",
                    "Rotherham": "rotherham_united",
                    "Rushden & D": "rushden_and_diamonds",
                    "Salford": "salford_city",
                    "Salisbury": "salisbury_city",
                    "Scarborough": "scarborough",
                    "Scunthorpe": "scunthorpe_united",
                    "Sheffield United": "sheffield_united",
                    "Sheffield Weds": "sheffield_wednesday",
                    "Shrewbury": "shrewsbury_town",
                    "Solihull": "solihull_moors",
                    "Southampton": "southampton",
                    "Southend": "southend_united",
                    "Southport": "southport",
                    "Stafford Rangers": "stafford_rangers",
                    "St. Albans": "st_albans",
                    "Stevenage": "stevenage",
                    "Stockport": "stockport_county",
                    "Stoke": "stoke_city",
                    "Sunderland": "sunderland",
                    "Sutton": "sutton_united",
                    "Swansea": "swansea_city",
                    "Swindon": "swindon_town",
                    "Swindon Town": "swindon_town",
                    "Tamworht": "tamworth",
                    "Telford United": "telford_united",
                    "Torquay": "torquay_united",
                    "Tottenham": "tottenham",
                    "Tottenham Hotspur": "tottenham",
                    "Tranmere": "tranmere_rovers",
                    "Walsall": "walsall",
                    "Watford": "watford",
                    "Wealdstone": "wealdstone",
                    "Welling United": "welling_united",
                    "West Brom": "west_bromwich_albion",
                    "West Bromwish Albion": "west_bromwich_albion",
                    "West Ham": "west_ham_united",
                    "West Ham United": "west_ham_united",
                    "Weymouth": "weymouth",
                    "Wigan": "wigan_athletic",
                    "Woking": "woking",
                    "Wolves": "wolverhampton",
                    "Wolverhampton Wanderers": "wolverhampton",
                    "Wrexham": "wrexham",
                    "Wycombe": "wycombe",
                    "Yeovil": "yeovil_town",
                    "York": "york_city"}

    df.loc[:, 'team'] = df['team'].replace(names_dict)
    df.loc[:, 'opponent'] = df['opponent'].replace(names_dict)
    df['team'] = df['team'].str.title()
    df['team'] = df['team'].str.replace('_', ' ')
    df['opponent'] = df['opponent'].str.title()
    df['opponent'] = df['opponent'].str.replace('_', ' ')
    return df



if __name__ == '__main__':
    cols_pred = [
        "match_id",
        "team",
        "pred_perc",
        "pred_score",
    ]

    cols_meta = [
        "match_id",
        "team",
        "opp",
        "model_name",
        "league",
        "gw",
        "date",
        "played",
        "nationality",
        "nationality_opp",
        "round",
        "location",
        "score",
        "score_opp",
        "listed_pt1"
    ]

    logging.info("Reading past predictions from db.")
    query = Query()
    query.read_last_future_predictions()
    loader = DBConnector()
    loader.run_query(query)

    predictions = loader.data
    leagues = ['Premier League', 'Championship', 'League One', 'League Two', 'National League']
    predictions = predictions[predictions['league'].isin(leagues)]
    predictions = update_team_name(predictions)
    predictions_table = output_predhub_table(predictions, cols_pred)
    meta_table = output_matches_meta_table(predictions, cols_meta)
    print(predictions_table)
    print(meta_table)

    os.environ["API_DB_USER"] = "tom"
    os.environ["API_DB_PASSWORD"] = "password"
    os.environ["API_DB_HOST"] = "localhost"
    os.environ["API_DB_PORT"] = "5430"
    os.environ["API_DB_DB"] = "api_data"

    TABLE_NAME_PRED = "predictions"
    sport = 'football'

    delete_sport_rows(TABLE_NAME_PRED, sport)
    add_sport_rows(TABLE_NAME_PRED, sport, predictions_table)

    TABLE_NAME_META = "matches_meta"
    sport = 'football'

    create_and_upload_matches_meta_table(meta_table, 'football')