import sys
from pathlib import Path
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import uuid

def main():
    print("== Archivist - Proof of Concept ==")
    pdf_path = input("Enter the path to the PDF file: ").strip()
    if not pdf_path:
        print("No file path provided. Exiting.")
        return    

    print(f"Processing PDF file: {pdf_path}")
    n_chunks = ingest_pdf(pdf_path)
    print(f"PDF file ingested successfully. Number of chunks created: {n_chunks}")

    print("Ask your question about the PDF content. Type 'exit' or 'quit' to quit.")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ('exit', 'quit'):
            print("Exiting the application. Goodbye!")
            break
        if not question:
            continue
        print("searching for answer...")
        result = query(question)

        print(f"Answer: {result['answer']}")
        print("\n" + "─" * 50 + "\n")
        print(f"sources: {', '.join(result['sources'])}")
        print(f"chunks: {', '.join(result['chunks_used'])} | latency: {result['latency']} seconds")
        print("\n" + "─" * 50 + "\n")

def query(question):
    # Placeholder for query logic
    # In a real implementation, this would involve searching the vector database,
    # retrieving relevant chunks, and using a language model to generate an answer.
    print(f"Simulating query processing for question: {question}")
    # Simulate a response
    return {
        "answer": "This is a simulated answer based on the PDF content.",
        "sources": ["source1.pdf", "source2.pdf"],
        "chunks_used": ["chunk1", "chunk2"],
        "latency": 0.5
    }

def ingest_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        print("The PDF file is empty. No content to ingest.")
        return 0
    text = " ".join(page.get_text() for page in doc)
    splitter  = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50, 
        separators=["\n\n", "\n", ".", " "]
        )
    #Connect to Qdrant vector database
    qdrant = QdrantClient(host="localhost", port=6333)
    if not qdrant.collection_exists(collection_name="documents"):
        print("Collection 'documents' not found. Creating it now...")
        qdrant.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
    
    chunks = splitter.split_text(text)
    points = []
    
    for chunk in chunks:
        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=chunk
        )
        vector = response['embedding']
        
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text":chunk, "source": pdf_path}    
        ))
    qdrant.upsert(collection_name="documents", points=points)
    return len(chunks)

if __name__ == "__main__":
    main()