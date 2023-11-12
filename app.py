from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
import os
from flask_cors import CORS
import mysql.connector
from controller.userController import (
    register_user,
    login_user,
    verify_user,
    get_info,
    update_user,
    student_apply,
    get_recruiter_jobs,
    get_student_jobs,
    recruiter_get_applied_students,
    change_applied_status,
    delete_student_apply
)
from controller.jobController import (
    create_job_,
    get_all_jobs,
    get_job_by_id,
    update_job_by_id,
    delete_job_by_id,
)
from controller.imageController import (
    encode_image_as_base64
)
from controller.tagController import get_all_available_tags
from controller.emailController import send_email

app = Flask(__name__)


CORS(app)

import mysql.connector.pooling

from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                  pool_size=32,
                                                  pool_reset_session=True,
                                                  host='localhost',
                                                  database='jobrapid',
                                                  user='root',
                                                  password='radu')

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

@app.route("/api/users/registration", methods=['POST'])
def register_handler():
    response = register_user(connection_pool, request, app.config['UPLOAD_FOLDER'])
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"]})


@app.route("/api/users/login", methods=['POST'])
def login_handler():
    response = login_user(connection_pool, request)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"token": response["token"]})

@app.route("/api/users/verify", methods=['GET'])
@jwt_required()
def verify_handler():
    response = verify_user(connection_pool)
    if "error" in response:
        return jsonify({"error": response["error"]})
    else:
        return response

@app.route("/api/users/getinfo", methods=['GET'])
def get_info_handler():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    response = get_info(connection_pool, response["id"])
    if(response == None or response == "NULL"):
        return response
    response["avatar"] = encode_image_as_base64("uploads/"+response["avatar"])
    return response


@app.route("/api/users/update", methods=['PUT'])
def update_profil():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    response = update_user(connection_pool, request, response["id"], response["role"], app.config['UPLOAD_FOLDER'])
    if("error" in response):
        return jsonify({"error": response["error"]})
    else:
        return jsonify({"message": response["message"], "token": response["token"]})


@app.route("/api/users/apply", methods=['POST'])
def student_apply_handle():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    if response["role"]=="Recruiter":
        return jsonify({"error": "Recruiter can't apply to a job"})

    try:
        response = student_apply(connection_pool, request, response['id'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")



@app.route("/api/users/getrecruiterjobs", methods=['GET'])
def get_recruiter_jobs_handle():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    if response["role"]=="Student":
        return jsonify({"error": "Student can't access jobs list"})
    try:
        response = get_recruiter_jobs(connection_pool, response['id'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")

@app.route("/api/users/getstudentjobs", methods=['GET'])
def get_student_jobs_handle():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    try:
        response = get_student_jobs(connection_pool, response['id'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error getting list: {err}")
    
@app.route("/api/users/deleteapply", methods=['DELETE'])
def delete_student_apply_handler():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    # try:
    response = delete_student_apply(connection_pool, response['id'], request)
    print("return response")
    return response
    # except mysql.connector.Error as err:
    #     return handle_bad_request(f"Error: {err}")

#http://127.0.0.1:5000/api/users/getstudents?job_id=127
@app.route("/api/users/getstudents", methods=['GET'])
def recruiter_get_applied_students_handle():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    if response["role"]=="Student":
        return jsonify({"error": "Student can't access jobs list"})
    try:
        response = recruiter_get_applied_students(connection_pool, request, response['id'])
        if "error" in response:
            return jsonify({"error": response["error"]})
        for res in response:
            if(res["avatar"] != "NULL"):
                res["avatar"] = encode_image_as_base64("uploads/"+res["avatar"])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")


@app.route("/api/users/changestatus", methods=['PUT'])
def change_applied_status_handle():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    if response["role"]=="Student":
        return jsonify({"error": "Student can't access jobs list"})
    try:
        response = change_applied_status(connection_pool, request, response['id'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Custom error handler for JSON responses
@app.errorhandler(400)
def handle_bad_request(e):
    response = jsonify(error=str(e))
    response.status_code = 400
    return response

# POST: Create a new job
@app.route("/api/jobs/post", methods=["POST"])
def create_job():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    if response["role"]=="Student":
        return jsonify({"error": "Student can't create job"})
    try:
        response = create_job_(connection_pool, request, response['id'], app.config['UPLOAD_FOLDER'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error creating job: {err}")

# GET: Retrieve all jobs
# http://127.0.0.1:5000/api/jobs/page?criteria=created&order=ASC&page_num=1&job_title=Dog
@app.route("/api/jobs/page", methods=["GET"])
def get_jobs():
    try:
        response = get_all_jobs(connection_pool, request)
        for job in response["data"]:
            if not(job["image"] == None or job["image"] == "NULL"):
                job["image"] = encode_image_as_base64("uploads/"+job["image"])
        return jsonify(response)
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving jobs: {err}")

# GET: Retrieve a job by ID
# http://127.0.0.1:5000/api/jobs/get?job_id=120
@app.route("/api/jobs/get", methods=["GET"])
def get_job_information():
    try:
        response = get_job_by_id(connection_pool, request, handle_bad_request)
        print(response)
        if not(response['image'] is None or response['image'] == "NULL"):
            response['image'] = encode_image_as_base64("uploads/"+response["image"])
        return jsonify(response)
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error retrieving job: {err}")

# PUT: Update a job by ID
# http://127.0.0.1:5000/api/jobs/put?job_id=125
@app.route("/api/jobs/put", methods=["PUT"])
def update_job():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    try:
        response = update_job_by_id(connection_pool, request, response["id"], app.config['UPLOAD_FOLDER'])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error updating job: {err}")

# DELETE: Delete a job by ID
@app.route("/api/jobs/delete", methods=["DELETE"])
def delete_job():
    response = verify_handler()
    if response == "Invalid token":
        return jsonify({"error": response})
    try:
        response = delete_job_by_id(connection_pool, request, response["id"])
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error deleting job: {err}")

# GET: Get all the available tags from the db
@app.route("/api/jobs/tags/get", methods=["GET"])
def get_all_tags():
    try:
        response = get_all_available_tags(connection_pool)
        return response
    except mysql.connector.Error as err:
        return handle_bad_request(f"Error getting all available tags: {err}")


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token):
    return jsonify({"error": "Invalid token"})


# Email Send
@app.route("/api/email", methods=["POST"])
def send_email_handler():
    try:
        send_email(request)
        return jsonify({"message": "Successfully sended"})
    except KeyError as err:
        return jsonify({"error": "Email was not sended"})



if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False, threaded=True)