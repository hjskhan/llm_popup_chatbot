from flask import Flask, render_template, request, session, redirect, url_for
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
app = Flask(__name__)
app.secret_key = 'your_secret_key'

def preprocess_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    raw_text = ''
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            raw_text += content

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=800,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    print('---------------------- Inside preprocess_pdf')
    return texts

@app.route('/')
def index():
    return render_template('try.html', uploaded_files=session.get('uploaded_files', []))

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append(file.filename)
            session['uploaded_files'] = uploaded_files
            print('------------------',uploaded_files)
            print('------------------',session)
            print('------------------',file)
            print('------------------',file.filename)
            print('------------------',request)
            print('------------------',request.files)
            print('------------------',request.files['file'])
            
            # Call preprocess_pdf function here
            texts = preprocess_pdf(file)
            print('Preprocessed Texts:', texts)

            return 'File uploaded successfully!'
    return 'No file selected!'

@app.route('/remove/<filename>')
def remove_file(filename):
    uploaded_files = session.get('uploaded_files', [])
    if filename in uploaded_files:
        uploaded_files.remove(filename)
        session['uploaded_files'] = uploaded_files
        return redirect(url_for('index'))
    return 'File not found!'

if __name__ == '__main__':
    app.run(debug=True)
