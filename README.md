# 🤖 LLM RAG Chatbot

## 📌 Overview
The **LLM RAG Chatbot** is an AI-powered conversational assistant that leverages **Retrieval-Augmented Generation (RAG)** to provide intelligent, context-aware responses. It utilizes:
- **Flask** for a lightweight web API backend 🌐
- **LangChain** for seamless integration of LLMs and retrieval techniques 🔗
- **OpenAI GPT-4o** for natural language understanding and response generation 🧠
- **AstraDB** (Powered by Apache Cassandra) for efficient, scalable vector storage 🗄️

This chatbot is designed to enhance user interactions by retrieving relevant knowledge from external sources and combining it with LLM capabilities for accurate responses.

---

## ⚙️ Features
- 🗣️ **Conversational AI:** Engage in meaningful, intelligent conversations.
- 🔍 **RAG-based Retrieval:** Fetches relevant documents from AstraDB before generating responses.
- 🏗️ **Modular Architecture:** Built using Flask for easy deployment and scalability.
- ⚡ **Fast & Scalable:** Optimized for high performance with AstraDB’s distributed storage.
- 🎯 **Context-Aware Responses:** Provides more relevant and precise answers.

---

## 🏗️ Tech Stack
- **[Flask](https://flask.palletsprojects.com/)** – Lightweight Python web framework
- **[LangChain](https://www.langchain.com/)** – Framework for LLM orchestration
- **[OpenAI GPT-4o](https://openai.com/research/gpt-4o)** – AI model for response generation
- **[AstraDB](https://www.datastax.com/products/datastax-astra)** – Vector database for retrieval
- **Python 3.10+** – Core programming language

---

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo/llm-rag-chatbot.git
cd llm-rag-chatbot
```

### 2️⃣ Install Dependencies
Ensure you have Python 3.10+ installed, then run:
```sh
pip install -r requirements.txt
```

### 3️⃣ Set Up API Keys
Create a `.env` file and add your API keys:
```env
OPENAI_API_KEY=your_openai_key
ASTRADB_APPLICATION_TOKEN=your_astradb_token
ASTRADB_DATABASE_ID=your_astradb_id
```

### 4️⃣ Run the Chatbot API
```sh
python app.py
```
The API will start on `http://127.0.0.1:5000`

---

## 🎯 Usage
### Make a Chat Request
Send a message to the chatbot via the API:
```sh
curl -X POST "http://127.0.0.1:5000/chat" -H "Content-Type: application/json" -d '{"message": "What is LangChain?"}'
```
### Expected Output
```json
{
  "response": "LangChain is an open-source framework for developing applications powered by LLMs."
}
```


## 🔥 Future Enhancements
- 🗣️ Voice input & response generation
- 🌍 Multi-language support
- 🤖 Advanced personalization
- 📡 Integration with messaging platforms

---

## 🤝 Contributing
Contributions are welcome! Feel free to:
- Open issues 🐞
- Submit PRs 📌
- Suggest improvements 🚀

