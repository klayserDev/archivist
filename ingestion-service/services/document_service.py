
import uuid
from pathlib import Path
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def process_and_store_document(file_bytes: bytes, filename: str)->tuple[str,int]:
    document_id = str(uuid.uuid4())

    save_filename = f"{document_id}_{filename}"
    file_path = UPLOAD_DIR / save_filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)
    doc = fitz.open(file_path)
    if doc.page_count == 0:
        print("The PDF file is empty. No content to ingest.")
        return document_id, 0
    text = " ".join(page.get_text() for page in doc)
    splitter  = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50, 
        separators=["\n\n", "\n", ".", " "]
        )
    chunks = splitter.split_text(text)

    qdrant = QdrantClient(host="localhost", port=6333)
    if not qdrant.collection_exists(collection_name="documents"):
        print("Collection 'documents' not found. Creating it now...")
        qdrant.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        #Index for the 'source' field to enable filtering by source or future deletion of documents based on their source
        qdrant.create_payload_index(
            collection_name="documents",
            field_name="source",
            field_schema=PayloadSchemaType.KEYWORD
        )
    
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
            payload={"text": chunk, "source": save_filename}
        ))
    qdrant.upsert(collection_name="documents", points=points)
    return document_id, len(chunks)
