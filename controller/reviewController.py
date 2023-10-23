from flask import request, jsonify
import mysql.connector
from datetime import datetime

# Backend, creating the review and posting it in the database
def create_review(mycursor, db, request):
    user_id = request.args.get('user_id', default=None, type=int)
    rating = request.form.get('rating')
    review_message = request.form.get('review_message')
    sql = """
            INSERT INTO jobrapid.reviews (user_id, rating, review_message, created)
            VALUES (%s, %s, %s, %s)
        """
    values = (user_id, rating, review_message, datetime.now())
    mycursor.execute(sql, values)
    db.commit()

    return jsonify({"message": "Job created successfully"}), 201


    def update_review_by_id(mycursor, db, request):
        review_id = request.args.get('review_id', default=None, type=int)
        user_id = request.args.get('user_id', default=None, type=int)
        mycursor.execute(f"SELECT review_id FROM jobrapid.review WHERE review_id={review_id}")
        result = mycursor.fetchone()
        if result and result[0] == review_id and result[1] == user_id:
            sql = """
                UPDATE jobrapid.reviews
                SET rating = %s, review_message = %s
                WHERE review_id = %s AND user_id = %s
                """
            rating = request.forms.get('rating')
            review_message = request.forms.get('review_message')
            values = (rating, review_message, review_id, user_id)
            mycursor.execute(sql, values)
            db.commit()

            return jsonify({"message": "Review updated successfully"})
        else:
            return jsonify({"error": "User id/review id not found"})

# Front-end, show the average_user_rating of a user as stars (UI)
def average_user_rating(mycursor, user_id):
    try:
        query = """
                    SELECT AVG(rating)
                    FROM jobrapid.reviews
                    WHERE user_id = %s
                """
        mycursor.execute(query, (user_id,))
        user_rating = mycursor.fetchone()
        if user_rating:
            user_rating = float(user_rating[0])
            # Change the print statements to whatever return value you need it to be for the front end
            print("User rating:", user_rating)
        else:
            print("No ratings found for this user.")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

# Front end, show the number of reviews to the right of the review stars
def user_rating_count(mycursor, user_id):
    try:
        query = """
                    SELECT COUNT(rating)
                    FROM jobrapid.reviews
                    WHERE user_id = %s
                """
        mycursor.execute(query, (user_id,))
        review_count = mycursor.fetchone()
        if review_count:
            review_count = int(review_count[0])
            # Change the print statements to whatever return value you need it to be for the front end
            print("Nr or ratings: (" + review_count + ")")
        else:
            print("No ratings found for this user.")

        return

    except Exception as e:
        print(f"Error: {e}")
        return

# Getting all the reviews of the user by the id
def get_reviews_by_id(mycursor, request, handle_bad_request):
    user_id = request.args.get('user_id', default=None, type=int)
    count = mycursor.execute("SELECT COUNT(*) FROM jobrapid.reviews WHERE user_id = %s", (user_id,))
    mycursor.execute("SELECT * FROM jobrapid.reviews WHERE user_id = %s", (user_id,))
    reviews = mycursor.fetchall()
    for x in range(count):
        review_dict = {
            "rating": reviews[x][2],
            "review_message": reviews[x][3],
            "created": reviews[x][4]
        }
        return jsonify(review_dict)
    else:
        return handle_bad_request(f"Reviews for user_id = {user_id} not found")
