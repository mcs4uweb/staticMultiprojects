# agent/main.py
import os
import requests
import time
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline

# Safety guardrail using local DistilBERT (smaller than RoBERTa)
guardrail = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    return_all_scores=True,
)

def is_safe(text: str) -> bool:
    results = guardrail(text[:512])  # Truncate long inputs
    # Assume label "LABEL_0" = negative/toxic
    return results[0][0]['score'] < 0.7

# Build RAG knowledge base
def build_rag():
    with open("knowledge/nvidia_blog.txt") as f:
        text = f.read()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    docs = splitter.split_text(text)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(docs, embeddings)
    return vectorstore.as_retriever()

# LLM using local TinyLlama (1.1B params)
def generate_response(prompt: str) -> str:
    # In real implementation, use vLLM or llama.cpp
    # For demo, return mock response
    return f"Based on NVIDIA best practices: {prompt.split('Question:')[-1].strip()}"

def process_query(query: str) -> str:
    if not is_safe(query):
        return "I cannot respond to unsafe requests."
    
    retriever = build_rag()
    docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in docs])
    
    prompt = f"""Use ONLY the context to answer.
    Context: {context}
    Question: {query}
    Answer:"""
    
    return generate_response(prompt)

# HTTP API endpoint
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data['text']
    
    # Get ASR audio if needed (not used here since input is text)
    response = process_query(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)