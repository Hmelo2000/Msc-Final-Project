import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

#Load the data
#read the downloaded data in CSV format into Python
df = pd.read_csv("test_data.csv")
#eliminate irrelevant columns
df = df.drop(["Extra", "Att.", "LOG","Notes"], axis=1)

#Transform the data
#add new features
df['goal_difference'] = df['Hg'] - df['Vg']

#create new variables to show home team win or loss result
df['home_win'] = np.where(df['goal_difference'] > 0, 1, 0)
df['home_loss'] = np.where(df['goal_difference'] < 0, 1, 0)

df_visitor = pd.get_dummies(df['Visitor'], dtype=np.int64)
df_home = pd.get_dummies(df['Home'], dtype=np.int64)

#Combine results to get the final dataset
#subtract home from visitor
df_model = df_home.sub(df_visitor) 
df_model['goal_difference'] = df['goal_difference']

#Build the predictive model (ridge regression)

ridge_regression_model = Ridge(alpha=0.001)

X = df_model.drop(['goal_difference'], axis=1)
y = df_model['goal_difference']

ridge_regression_model.fit(X, y)

#Display the results (coefficients of the model)
df_ratings = pd.DataFrame(data={'team': X.columns, 'rating': ridge_regression_model.coef_})
print(df_ratings)


