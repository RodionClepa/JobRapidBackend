from flask import request, jsonify
import mysql.connector
from datetime import datetime

# Backend, creating the review and posting it in the database
def create_review(connection_pool, request, user_id):
    db = connection_pool.get_connection()
    mycursor = db.cursor(buffered=True)
    rating = request.form.get('rating')
    user_referenced = int(request.form.get('user_referenced'))
    mycursor.execute(f"SELECT 1 FROM user WHERE user_id = {user_referenced}")
    value = mycursor.fetchone()

    if value is None:
        db.close()
        mycursor.close()
        return jsonify({"error": "Referenced user id not found"}), 400

    if user_referenced == user_id:
        db.close()
        mycursor.close()
        return jsonify({"error": "Can't post a review for yourself"}), 400

    mycursor.execute(f"SELECT * FROM jobrapid.reviews WHERE user_id_referenced={user_referenced} AND user_id={user_id}")
    value = mycursor.fetchone()
    if value:
        db.close()
        mycursor.close()
        return jsonify({"error": "User already has a review for the referenced user"}), 400

    try:
        if int(rating) < 1 or int(rating) > 5 or not(isinstance(int(rating), int)):
            db.close()
            mycursor.close()
            return jsonify({"error": "Invalid rating, it needs to be an integer between 1 and 5"}), 400
    except ValueError:
        db.close()
        mycursor.close()
        return jsonify({"error": "Invalid rating, it needs to be an integer between 1 and 5"}), 400

    review_message = request.form.get('review_message')

    try:
        sql = """
                INSERT INTO jobrapid.reviews (user_id, rating, review_message, created, user_id_referenced)
                VALUES (%s, %s, %s, %s, %s)
            """
        values = (user_id, rating, review_message, datetime.now(), user_referenced)
        mycursor.execute(sql, values)
        db.commit()

        db.close()
        mycursor.close()
        return jsonify({"message": "Review created successfully"}), 201

    except Exception as e:
        db.close()
        mycursor.close()
        return jsonify(f"Error: {e}"), 400


def update_review_by_id(connection_pool, request, user_id):
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    review_id = request.args.get('review_id', default=None, type=int)
    mycursor.execute(f"SELECT * FROM jobrapid.reviews WHERE review_id={review_id} and user_id={user_id}")
    value = mycursor.fetchone()
    if value is None:
        db.close()
        mycursor.close()
        return jsonify({"message": "User review not found."}), 400

    try:
        sql = """
            UPDATE jobrapid.reviews
            SET rating = %s, review_message = %s
            WHERE review_id = %s AND user_id = %s
            """
        rating = request.form.get('rating')
        review_message = request.form.get('review_message')
        values = (rating, review_message, review_id, user_id)
        mycursor.execute(sql, values)
        db.commit()
        db.close()
        mycursor.close()
        return jsonify({"message": "Review updated successfully"}), 201

    except Exception as e:
        db.close()
        mycursor.close()
        return jsonify(f"Error: {e}"), 400

# Getting all the reviews of the user by the id
def get_reviews_by_id(connection_pool, request):
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    user_referenced = request.args.get('user_referenced', default=None, type=int)

    try:
        mycursor.execute("SELECT COUNT(*) FROM jobrapid.reviews WHERE user_id_referenced = %s", (user_referenced,))
        count = mycursor.fetchone()
        if count[0] > 0:
            review_list = []
            mycursor.execute("SELECT * FROM jobrapid.reviews WHERE user_id_referenced = %s", (user_referenced,))
            reviews = mycursor.fetchall()
            for x in range(count[0]):
                review_dict = {
                    "user_id_posted": reviews[x][1],
                    "rating": reviews[x][2],
                    "review_message": reviews[x][3],
                    "created": reviews[x][4]
                }
                review_list.append(review_dict)
            db.close()
            mycursor.close()
            return jsonify(review_list), 201

        else:
            db.close()
            mycursor.close()
            return jsonify({"Error": f"User_referenced = {user_referenced} has no reviews"}), 400

    except Exception as e:
        db.close()
        mycursor.close()
        return jsonify(f"Error: {e}"), 400

# Front-end, show the average_user_rating of a user as stars (UI)
def average_user_rating(connection_pool, request):
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    user_referenced = request.args.get('user_referenced', default=None, type=int)
    try:
        query = """
                    SELECT AVG(rating)
                    FROM jobrapid.reviews
                    WHERE user_id_referenced = %s
                """
        mycursor.execute(query, (user_referenced,))
        user_rating = mycursor.fetchone()
        if user_rating and user_rating[0] is not None:
            user_rating = float(user_rating[0])
            mycursor.close()
            db.close()
            return jsonify(user_rating), 201

        else:
            mycursor.close()
            db.close()
            return jsonify({"message" : f"No user ratings found for user_referenced = {user_referenced}"}), 400


    except Exception as e:
        db.close()
        mycursor.close()
        print(f"Error: {e}"), 400
        return

