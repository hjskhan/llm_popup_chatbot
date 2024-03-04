from flask import Flask, render_template, request, redirect
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for home page
@app.route('/')
def index():
    return render_template('try.html')


# Route to handle file upload and text extraction
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    # If the user does not select a file, browser also submits an empty part without filename
    if file.filename == '':
        return redirect(request.url)

    # If the file is allowed, save it and perform text extraction
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Simulate some processing delay
        time.sleep(2)

        # Read the text from the file (you may need to adjust based on the file type)
        with open(filepath, 'r') as f:
            text = f.read()

        # Remove the file after processing (optional)
        os.remove(filepath)

        return text

    return 'Invalid file format'


if __name__ == '__main__':
    app.run(debug=True)
