# Querious - Chat with your documents

Querious is an intelligent document Q&A agent that allows you to upload PDFs and ask questions in plain English. It uses RAG (Retrieval-Augmented Generation) to provide accurate answers with source citations.

## Features

- **Document Ingestion**: Upload PDF documents which are processed, chunked, and embedded for search.
- **RAG Powered Q&A**: Ask questions and get answers based _only_ on your documents to reduce hallucinations.
- **Source Citations**: Every answer includes citations linking back to the specific part of the document usable for verification.
- **Project Organization**: Group chats and documents into projects.
- **Secure Authentication**: Full user management with secure password hashing and session control.
- **Modern UI**: specialized interface for reading documents and chatting simultaneously.

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, TanStack Query
- **Backend**: Python (FastAPI), MongoDB (Data), Qdrant (Vectors)
- **AI**: OpenAI (Embeddings), DeepSeek (LLM)
- **Infrastructure**: Inngest (Background Jobs), AWS S3 (File Storage)

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account
- Qdrant Cloud cluster
- AWS S3 bucket
- OpenAI & DeepSeek API keys

### Environment Variables

Copy `.env.example` to `.env` in the root directory and fill in your secrets:

```bash
cp .env.example .env
```

Copy `frontend/.env.example` to `frontend/.env.local`:

```bash
cp frontend/.env.example frontend/.env.local
```

### Installation

1. **Backend**:

   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### Running Locally

1. **Start Backend**:

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start Frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Start Inngest** (for background jobs):
   ```bash
   npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
   ```

## License

This project is licensed under AGPL-3.0. If you use, modify, or deploy this code (including as a web service), you must open-source your changes under the same license.
