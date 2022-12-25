import pandas as pd
import statsmodels.api as sm

# Load the data
df = pd.read_csv('football_data.csv')

# Preprocess the data
# Create a sample dataframe
df = pd.DataFrame({'Group': ['A', 'A', 'B', 'B', 'A', 'B'], 'Value': [1, 2, 3, 4, 5, 6]})

window = 30

# Calculate the moving average for the 'Value' column, grouped by the 'Group' column
df['home_goals_scored'] = df.groupby('pt1')['home_goals_scored'].rolling(window).mean().reset_index(0, drop=True)
df['home_goals_conceded'] = df.groupby('pt1')['away_goals_scored'].rolling(window).mean().reset_index(0, drop=True)
df['away_goals_scored'] = df.groupby('pt2')['away_goals_scored'].rolling(window).mean().reset_index(0, drop=True)
df['away_goals_conceded'] = df.groupby('pt2')['home_goals_scored'].rolling(window).mean().reset_index(0, drop=True)

print(df)

df = df.dropna()
df['home_strength'] = (df['home_goals_scored'] - df['home_goals_conceded']) / window
df['away_strength'] = (df['away_goals_scored'] - df['away_goals_conceded']) / window

# Split the data into training and test sets
train_df = df.sample(frac=0.8, random_state=1)
test_df = df.drop(train_df.index)

# Define the Dixon-Coles model
poisson_model = sm.Poisson(train_df['home_goals'], train_df[['home_strength', 'away_strength', 'home']])

# Fit the model to the training data
poisson_model_fit = poisson_model.fit()

# Make predictions on the test data
predictions = poisson_model_fit.predict(test_df[['home_strength', 'away_strength', 'home']])

# Evaluate the performance of the model
mse = mean_squared_error(test_df['home_goals'], predictions)
print(f'Mean squared error: {mse}')
