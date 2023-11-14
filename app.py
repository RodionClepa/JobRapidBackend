from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
import os
from flask_cors import CORS
import mysql.connector
from controller.userController import (
    register_user,
    login_user,
    verify_user,
    get_info,
)

app = Flask(__name__)


CORS(app)

import mysql.connector.pooling

from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                              pool_size=32,
                                              pool_reset_session=True,
                                              host='localhost',
                                              database='jobrapid',
                                              user='root',
                                              password='test123')

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

@app.route("/api/users/registration", methods=['POST'])
def register_handler():
    response = register_user(connection_pool, request, app.config['UPLOAD_FOLDER'])
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"]})


@app.route("/api/users/login", methods=['POST'])
def login_handler():
    response = login_user(connection_pool, request)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"token": response["token"]})

@app.route("/api/users/verify", methods=['GET'])
@jwt_required()
def verify_handler():
    response = verify_user(connection_pool)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return response

@app.route("/api/users/getinfo", methods=['GET'])
def get_info_handler():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    response = get_info(connection_pool, response["id"])
    #     response["avatar"] = encode_image_as_base64("uploads/"+response["avatar"])
    return response

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Custom error handler for JSON responses
@app.errorhandler(400)
def handle_bad_request(e):
    response = jsonify(error=str(e))
    response.status_code = 400
    return response

@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token):
    return jsonify({"error": "Invalid token"})


from controller.reviewController import create_review
@app.route("/api/reviews/create", methods=["POST"])
def create_user_review():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    try:
        response = create_review(connection_pool, request, response["id"])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating review: {err}")

# PUT: Function to update the review of a user by user_id
from controller.reviewController import update_review_by_id
@app.route("/api/reviews/put", methods=["PUT"])
def update_user_review_by_id():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    try:
        response = update_review_by_id(connection_pool, request, response["id"])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error updating review: {err}")



if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False, threaded=True)
