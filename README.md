# Archivist: Local RAG System with Microservices
A fully containerized, local Retrieval-Augmented Generation system built with FastAPI, Ollama, and Qdrant.
## Architecture Overview

The system is built using a microservices architecture, orchestrated via Docker Compose. This ensures scalability, separation of concerns, and isolated environments for each component.

### Core Services:

* **API Gateway (`:8000`):** Acts as the single entry point for the client. Routes requests to the appropriate internal services and handles rate limiting.
* **Ingestion Service (`:8001`):** Responsible for document processing. It receives PDF files, extracts text using `PyMuPDF`, performs semantic chunking, generates embeddings, and upserts them into the vector database.
* **Query Service (`:8002`):** Handles user questions. It embeds the user query, performs a similarity search in the vector database, and streams the prompt to the local LLM to generate a context-aware answer.

### Infrastructure:

* **Vector Store (Qdrant):** Stores document embeddings and metadata for fast vector similarity search.
* **LLM Engine (Ollama):** Runs local open-source models (e.g., Llama 3) for privacy-preserving, air-gapped generation.

---

## Project Structure

```text
rag-system/
├── docker-compose.yml       # Infrastructure orchestration
├── api-gateway/             # FastAPI routing service
├── ingestion-service/       # PDF processing & embedding logic
├── query-service/           # Retrieval & generation logic
└── poc/                     # Proof of Concept scripts and sandbox