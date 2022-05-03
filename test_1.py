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
#print(df_ratings)

# Graphical User Interface

#Importing Libraries
from tkinter import *
from PIL import ImageTk, Image
 
root = Tk()
root.title("American Sports Prediction System") #Set Title of the Window
root.geometry("725x500") # Setting Dimensions

Title = Label(root, text="Which sport (out of the 2 below) would you like to make a prediciton in: ", font=("Gamerock", 17, "bold"))
Title.grid(row=0, column=0)

#create button for the basketball sport
BasketballButton = Button(root, text="Basketball", padx=4, pady=3, command=basketballfunction, fg="orange", font=("Gamerock", 14, "italic"))
BasketballButton.grid(row=1, column=0) # Position the button

#create button for the hockey sport
HockeyButton = Button(root, text="Hockey", padx=4, pady=3, command=hockeyfunction, fg="blue", font=("Gamerock", 14, "italic"))
HockeyButton.grid(row=2, column=0) # Position the button

#Create and display downloaded sports image on the GUI 
my_img = ImageTk.PhotoImage(Image.open("icon.jpeg"))
photo = Label(image=my_img)
photo.grid(row=3, column=0)

#Create button for the prediction
PredictButton = Button(root, text="Predict", padx=4, pady=4, command=predictfunction, fg="green")
#Create button that will allow you to make other predictions
AnotherPredictionButton = Button(root, text="Make Another Prediction", padx=4, pady=4, command=AnotherPrediction, fg="red")

root.mainloop()


