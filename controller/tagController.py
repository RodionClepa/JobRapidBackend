def get_tags_for_job(connection_pool, job_id):
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    print(job_id)
    mycursor.execute(f"SELECT t.tag_id, t.tag_name FROM tags AS t INNER JOIN jobs_tags AS j ON t.tag_id = j.tag_id WHERE j.job_id = {job_id}")
    result = mycursor.fetchall()
    mycursor.close()
    db.close()
    tags = [{"tag_id":tag[0], "tag_name":tag[1]} for tag in result]
    return tags

def get_all_available_tags(connection_pool):
    db = connection_pool.get_connection()
    mycursor = db.cursor()
    mycursor.execute("SELECT tag_id, tag_name FROM jobrapid.tags")
    result = mycursor.fetchall()
    mycursor.close()
    db.close()
    tags = [{"tag_id":tag[0], "tag_name":tag[1]} for tag in result]
    # Returns as a tuple, use the tag_name for the frontend and return the tag_id to the backend
    return tags


# Adding tags to a job
def set_tags_to_job(connection_pool, job_id, tag_ids):

    db = connection_pool.get_connection()
    mycursor = db.cursor()
    
    # Checking if the tag_ids is not null
    if tag_ids is None or not tag_ids:
        mycursor.execute(f"DELETE FROM jobrapid.jobs_tags WHERE job_id = {job_id}")
        db.commit()
        mycursor.close()
        db.close()
        return
    
    tag_id_list = []
    for tag_id in tag_ids.split(","):
        try:
            tag_id_list.append(int(tag_id))
        except ValueError:
            mycursor.close()
            db.close()
            return
    for tag_id in tag_id_list:
        mycursor.execute(f"SELECT COUNT(*) FROM tags WHERE tag_id = {tag_id}")
        check = mycursor.fetchone()[0]
        if check == 0:
            mycursor.close()
            db.close()
            return
    
    mycursor.execute(f"DELETE FROM jobrapid.jobs_tags WHERE job_id = {job_id}")
    db.commit()
    
    for tag_id in tag_id_list:
        # Inserting into jobs_tags table the tags for the job
        sql = "INSERT INTO jobs_tags (job_id, tag_id) VALUES (%s, %s)"
        values = (job_id, tag_id)
        mycursor.execute(sql, values)
        db.commit()
    
    mycursor.close()
    db.close()
