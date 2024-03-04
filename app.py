from flask import Flask, render_template, request, redirect, url_for, session, jsonify, current_app
from flask_session import Session
import os
import sys
import openai
import pickle
from langchain.adapters import openai as lc_openai #for chatbot two way conversations
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Cassandra
from langchain.embeddings.openai import OpenAIEmbeddings
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
import cassio
from dotenv import load_dotenv
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["AstraVectorIndex"] = None
Session(app)

# Load environment variables from .env file
load_dotenv(override=True)

ASTRA_DB_APPLICATION_TOKEN = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
ASTR_DB_ID = os.getenv('ASTR_DB_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app.secret_key = 'app_secret_key'


####################################################
# AstraDB connection and vector store initialization
def initialize_astra_vector_store():
    cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTR_DB_ID)
    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    astra_vector_store = Cassandra(
        embedding=embedding,
        table_name='pdfquery02',
        session=None,
        keyspace=None
    )
    return astra_vector_store
####################################################

####################################################
####################################################
# Function to preprocess url
def preprocess_url(url):
    texts = []
    print('---------------------- Inside preprocess_url')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

    raw_text = soup.get_text()

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    print('---------------------- chunks created from url')
    print('---------------------- preprocess_url done')
    return texts

# Function to preprocess the uploaded file
def preprocessor_files(uploaded_files):
    texts = []
    if uploaded_files:
        print('---------------------- Inside preprocessor')
        if uploaded_files.filename.endswith('.pdf'):
            texts.extend(preprocess_pdf(uploaded_files))
        elif uploaded_files.filename.endswith(('.doc', '.docx')):
            texts.extend(preprocess_word(uploaded_files))
        elif uploaded_files.filename.endswith('.txt'):
            texts.extend(preprocess_text(uploaded_files))
        elif uploaded_files.filename.endswith('.md'):
            texts.extend(preprocess_markdown(uploaded_files))
        elif uploaded_files.filename.endswith(('.html', '.htm')):
            texts.extend(preprocess_html(uploaded_files))
        elif uploaded_files.filename.endswith(('.pptx')):
            texts.extend(preprocess_pptx(uploaded_files))

    return texts



# Sub-Function to preprocess powerpoint file (.pptx)
def preprocess_pptx(uploaded_file):
    prs = Presentation(uploaded_file)
    raw_text = ''

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                raw_text += shape.text + '\n'    

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    return texts

# Sub-Function to preprocess plain text file (.txt)
def preprocess_text(uploaded_file):
    raw_text = uploaded_file.read().decode('utf-8')

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    return texts

# Sub-Function to preprocess markdown file (.md)
def preprocess_markdown(uploaded_file):
    
    raw_text = uploaded_file.read().decode('utf-8')

    # Additional markdown processing logic if needed

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    return texts

# Sub-Function to preprocess HTML file (.html)
def preprocess_html(uploaded_file):
    # Additional HTML processing logic if needed
    raw_text = uploaded_file.read().decode('utf-8')

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    return texts



# Sub-Function to preprocess pdf
def preprocess_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    raw_text = ''
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            raw_text += content

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    print('---------------------- Inside preprocess_pdf')
    return texts

# Sub-Function to preprocess word document
def preprocess_word(uploaded_file):
    document = Document(uploaded_file)
    raw_text = ''
    for paragraph in document.paragraphs:
        raw_text += paragraph.text

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)
    return texts
####################################################


####################################################
# Function to perform query from AstraDB
def perform_query(query_text, astra_vector_index):
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    answer = astra_vector_index.query(query_text, llm=llm).strip()
    return answer
####################################################


message_history = []# message history
# initial message
message_text = [{"role":"system","content":"You are an AI assistant that helps people by answering the questions asked."}]
message_history.extend(message_text)
# Define Flask routes for chatbot
@app.route('/')
def index():
    return render_template('index.html', uploaded_files=session.get('uploaded_files', []))

@app.route('/upload', methods=['POST'])
def upload():
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append(file.filename)
            session['uploaded_files'] = uploaded_files
            # preprocess the file and store the texts in session
            session['texts'] = preprocessor_files(file)
            texts = session.get('texts')
            astra_vector_store = initialize_astra_vector_store() # Initialize once before processing
            print('----------------------astraDB initialized')
            astra_vector_store.add_texts(texts)
            print('----------------------texts added to astraDB')
            astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
            current_app.config["AstraVectorIndex"] = astra_vector_index
            # session['astra_vector_index'] = astra_vector_index  # Store the vector index in session
            return 'File uploaded and preprocessed successfully!'
    return 'No file selected!'

@app.route('/remove/<filename>')
def remove_file(filename):
    uploaded_files = session.get('uploaded_files', [])
    if filename in uploaded_files:
        uploaded_files.remove(filename)
        session['uploaded_files'] = uploaded_files
        return redirect(url_for('index'))
    return 'File not found!'

@app.route('/upload_url', methods=['POST'])
def upload_url():
    
    if 'url' in request.form:
        url = request.form['url']
        url_links = session.get('url_links', [])
        url_links.append(url)
        session['url_links'] = url_links

        # preprocess the url and store the texts in session
        session['texts'] = preprocess_url(url)
        texts = session.get('texts')
        astra_vector_store = initialize_astra_vector_store() # Initialize once before processing
        print('----------------------astraDB initialized')
        astra_vector_store.add_texts(texts)
        print('----------------------texts added to astraDB')
        astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
        current_app.config["AstraVectorIndex"] = astra_vector_index  # Store the vector index in session
        return 'URL uploaded successfully!'
    return 'No URL selected!'

@app.route('/remove_url/<url>')
def remove_url(url):
    url_links = session.get('url_links', [])
    if url in url_links:
        url_links.remove(url)
        session['url_links'] = url_links
        return redirect(url_for('index'))
    return 'URL not found!'

@app.route('/chat', methods=['GET', 'POST'])
def chatbot():
    
    if request.method == 'POST': # if there is file upload then preprocess it\
        user_message = request.form.get('message')
        # if 'astra_vector_index' in session:
            # astra_vector_index = session.get('astra_vector_index')
        if current_app.config["AstraVectorIndex"] is not None:
            astra_vector_index = current_app.config["AstraVectorIndex"]
            print('----------------------astra_vector_index is not None')
            # Perform initial query on VectorDB
            vectorDB_answer = perform_query(user_message, astra_vector_index)
            print('----------------------vectorDB query performed')
            message_history.append({"role": "user", "content": f"Answer this: {user_message}, you can use this additional information if required {vectorDB_answer}"})

        else:
            print('----------------------astra_vector_index not found in session')
            message_history.append({"role": "user", "content": user_message})

    # Rest of the code for chat processing

    # send message to openai
    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages = message_history,
    temperature=0.7,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
    # stream=True
    )
    # append assistant message to message history
    message_history.append({"role":"assistant","content":response.choices[0].message.content})
    return jsonify({"response": response.choices[0].message.content})


if __name__ == '__main__':
    app.run(debug=True)