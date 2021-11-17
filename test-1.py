from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
from bson import ObjectId
import random
from datetime import datetime

# DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.FIFAplayerDB  # select DB
players = db.FifaPlayers  # players collection
users = db.users  # users collection

loyal_players = []

for player in players.find():
    # get time players have been at club
    current_date = datetime.today()
    joined_club = player['club_joined']

    time_at_club = relativedelta(current_date, joined_club)
    time_at_club_years = time_at_club.years

    # check if they are over 10 years
    if time_at_club_years >= 10:
        loyal_players.append(player)
        print(loyal_players)
