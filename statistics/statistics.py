from datetime import datetime,timedelta
# Subject to change, import the database and cursor
from app import db, mycursor

# Backend, get the number of jobs that were created last month
def jobs_created_last_month():
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        query = """
                SELECT *
                FROM jobrapid.jobs
                WHERE created >= %s
            """

        mycursor.execute(query, (one_month_ago,))
        jobs = mycursor.fetchone()
        count = 0
        while jobs is not None:
            # Comment this out if you need it
            # print(jobs)
            jobs = mycursor.fetchone()
            count += 1

        return count

    except Exception as e:
        print(f"Error: {e}")
        return []

# Backend, get the number of users that were created in a month
def job_taggers_created_last_month():
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        query = """
                    SELECT *
                    FROM jobrapid.user
                    WHERE created >= %s
                """

        mycursor.execute(query, (one_month_ago,))
        users = mycursor.fetchone()
        count = 0
        while users is not None:
            # Comment this out if you need it
            # print(users)
            users = mycursor.fetchone()
            count += 1

        return count

    except Exception as e:
        print(f"Error: {e}")
        return

# Backend, get the number of jobs that are currently in progress
def jobs_in_progress():
    try:
        query = """
                    SELECT *
                    FROM jobrapid.jobs
                    WHERE taken = true AND finished = false
                """

        mycursor.execute(query)
        jobs = mycursor.fetchone()
        count = 0
        while jobs is not None:
            # Comment this out if you need it
            print(jobs)
            jobs = mycursor.fetchone()
            count += 1

        return count

    except Exception as e:
        print(f"Error: {e}")
        return

# Front end, show the number of reviews to the right of the review stars
def user_rating_count(user_id):
    try:
        query = """
                    SELECT Count(rating)
                    FROM jobrapid.reviews
                    WHERE user_id = %s
                """
        mycursor.execute(query, (user_id,))
        review_count = mycursor.fetchone()
        if review_count:
            review_count = int(review_count[0])
            print("Nr or ratings: (" + review_count + ")")
        else:
            print("No ratings found for this user.")

        return

    except Exception as e:
        print(f"Error: {e}")
        return


# Front-end, show the average_user_rating of an user as stars (UI)
def average_user_rating(user_id):
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
            print("User rating:", user_rating)
        else:
            print("No ratings found for this user.")

        return

    except Exception as e:
        print(f"Error: {e}")
        return


# job_taggers_created_last_month()
# print(job_taggers_created_last_month())
# jobs_created_last_month()
# print(jobs_created_last_month())
# print(jobs_in_progress())
# average_user_rating(7)
# user_rating_count(7)


