##  AI Voice Agent with Document-based Q&A

An AI-powered **voice assistant** capable of answering questions based on custom PDF documents.  
Built using **FastAPI**, **LangChain**, **FAISS**, and **React**, this project combines **Retrieval-Augmented Generation (RAG)** and **Text-to-Speech (TTS)** to provide an end-to-end intelligent voice experience.

---

##  Features

-  **Document-based Q&A** – Upload and query PDFs (RAG pipeline with FAISS + LangChain)
-  **Local LLM Inference** – Uses lightweight `google/flan-t5-small` model for efficient reasoning
-  **Text-to-Speech Output** – Converts answers into human-like audio with `pyttsx3`
-  **Frontend Integration** – React-based interface for interacting with the backend
-  **Modular Design** – Easy to extend for more documents or models

---

##  Installation & Setup

###  1. Clone the Repository

```bash
git clone https://github.com/khushipy/voice-agent.git
cd voice-agent
```
### 2. Backend Setup
In a new terminal:
```bash
cd backend
python -m venv venv
venv\Scripts\activate     # (Windows)
# source venv/bin/activate  (Mac/Linux)

pip install -r requirements.txt

```
### Run the backend
```bash
uvicorn main:app --reload
```
Access API docs:
 http://127.0.0.1:8000/docs

### 2. Frontend Setup
In a new terminal:

```bash
cd ../frontend
npm install
npm run dev
```
Frontend runs on:
http://localhost:5173

# How It Works (Internally)
Document Loading:
PDFs from the data/ folder are loaded using PyPDFLoader.

Text Splitting:
Text is chunked into manageable parts using RecursiveCharacterTextSplitter.

Vectorization & Storage:
Each chunk is embedded using sentence-transformers/all-MiniLM-L6-v2 and stored in a FAISS vector index.

Querying:
When the user asks a question, the retriever fetches the most relevant chunks from FAISS.

Answer Generation:
The lightweight model google/flan-t5-small forms a contextual answer using the retrieved text.

Voice Output:
The response is converted to audio using pyttsx3 and played or downloaded by the user.

# Example Query
```bash
POST /ask
{
  "question": "What is Retrieval-Augmented Generation?"
}

```
# Response:
```bash
json
{
  "answer": "Retrieval-Augmented Generation combines information retrieval and text generation to answer contextually from external documents.",
  "audio_file": "outputs/answer.mp3"
}
```
## 🪶 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend** | FastAPI, LangChain, FAISS, PyPDFLoader |
| **LLM** | `google/flan-t5-small` (via HuggingFace) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **TTS** | pyttsx3 |
| **Frontend** | React + Vite |
| **Vector Store** | FAISS |
# Sample Output
[Download Audio Sample](./backend/outputs/response_20251102_154205.mp3)

Author - Khushi Pal 📍 GitHub Profile
