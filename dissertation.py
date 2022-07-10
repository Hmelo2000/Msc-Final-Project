import numpy as np 
import pandas as pd


#Read Data
results2020_2021_nba = pd.read_csv('NBA2020_2021.csv')
results2020_2021_nhl = pd.read_csv('NHL2020_2021.csv')
results2020_mlb = pd.read_csv('MLB2020.csv')

# Fix the name of the columns, if necessary
results2020_2021_nba.columns = ["Date", "Start Time", "Visitor Team", "VisitorPts", "Home Team", "HomePts", "Score Type", "OT?", "Attendance", "Arena", "Notes"]
results2020_2021_nhl.columns = ["Date", "Visitor Team", "VisitorPts", "Home Team", "HomePts", "OT?", "Attendance", "Length of Game", "Notes"]

# Drop unnecessary columns
results2020_2021_nba=results2020_2021_nba.drop(["Start Time", "Score Type", "OT?", "Attendance", "Arena", "Notes"], axis=1)
results2020_2021_nhl=results2020_2021_nhl.drop(["OT?", "Attendance", "Length of Game", "Notes"], axis=1)
results2020_mlb=results2020_mlb.drop(["Day of Week", "Day or Night", "Time of Game (minutes)"], axis=1)

results2020_2021_nba['HomeWin'] = results2020_2021_nba["VisitorPts"] < results2020_2021_nba["HomePts"]
results2020_2021_nhl['HomeWin'] = results2020_2021_nhl["VisitorPts"] < results2020_2021_nhl["HomePts"]
results2020_mlb['HomeWin'] = results2020_mlb["VisitorPts"] < results2020_mlb["HomePts"]

# Our 'class values'
y_true_nba_2020_2021 = results2020_2021_nba["HomeWin"].values
y_true_nhl_2020_2021 = results2020_2021_nhl["HomeWin"].values
y_true_mlb_2020 = results2020_mlb["HomeWin"].values


# Creating some more features   
results2020_2021_nba["HomeLastWin"] = False
results2020_2021_nba["VisitorLastWin"] = False

results2020_2021_nhl["HomeLastWin"] = False
results2020_2021_nhl["VisitorLastWin"] = False

results2020_mlb["HomeLastWin"] = False
results2020_mlb["VisitorLastWin"] = False

# Now compute the actual values for these
# Did the home and visitor teams win their last game?
from collections import defaultdict

won_last_nba = defaultdict(int)

for index, row in results2020_2021_nba.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_nba[home_team]
    row["VisitorLastWin"] = won_last_nba[visitor_team]
    results2020_2021_nba.iloc[index] = row
    # Set current win
    won_last_nba[home_team] = row["HomeWin"]
    won_last_nba[visitor_team] = not row["HomeWin"]
    
won_last_nhl = defaultdict(int)

for index, row in results2020_2021_nhl.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_nhl[home_team]
    row["VisitorLastWin"] = won_last_nhl[visitor_team]
    results2020_2021_nhl.iloc[index] = row
    # Set current win
    won_last_nhl[home_team] = row["HomeWin"]
    won_last_nhl[visitor_team] = not row["HomeWin"]
    
won_last_mlb = defaultdict(int)
    
for index, row in results2020_mlb.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_mlb[home_team]
    row["VisitorLastWin"] = won_last_mlb[visitor_team]
    results2020_mlb.iloc[index] = row
    # Set current win
    won_last_mlb[home_team] = row["HomeWin"]
    won_last_mlb[visitor_team] = not row["HomeWin"]
    

# Let's see which team finished higher the previous year (to not overfit)    
NBA2019_2020_Standings = pd.read_csv("StandingsNBA2019_2020.csv", skiprows=[0], index_col="Team")
NHL2019_2020_Standings = pd.read_csv("StandingsNHL2019_2020.csv", index_col="Team")
MLB2019_Standings = pd.read_csv("StandingsMLB2019.csv", index_col="Team")


