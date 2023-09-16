from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
import os

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

from controller.userController import registerUser
@app.route("/api/users/registration", methods=['POST'])
def registerHandler():
    response = registerUser(mycursor, db, request)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"]})


from controller.userController import loginUser
@app.route("/api/users/login", methods=['POST'])
def loginHandler():
    response = loginUser(mycursor, request)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"token": response["token"]})


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token):
    return jsonify({"error": "Invalid token"})

from controller.userController import verifyUser
@app.route("/api/users/verify", methods=['GET'])
@jwt_required()
def verifyHandler():
    token = request.headers.get('Authorization')
    response = verifyUser(mycursor)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return response

from controller.userController import getInfo
@app.route("/api/users/getinfo", methods=['GET'])
def getInfoHandler():
    response = verifyHandler()
    if "error" in response:
        return jsonify({"error": response["error"]})
    response = getInfo(mycursor, response["id"])
    return response

# mycursor.execute("CREATE TABLE mytest (personid int PRIMARY KEY NOT NULL AUTO_INCREMENT,name VARCHAR(30) NOT NULL, created datetime, gender ENUM('M','F','O') NOT NULL)")
    # mycursor.execute("CREATE DATABASE Fortest")
    # mycursor.execute("INSERT INTO mytest (name, created, gender) VALUES (%s, %s, %s)", ("Rodion", datetime.now(), "M"))

# mycursor.execute("INSERT INTO mytest (name, created, gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, datetime.now(), gender))
    # mycursor.execute("INSERT INTO user (first_name, last_name, email, phone, date_of_birth, address, gender, skills, password, created) VALUES (%s, %s, %s)", (first_name, last_name, email, phone, date_of_birth, address, gender, skills, password, datetime.now()))

