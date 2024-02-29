from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import os
import openai
from langchain.adapters import openai as lc_openai #for chatbot two way conversations
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Cassandra
from langchain.embeddings.openai import OpenAIEmbeddings
from PyPDF2 import PdfReader
from docx import Document
import cassio
from dotenv import load_dotenv
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
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
# Function to preprocess the uploaded file
def preprocessor(uploaded_files, url):
    texts = []
    if uploaded_files:
        print('---------------------- Inside preprocessor')
        for uploaded_file in uploaded_files:
            print('---------------------- Inside preprocessor for loop')
            if uploaded_file.filename.endswith('.pdf'):
                print('---------------------- Inside preprocessor for loop pdf')
                texts.extend(preprocess_pdf(uploaded_file))
            elif uploaded_file.filename.endswith(('.doc', '.docx')):
                texts.extend(preprocess_word(uploaded_file))
    if url:
        texts.extend(preprocess_url(url))
    return texts


# Sub-Function to preprocess url
def preprocess_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

    raw_text = soup.get_text()

    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=800,
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
        chunk_size=800,
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
        chunk_size=800,
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
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST': # if there is file upload then preprocess it\
        user_message = request.form.get('message')
        uploaded_files = request.files.getlist('file')
        # uploaded_files = uploaded_files.filename
        print('----------------------',uploaded_files)
        # url = request.('url')
        if uploaded_files:
            # Preprocess files and retrieve texts from VectorDB
            session['texts'] = preprocessor(uploaded_files,None)
            
            texts = session.get('texts')

            astra_vector_store = initialize_astra_vector_store() # Initialize once before processing
            print('----------------------astraDB initialized')
            astra_vector_store.add_texts(texts)
            print('----------------------texts added to astraDB')
            astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)

            # Perform initial query on VectorDB
            vectorDB_answer = perform_query(user_message, astra_vector_index)
            print('----------------------vectorDB query performed')
            message_history.append({"role": "user", "content": f"Answer this: {user_message}, you can use this additional information if required {vectorDB_answer}"})

        else:
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