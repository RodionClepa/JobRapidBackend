import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="flask",
    passwd="python123",
    database="jobrapid"
)

mycursor = db.cursor()

#mycursor.execute("SELECT * FROM jobs")

#mycursor.execute("CREATE TABLE jobs(job_id INT PRIMARY KEY AUTO_INCREMENT, job_title VARCHAR(50), job_description VARCHAR(255), location VARCHAR(50),salary VARCHAR(30),application_deadline datetime,job_email VARCHAR(50),job_phone VARCHAR(30));")

#mycursor.execute("ALTER TABLE jobs AUTO_INCREMENT=1")