import os

import bcrypt
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

uri = os.environ.get('URI')

client = MongoClient(uri)

db = client["vantevo-backend-practice"]

users = db.users
companies = db.companies
listings = db.listings


@app.route("/users", methods=["GET"])
def get_users():
    try:
        user_list = list(users.find({}, {"password": 0}))
        for user in user_list:
            user["_id"] = str(user["_id"])
        return jsonify(user_list)
    except Exception as e:
        print(f"Error querying users: {e}")
        return jsonify({"error": "An error occurred while querying users."})


@app.route("/companies", methods=["GET", "POST"])
def companies_route():
    if request.method == "GET":
        try:
            company_list = list(companies.find({}, {"_id": 0}))
            return jsonify(company_list)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            data = request.json
            company_name = data.get("name")
            company_id = companies.insert_one({"name": company_name}).inserted_id
            return jsonify({"message": "Company added successfully.", "company_id": str(company_id)}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/listings", methods=["GET", "POST"])
def listings_route():
    if request.method == "GET":
        try:
            listing_list = list(listings.find({}, {"_id": 0}))
            return jsonify(listing_list)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            data = request.json
            listing_title = data.get("title")
            listing_id = listings.insert_one({"title": listing_title}).inserted_id
            return jsonify({"message": "Listing added successfully.", "listing_id": str(listing_id)}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists."}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_id = users.insert_one({"name": first_name, "lastname": last_name, "email": email, "password": hashed_password,
                                "isAdmin": "false"}).inserted_id

    return jsonify({"message": "User registered successfully.", "user_id": str(user_id)}), 201


@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"error": "Invalid username or password."}), 401


if __name__ == "__main__":
    app.run(debug=True)
