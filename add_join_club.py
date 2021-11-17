# Script is used to add club_joined to each player if not there
# imports
from datetime import datetime

from pymongo import MongoClient
from bson import ObjectId

# DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.FIFAplayerDB  # select DB
players = db.FifaPlayers  # players collection

no_club = []

for player in players.find():     # gets just club joined
    players.update_one(
        {"_id": player['_id']},
        {
            "$set": {
                "club_joined": [datetime.today()]
            }
        }
    )
