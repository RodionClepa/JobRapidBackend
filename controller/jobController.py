from flask import request, jsonify
from datetime import datetime
import math

from controller.tagController import (
    get_tags_for_job,
    set_tags_to_job
)

from controller.imageController import (
    upload_avatar,
    delete_avatar
)

def create_job_(connection_pool, request, user_id, folder_name):
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')
    location = request.form.get('location')
    salary = request.form.get('salary')
    application_deadline = request.form.get('application_deadline')
    job_email = request.form.get('job_email')
    job_phone = request.form.get('job_phone')
    tag_ids = request.form.get('tags')
    print (request.form)
    filename = request.files.get('image')
    filename = upload_avatar(filename, folder_name)

    # Insert the job data into the database
    sql = """
                INSERT INTO jobs (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, created, image)
                VALUES (%s, %s, %s, %s, STR_TO_DATE(%s, '%d-%m-%Y'), %s, %s, %s, %s, %s)
            """
    values = (job_title, job_description, location, salary, application_deadline, job_email, job_phone, user_id, datetime.now(), filename)
    
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
    job_title = request.args.get('job_title', default="", type=str)
    tag_id = request.args.get('tag_id', default=None, type=int)
    list_of_available_criterias = ["job_title", "application_deadline", "created"]
    
    if order.upper() != "DESC" and order.upper() != "ASC":
        return jsonify({"error":"Invalid order use DESC/ASC"})
    
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    
    if criteria not in list_of_available_criterias:
        return jsonify({"error": "Invalid Criteria"})

    if tag_id is None:
        mycursor.execute(f"SELECT job_id, created, job_title, application_deadline, job_description, salary, location, image FROM jobs WHERE job_title LIKE %s ORDER BY {criteria} {order}", (f"%{job_title}%", ))
    else:
        mycursor.execute(f"SELECT a.job_id, a.created, a.job_title, a.application_deadline, a.job_description, a.salary, a.location, a.image FROM jobs AS a WHERE job_title LIKE %s AND %s IN (SELECT tag_id FROM jobs_tags WHERE job_id = a.job_id) ORDER BY {criteria} {order}", (f"%{job_title}%", tag_id))

    column_names = [desc[0] for desc in mycursor.description]
    result = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
    mycursor.close()
    db.close()

    for job in result:
        job["tags"] = get_tags_for_job(connection_pool, job["job_id"])

    return {
        "data": result
    }

def get_job_by_id(connection_pool, request, handle_bad_request):
    job_id = request.args.get('job_id', default=1, type=int)

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    job_description = mycursor.description
    job = mycursor.fetchone()
    if job:
        column_names = [desc[0] for desc in job_description]
        job_dict = dict(zip(column_names, job))
        print("-==================")
        print(job_dict)
        mycursor.execute("SELECT user_id, first_name, last_name, email, phone FROM user WHERE user_id=%s", (job_dict['user_id'],))
        user = mycursor.fetchone()
        print(user)
        user_dict = {
            "user_id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone": user[4],
        }

        job_dict["author"] = user_dict
        job_dict["tags"] = get_tags_for_job(connection_pool, job_dict["job_id"])

        mycursor.close()
        db.close()
        return job_dict
    else:
        mycursor.close()
        db.close()
        return {"error": "Job not found"}

def update_job_by_id(connection_pool, request, user_id, folder_name):
        # Update the job data in the database
        job_id = request.args.get('job_id', default=1, type=int)
        db = connection_pool.get_connection()
        mycursor = db.cursor()
        # Check if user owns this job
        mycursor.execute(f"SELECT user_id, image FROM jobs WHERE job_id={job_id}")
        result = mycursor.fetchone()
        if result and result[0] == user_id:
            req, null_fields = forms_request()
            if null_fields:
                missing_fields = ", ".join(null_fields)
                if len(null_fields) > 1:
                    return jsonify({"error": f"{missing_fields} fields are missing!"})
                else:
                    return jsonify({"error": f"{missing_fields} field is missing!"})
            if result[1] != req["filename"]:
                delete_avatar(result[1], folder_name)
                req["filename"] = upload_avatar(req["filename"], folder_name)
            sql = """
                        UPDATE jobs
                        SET job_title = %(job_title)s, job_description = %(job_description)s, location = %(location)s, salary = %(salary)s,
                            application_deadline = STR_TO_DATE(%(application_deadline)s, '%d-%m-%Y'), job_email = %(job_email)s, job_phone = %(job_phone)s, image = %(image)s
                        WHERE job_id = %(job_id)s and user_id = %(user_id)s
                        """
            #values = (req["job_title"], req["job_description"], req["location"], req["salary"], req["application_deadline"], req["job_email"], req["job_phone"], req["filename"], job_id,user_id)
            #mycursor.execute(sql, values)
            mycursor.execute(sql, {'job_title': req["job_title"], 'job_description': req["job_description"],
                                   'location': req["location"], 'salary': req["salary"],
                                   'application_deadline': req["application_deadline"],
                                   'job_email': req["job_email"], 'job_phone': req["job_phone"],
                                   'image': req["filename"], 'job_id': job_id, 'user_id': user_id, })
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
    null_fields = []
    fields_to_check = ["job_title", "job_description", "location", "salary", "application_deadline", "job_email", "job_phone"]
    request_values["tag_ids"] = request.form.get("tags")

    for field in fields_to_check:
        value = request.form.get(field)
        if value is not None:
            request_values[field] = value
        else:
            request_values[field] = None
            null_fields.append(field)

    request_values['filename'] = request.files.get('image')

    return request_values, null_fields

