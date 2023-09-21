from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = mysql.connector.connect(
    host="localhost",
    user="flask",
    passwd="python123",
    database="jobrapid"
)

mycursor = db_config.cursor()

# Custom error handler for JSON responses
@app.errorhandler(400)
def handle_bad_request(e):
    response = jsonify(error=str(e))
    response.status_code = 400
    return response

# POST: Create a new job
@app.route("/jobs", methods=["POST"])
def create_job():
    try:
        # Extract data from the request
        data = request.json
        title = data.get("title")
        description = data.get("description")
        location = data.get("location")
        salary = data.get("salary")
        application_deadline = data.get("application_deadline")
        job_email = data.get("job_email")
        job_phone = data.get("job_phone")

        # Insert the job data into the database
        sql = """
            INSERT INTO jobs (job_title, job_description, location, salary, application_deadline, job_email, job_phone)
            VALUES (%s, %s, %s, %s, STR_TO_DATE(%s, '%d-%m-%Y'), %s, %s)
        """
        values = (title, description, location, salary, application_deadline, job_email, job_phone)
        mycursor.execute(sql, values)

        return jsonify({"message": "Job created successfully"}), 201

    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")

# GET: Retrieve all jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:

        # Retrieve all jobs from the database
        mycursor.execute("SELECT * FROM jobs")
        jobs = mycursor.fetchall()

        # Convert the result to a list of dictionaries
        job_list = []
        for job in jobs:
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
            job_list.append(job_dict)

        return jsonify(job_list)

    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving jobs: {err}")

# GET: Retrieve a job by ID
@app.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    try:

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

    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving job: {err}")

# PUT: Update a job by ID
@app.route("/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        # Extract data from the request
        data = request.json
        title = data.get("title")
        description = data.get("description")
        location = data.get("location")
        salary = data.get("salary")
        application_deadline = data.get("application_deadline")
        job_email = data.get("job_email")
        job_phone = data.get("job_phone")

        # Update the job data in the database
        sql = """
            UPDATE jobs
            SET job_title = %s, job_description = %s, location = %s, salary = %s,
                application_deadline = STR_TO_DATE(%s, '%d-%m-%Y'), job_email = %s, job_phone = %s
            WHERE job_id = %s
        """
        values = (title, description, location, salary, application_deadline, job_email, job_phone, job_id)
        mycursor.execute(sql, values)

        return jsonify({"message": "Job updated successfully"})

    except mysql.connector.Error as err:
        return handle_bad_request(f"Error updating job: {err}")

# DELETE: Delete a job by ID
@app.route("/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        # Delete a job by ID from the database
        mycursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))

        return jsonify({"message": "Job deleted successfully"})

    except mysql.connector.Error as err:
        return handle_bad_request(f"Error deleting job: {err}")

if __name__ == "__main__":
    app.run(debug=True)