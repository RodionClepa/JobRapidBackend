from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
import os
import math

app = Flask(__name__)

import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user="root",
    passwd='radu',
    database='jobrapid'
)

mycursor = db.cursor()

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

from controller.userController import register_user
@app.route("/api/users/registration", methods=['POST'])
def register_handler():
    response = register_user(mycursor, db, request, app.config['UPLOAD_FOLDER'])
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"]})


from controller.userController import login_user
@app.route("/api/users/login", methods=['POST'])
def login_handler():
    response = login_user(mycursor, request)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"token": response["token"]})


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token):
    return jsonify({"error": "Invalid token"})

from controller.userController import verify_user
@app.route("/api/users/verify", methods=['GET'])
@jwt_required()
def verify_handler():
    response = verify_user(mycursor)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return response

from flask import send_from_directory
from controller.userController import get_info
@app.route("/api/users/getinfo", methods=['GET'])
def get_info_handler():
    response = verify_handler()
    # print(response)
    if response == "Invalid token":
        return jsonify({"error": response})
    response = get_info(mycursor, response["id"])
    response["avatar"] = encode_image_as_base64("uploads/"+response["avatar"])
    print(response)
    return response

import base64

def encode_image_as_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

# http://127.0.0.1:5000/api/users/page?page_num=4&criteria=first_name&order=desc
@app.route("/api/users/page", methods=['GET'])
def get_users():
    criteria = request.args.get('criteria', default='created', type=str)
    order = request.args.get('order', default="ASC", type=str)
    page_num = request.args.get('page_num', default=1, type=int)
    records_per_page = 10
    list_of_available_criterias = ["id", "email", "first_name", "last_name", "phone", "date_of_birth", "address", "gender", "skills", "created"]

    mycursor.execute("SELECT COUNT(*) FROM user")
    total_records = mycursor.fetchone()[0]

    total_pages = math.ceil(total_records/records_per_page)
    if(total_pages<page_num):
        return jsonify({"error":"Invalid page number"})

    if criteria not in list_of_available_criterias:
        return jsonify({"error": "Invalid Request"})
    mycursor.execute(f"SELECT * FROM user ORDER BY {criteria} {order} LIMIT {records_per_page} OFFSET %s", ((page_num-1)*10,))
    column_names = [desc[0] for desc in mycursor.description]
    result = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
    # result = mycursor.fetchall()
    return jsonify({
        "data": result,
        "total_pages": total_pages,
        "current_page": page_num
    })

from controller.userController import update_user
@app.route("/api/users/update", methods=['PUT'])
def update_profil():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    response = update_user(mycursor, db, request, response["id"], app.config['UPLOAD_FOLDER'])
    if("error" in response):
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"], "token": response["token"]})


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
