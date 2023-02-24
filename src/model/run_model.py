"""
This file is to run the model over future matches and output predictions.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

torch.device("mps")


def load_model(PATH):
    model = torch.load(PATH)
    model.train()
    return model


def load_future_matches():
    future = pd.read_csv("../data/future_matches_processed.csv", index_col=0)
    future.columns = future.columns.str.split('.').str[0]
    future = future.loc[:,~future.columns.duplicated()].copy()
    future['date'] = pd.to_datetime(future['date'])
    future.sort_values(by=['date', 'team'], inplace=True)
    future.reset_index(inplace=True, drop=True)
    matches = store_matches(future)
    future = build_future_dataset(future)
    return future, matches


def future_to_tensor(df):
    X = df.drop(['league', 'date', 'team', 'opponent'], axis=1).to_numpy()
    X = torch.tensor(X).float()
    
    return X


def build_future_dataset(df):
    df_copy = df.copy()
    # date = df_copy[['date']].iloc[:,0]
    df_copy.drop(['league', 'date', 'team', 'opponent'], axis=1, inplace=True)
    # df_copy['date'] = date
    # df_copy.drop(['date'], axis=1, inplace=True)
    
    X = df_copy.drop(['result'], axis=1).to_numpy()
    X = torch.tensor(X).float()
    
    return X


def store_matches(df):
    matches = df[['league', 'date', 'team', 'opponent', 'home']]
    matches = matches.loc[:,~matches.columns.duplicated()].copy()
    return matches


@torch.no_grad()
def predict(x):
    x = x[:, None, :]
    logits = model(x)
    preds = torch.softmax(logits, dim=1)
    
    return preds


def preds_to_matches(preds, matches):
    preds = pd.DataFrame(preds.numpy())
    future_preds = pd.concat([matches, preds], axis=1)
    return future_preds


# PATH = "trained_models/3_linear_layer.pt"
PATH = "model/trained_models/wavenet_4.pt"
model = load_model(PATH)
model.train()
future, matches = load_future_matches()
predictions = predict(future)
future = preds_to_matches(predictions, matches)
future.to_csv("../data/future_predictions.csv")
print(future[future['team']=='cesena'].head(1))
print(future[future['team']=='fermana'].head(1))