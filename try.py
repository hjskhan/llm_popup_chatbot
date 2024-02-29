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

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app.secret_key = 'app_secret_key'


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
    if request.method == 'POST':
        user_message = request.json.get('message')
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