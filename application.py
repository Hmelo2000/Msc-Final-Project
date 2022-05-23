#Import Libraries
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.svm import SVR

#Load the data
#read the downloaded data in CSV format into Python
df_hockey = pd.read_csv("HockeyResults.csv")
df_basketball = pd.read_csv("BasketballResults.csv")

#eliminate irrelevant columns
df_hockey = df_hockey.drop(["ExtraTime", "Att.", "LOG","Notes"], axis=1)
df_basketball = df_basketball.drop(["BoxScore","ExtraTime", "Attend.","Notes"], axis=1)

#Transform the data
#add new features
df_hockey['goal_difference'] = df_hockey['Hg'] - df_hockey['Vg']
df_basketball['goal_difference'] = df_basketball['HPTS'] - df_basketball['VPTS']

#create new variables to show home team win or loss result
df_hockey['home_win'] = np.where(df_hockey['goal_difference'] > 0, 1, 0)
df_hockey['home_loss'] = np.where(df_hockey['goal_difference'] < 0, 1, 0)
df_basketball['home_win'] = np.where(df_basketball['goal_difference'] > 0, 1, 0)
df_basketball['home_loss'] = np.where(df_basketball['goal_difference'] < 0, 1, 0)

df_visitor_hockey = pd.get_dummies(df_hockey['Visitor'], dtype=np.int64)
df_home_hockey = pd.get_dummies(df_hockey['Home'], dtype=np.int64)
df_visitor_basketball = pd.get_dummies(df_basketball['Visitor'], dtype=np.int64)
df_home_basketball = pd.get_dummies(df_basketball['Home'], dtype=np.int64)

#Combine results to get the final dataset
#subtract home from visitor
df_model_hockey = df_home_hockey.sub(df_visitor_hockey) 
df_model_hockey['goal_difference'] = df_hockey['goal_difference']

df_model_basketball = df_home_basketball.sub(df_visitor_basketball) 
df_model_basketball['goal_difference'] = df_basketball['goal_difference']

#Separating X and y (goal difference) for training the models
X_hockey = df_model_hockey.drop(['goal_difference'], axis=1)
y_hockey = df_model_hockey['goal_difference']

X_basketball = df_model_basketball.drop(['goal_difference'], axis=1)
y_basketball= df_model_basketball['goal_difference']

#Build the predictive model #1 (ridge)
ridge_model_hockey = Ridge(alpha=0.001)
ridge_model_basketball = Ridge(alpha=0.001)

ridge_model_hockey.fit(X_hockey, y_hockey)
ridge_model_basketball.fit(X_basketball, y_basketball)

#Compute coefficients of the model #1 (ridge)
df_ratings_hockey_ridge = pd.DataFrame(data={'team': X_hockey.columns, 'rating': ridge_model_hockey.coef_})
df_ratings_basketball_ridge = pd.DataFrame(data={'team': X_basketball.columns, 'rating': ridge_model_basketball.coef_})

#Build the predictive model #2 (SVR)
svr_model_hockey = SVR(C=1.0, epsilon=0.2, kernel='linear')
svr_model_basketball = SVR(C=1.0, epsilon=0.2, kernel='linear')

svr_model_hockey.fit(X_hockey, y_hockey)
svr_model_basketball.fit(X_basketball, y_basketball)

#Compute coefficients of the model #2 (SVR)
df_ratings_hockey_svr = pd.DataFrame(data={'team': X_hockey.columns, 'rating': svr_model_hockey.coef_.flatten()})
df_ratings_basketball_svr = pd.DataFrame(data={'team': X_basketball.columns, 'rating': svr_model_basketball.coef_.flatten()})


# Graphical User Interface

#Importing Libraries
from tkinter import *
from PIL import ImageTk, Image
 
root = Tk()
root.title("Sports Prediction System") #Set Title of the Window
root.geometry("720x555") # Setting Dimensions

Title = Label(root, text="Which sport (out of the 2 below) would you like to make a prediciton in: ", font=("Gamerock", 17, "bold"))
Title.grid(row=0, column=0)

