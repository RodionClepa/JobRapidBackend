from flask import jsonify
import mysql.connector
from datetime import datetime
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta
from controller.tagController import get_tags_for_job
import os
from controller.imageController import (
    upload_avatar,
    delete_avatar
)

from controller.reviewController import (
    average_user_rating,
    user_rating_count
)

def register_user(connection_pool, request, folder_name):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date_of_birth = request.form.get('date_of_birth')
    address = request.form.get('address')
    gender = request.form.get('gender')
    skills = request.form.get('skills')
    password = request.form.get('password')
    role = request.form.get('role')

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT count(*) FROM user WHERE email=%s", (email,))
    checking_email = mycursor.fetchone()

    if not (first_name and last_name and email and phone and gender and password):
        return {"error": "Please fill in all fields"}
    
    if checking_email[0]>0:
        return {"error": "Email has already been taken"}

    filename = request.files.get('image')
    filename = upload_avatar(filename, folder_name)
    # filename = "NULL"

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    sql = "INSERT INTO user (first_name, last_name, email, phone, date_of_birth, address, gender, skills, password, created, avatar, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (first_name, last_name, email, phone, date_of_birth, address, gender, skills, hashed_password, datetime.now(), filename, role)
    mycursor.execute(sql, values)
    db.commit()
    mycursor.close()
    db.close()
    return {"message": "Successfully registered"}

def generate_token(id, first_name, last_name, email, role):
    return create_access_token(identity={"id": id, "email": email,"first_name": first_name, "last_name": last_name, "role": role}, expires_delta=timedelta(days=30))


