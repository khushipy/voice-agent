from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import RetrievalQA

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline



def answer_from_docs(query: str) -> str:
    """Retrieve answers from local PDFs using FAISS + local HuggingFace model."""

    # Load PDFs
    loaders = [
        PyPDFLoader("data/llm.pdf"),
        PyPDFLoader("data/rag.pdf")
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(docs)

    # Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Vector store
    vectorstore = FAISS.from_documents(texts, embeddings)
    retriever = vectorstore.as_retriever()

    # Local model pipeline
    model_name = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=256,
        device_map="auto"
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    # Combine retriever + model
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    return qa.run(query)