def mainfunction(button, teams):
    #Disable chosen button (sport already chosen)
    button['state'] = DISABLED

    #Display predict and make another prediction buttons
    PredictButton.grid(row=9, column=0)
    AnotherPredictionButton.grid(row=10, column=0)

    #Disable  make another prediction Button
    AnotherPredictionButton['state'] = DISABLED

    #Create Home and Away Labels
    HomeLabel = Label(root, text="Home Team: ")
    AwayLabel = Label(root, text="Away Team: ")

    #Display both Labels
    HomeLabel.grid(row=5, column=0)
    AwayLabel.grid(row=7, column=0)

    #Create global variables that hold the team chosen in the drop down boxes
    global home_team
    global away_team
    global drop_menu_1
    global drop_menu_2

    #Create drop down box that will allow the user to pick the home team
    home_team= StringVar()
    home_team.set(teams[0])
    drop_menu_1 = OptionMenu(root, home_team, *teams)
    drop_menu_1.grid(row=6, column=0)

    #Create drop down box that will allow the user to pick the away team
    away_team= StringVar()
    away_team.set(teams[1])
    drop_menu_2 = OptionMenu(root, away_team, *teams)
    drop_menu_2.grid(row=8, column=0)

#What happens when the user clicks the predict button
def predictfunction():
    #Check which sport and teams (home and away) the user chose 
    if HockeyButton['state'] == DISABLED:
        for i in range(len(df_ratings_hockey_ridge)):
            if df_ratings_hockey_ridge.iloc[i, 0] == home_team.get():
                x = i
        for i in range(len(df_ratings_hockey_ridge)):
            if df_ratings_hockey_ridge.iloc[i, 0] == away_team.get():
                y = i

        # create global variable for the predicted winner for the multiple models
        global winnerLabel
        global winnerLabel2

        #Find out whether the home or away team is the most likely team to win according to ridge regression
        if (df_ratings_hockey_ridge.iloc[x, 1] > df_ratings_hockey_ridge.iloc[y, 1]):
            winnerLabel = Label(root, text="Most likely Winner (Ridge Regression): " + home_team.get() + " (Home Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel.grid(row=11, column=0)
        else:
            winnerLabel = Label(root, text="Most likely Winner (Ridge Regression): " + away_team.get() + " (Away Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel.grid(row=11, column=0)
            
        #Find out whether the home or away team is the most likely team to win according to SVR
        if (df_ratings_hockey_svr.iloc[x, 1] > df_ratings_hockey_svr.iloc[y, 1]):
            winnerLabel2 = Label(root, text="Most likely Winner (Support Vector Regression): " + home_team.get() + " (Home Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel2.grid(row=12, column=0)
        else:
            winnerLabel2 = Label(root, text="Most likely Winner (Support Vector Regression): " + away_team.get() + " (Away Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel2.grid(row=12, column=0)

        #Disable predict button 
        PredictButton['state'] = DISABLED
        #Enable another prediction button
        AnotherPredictionButton['state'] = NORMAL

        #Disable both drop down boxes that  have been just used
        drop_menu_1['state'] = DISABLED
        drop_menu_2['state'] = DISABLED

        #Disable every sports button
        HockeyButton['state'] = DISABLED
        BasketballButton['state'] = DISABLED

    #Check which sport and teams the user chose 
    elif BasketballButton['state'] == DISABLED:
        for i in range(len(df_ratings_basketball_ridge)):
            if df_ratings_basketball_ridge.iloc[i, 0] == home_team.get():
                x = i
        for i in range(len(df_ratings_basketball_ridge)):
            if df_ratings_basketball_ridge.iloc[i, 0] == away_team.get():
                y = i

        #Find out whether the home or away team is the most likely team to win according to ridge regression
        if (df_ratings_basketball_ridge.iloc[x, 1] > df_ratings_basketball_ridge.iloc[y, 1]):
            winnerLabel = Label(root, text="Most likely Winner (Ridge Regression): " + home_team.get() + " (Home Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel.grid(row=11, column=0)
        else:
            winnerLabel = Label(root, text="Most likely Winner (Ridge Regression): " + away_team.get() + " (Away Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel.grid(row=11, column=0)

        #Find out whether the home or away team is the most likely team to win according to SVR
        if (df_ratings_basketball_svr.iloc[x, 1] > df_ratings_basketball_svr.iloc[y, 1]):
            winnerLabel2 = Label(root, text="Most likely Winner (Support Vector Regression): " + home_team.get() + " (Home Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel2.grid(row=12, column=0)
        else:
            winnerLabel2 = Label(root, text="Most likely Winner (Support Vector Regression): " + away_team.get() + " (Away Team)", font=("Times New Roman", 18, "bold"))
            winnerLabel2.grid(row=12, column=0)

        #Disable predict button 
        PredictButton['state'] = DISABLED
        #Enable another prediction button
        AnotherPredictionButton['state'] = NORMAL

        #Disable both drop down boxes that  have been just used
        drop_menu_1['state'] = DISABLED
        drop_menu_2['state'] = DISABLED

        #Disable every sports button
        HockeyButton['state'] = DISABLED
        BasketballButton['state'] = DISABLED

# Make another prediction button
def AnotherPrediction():
    #Find out which sport has just been used and enable the button for the other ones
    if home_team.get() in teams_hockey:
        BasketballButton['state'] = NORMAL
        
    if home_team.get() in teams_basketball:
        HockeyButton['state'] = NORMAL

    #Eliminate the label related to the predicted winner for the various models
    winnerLabel.destroy()
    winnerLabel2.destroy()

    #Enable predict button 
    PredictButton['state'] = NORMAL
    #Disable another prediction button
    AnotherPredictionButton['state'] = DISABLED

    #Enable drop down boxes so the user can pick different teams if he wishes
    drop_menu_1['state'] = NORMAL
    drop_menu_2['state'] = NORMAL

# Hockey Button function
def hockeyfunction():
    # If a prediction has just beeen made in another sport, erase the previous drop down boxes so that they don't overlap with the ones
    if BasketballButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    elif HockeyButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    #Enable basketball, football and predict button
    BasketballButton['state'] = NORMAL
    PredictButton['state'] = NORMAL
    
    #Call mainfunction with the respective sport button and teams
    mainfunction(HockeyButton, teams_hockey)

def basketballfunction():
     # If a prediction has just beeen made in another sport, erase the previous drop down boxes so that they don't overlap with the ones
    if HockeyButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()
        
    #Enable hockey, football and predict button
    HockeyButton['state'] = NORMAL
    PredictButton['state'] = NORMAL
    
    #Call mainfunction with the respective sport button and teams
    mainfunction(BasketballButton, teams_basketball)

#create list called teams that contains every hockey team's name
teams_hockey = []
for i in range(len(df_ratings_hockey_ridge)):
    teams_hockey.append(df_ratings_hockey_ridge.iloc[i, 0])

#create list called teams that contains every basketball team's name
teams_basketball = []
for i in range(len(df_ratings_basketball_ridge)):
    teams_basketball.append(df_ratings_basketball_ridge.iloc[i, 0])

#create button for the hockey sport
HockeyButton = Button(root, text="Hockey", padx=4, pady=3, command=hockeyfunction, fg="blue", font=("Gamerock", 14, "italic"))
HockeyButton.grid(row=1, column=0) # Position the button

#create button for the basketball sport
BasketballButton = Button(root, text="Basketball", padx=4, pady=3, command=basketballfunction, fg="orange", font=("Gamerock", 14, "italic"))
BasketballButton.grid(row=2, column=0) # Position the button

#Create and display downloaded sports image on the GUI 
my_img = ImageTk.PhotoImage(Image.open("icon.jpeg"))
photo = Label(image=my_img)
photo.grid(row=4, column=0)

#Create button for the prediction
PredictButton = Button(root, text="Predict", padx=4, pady=4, command=predictfunction, fg="green")
#Create button that will allow you to make other predictions
AnotherPredictionButton = Button(root, text="Make Another Prediction", padx=4, pady=4, command=AnotherPrediction, fg="red")

root.mainloop()
