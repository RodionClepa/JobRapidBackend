from flask import request, jsonify
import mysql.connector

def create_job_(mycursor, db, request):
    job_title = request.form.get('job_title')
    job_description = request.form.get('job_description')
    location = request.form.get('location')
    salary = request.form.get('salary')
    application_deadline = request.form.get('application_deadline')
    job_email = request.form.get('job_email')
    job_phone = request.form.get('job_phone')

    # Insert the job data into the database
    sql = """
                INSERT INTO jobs (job_title, job_description, location, salary, application_deadline, job_email, job_phone)
                VALUES (%s, %s, %s, %s, STR_TO_DATE(%s, '%d-%m-%Y'), %s, %s)
            """
    values = (job_title, job_description, location, salary, application_deadline, job_email, job_phone)
    mycursor.execute(sql, values)
    db.commit()

    return jsonify({"message": "Job created successfully"}), 201

def get_all_jobs(mycursor):
    # Retrieve all jobs from the database
    mycursor.execute("SELECT job_title, job_description, location, salary, application_deadline FROM jobs")
    jobs = mycursor.fetchall()

    # Convert the result to a list of dictionaries
    job_list = []
    for job in jobs:
        job_dict = {
            "title": job[0],
            "description": job[1],
            "location": job[2],
            "salary": job[3],
            "application_deadline": job[4],
        }
        job_list.append(job_dict)

    return jsonify(job_list)

def get_job_by_id(mycursor, job_id, handle_bad_request):
    mycursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    job = mycursor.fetchone()

    if job:
        job_dict = {
            "id": job[0],
            "title": job[1],
            "description": job[2],
            "location": job[3],
            "salary": job[4],
            "application_deadline": job[5],
            "job_email": job[6],
            "job_phone": job[7]
        }
        return jsonify(job_dict)
    else:
        return handle_bad_request("Job not found")


def update_job_by_id(mycursor, db, job_id: int):
        # Update the job data in the database
        sql = """
            UPDATE jobs
            SET job_title = %s, job_description = %s, location = %s, salary = %s,
                application_deadline = STR_TO_DATE(%s, '%d-%m-%Y'), job_email = %s, job_phone = %s
            WHERE job_id = %s
        """
        values = forms_request() + (job_id,)
        mycursor.execute(sql, values)
        db.commit()

        return jsonify({"message": "Job updated successfully"})

def delete_job_by_id(mycursor, db, job_id):
    mycursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    db.commit()

    return jsonify({"message": "Job deleted successfully"})

def json_request():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    location = data.get("location")
    salary = data.get("salary")
    application_deadline = data.get("application_deadline")
    job_email = data.get("job_email")
    job_phone = data.get("job_phone")
    return title, description, location, salary, application_deadline, job_email, job_phone

def forms_request():
    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    salary = request.form.get("salary")
    application_deadline = request.form.get("application_deadline")
    job_email = request.form.get("job_email")
    job_phone = request.form.get("job_phone")
    return title, description, location, salary, application_deadline, job_email, job_phone
