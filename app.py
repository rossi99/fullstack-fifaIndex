# imports
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
# Player routes include:
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
        # for review in player['reviews']:
        #     review["_id"] = str(review["_id"])
        data_to_return.append(player)

    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/players/<string:id>", methods=["GET"])
def show_one_player(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response(jsonify({"error": "Invalid player ID"}), 404)
    player = players.find_one({'_id': ObjectId(id)})
    if player is not None:
        player['_id'] = str(player['_id'])
        # for review in player['reviews']:
        #     review['_id'] = str(review['_id'])
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


# Review routes include:
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
        {"$push": {"reviews": new_review}}
    )
    new_review_link = "http://localhost:5000/api/v1.0/players/" + id + "/reviews/" + str(new_review['_id'])
    return make_response(jsonify({"url": new_review_link}), 201)


@app.route("/api/v1.0/players/<string:id>/reviews", methods=["GET"])
def fetch_all_player_reviews(id):
    data_to_return = []
    player = players.find_one({"_id": ObjectId(id)}, {"reviews": 1, "_id": 0})
    for review in player["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["GET"])
def fetch_one_player_review(pid, rid):
    player = players.find_one({"reviews._id": ObjectId(rid)}, {"_id": 0, "reviews.$": 1})
    if player is None:
        return make_response(jsonify({"error": "Invalid player ID or review ID"}), 404)
    player['reviews'][0]['_id'] = str(player['reviews'][0]['_id'])
    return make_response(jsonify(player['reviews'][0]), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["PUT"])
def edit_player_review(pid, rid):
    edited_review = {
        "reviews.$.username": request.form["username"],
        "reviews.$.comment": request.form["comment"],
        "reviews.$.rating": request.form['rating']
    }
    players.update_one(
        {"reviews._id": ObjectId(rid)},
        {"$set": edited_review}
    )
    edit_review_url = "http://localhost:5000/api/v1.0/players/" + pid + "/reviews/" + rid
    return make_response(jsonify({"url": edit_review_url}), 200)


@app.route("/api/v1.0/players/<pid>/reviews/<rid>", methods=["DELETE"])
def delete_player_review(pid, rid):
    players.update_one(
        {"_id": ObjectId(pid)},
        {"$pull": {"reviews": {"_id": ObjectId(rid)}}}
    )
    return make_response(jsonify({}), 204)


# Extra routes include:
#   - add 'chemistry styles' to players to enhance stats
#   - get skillful players (5 star skills & 5 star weak foot)
#   - get most loyal players (players that have been at their current club for 10 year plus)
@app.route("/api/v1.0/players/<pid>/chemistry/<chem>")
def add_player_chemistry(pid, chem):
    player = players.find_one({'_id': ObjectId(pid)})
    val_update = random.randint(1, 10)

    if chem == "sniper":  # increases shooting and physical
        positioning = int(player["mentality_positioning"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        long_shots = int(player["power_long_shots"]) + val_update
        volleys = int(player["attacking_volleys"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        # Stats can't be over 99, so if block checks this
        if positioning >= 100:
            positioning = 99
        if shot_power >= 100:
            shot_power = 99
        if long_shots >= 100:
            long_shots = 99
        if volleys >= 100:
            volleys = 99
        if penalties >= 100:
            penalties = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "positioning": positioning,
            "shot_power": shot_power,
            "long_shots": long_shots,
            "volleys": volleys,
            "penalties": penalties,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "finisher":
        positioning = int(player["mentality_positioning"]) + val_update
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        volleys = int(player["attacking_volleys"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update
        agility = int(player["movement_agility"]) + val_update
        balance = int(player["movement_balance"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update

        if positioning >= 100:
            positioning = 99
        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if volleys >= 100:
            volleys = 99
        if penalties >= 100:
            penalties = 99
        if agility >= 100:
            agility = 99
        if balance >= 100:
            balance = 99
        if dribbling >= 100:
            dribbling = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "positioning": positioning,
            "finishing": finishing,
            "shot_power": shot_power,
            "volleys": volleys,
            "penalties": penalties,
            "agility": agility,
            "balance": balance,
            "dribbling": dribbling
        }
        return make_response(jsonify(stats), 200)

    if chem == "deadeye":
        positioning = int(player["mentality_positioning"]) + val_update
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        long_shots = int(player["power_long_shots"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update
        vision = int(player["mentality_vision"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update

        if positioning >= 100:
            positioning = 99
        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if long_shots >= 100:
            long_shots = 99
        if penalties >= 100:
            penalties = 99
        if vision >= 100:
            vision = 99
        if short_passing >= 100:
            short_passing = 99
        if curve >= 100:
            curve = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "positioning": positioning,
            "finishing": finishing,
            "shot_power": shot_power,
            "long_shots": long_shots,
            "penalties": penalties,
            "vision": vision,
            "short_passing": short_passing,
            "curve": curve
        }
        return make_response(jsonify(stats), 200)

    if chem == "marksman":
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        long_shots = int(player["power_long_shots"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update
        reactions = int(player["movement_reactions"]) + val_update
        ball_control = int(player["skill_ball_control"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update

        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if long_shots >= 100:
            long_shots = 99
        if penalties >= 100:
            penalties = 99
        if reactions >= 100:
            reactions = 99
        if ball_control >= 100:
            ball_control = 99
        if dribbling >= 100:
            dribbling = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "finishing": finishing,
            "shot_power": shot_power,
            "long_shots": long_shots,
            "penalties": penalties,
            "reactions": reactions,
            "ball_control": ball_control,
            "dribbling": dribbling,
            "jumping": jumping,
            "strength": strength
        }
        return make_response(jsonify(stats), 200)

    if chem == "hawk":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        positioning = int(player["mentality_positioning"]) + val_update
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        long_shots = int(player["power_long_shots"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if positioning >= 100:
            positioning = 99
        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if long_shots >= 100:
            long_shots = 99
        if penalties >= 100:
            penalties = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "positioning": positioning,
            "finishing": finishing,
            "shot_power": shot_power,
            "long_shots": long_shots,
            "penalties": penalties,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "artist":
        vision = int(player["mentality_vision"]) + val_update
        crossing = int(player["attacking_crossing"]) + val_update
        free_kick_accuracy = int(player["skill_fk_accuracy"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update
        agility = int(player["movement_agility"]) + val_update
        reactions = int(player["movement_reactions"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update

        if vision >= 100:
            vision = 99
        if crossing >= 100:
            crossing = 99
        if free_kick_accuracy >= 100:
            free_kick_accuracy = 99
        if long_passing >= 100:
            long_passing = 99
        if curve >= 100:
            curve = 99
        if agility >= 100:
            agility = 99
        if reactions >= 100:
            reactions = 99
        if dribbling >= 100:
            dribbling = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "vision": vision,
            "crossing": crossing,
            "free_kick_accuracy": free_kick_accuracy,
            "long_passing": long_passing,
            "curve": curve,
            "agility": agility,
            "reactions": reactions,
            "dribbling": dribbling
        }
        return make_response(jsonify(stats), 200)

    if chem == "architect":
        vision = int(player["mentality_vision"]) + val_update
        free_kick_accuracy = int(player["skill_fk_accuracy"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        if vision >= 100:
            vision = 99
        if free_kick_accuracy >= 100:
            free_kick_accuracy = 99
        if short_passing >= 100:
            short_passing = 99
        if long_passing >= 100:
            long_passing = 99
        if curve >= 100:
            curve = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "vision": vision,
            "free_kick_accuracy": free_kick_accuracy,
            "short_passing": short_passing,
            "long_passing": long_passing,
            "curve": curve,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "powerhouse":
        vision = int(player["mentality_vision"]) + val_update
        crossing = int(player["attacking_crossing"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update

        if vision >= 100:
            vision = 99
        if crossing >= 100:
            crossing = 99
        if short_passing >= 100:
            short_passing = 99
        if long_passing >= 100:
            long_passing = 99
        if curve >= 100:
            curve = 99
        if interceptions >= 100:
            interceptions = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "vision": vision,
            "crossing": crossing,
            "short_passing": short_passing,
            "long_passing": long_passing,
            "curve": curve,
            "interceptions": interceptions,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle
        }
        return make_response(jsonify(stats), 200)

    if chem == "maestro":
        shot_power = int(player["power_shot_power"]) + val_update
        long_shots = int(player["power_long_shots"]) + val_update
        volleys = int(player["attacking_volleys"]) + val_update
        vision = int(player["mentality_vision"]) + val_update
        free_kick_accuracy = int(player["skill_fk_accuracy"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        reactions = int(player["movement_reactions"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update

        if shot_power >= 100:
            shot_power = 99
        if long_shots >= 100:
            long_shots = 99
        if volleys >= 100:
            volleys = 99
        if vision >= 100:
            vision = 99
        if free_kick_accuracy >= 100:
            free_kick_accuracy = 99
        if short_passing >= 100:
            short_passing = 99
        if long_passing >= 100:
            long_passing = 99
        if reactions >= 100:
            reactions = 99
        if dribbling >= 100:
            dribbling = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "shot_power": shot_power,
            "long_shots": long_shots,
            "volleys": volleys,
            "vision": vision,
            "free_kick_accuracy": free_kick_accuracy,
            "short_passing": short_passing,
            "long_passing": long_passing,
            "reactions": reactions,
            "dribbling": dribbling
        }
        return make_response(jsonify(stats), 200)

    if chem == "engine":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        vision = int(player["mentality_vision"]) + val_update
        crossing = int(player["attacking_crossing"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update
        agility = int(player["movement_agility"]) + val_update
        balance = int(player["movement_balance"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if vision >= 100:
            vision = 99
        if crossing >= 100:
            crossing = 99
        if short_passing >= 100:
            short_passing = 99
        if long_passing >= 100:
            long_passing = 99
        if curve >= 100:
            curve = 99
        if agility >= 100:
            agility = 99
        if balance >= 100:
            balance = 99
        if dribbling >= 100:
            dribbling = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "vision": vision,
            "crossing": crossing,
            "short_passing": short_passing,
            "long_passing": long_passing,
            "curve": curve,
            "agility": agility,
            "balance": balance,
            "dribbling": dribbling
        }
        return make_response(jsonify(stats), 200)

    if chem == "sentinel":
        interceptions = int(player["mentality_interceptions"]) + val_update
        heading_accuracy = int(player["attacking_heading_accuracy"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        if interceptions >= 100:
            interceptions = 99
        if heading_accuracy >= 100:
            heading_accuracy = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "interceptions": interceptions,
            "heading_accuracy": heading_accuracy,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "guardian":
        balance = int(player["movement_balance"]) + val_update
        ball_control = int(player["skill_ball_control"]) + val_update
        dribbling = int(player["skill_dribbling"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        heading_accuracy = int(player["attacking_heading_accuracy"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update

        if balance >= 100:
            balance = 99
        if ball_control >= 100:
            ball_control = 99
        if dribbling >= 100:
            dribbling = 99
        if interceptions >= 100:
            interceptions = 99
        if heading_accuracy >= 100:
            heading_accuracy = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "balance": balance,
            "ball_control": ball_control,
            "dribbling": dribbling,
            "interceptions": interceptions,
            "heading_accuracy": heading_accuracy,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle
        }
        return make_response(jsonify(stats), 200)

    if chem == "gladiator":
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        volleys = int(player["attacking_volleys"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        heading_accuracy = int(player["attacking_heading_accuracy"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update

        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if volleys >= 100:
            volleys = 99
        if interceptions >= 100:
            interceptions = 99
        if heading_accuracy >= 100:
            heading_accuracy = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "finishing": finishing,
            "shot_power": shot_power,
            "volleys": volleys,
            "interceptions": interceptions,
            "heading_accuracy": heading_accuracy,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle
        }
        return make_response(jsonify(stats), 200)

    if chem == "backbone":
        vision = int(player["mentality_vision"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        if vision >= 100:
            vision = 99
        if long_passing >= 100:
            long_passing = 99
        if interceptions >= 100:
            interceptions = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "vision": vision,
            "long_passing": long_passing,
            "interceptions": interceptions,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "anchor":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        heading_accuracy = int(player["attacking_heading_accuracy"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update
        jumping = int(player["power_jumping"]) + val_update
        strength = int(player["power_strength"]) + val_update
        aggression = int(player["mentality_aggression"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if interceptions >= 100:
            interceptions = 99
        if heading_accuracy >= 100:
            heading_accuracy = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99
        if jumping >= 100:
            jumping = 99
        if strength >= 100:
            strength = 99
        if aggression >= 100:
            aggression = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "interceptions": interceptions,
            "heading_accuracy": heading_accuracy,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle,
            "jumping": jumping,
            "strength": strength,
            "aggression": aggression
        }
        return make_response(jsonify(stats), 200)

    if chem == "hunter":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        positioning = int(player["mentality_positioning"]) + val_update
        finishing = int(player["attacking_finishing"]) + val_update
        shot_power = int(player["power_shot_power"]) + val_update
        volleys = int(player["attacking_volleys"]) + val_update
        penalties = int(player["mentality_penalties"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if positioning >= 100:
            positioning = 99
        if finishing >= 100:
            finishing = 99
        if shot_power >= 100:
            shot_power = 99
        if volleys >= 100:
            volleys = 99
        if penalties >= 100:
            penalties = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "positioning": positioning,
            "finishing": finishing,
            "shot_power": shot_power,
            "volleys": volleys,
            "penalties": penalties
        }
        return make_response(jsonify(stats), 200)

    if chem == "catalyst":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        crossing = int(player["attacking_crossing"]) + val_update
        free_kick_accuracy = int(player["skill_fk_accuracy"]) + val_update
        short_passing = int(player["attacking_short_passing"]) + val_update
        long_passing = int(player["skill_long_passing"]) + val_update
        curve = int(player["skill_curve"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if crossing >= 100:
            crossing = 99
        if free_kick_accuracy >= 100:
            free_kick_accuracy = 99
        if short_passing >= 100:
            short_passing = 99
        if long_passing >= 100:
            long_passing = 99
        if curve >= 100:
            curve = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "crossing": crossing,
            "free_kick_accuracy": free_kick_accuracy,
            "short_passing": short_passing,
            "long_passing": long_passing,
            "curve": curve
        }
        return make_response(jsonify(stats), 200)

    if chem == "shadow":
        acceleration = int(player["movement_acceleration"]) + val_update
        sprint_speed = int(player["movement_sprint_speed"]) + val_update
        interceptions = int(player["mentality_interceptions"]) + val_update
        heading_accuracy = int(player["attacking_heading_accuracy"]) + val_update
        defending_awareness = int(player["defending_marking_awareness"]) + val_update
        standing_tackle = int(player["defending_standing_tackle"]) + val_update
        sliding_tackle = int(player["defending_sliding_tackle"]) + val_update

        if acceleration >= 100:
            acceleration = 99
        if sprint_speed >= 100:
            sprint_speed = 99
        if interceptions >= 100:
            interceptions = 99
        if heading_accuracy >= 100:
            heading_accuracy = 99
        if defending_awareness >= 100:
            defending_awareness = 99
        if standing_tackle >= 100:
            standing_tackle = 99
        if sliding_tackle >= 100:
            sliding_tackle = 99

        stats = {
            "_id": str(ObjectId(pid)),
            "name": player['short_name'],
            "acceleration": acceleration,
            "sprint_speed": sprint_speed,
            "interceptions": interceptions,
            "heading_accuracy": heading_accuracy,
            "defending_awareness": defending_awareness,
            "standing_tackle": standing_tackle,
            "sliding_tackle": sliding_tackle
        }
        return make_response(jsonify(stats), 200)


@app.route("/api/v1.0/players/skilled")
def get_skillful_players():
    players_returned = []

    pipeline = [
        {"$match": {"skill_moves": 5}},
        {"$match": {"weak_foot": 5}}
    ]

    for player in players.aggregate(pipeline):
        if player is None:
            return make_response(jsonify({"error": "No players found"}), 404)
        player['_id'] = str(player['_id'])
        for review in player["review"]:
            review["_id"] = str(review["_id"])
        players_returned.append(player)

    return make_response(jsonify(players_returned), 200)


@app.route("/api/v1.0/players/loyal")
def get_loyal_players():
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

    return make_response(jsonify(loyal_players), 200)


if __name__ == "__main__":
    app.run(debug=True)
