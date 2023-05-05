import pandas as pd
from sklearn.linear_model import LinearRegression


class Model:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.model = LinearRegression()

    def train(self) -> None:
        # train the model on the data
        self.model.fit(self.data)