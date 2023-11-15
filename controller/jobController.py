from flask import request, jsonify
from datetime import datetime
import math

from controller.tagController import (
    get_tags_for_job,
    set_tags_to_job
)

def create_job_(connection_pool, request, user_id):
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')
    location = request.form.get('location')
    salary = request.form.get('salary')
    application_deadline = request.form.get('application_deadline')
    job_email = request.form.get('job_email')
    job_phone = request.form.get('job_phone')
    tag_ids = request.form.get('tags')

    # Insert the job data into the database
    sql = """
                INSERT INTO jobs (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, created)
                VALUES (%s, %s, %s, %s, STR_TO_DATE(%s, '%d-%m-%Y'), %s, %s, %s, %s)
            """
    values = (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, datetime.now())    
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute(sql, values)
    sql = "SELECT LAST_INSERT_ID()"
    mycursor.execute(sql)
    job_id = mycursor.fetchone()[0]
    print(job_id)
    db.commit()
    mycursor.close()
    db.close()

    set_tags_to_job(connection_pool, job_id, tag_ids)

    return jsonify({"message": "Job created successfully"}), 201


def get_all_jobs(connection_pool, request):
    criteria = request.args.get('criteria', default='created', type=str)
    order = request.args.get('order', default="ASC", type=str)
    page_num = request.args.get('page_num', default=1, type=int)
    job_title = request.args.get('job_title', default="", type=str)
    records_per_page = 10
    list_of_available_criterias = ["job_title", "application_deadline", "created"]

    if order.upper() != "DESC" and order.upper() != "ASC":
        return jsonify({"error":"Invalid order use DESC/ASC"})
    
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT COUNT(*) FROM jobs WHERE job_title LIKE %s", (f"%{job_title}%",))
        
    total_records = mycursor.fetchone()[0]
    # mycursor.fetchall()

    total_pages = math.ceil(total_records/records_per_page)
    if(total_pages<page_num):
        return jsonify({"error":"Invalid page number"})
    
    if criteria not in list_of_available_criterias:
        return jsonify({"error": "Invalid Criteria"})
    
    mycursor.execute(f"SELECT job_id, created, job_title, application_deadline, job_description, salary, location FROM jobs WHERE job_title LIKE %s ORDER BY {criteria} {order} LIMIT {records_per_page} OFFSET %s", (f"%{job_title}%", (page_num-1)*10))

    column_names = [desc[0] for desc in mycursor.description]
    result = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
    mycursor.close()
    db.close()

    for job in result:
        job["tags"] = get_tags_for_job(connection_pool, job["job_id"])

    return jsonify({
        "data": result,
        "total_pages": total_pages,
        "current_page": page_num
    })

def get_job_by_id(connection_pool, request, handle_bad_request):
    job_id = request.args.get('job_id', default=1, type=int)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    job = mycursor.fetchone()
    if job:
        mycursor.execute(f"SELECT user_id, first_name, last_name, email, phone FROM user WHERE user_id={job[8]}")
        user = mycursor.fetchone()
        user_dict = {
            "user_id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone": user[4],
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
            "author": user_dict,
            "tags": get_tags_for_job(connection_pool, job[0])
        }
        mycursor.close()
        db.close()
        return jsonify(job_dict)
    else:
        mycursor.close()
        db.close()
        return handle_bad_request("Job not found")

# Updated to protect my from SQL injection, check by setting a parameter to ['; select * from jobs; --] parantheses not needed
def update_job_by_id(connection_pool, request, user_id):
        # Update the job data in the database
        job_id = request.args.get('job_id', default=1, type=int)
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        # Check if user owns this job
        mycursor.execute(f"SELECT user_id FROM jobs WHERE job_id={job_id}")
        result = mycursor.fetchone()
        if result and result[0] == user_id:
            sql = """
            UPDATE jobs
            SET job_title = %(job_title)s, job_description = %(job_description)s, location = %(location)s, salary = %(salary)s,
                application_deadline = STR_TO_DATE(%(application_deadline)s, '%d-%m-%Y'), job_email = %(job_email)s, job_phone = %(job_phone)s
            WHERE job_id = %(job_id)s and user_id = %(user_id)s
            """
            req = forms_request()
            # values = (req["job_title"], req["job_description"], req["location"], req["salary"], req["application_deadline"], req["job_email"], req["job_phone"],job_id,user_id)
            mycursor.execute(sql, {'job_title' : req["job_title"], 'job_description' : req["job_description"],
                                   'location' : req["location"], 'salary' : req["salary"], 'application_deadline' : req["application_deadline"],
                                   'job_email' : req["job_email"], 'job_phone' : req["job_phone"], 'job_id' : job_id, 'user_id' : user_id,})
            db.commit()
            mycursor.close()
            db.close()
            set_tags_to_job(connection_pool, job_id, req["tag_ids"])
            return jsonify({"message": "Job updated successfully"})
        else:
            mycursor.close()
            db.close()
            return jsonify({"error": "User doesn't own this job"})
# http://127.0.0.1:5000/api/jobs/delete?job_id=125
def delete_job_by_id(connection_pool, request, user_id):
    job_id = request.args.get('job_id', default=1, type=int)
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    # Check if user owns this job
    mycursor.execute(f"SELECT user_id FROM jobs WHERE job_id={job_id}")
    result = mycursor.fetchone()
    if result and result[0] == user_id:
        mycursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        db.commit()
        mycursor.close()
        db.close()
        return jsonify({"message": "Job deleted successfully"})
    else:
        mycursor.close()
        db.close()
        return jsonify({"error": "User doesn't own this job"})

def forms_request():
    request_values = {}
    request_values["job_title"] = request.form.get("job_title")
    request_values["job_description"] = request.form.get("job_description")
    request_values["location"] = request.form.get("location")
    request_values["salary"] = request.form.get("salary")
    request_values["application_deadline"] = request.form.get("application_deadline")
    request_values["job_email"] = request.form.get("job_email")
    request_values["job_phone"] = request.form.get("job_phone")
    request_values["tag_ids"] = request.form.get("tags")
    return request_values
