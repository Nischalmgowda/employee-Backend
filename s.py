import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# Load and preprocess data
df = pd.read_csv('smg.csv', parse_dates=['Datetime'])
df['dayofyear'] = df['Datetime'].dt.dayofyear
df['year'] = df['Datetime'].dt.year

# Select relevant features and target
features = ['dayofyear', 'Temperature']
target = 'Consumption'

# Train-test split
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Linear Regression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Evaluate the model
lr_predictions = lr_model.predict(X_test)
lr_mae = mean_absolute_error(y_test, lr_predictions)
print(f'Linear Regression MAE: {lr_mae}')
# Predict for a specific date
from datetime import datetime

# Specify the date for prediction
date_str = '2024-08-30'  # Example date
selected_date = pd.to_datetime(date_str)
dayofyear = selected_date.dayofyear

# Assume we have temperature data for that date (e.g., 25 degrees)
temperature = 35

# Create a DataFrame for the new data
X_new = pd.DataFrame({'dayofyear': [dayofyear], 'Temperature': [temperature]})

# Make prediction
lr_prediction = lr_model.predict(X_new)[0]
print(f'Predicted consumption on {date_str}: {lr_prediction} kWh')