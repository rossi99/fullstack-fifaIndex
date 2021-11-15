# Script is used to add reviews to each player
# imports
from pymongo import MongoClient
from bson import ObjectId
import random

# DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.FIFAplayerDB  # select DB
players = db.FifaPlayers  # players collection
users = db.users  # users collection

# arrays used to populate using random select
usernames = []  # 'usernames' is populated using for loop and pipeline
commentSection = [  # Comment section provides 5 comments that will be selected at random
    'Very Good!', 'Can be good sometimes', 'Just average', 'Can have the odd good game', 'WASTE OF COINS'
]

# populates 'usernames' array
pipeline = [{"$limit": 50}]
for user in users.aggregate(pipeline):
    usernames.append(user["name"])

# adding the reviews fields
for player in players.find():
    players.update_one(
        {"_id": player['_id']},
        {
            "$set": {
                "review": []
            }
        }
    )
