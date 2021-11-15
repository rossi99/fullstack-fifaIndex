# imports
from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
import string

# app def
app = Flask(__name__)

# DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.FIFAplayerDB  # select DB
players = db.FifaPlayers  # select Collection


# App Functionality
# These routes include:
#   - returning all players
#   - adding a player
#   - editing a player
#   - deleting a player
@app.route("/api/v1.0/players", methods=["GET"])
def show_all_players():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))
    data_to_return = []
    for player in players.find().skip(page_start).limit(page_size):
        player['_id'] = str(player['_id'])
        for review in player["review"]:
            review["_id"] = str(review["_id"])
        data_to_return.append(player)

    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/players/<string:id>", methods=["GET"])
def show_one_player(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response(jsonify({"error": "Invalid player ID"}), 404)
    player = players.find_one({'_id': ObjectId(id)})
    if player is not None:
        player['_id'] = str(player['_id'])
        for review in player["review"]:
            review['_id'] = str(review['_id'])
        return make_response(jsonify(player), 200)
    else:
        return make_response(jsonify({"error": "Invalid player ID"}), 404)


@app.route("/api/v1.0/players", methods=["POST"])
def add_player():
    # what is required to be passed in
    if \
            "overall" in request.form and "club_position" in request.form and "nation_flag_url" in request.form and \
            "club_logo_url" in request.form and "short_name" in request.form and "pace" in request.form and \
            "shooting" in request.form and "passing" in request.form and "dribbling" in request.form and \
            "defending" in request.form and "physic" in request.form:

        new_player = {
            "overall": request.form["overall"],
            "club_position": request.form["club_position"],
            "nation_flag_url": request.form["nation_flag_url"],
            "club_logo_url": request.form["club_logo_url"],
            "short_name": request.form["short_name"],
            "pace": request.form["pace"],
            "shooting": request.form["shooting"],
            "passing": request.form["passing"],
            "dribbling": request.form["dribbling"],
            "defending": request.form["defending"],
            "physic": request.form["physic"]
        }
        new_player_id = players.insert_one(new_player)
        new_player_link = "http://localhost:5000/api/v1.0/players/" + str(new_player_id.inserted_id)
        return make_response(jsonify({"url": new_player_link}), 201)
    else:
        return make_response(jsonify({"error": "Missing form data"}), 404)


@app.route("/api/v1.0/players/<string:id>", methods=["PUT"])
def edit_player(id):
    if \
            "overall" in request.form and "club_position" in request.form and "nation_flag_url" in request.form and \
            "club_logo_url" in request.form and "short_name" in request.form and "pace" in request.form and \
            "shooting" in request.form and "passing" in request.form and "dribbling" in request.form and \
            "defending" in request.form and "physic" in request.form:

        result = players.update_one(
            {"_id": ObjectId(id)},  # search clause
            {
                "$set": {
                    "overall": request.form["overall"],
                    "club_position": request.form["club_position"],
                    "nation_flag_url": request.form["nation_flag_url"],
                    "club_logo_url": request.form["club_logo_url"],
                    "short_name": request.form["short_name"],
                    "pace": request.form["pace"],
                    "shooting": request.form["shooting"],
                    "passing": request.form["passing"],
                    "dribbling": request.form["dribbling"],
                    "defending": request.form["defending"],
                    "physic": request.form["physic"]
                }
            })

        if result.matched_count == 1:
            edited_player_link = "http://localhost:5000/api/v1.0/players/" + id
            return make_response(jsonify({"url": edited_player_link}), 200)
        else:
            return make_response(jsonify({"error": "Invalid player ID"}), 404)
    else:
        return make_response(jsonify({"error": "Missing form data"}), 404)


@app.route("/api/v1.0/players/<string:id>", methods=["DELETE"])
def delete_player(id):
    result = players.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "Invalid player ID"}), 404)


# These routes include:
#   - adding a review for a player
#   - getting all reviews relating to a player
#   - get a single review for a player
#   - edit a review
#   - delete a review
@app.route("/api/v1.0/players/<string:id>/reviews", methods=["POST"])
def add_new_player_review(id):
    new_review = {
        "_id": ObjectId(),
        "username": request.form["username"],
        "comment": request.form["comment"],
        "rating": request.form["rating"]
    }
    players.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"review": new_review}}
    )
    new_review_link = "http://localhost:5000/api/v1.0/players/" + id + "/reviews/" + str(new_review['_id'])
    return make_response(jsonify({"url": new_review_link}), 201)


@app.route("/api/v1.0/players/<string:id>/reviews", methods=["GET"])
def fetch_all_player_reviews(id):
    data_to_return = []
    player = players.find_one({"_id": ObjectId(id)}, {"review": 1, "_id": 0})
    if player is None:
        return make_response(jsonify({"error": "Invalid player ID or review ID"}), 404)
    for review in player["review"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["GET"])
def fetch_one_player_review(pid, rid):
    player = players.find_one({"review._id": ObjectId(rid)}, {"_id": 0, "review.$": 1})
    if player is None:
        return make_response(jsonify({"error": "Invalid player ID or review ID"}), 404)
    player['review'][0]['_id'] = str(player['review'][0]['_id'])
    return make_response(jsonify(player['review'][0]), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["PUT"])
def edit_player_review(pid, rid):
    edited_review = {
        "review.$.username": request.form["username"],
        "review.$.comment": request.form["comment"],
        "review.$.rating": request.form['rating']
    }
    players.update_one(
        {"review._id": ObjectId(rid)},
        {"$set": edited_review}
    )
    edit_review_url = "http://localhost:5000/api/v1.0/players/" + pid + "/reviews/" + rid
    return make_response(jsonify({"url": edit_review_url}), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["DELETE"])
def delete_player_review(pid, rid):
    players.update_one(
        {"_id": ObjectId(pid)},
        {"$pull": {"review": {"_id": ObjectId(rid)}}}
    )
    return make_response(jsonify({}), 204)


if __name__ == "__main__":
    app.run(debug=True)
