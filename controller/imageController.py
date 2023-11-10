import uuid
from werkzeug.utils import secure_filename
import os
import base64

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_avatar(file, folder_name):
    if file == None  or file.filename == '':
        filename = None
    elif allowed_file(file.filename):
        filename = secure_filename(str(uuid.uuid4()))+file.filename[file.filename.find("."):];
        file.save(os.path.join(folder_name, filename))
        return filename
    else:
        return {"error": "Invalid image format"}
    
def encode_image_as_base64(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_image
    except FileNotFoundError:
        print(f"Error: File not found - {image_path}")
        return None