# We can then create a new feature -- HomeTeamRanksHigher

def home_team_ranks_higher_nba_2019_2020(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = NBA2019_2020_Standings.loc[home_team]["Rk"]
    visitor_rank = NBA2019_2020_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

def home_team_ranks_higher_nhl_2019_2020(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = NHL2019_2020_Standings.loc[home_team]["Rk"]
    visitor_rank = NHL2019_2020_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

def home_team_ranks_higher_mlb_2019(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = MLB2019_Standings.loc[home_team]["Rk"]
    visitor_rank = MLB2019_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

results2020_2021_nba["HomeTeamRanksHigher"] = results2020_2021_nba.apply(home_team_ranks_higher_nba_2019_2020, axis=1)
results2020_2021_nhl["HomeTeamRanksHigher"] = results2020_2021_nhl.apply(home_team_ranks_higher_nhl_2019_2020, axis=1)
results2020_mlb["HomeTeamRanksHigher"] = results2020_mlb.apply(home_team_ranks_higher_mlb_2019, axis=1)


last_match_winner_nba = defaultdict(int)

def home_team_won_last_nba(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    #Sort for a consistent ordering
    teams = tuple(sorted([home_team, visitor_team]))
    result = 1 if last_match_winner_nba[teams] == row["Home Team"] else 0
    #Update record for next encounter
    winner = row["Home Team"] if row["HomeWin"] else row["Visitor Team"]
    
    last_match_winner_nba[teams] = winner
    
    return result

results2020_2021_nba["HomeTeamWonLast"] = results2020_2021_nba.apply(home_team_won_last_nba, axis=1)
#results2020_2021_nhl["HomeTeamWonLast"] = results2020_2021_nhl.apply(home_team_won_last_nhl, axis=1)


 
X_nba_2020_2021 = results2020_2021_nba[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher", "HomeTeamWonLast"]].values
X_nhl_2020_2021 = results2020_2021_nhl[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"]].values
X_mlb_2020 = results2020_mlb[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"]].values


# TESTING on 2021/2022 Season

#Read Data
results2021_2022_nba = pd.read_csv('NBA2021_2022.csv')
results2021_2022_nhl = pd.read_csv('NHL2021_2022.csv')
results2021_mlb = pd.read_csv('MLB2021.csv')

# Fix the name of the columns
results2021_2022_nba.columns = ["Date", "Start Time", "Visitor Team", "VisitorPts", "Home Team", "HomePts", "Score Type", "OT?", "Attendance", "Arena", "Notes"]
results2021_2022_nhl.columns = ["Date", "Visitor Team", "VisitorPts", "Home Team", "HomePts", "OT?", "Attendance", "Length of Game", "Notes"]

# Drop unnecessary columns
results2021_2022_nba=results2021_2022_nba.drop(["Start Time", "Score Type", "OT?", "Attendance", "Arena", "Notes"], axis=1)
results2021_2022_nhl=results2021_2022_nhl.drop(["OT?", "Attendance", "Length of Game", "Notes"], axis=1)
results2021_mlb=results2021_mlb.drop(["Day of Week", "Day or Night", "Attendance", "Time of Game (minutes)"], axis=1)

results2021_2022_nba['HomeWin'] = results2021_2022_nba["VisitorPts"] < results2021_2022_nba["HomePts"]
results2021_2022_nhl['HomeWin'] = results2021_2022_nhl["VisitorPts"] < results2021_2022_nhl["HomePts"]
results2021_mlb['HomeWin'] = results2021_mlb["VisitorPts"] < results2021_mlb["HomePts"]

# Our 'class values'
y_true_nba_2021_2022 = results2021_2022_nba["HomeWin"].values
y_true_nhl_2021_2022 = results2021_2022_nhl["HomeWin"].values
y_true_mlb_2021 = results2021_mlb["HomeWin"].values


# What's the baseline for each sport (Home Teams win games more frequently)
n_games_nba = len(results2021_2022_nba["HomeWin"])
n_homewins_nba = results2021_2022_nba["HomeWin"].sum()
win_percentage_nba = n_homewins_nba/n_games_nba
print("Home Win percentage for NBA: ", 100*win_percentage_nba)

n_games_nhl = len(results2021_2022_nhl["HomeWin"])
n_homewins_nhl = results2021_2022_nhl["HomeWin"].sum()
win_percentage_nhl = n_homewins_nhl/n_games_nhl
print("Home Win percentage for NHL: ", 100*win_percentage_nhl)

n_games_mlb = len(results2021_mlb["HomeWin"])
n_homewins_mlb = results2021_mlb["HomeWin"].sum()
win_percentage_mlb = n_homewins_mlb/n_games_mlb
print("Home Win percentage for MLB: ", 100*win_percentage_mlb)


# Creating some more features   
results2021_2022_nba["HomeLastWin"] = False
results2021_2022_nba["VisitorLastWin"] = False

results2021_2022_nhl["HomeLastWin"] = False
results2021_2022_nhl["VisitorLastWin"] = False

results2021_mlb["HomeLastWin"] = False
results2021_mlb["VisitorLastWin"] = False

# Now compute the actual values for these
# Did the home and visitor teams win their last game?
for index, row in results2021_2022_nba.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_nba[home_team]
    row["VisitorLastWin"] = won_last_nba[visitor_team]
    results2021_2022_nba.iloc[index] = row
    # Set current win
    won_last_nba[home_team] = row["HomeWin"]
    won_last_nba[visitor_team] = not row["HomeWin"]
    
for index, row in results2021_2022_nhl.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_nhl[home_team]
    row["VisitorLastWin"] = won_last_nhl[visitor_team]
    results2021_2022_nhl.iloc[index] = row
    # Set current win
    won_last_nhl[home_team] = row["HomeWin"]
    won_last_nhl[visitor_team] = not row["HomeWin"]
    
for index, row in results2021_mlb.iterrows():
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    row["HomeLastWin"] = won_last_mlb[home_team]
    row["VisitorLastWin"] = won_last_mlb[visitor_team]
    results2021_mlb.iloc[index] = row
    # Set current win
    won_last_mlb[home_team] = row["HomeWin"]
    won_last_mlb[visitor_team] = not row["HomeWin"]

# Let's see which team finished higher the previous year (to not overfit)    
NBA2020_2021_Standings = pd.read_csv("StandingsNBA2020_2021.csv", skiprows=[0], index_col="Team")
NHL2020_2021_Standings = pd.read_csv("StandingsNHL2020_2021.csv", index_col="Team")
MLB2020_Standings = pd.read_csv("StandingsMLB2020.csv", index_col="Team")

# We can then create a new feature -- HomeTeamRanksHigher
def home_team_ranks_higher_nba_2020_2021(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = NBA2020_2021_Standings.loc[home_team]["Rk"]
    visitor_rank = NBA2020_2021_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

def home_team_ranks_higher_nhl_2020_2021(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = NHL2020_2021_Standings.loc[home_team]["Rk"]
    visitor_rank = NHL2020_2021_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

def home_team_ranks_higher_mlb_2020(row):
    home_team = row["Home Team"]
    visitor_team = row["Visitor Team"]
    
    home_rank = MLB2020_Standings.loc[home_team]["Rk"]
    visitor_rank = MLB2020_Standings.loc[visitor_team]["Rk"]
    return home_rank < visitor_rank #Ranking higher == lower rank number

results2021_2022_nba["HomeTeamRanksHigher"] = results2021_2022_nba.apply(home_team_ranks_higher_nba_2020_2021, axis=1)
results2021_2022_nhl["HomeTeamRanksHigher"] = results2021_2022_nhl.apply(home_team_ranks_higher_nhl_2020_2021, axis=1)
results2021_mlb["HomeTeamRanksHigher"] = results2021_mlb.apply(home_team_ranks_higher_mlb_2020, axis=1)


results2021_2022_nba["HomeTeamWonLast"] = results2021_2022_nba.apply(home_team_won_last_nba, axis=1)
#results2021_2022_nhl["HomeTeamWonLast"] = results2021_2022_nhl.apply(home_team_won_last_nhl, axis=1)


X_nba_2021_2022 = results2021_2022_nba[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher", "HomeTeamWonLast"]].values
X_nhl_2021_2022 = results2021_2022_nhl[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"]].values
X_mlb_2021 = results2021_mlb[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"]].values



from sklearn.metrics import classification_report


from sklearn.linear_model import LogisticRegression

logistic_regression_nba = LogisticRegression()
logistic_regression_nba.fit(X_nba_2020_2021, y_true_nba_2020_2021)

y_pred_nba_2021_2022_logistic_regression = logistic_regression_nba.predict(X_nba_2021_2022)

print("")
print("Classification Report NBA (Logistic Regression):")
print(classification_report(y_true_nba_2021_2022, y_pred_nba_2021_2022_logistic_regression))
print("Using Logistic Regression results in getting {:.1f}% of predictions of the NBA correct!".format(100*np.mean(y_pred_nba_2021_2022_logistic_regression == y_true_nba_2021_2022)))

logistic_regression_nhl = LogisticRegression()
logistic_regression_nhl.fit(X_nhl_2020_2021, y_true_nhl_2020_2021)

y_pred_nhl_2021_2022_logistic_regression = logistic_regression_nhl.predict(X_nhl_2021_2022)

print("")
print("Classification Report NHL (Logistic Regression):")
print(classification_report(y_true_nhl_2021_2022, y_pred_nhl_2021_2022_logistic_regression))
print("Using Logistic Regression results in getting {:.1f}% of predictions of the NHL correct!".format(100*np.mean(y_pred_nhl_2021_2022_logistic_regression == y_true_nhl_2021_2022)))

logistic_regression_mlb = LogisticRegression()
logistic_regression_mlb.fit(X_mlb_2020, y_true_mlb_2020)

y_pred_mlb_2021_logistic_regression = logistic_regression_mlb.predict(X_mlb_2021)

print("")
print("Classification Report MLB (Logistic Regression):")
print(classification_report(y_true_mlb_2021, y_pred_mlb_2021_logistic_regression))
print("Using Logistic Regression results in getting {:.1f}% of predictions of the MLB correct!".format(100*np.mean(y_pred_mlb_2021_logistic_regression == y_true_mlb_2021)))

from sklearn.tree import DecisionTreeClassifier

decision_tree_nba = DecisionTreeClassifier()
decision_tree_nba.fit(X_nba_2020_2021, y_true_nba_2020_2021)

y_pred_nba_2021_2022_decision_tree = decision_tree_nba.predict(X_nba_2021_2022)

print("")
print("Classification Report NBA (Decision Tree):")
print(classification_report(y_true_nba_2021_2022, y_pred_nba_2021_2022_decision_tree))
print("Using Decision Tree results in getting {:.1f}% of predictions of the NBA correct!".format(100*np.mean(y_pred_nba_2021_2022_decision_tree == y_true_nba_2021_2022)))

decision_tree_nhl = DecisionTreeClassifier()
decision_tree_nhl.fit(X_nhl_2020_2021, y_true_nhl_2020_2021)

y_pred_nhl_2021_2022_decision_tree = decision_tree_nhl.predict(X_nhl_2021_2022)

print("")
print("Classification Report NHL (Decision Tree):")
print(classification_report(y_true_nhl_2021_2022, y_pred_nhl_2021_2022_decision_tree))
print("Using Decision Tree results in getting {:.1f}% of predictions of the NHL correct!".format(100*np.mean(y_pred_nhl_2021_2022_decision_tree == y_true_nhl_2021_2022)))

decision_tree_mlb = DecisionTreeClassifier()
decision_tree_mlb.fit(X_mlb_2020, y_true_mlb_2020)

y_pred_mlb_2021_decision_tree = decision_tree_mlb.predict(X_mlb_2021)

print("")
print("Classification Report MLB (Decision Tree):")
print(classification_report(y_true_mlb_2021, y_pred_mlb_2021_decision_tree))
print("Using Decision Tree results in getting {:.1f}% of predictions of the MLB correct!".format(100*np.mean(y_pred_mlb_2021_decision_tree == y_true_mlb_2021)))

from sklearn.neighbors import KNeighborsClassifier

nearest_neighbors_nba = KNeighborsClassifier()
nearest_neighbors_nba.fit(X_nba_2020_2021, y_true_nba_2020_2021)

y_pred_nba_2021_2022_nearest_neighbor = nearest_neighbors_nba.predict(X_nba_2021_2022)

print("")
print("Classification Report NBA (K-Nearest Neighbours):")
print(classification_report(y_true_nba_2021_2022, y_pred_nba_2021_2022_nearest_neighbor))
print("Using Nearest Neighbor results in getting {:.1f}% of predictions of the NBA correct!".format(100*np.mean(y_pred_nba_2021_2022_nearest_neighbor == y_true_nba_2021_2022)))

nearest_neighbors_nhl = KNeighborsClassifier()
nearest_neighbors_nhl.fit(X_nhl_2020_2021, y_true_nhl_2020_2021)

y_pred_nhl_2021_2022_nearest_neighbor = nearest_neighbors_nhl.predict(X_nhl_2021_2022)

print("")
print("Classification Report NHL (K-Nearest Neighbours):")
print(classification_report(y_true_nhl_2021_2022, y_pred_nhl_2021_2022_nearest_neighbor))
print("Using Nearest Neighbor results in getting {:.1f}% of predictions of the NHL correct!".format(100*np.mean(y_pred_nhl_2021_2022_nearest_neighbor == y_true_nhl_2021_2022)))

nearest_neighbors_mlb = KNeighborsClassifier()
nearest_neighbors_mlb.fit(X_mlb_2020, y_true_mlb_2020)

y_pred_mlb_2021_nearest_neighbor = nearest_neighbors_mlb.predict(X_mlb_2021)

print("")
print("Classification Report MLB (K-Nearest Neighbours):")
print(classification_report(y_true_mlb_2021, y_pred_mlb_2021_nearest_neighbor))
print("Using Nearest Neighbor results in getting {:.1f}% of predictions of the MLB correct!".format(100*np.mean(y_pred_mlb_2021_nearest_neighbor == y_true_mlb_2021)))

from sklearn.neural_network import MLPClassifier

mlp_nba = MLPClassifier()
mlp_nba.fit(X_nba_2020_2021, y_true_nba_2020_2021)

y_pred_nba_2021_2022_mlp = mlp_nba.predict(X_nba_2021_2022)

print("")
print("Classification Report NBA (MLP):")
print(classification_report(y_true_nba_2021_2022, y_pred_nba_2021_2022_mlp))
print("Using MLP results in getting {:.1f}% of predictions of the NBA correct!".format(100*np.mean(y_pred_nba_2021_2022_mlp == y_true_nba_2021_2022)))

mlp_nhl = MLPClassifier()
mlp_nhl.fit(X_nhl_2020_2021, y_true_nhl_2020_2021)

y_pred_nhl_2021_2022_mlp = mlp_nhl.predict(X_nhl_2021_2022)

print("")
print("Classification Report NHL (MLP):")
print(classification_report(y_true_nhl_2021_2022, y_pred_nhl_2021_2022_mlp))
print("Using MLP results in getting {:.1f}% of predictions of the NHL correct!".format(100*np.mean(y_pred_nhl_2021_2022_mlp == y_true_nhl_2021_2022)))

mlp_mlb = MLPClassifier()
mlp_mlb.fit(X_mlb_2020, y_true_mlb_2020)

y_pred_mlb_2021_mlp = mlp_mlb.predict(X_mlb_2021)

print("")
print("Classification Report MLB (MLP):")
print(classification_report(y_true_mlb_2021, y_pred_mlb_2021_mlp))
print("Using MLP results in getting {:.1f}% of predictions of the MLB correct!".format(100*np.mean(y_pred_mlb_2021_mlp == y_true_mlb_2021)))



# Graphical User Interface

#Importing Libraries
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
 
root = Tk()
root.title("American Sports Prediction System") #Set Title of the Window
root.geometry("720x585") # Setting Dimensions

Title = Label(root, text="Which sport (out of the 3 below) would you like to make a prediciton in: ", font=("Gamerock", 17, "bold"))
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
    #Checks to see if Home Team and Away Team is the same team (Validation)
    if home_team.get() == away_team.get():
        #Shows error message if home team and away team is the same team
        messagebox.showwarning("warning", "Home Team and Away Team can't be the same team! Please choose diferent teams")  
    else:
        
        is_activated = False

        #Function that creates X for the prediction
        def X_prediction(results, standings, logistic_regression_sport, decision_tree_sport, nearest_neighbors_sport, mlp_sport):
            
            myList = []
            
            x = results.loc[(results['Home Team'] == home_team.get()) | (results['Visitor Team'] == home_team.get())].iloc[-1:]
            y = x['Home Team'].to_numpy()
            z = str(x["HomeWin"].to_numpy())[2:-1]
            if y[0] == home_team.get():
                if z == 'True':
                    myList.append(True)
                else:
                    myList.append(False)
            else:
                if z == "True":
                    myList.append(False)
                else:
                    myList.append(True)

            x = results.loc[(results['Home Team'] == away_team.get()) | (results['Visitor Team'] == away_team.get())].iloc[-1:]
            y = x['Home Team'].to_numpy()
            z = str(x["HomeWin"].to_numpy())[2:-1]
            if y[0] == away_team.get():
                if z == 'True':
                    myList.append(True)
                else:
                    myList.append(False)
            else:
                if z == "True":
                    myList.append(False)
                else:
                    myList.append(True)

            home_team_rank = standings.loc[home_team.get()]["Rk"]
            visitor_team_rank = standings.loc[away_team.get()]["Rk"]
            
            if home_team_rank < visitor_team_rank: #Ranking higher == lower rank number
                myList.append(True)
            else:
                myList.append(False)

            if BasketballButton['state'] == DISABLED:
                x = results.loc[(results['Home Team'] == home_team.get()) | (results['Visitor Team'] == home_team.get())]
                x = x.loc[(x['Home Team'] == away_team.get()) | (x['Visitor Team'] == away_team.get())].iloc[-1:]
                y = x['Home Team'].to_numpy()
                z = str(x["HomeWin"].to_numpy())[2:-1]
                if y[0] == home_team.get():
                    if z == 'True':
                        myList.append(1)
                    else:
                        myList.append(0)
                else:
                    if z == "True":
                        myList.append(0)
                    else:
                        myList.append(1)
                    
                myList=[myList]
                df = pd.DataFrame(myList, columns=["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher", "HomeTeamWonLast"])
                X_prediction_results = df[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher", "HomeTeamWonLast"]].values
            else:
                myList=[myList]
                df = pd.DataFrame(myList, columns=["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"])
                X_prediction_results = df[["HomeLastWin", "VisitorLastWin", "HomeTeamRanksHigher"]].values
                
            y_pred_logistic = logistic_regression_sport.predict(X_prediction_results)
            y_pred_logistic = str(y_pred_logistic)[2:-1]
            #Display and position the most likely winners according to each algorithm
            if y_pred_logistic == 'True':
                global winnerLabel
                winnerLabel = Label(root, text="Most likely winner (Logistic Regression): " + home_team.get() + "(Home Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel.grid(row=11, column=0)
            else:
                winnerLabel = Label(root, text="Most likely winner (Logistic Regression): " + away_team.get() + "(Away Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel.grid(row=11, column=0)

            y_pred_decision = decision_tree_sport.predict(X_prediction_results)
            y_pred_decision = str(y_pred_decision)[2:-1]
            #Display and position the most likely winners according to each algorithm
            if y_pred_decision == 'True':
                global winnerLabel2
                winnerLabel2 = Label(root, text="Most likely winner (Decision Tree): " + home_team.get() + "(Home Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel2.grid(row=12, column=0)
            else:
                winnerLabel2 = Label(root, text="Most likely winner (Decision Tree): " + away_team.get() + "(Away Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel2.grid(row=12, column=0)
                
            y_pred_neighbors = nearest_neighbors_sport.predict(X_prediction_results)
            y_pred_neighbors = str(y_pred_neighbors)[2:-1]
            #Display and position the most likely winners according to each algorithm
            if y_pred_neighbors == 'True':
                global winnerLabel3
                winnerLabel3 = Label(root, text="Most Likely winner (Nearest Neighbors): " + home_team.get() + "(Home Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel3.grid(row=13, column=0)
            else:
                winnerLabel3 = Label(root, text="Most Likely winner (Nearest Neighbors): " + away_team.get() + "(Away Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel3.grid(row=13, column=0)
                
            y_pred_mlp = mlp_sport.predict(X_prediction_results)
            y_pred_mlp = str(y_pred_mlp)[2:-1]
            #Display and position the most likely winners according to each algorithm
            if y_pred_mlp == 'True':
                global winnerLabel4
                winnerLabel4 = Label(root, text="Most Likely winner (MLP Classifier): " + home_team.get() + "(Home Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel4.grid(row=14, column=0)
            else:
                winnerLabel4 = Label(root, text="Most Likely winner (MLP Classifier): " + away_team.get() + "(Away Team)", font=("Times New Roman", 18, "bold"))
                winnerLabel4.grid(row=14, column=0)
                
        #Check which sport and teams (home and away) the user chose
        if BasketballButton['state'] == DISABLED:
            X_prediction(results2020_2021_nba, NBA2019_2020_Standings, logistic_regression_nba, decision_tree_nba, nearest_neighbors_nba, mlp_nba)
            is_activated = True
            
        elif HockeyButton['state'] == DISABLED:
            X_prediction(results2020_2021_nhl, NHL2019_2020_Standings, logistic_regression_nhl, decision_tree_nhl, nearest_neighbors_nhl, mlp_nhl)
            is_activated = True

        elif BaseballButton['state'] == DISABLED:
            X_prediction(results2020_mlb, MLB2019_Standings, logistic_regression_mlb, decision_tree_mlb, nearest_neighbors_mlb, mlp_mlb)
            is_activated = True

        if is_activated:
            #Disable predict button 
            PredictButton['state'] = DISABLED
            #Enable another prediction button
            AnotherPredictionButton['state'] = NORMAL

            #Disable both drop down boxes that  have been just used
            drop_menu_1['state'] = DISABLED
            drop_menu_2['state'] = DISABLED

            #Disable every sports button
            BasketballButton['state'] = DISABLED
            HockeyButton['state'] = DISABLED
            BaseballButton['state'] = DISABLED
            
# Make another prediction button
def AnotherPrediction():
    #Find out which sport has just been used and enable the button for the other ones
    if home_team.get() in teams_basketball:
        HockeyButton['state'] = NORMAL
        BaseballButton['state'] = NORMAL
        
    if home_team.get() in teams_hockey:
        BasketballButton['state'] = NORMAL
        BaseballButton['state'] = NORMAL
        
    if home_team.get() in teams_baseball:
        HockeyButton['state'] = NORMAL
        BasketballButton['state'] = NORMAL

    #Eliminate the label related to the predicted winner for the various models
    winnerLabel.destroy()
    winnerLabel2.destroy()
    winnerLabel3.destroy()
    winnerLabel4.destroy()

    #Enable predict button 
    PredictButton['state'] = NORMAL
    #Disable another prediction button
    AnotherPredictionButton['state'] = DISABLED

    #Enable drop down boxes so the user can pick different teams if he wishes
    drop_menu_1['state'] = NORMAL
    drop_menu_2['state'] = NORMAL
            
def basketballfunction():
     # If a prediction has just beeen made in another sport, erase the previous drop down boxes so that they don't overlap with the ones
    if HockeyButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    elif BaseballButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()
        
    #Enable hockey, football and predict button
    HockeyButton['state'] = NORMAL
    BaseballButton['state'] = NORMAL
    PredictButton['state'] = NORMAL

    #Call mainfunction with the respective sport button and teams
    mainfunction(BasketballButton, teams_basketball)

# Hockey Button function
def hockeyfunction():
    # If a prediction has just beeen made in another sport, erase the previous drop down boxes so that they don't overlap with the ones
    if BasketballButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    elif BaseballButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    #Enable basketball, football and predict button
    BasketballButton['state'] = NORMAL
    BaseballButton['state'] = NORMAL
    PredictButton['state'] = NORMAL
    
    #Call mainfunction with the respective sport button and teams
    mainfunction(HockeyButton, teams_hockey)

def baseballfunction():
     # If a prediction has just beeen made in another sport, erase the previous drop down boxes so that they don't overlap with the ones
    if HockeyButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    elif BasketballButton['state'] == DISABLED:
        drop_menu_1.destroy()
        drop_menu_2.destroy()

    #Enable hockey, basketball and predict button
    HockeyButton['state'] = NORMAL
    BasketballButton['state'] = NORMAL
    PredictButton['state'] = NORMAL
    
    #Call mainfunction with the respective sport button and teams
    mainfunction(BaseballButton, teams_baseball)

NBA2020_2021_Standings = pd.read_csv("StandingsNBA2020_2021.csv", skiprows=[0])
#create list called teams that contains every basketball team's name
teams_basketball = []
for i in range(len(NBA2020_2021_Standings)):
    teams_basketball.append(NBA2020_2021_Standings.iloc[i, 1])
    teams_basketball.sort()
    
NHL2020_2021_Standings = pd.read_csv("StandingsNHL2020_2021.csv", skiprows=[32])
#create list called teams that contains every hockey team's name
teams_hockey = []
for i in range(len(NHL2020_2021_Standings)):
    teams_hockey.append(NHL2020_2021_Standings.iloc[i, 1])
    teams_hockey.sort()
    
MLB2020_Standings = pd.read_csv("StandingsMLB2020.csv")
#create list called teams that contains every baseball team's name
teams_baseball= []
for i in range(len(MLB2020_Standings)):
    teams_baseball.append(MLB2020_Standings.iloc[i, 1])
    teams_baseball.sort()
    
#create button for the basketball sport
BasketballButton = Button(root, text="Basketball", padx=4, pady=3, command=basketballfunction, fg="orange", font=("Gamerock", 14, "italic"))
BasketballButton.grid(row=1, column=0) # Position the button

#create button for the hockey sport
HockeyButton = Button(root, text="Hockey", padx=4, pady=3, command=hockeyfunction, fg="blue", font=("Gamerock", 14, "italic"))
HockeyButton.grid(row=2, column=0) # Position the button

#create button for the baseball sport
BaseballButton = Button(root, text="Baseball", padx=4, pady=3, command=baseballfunction, fg="red", font=("Gamerock", 14, "italic"))
BaseballButton.grid(row=3, column=0) # Position the button

#Create and display downloaded sports image on the GUI 
my_img = ImageTk.PhotoImage(Image.open("icon.jpeg"))
photo = Label(image=my_img)
photo.grid(row=4, column=0)

#Create button for the prediction
PredictButton = Button(root, text="Predict", padx=4, pady=4, command=predictfunction, fg="green")
#Create button that will allow you to make other predictions
AnotherPredictionButton = Button(root, text="Make Another Prediction", padx=4, pady=4, command=AnotherPrediction, fg="red")

root.mainloop()
