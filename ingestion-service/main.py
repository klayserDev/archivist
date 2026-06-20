from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uvicorn

from services.document_service import process_and_store_document

app = FastAPI(title="Ingestion Service")

class IngestionResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str

@app.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    document_id,chunks_created = await process_and_store_document(await file.read(), file.filename)
    return IngestionResponse(document_id=document_id, chunks_created=chunks_created, status="success")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)