from flask import request, jsonify
import mysql.connector
from datetime import datetime
import math

def create_job_(mycursor, db, request, user_id):
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')
    location = request.form.get('location')
    salary = request.form.get('salary')
    application_deadline = request.form.get('application_deadline')
    job_email = request.form.get('job_email')
    job_phone = request.form.get('job_phone')

    # Insert the job data into the database
    sql = """
                INSERT INTO jobs (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, created)
                VALUES (%s, %s, %s, %s, STR_TO_DATE(%s, '%d-%m-%Y'), %s, %s, %s, %s)
            """
    values = (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, datetime.now())
    mycursor.execute(sql, values)
    db.commit()

    return jsonify({"message": "Job created successfully"}), 201


def get_all_jobs(mycursor, request):
    criteria = request.args.get('criteria', default='created', type=str)
    order = request.args.get('order', default="ASC", type=str)
    page_num = request.args.get('page_num', default=1, type=int)
    records_per_page = 10
    list_of_available_criterias = ["job_title", "application_deadline", "created"]

    if order.upper() != "DESC" and order.upper() != "ASC":
        return jsonify({"error":"Invalid order use DESC/ASC"})

    mycursor.execute("SELECT COUNT(*) FROM user")
    total_records = mycursor.fetchone()[0]

    total_pages = math.ceil(total_records/records_per_page)
    if(total_pages<page_num):
        return jsonify({"error":"Invalid page number"})
    
    if criteria not in list_of_available_criterias:
        return jsonify({"error": "Invalid Criteria"})
    
    mycursor.execute(f"SELECT job_id, created, job_title, application_deadline, job_description, salary, location FROM jobs ORDER BY {criteria} {order} LIMIT {records_per_page} OFFSET %s", ((page_num-1)*10,))
    column_names = [desc[0] for desc in mycursor.description]
    result = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
    return jsonify({
        "data": result,
        "total_pages": total_pages,
        "current_page": page_num
    })

def get_job_by_id(mycursor, request, handle_bad_request):
    job_id = request.args.get('job_id', default=1, type=int)
    mycursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    job = mycursor.fetchone()
    if job:
        mycursor.execute(f"SELECT first_name, last_name, email, phone FROM user WHERE user_id={job[8]}")
        user = mycursor.fetchone()
        user_dict = {
            "first_name": user[0],
            "last_name": user[1],
            "email": user[2],
            "phone": user[3],
        }
        job_dict = {
            "id": job[0],
            "title": job[1],
            "description": job[2],
            "location": job[3],
            "salary": job[4],
            "application_deadline": job[5],
            "job_email": job[6],
            "job_phone": job[7],
            "author": user_dict
        }
        return jsonify(job_dict)
    else:
        return handle_bad_request("Job not found")


def update_job_by_id(mycursor, db, request, user_id):
        # Update the job data in the database
        job_id = request.args.get('job_id', default=1, type=int)
        # Check if user owns this job
        mycursor.execute(f"SELECT user_id FROM jobs WHERE job_id={job_id}")
        result = mycursor.fetchone()
        if result and result[0] == user_id:
            sql = """
            UPDATE jobs
            SET job_title = %s, job_description = %s, location = %s, salary = %s,
                application_deadline = STR_TO_DATE(%s, '%d-%m-%Y'), job_email = %s, job_phone = %s
            WHERE job_id = %s and user_id=%s
            """
            values = forms_request() + (job_id,user_id)
            mycursor.execute(sql, values)
            db.commit()

            return jsonify({"message": "Job updated successfully"})
        else:
            return jsonify({"error": "User doesn't own this job"})

def delete_job_by_id(mycursor, db, request, user_id):
    job_id = request.args.get('job_id', default=1, type=int)
    # Check if user owns this job
    mycursor.execute(f"SELECT user_id FROM jobs WHERE job_id={job_id}")
    result = mycursor.fetchone()
    if result and result[0] == user_id:
        mycursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        db.commit()
        return jsonify({"message": "Job deleted successfully"})
    else:
        return jsonify({"error": "User doesn't own this job"})

def forms_request():
    title = request.form.get("job_title")
    description = request.form.get("job_description")
    location = request.form.get("location")
    salary = request.form.get("salary")
    application_deadline = request.form.get("application_deadline")
    job_email = request.form.get("job_email")
    job_phone = request.form.get("job_phone")
    return title, description, location, salary, application_deadline, job_email, job_phone
