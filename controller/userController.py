import mysql.connector
from datetime import datetime
import bcrypt
import base64
from flask_jwt_extended import create_access_token
from datetime import timedelta

def registerUser(mycursor, db, request):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date_of_birth = request.form.get('date_of_birth')
    address = request.form.get('address')
    gender = request.form.get('gender')
    skills = request.form.get('skills')
    password = request.form.get('password')

    if not (first_name and last_name and email and phone and gender and password):
        return {"error": "Please fill in all fields"}
    
    mycursor.execute("SELECT count(*) FROM user WHERE email=%s", (email,))
    checking_email = mycursor.fetchone()
    if checking_email[0]>0:
        return {"error": "Email has already been taken"}
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    sql = "INSERT INTO user (first_name, last_name, email, phone, date_of_birth, address, gender, skills, password, created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (first_name, last_name, email, phone, date_of_birth, address, gender, skills, hashed_password, datetime.now())
    mycursor.execute(sql, values)
    db.commit()
    return {"message": "Successfully registered"}

def generateToken(id,first_name, last_name, email):
    return create_access_token(identity={"id": id, "email": email,"first_name": first_name, "last_name": last_name}, expires_delta=timedelta(days=30))


def loginUser(mycursor, request):
    email = request.form.get('email')
    password = request.form.get('password')
    if not(email and password):
        return {"error": "Please fill in all fields"}
    mycursor.execute("SELECT user_id, password, first_name, last_name, email FROM user WHERE email=%s", (email, ))
    result = mycursor.fetchone()
    if(result is None):
        return {"error": "Invalid credentials"}
    if(bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8'))):
        return {"token": generateToken(result[0],result[2], result[3], result[4])}

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
def verifyUser(mycursor):
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if "id" not in current_user and "email" not in current_user and "first_name" not in current_user and "last_name" not in current_user:
        return {"error": "Invalid token"}
    mycursor.execute("SELECT COUNT(*) FROM user WHERE user_id=%s and email=%s and first_name=%s and last_name=%s", (current_user["id"], current_user["email"], current_user["first_name"], current_user["last_name"]))
    checking_token = mycursor.fetchone()
    if(checking_token[0]>0):
        return current_user
        # return {
        #     "email":current_user["email"],
        #     "first_name":current_user["first_name"],
        #     "last_name":current_user["last_name"],
        # }
        # return {"response": "Valid Token"}
    else:
        return "Invalid token"

def getInfo(mycursor, user_id):
    mycursor.execute("SELECT first_name, last_name, email, phone, date_of_birth, address, gender, skills FROM user WHERE user_id=%s", (user_id,))
    result = mycursor.fetchone()
    print(result)
    return {
        "first_name": result[0],
        "last_name": result[1],
        "email": result[2],
        "phone": result[3],
        "date_of_birth": result[4],
        "address": result[5],
        "gender": result[6],
        "skills": result[7],
    }
