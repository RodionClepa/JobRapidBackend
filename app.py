from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="flask",
    passwd="python123",
    database="jobrapid"
)

mycursor = db.cursor()

# Custom error handler for JSON responses
@app.errorhandler(400)
def handle_bad_request(e):
    response = jsonify(error=str(e))
    response.status_code = 400
    return response

from controller.jobController import create_job_
# POST: Create a new job
@app.route("/jobs", methods=["POST"])
def create_job():
    try:
        response = create_job_(mycursor, db)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")

# GET: Retrieve all jobs
from controller.jobController import get_all_jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        response = get_all_jobs(mycursor, db)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving jobs: {err}")

# GET: Retrieve a job by ID
from controller.jobController import get_job_by_id
@app.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    try:
        response = get_job_by_id(mycursor, db, job_id, handle_bad_request)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving job: {err}")

# PUT: Update a job by ID
from controller.jobController import update_job_by_id
@app.route("/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        response = update_job_by_id(mycursor, db, job_id)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error updating job: {err}")

# DELETE: Delete a job by ID
from controller.jobController import delete_job_by_id
@app.route("/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        response = delete_job_by_id(mycursor, db, job_id)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error deleting job: {err}")

if __name__ == "__main__":
    app.run(debug=True)