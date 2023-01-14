"""
This file pulls all historical matches from football-data.co.uk. This site only contains information for Serie A and B (not Serie C), and so can
only be used as reference.
"""

import bs4 as bs
import os
import pandas as pd
import requests


def pull_italy_links(url):
    req = requests.get(url + "/italym.php")
    soup = bs.BeautifulSoup(req.content, features="html.parser")
    links = [f"{url}/{a['href']}" for a in soup.find_all('a', href=True) if ".csv" in a["href"]]
    return links


def correct_csv(csv_file):
    """
    Correct csv files with rows
    with more items than headers.
    """
    with open(csv_file, encoding="utf8", errors='ignore') as f:
        csvfile = f.read().split("\n")
        headers = csvfile[0].split(",")
        total_headers = len(headers)
        new_lines = []
        for lines in csvfile[1:]:
            new_line = lines.split(",")[:total_headers]
            new_lines.append(new_line)
        df = pd.DataFrame(new_lines)
        df.columns = headers
        df.to_csv(csv_file)


def read_table(url):
    filepath = "temp.csv"
    req = requests.get(url, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in req.iter_content(1024):
            f.write(chunk)
    try:
        df = pd.read_csv(filepath, sep=",", na_values=["", " ", "-"])
    except Exception:
        correct_csv(filepath)
        df = pd.read_csv(filepath, sep=",", na_values=["", " ", "-"])
    os.remove(filepath)

    return df


def read_links(links):
    i = 0
    for link in links:
        try:
            df = pd.read_csv(link,
                            # index_col = 0,
                            error_bad_lines=False)
            if i == 0:
                main = df.copy()
                i += 1
            else:
                main = main.append(df)
            print(link)
        except:
            print(link)
            df = pd.read_csv(link, sep=",", encoding='cp1252', index_col = 0, error_bad_lines=False)
            # print(df.head())
            if i == 0:
                main = df.copy()
                i += 1
            else:
                main = main.append(df)
            print('Updated: ' + link)
    return main


def rename_columns(df):
    df.rename(columns={
        'Div': 'div',
        'Date': 'date',
        'Time': 'time', 
        'HomeTeam': 'home_team',
        'AwayTeam': 'away_team',
        'HS': 'home_shots',
        'AS': 'away_shots'
    }, inplace=True)

    return df


base_url = "https://www.football-data.co.uk"
list_of_links = pull_italy_links(base_url)
data = read_links(list_of_links)
data = rename_columns(data)
data.reset_index(inplace=True, drop=True)
data.to_csv("../../data/serie_a_b_matches.csv")