def login_user(connection_pool, request):
    email = request.form.get('email')
    password = request.form.get('password')
    if not(email and password):
        return {"error": "Please fill in all fields"}
    
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT user_id, password, first_name, last_name, email, role FROM user WHERE email=%s", (email, ))
    result = mycursor.fetchone()
    mycursor.close()
    db.close()
    
    if(result is None):
        return {"error": "Invalid credentials"}
    if(bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8'))):
        return {"token": generate_token(result[0],result[2], result[3], result[4], result[5])}

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def verify_user(connection_pool):
    db = connection_pool.get_connection()
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    if "id" not in current_user and "email" not in current_user and "first_name" not in current_user and "last_name" not in current_user:
        return {"error": "Invalid token"}
    mycursor = db.cursor()
    mycursor.execute("SELECT COUNT(*) FROM user WHERE user_id=%s and email=%s and first_name=%s and last_name=%s", (current_user["id"], current_user["email"], current_user["first_name"], current_user["last_name"]))
    checking_token = mycursor.fetchone()
    mycursor.fetchall()
    mycursor.close()
    db.close()

    if checking_token[0] > 0:
        return current_user
    else:
        return "Invalid token"


def get_info(connection_pool, user_id):
    try:
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        mycursor.execute("SELECT first_name, last_name, email, phone, date_of_birth, address, gender, skills, avatar, role FROM user WHERE user_id=%s", (user_id,))
        result = mycursor.fetchone()
        print(result[8])
        mycursor.fetchall()
        mycursor.close()
        db.close()


        return {
            "user_id": user_id,
            "first_name": result[0],
            "last_name": result[1],
            "email": result[2],
            "phone": result[3],
            "date_of_birth": result[4],
            "address": result[5],
            "gender": result[6],
            "skills": result[7],
            "avatar": result[8],
            "role": result[9],
            "avg_rating": average_user_rating(connection_pool, user_id),
            "rating_count": user_rating_count(connection_pool, user_id),
        }
    except mysql.connector.Error as e:
        return jsonify({"Error" : f"{e}"})

def get_info_by_id(connection_pool, request):
    try:
        user_id = request.args.get('user_id', default=None,type=int)
        if(user_id is None):
            return jsonify({"error": "User id wasn't passed or isn't valid"})
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        mycursor.execute("SELECT first_name, last_name, email, phone, date_of_birth, address, gender, skills, avatar, role FROM user WHERE user_id=%s", (user_id,))
        result = mycursor.fetchone()
        mycursor.fetchall()
        mycursor.close()
        db.close()
        if result is None:
            return jsonify({"error": "User id is invalid"})
        return {
            "user_id": user_id,
            "first_name": result[0],
            "last_name": result[1],
            "email": result[2],
            "phone": result[3],
            "date_of_birth": result[4],
            "address": result[5],
            "gender": result[6],
            "skills": result[7],
            "avatar": result[8],
            "role": result[9],
            "avg_rating": average_user_rating(connection_pool, user_id),
            "rating_count": user_rating_count(connection_pool, user_id),
        }
    except mysql.connector.Error as e:
        return jsonify({"Error" : f"{e}"})


def update_user(connection_pool, request, id, role, folder_name):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date_of_birth = request.form.get('date_of_birth')
    address = request.form.get('address')
    gender = request.form.get('gender')
    skills = request.form.get('skills')
    print('+')
    file = request.files.get('image')
    print('-')
        
    if not(email and first_name and last_name and gender):
        return {"error": "Please fill in all fields"}

    try:
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        mycursor.execute("SELECT first_name, last_name, email, phone, date_of_birth, address, gender, skills, avatar FROM user WHERE user_id=%s", (id,))
        result = mycursor.fetchone()
        image_name = result[8]
        if file is None:
            filename = None
        else:
            filename = file.filename
        
        if(image_name!=filename):
            print("WHY?")
            delete_avatar(image_name, folder_name)
            filename = upload_avatar(file, folder_name)
            sql = ("UPDATE user SET first_name=%s, last_name=%s, email=%s, phone=%s, date_of_birth=%s, address=%s, gender=%s, skills=%s, avatar=%s WHERE user_id = %s")
            values = (first_name, last_name, email, phone, date_of_birth, address, gender, skills, filename, id)
            mycursor.execute(sql, values)
            db.commit()
            mycursor.close()
            db.close()
        else:
            print('-----------')
            sql = ("UPDATE user SET first_name=%s, last_name=%s, email=%s, phone=%s, date_of_birth=%s, address=%s, gender=%s, skills=%s WHERE user_id = %s")
            values = (first_name, last_name, email, phone, date_of_birth, address, gender, skills, id)
            mycursor.execute(sql, values)
            db.commit()
            mycursor.close()
            db.close()
        return {"message": "Successfully updated", "token": generate_token(id, first_name, last_name, email, role)}
    
    except mysql.connector.Error as err:
        return {"error": str(err)}

def student_apply(connection_pool, request, user_id):
    job_id = request.form.get("job_id")
    # Check if student already applied to this job
    sql = "SELECT COUNT(*) FROM jobs WHERE job_id = %s"
    values = (job_id,)  # Note the comma to create a tuple with a single element
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    check = mycursor.fetchone()
    if check[0] < 1:
        mycursor.close()
        db.close()
        return {"error": "No such job id"}

    sql = "SELECT COUNT(*) FROM student_job WHERE student_id = %s AND job_id = %s"
    values = (user_id, job_id)
    mycursor.execute(sql, values)
    check = mycursor.fetchone()
    if check[0] > 0:
        mycursor.close()
        db.close()
        return {"error": "Student already applied to this job"}
    
    sql = "INSERT INTO student_job (student_id, job_id, created_date, status) VALUES (%s, %s, %s, %s)"
    values = (user_id, job_id, datetime.now(), "Waiting")
    mycursor.execute(sql, values)
    db.commit()
    mycursor.close()
    db.close()
    return {"message": "Student successfully applied"}

def get_recruiter_jobs(connection_pool, user_id):
    sql = "SELECT * FROM jobs WHERE user_id = %s;"
    values = (user_id,)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    
    jobs_list = []

    column_names = [desc[0] for desc in mycursor.description]
    jobs_list = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
    for job in jobs_list:
        job["tags"] = get_tags_for_job(connection_pool, job["job_id"])
    mycursor.close()
    db.close()
    return jobs_list

def get_student_jobs(connection_pool, user_id):
    sql = '''
        SELECT
        s.job_id, 
        s.status,
        j.job_id,
        j.job_title,
        j.created,
        j.application_deadline
        FROM student_job s
        INNER JOIN jobs j ON s.job_id = j.job_id
        WHERE s.student_id = %s;
    '''
    values = (user_id,)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    if mycursor.description is None:
        mycursor.fetchall()
        mycursor.close()
        db.close()
        return jsonify({"data": []})

    jobs_list = []

    column_names = [desc[0] for desc in mycursor.description]
    jobs_list = [dict(zip(column_names, row)) for row in mycursor.fetchall()]

    mycursor.close()
    db.close()
    return jobs_list

def delete_student_apply(connection_pool, user_id, request):
    job_id = request.form.get("job_id")

    sql = "SELECT COUNT(*) FROM jobs WHERE job_id = %s"
    values = (job_id,)
    try:
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        mycursor.execute(sql, values)
        check = mycursor.fetchone()

        if check[0] < 1:
            mycursor.close()
            db.close()
            return {"error": "No such job id"}
        
        sql = "SELECT COUNT(*) FROM student_job WHERE student_id = %s AND job_id = %s"
        values = (user_id, job_id)
        mycursor.execute(sql, values)
        check = mycursor.fetchone()
        if check[0] == 0:
            mycursor.close()
            db.close()
            return {"error": "Student didn't applied to this job"}

        sql = "DELETE FROM student_job WHERE student_id = %s AND job_id = %s"
        values = (user_id, job_id)
        mycursor.execute(sql, values)
        db.commit()
        mycursor.close()
        db.close()

        return {"response": "Successfully deleted apply"}
    except mysql.connector.Error as err:
        # Handle the database error
        return {"error": f"Error deleting student application: {err}"}



def recruiter_get_applied_students(connection_pool, request,user_id):
    job_id = request.args.get('job_id', type=int)
    if job_id is None:
        return {"error": "Should receive job_id"}
    sql = "SELECT count(*) FROM jobs WHERE user_id = %s AND job_id = %s;"
    values = (user_id, job_id)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    check = mycursor.fetchone()
    if check is None:
        mycursor.close()
        db.close()
        return {"error": "No such job or user didn't create this job"}

    if check[0] < 1:
        mycursor.close()
        db.close()
        return {"error": "No such job or user didn't create this job"}

    
    sql = '''SELECT u.user_id, u.first_name, u.last_name, u.email, u.phone, 
    u.date_of_birth, u.address, u.gender, u.skills, u.avatar, s.created_date, s.status
    FROM user u JOIN student_job s ON u.user_id = s.student_id WHERE s.job_id=%s;'''
    values = (job_id,)
    mycursor.execute(sql, values)
    
    applied_students = []

    for row in mycursor.fetchall():
        student_dict = {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "date_of_birth": row[5],
            "address": row[6],
            "gender": row[7],
            "skills": row[8],
            "avatar": row[9],
            "created_date": row[10],
            "status": row[11]
        }
        applied_students.append(student_dict)
    mycursor.close()
    db.close()
    return applied_students

def change_applied_status(connection_pool, request, user_id):
    student_id = request.form.get("student_id")
    job_id = request.form.get("job_id")
    status = request.form.get("status")

    if not(student_id and job_id and status):
        return {"error": "Please fill all fields"}

    sql = "SELECT count(*) FROM jobs WHERE user_id = %s AND job_id = %s;"
    values = (user_id, job_id)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    check = mycursor.fetchone()

    if check is None:
        return {"error": "No such job or user didn't create this job"}

    if check[0] < 1:
        return {"error": "No such job or user didn't create this job"}

    sql = "SELECT count(*) FROM student_job WHERE student_id = %s AND job_id = %s;"
    values = (student_id, job_id)
    mycursor.execute(sql, values)
    check = mycursor.fetchone()

    if check is None:
        return {"error": "Student didn't apply for this job"}

    if check[0] < 1:
        return {"error": "Student didn't apply for this job"}
    
    sql = '''UPDATE student_job SET status=%s WHERE job_id=%s AND student_id=%s'''
    values = (status, job_id, student_id)
    mycursor.execute(sql, values)
    db.commit()
    mycursor.close()
    db.close()

    return {"message": "Successfully changed status"}

def recruiter_delete_job(connection_pool, request, user_id):
    job_id = request.args.get('job_id', type=int)
    if job_id is None:
        return {"error": "Should receive job_id"}
    sql = "SELECT count(*) FROM jobs WHERE user_id = %s AND job_id = %s;"
    values = (user_id, job_id)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    check = mycursor.fetchone()
    if check is None:
        mycursor.close()
        db.close()
        return {"error": "No such job or user didn't create this job"}

    if check[0] < 1:
        mycursor.close()
        db.close()
        return {"error": "No such job or user didn't create this job"}
    
    sql = '''DELETE FROM jobs_tags WHERE job_id=%s'''
    values = (job_id,)
    mycursor.execute(sql, values)
    db.commit()

    sql = '''DELETE FROM jobs WHERE job_id=%s'''
    values = (job_id,)
    mycursor.execute(sql, values)
    db.commit()
    mycursor.close()
    db.close()
    return {"message":"Job successfully deleted"}