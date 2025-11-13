import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "data/faiss_index"
PDFS = ["pdfs/llm.pdf", "pdfs/rag.pdf"]

def ingest_pdfs():
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("HUGGINGFACE_EMBEDDINGS_MODEL"))
    all_chunks = []

    for pdf_path in PDFS:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    os.makedirs(DB_PATH, exist_ok=True)
    vectorstore.save_local(DB_PATH)
    return "PDFs ingested and FAISS index created."

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("HUGGINGFACE_EMBEDDINGS_MODEL"))
    if not os.path.exists(DB_PATH):
        ingest_pdfs()
    return FAISS.load_local(DB_PATH, embeddings)

