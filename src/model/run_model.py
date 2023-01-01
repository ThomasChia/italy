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
    future = pd.read_csv("../../data/future_matches_processed.csv", index_col=0)
    future.reset_index(inplace=True, drop=True)
    matches = store_matches(future)
    future = future_to_tensor(future)
    return future, matches


def future_to_tensor(df):
    X = df.drop(['league', 'date', 'team', 'opponent'], axis=1).to_numpy()
    X = torch.tensor(X).float()
    
    return X


def store_matches(df):
    matches = df[['league', 'date', 'team', 'opponent', 'home']]
    return matches


@torch.no_grad()
def predict(x):
    logits = model(x)
    preds = torch.softmax(logits, dim=1)
    
    return preds


def preds_to_matches(preds, matches):
    preds = pd.DataFrame(preds.numpy())
    future_preds = pd.concat([matches, preds], axis=1)
    return future_preds


PATH = "trained_models/3_linear_layer.pt"
model = load_model(PATH)
future, matches = load_future_matches()
predictions = predict(future)
future = preds_to_matches(predictions, matches)
future.to_csv("../../data/future_predictions.csv")