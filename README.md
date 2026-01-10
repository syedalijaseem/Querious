# Querious - Chat with your documents

![Landing Page](docs/screenshots/landing_page.png)

Querious is an intelligent document Q&A agent that allows you to upload PDFs and ask questions in plain English. It uses RAG (Retrieval-Augmented Generation) to provide accurate answers with source citations.

🌐 **Live Demo:** [querious.dev](https://querious.dev)

📜 **Technical Details:** [Building a Production RAG System](https://syedalijaseem.medium.com/building-a-production-rag-system-architecture-and-technical-decisions-bf817c8b519f?source=friends_link&sk=53acae6115cce8267bd38e6572dab947)

## Features

- **Document Ingestion**: Upload PDF documents which are processed, chunked, and embedded for search.
- **RAG Powered Q&A**: Ask questions and get answers based _only_ on your documents to reduce hallucinations.
- **Source Citations**: Every answer includes citations linking back to the specific part of the document usable for verification.
- **Project Organization**: Group chats and documents into projects.
- **Secure Authentication**: Full user management with secure password hashing and session control.
- **Dark/Light Themes**: Modern interface with theme support.

## Screenshots

### Chat Interface

![Chat - Dark Mode](docs/screenshots/chat_dark.png)

### Projects

![Projects](docs/screenshots/projects_dark.png)

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, TanStack Query
- **Backend**: Python (FastAPI), MongoDB (Data + Vector Storage)
- **AI**: OpenAI (Embeddings), DeepSeek (LLM)
- **Infrastructure**: Inngest (Background Jobs), AWS S3 / Cloudflare R2 (File Storage)

## Architecture

![RAG Pipeline Architecture](docs/screenshots/architecture.png)

The system uses a two-pipeline RAG (Retrieval-Augmented Generation) architecture:

- **Document Ingestion**: PDFs are uploaded to S3, parsed, chunked, embedded via OpenAI, and stored in MongoDB Atlas with vector indexes.
- **Query Retrieval**: User queries are embedded, matched via cosine similarity, and the top-K chunks are fed to the LLM for response generation.

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB Atlas account
- Cloudflare R2 or AWS S3 bucket
- OpenAI & DeepSeek API keys

### Quick Start

```bash
# Clone the repository
git clone https://github.com/syedalijaseem/Querious.git
cd Querious

# Backend setup
cp .env.example .env
# Fill in your API keys and secrets (see Environment Variables section)
uv sync
uv run uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Inngest (new terminal, optional for background jobs)
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
```

### Ports

| Service            | Port   |
| ------------------ | ------ |
| Frontend (Vite)    | `5173` |
| Backend (FastAPI)  | `8000` |
| Inngest Dev Server | `8288` |

## Environment Variables

Contributors must provide their own API keys and secrets. Copy `.env.example` to `.env` and fill in the values.

```bash
cp .env.example .env
```

### Required Variables

| Variable               | Description                                           |
| ---------------------- | ----------------------------------------------------- |
| `MONGODB_URI`          | MongoDB Atlas connection string                       |
| `JWT_SECRET_KEY`       | Secret for JWT tokens (use `openssl rand -base64 32`) |
| `OPENAI_API_KEY`       | OpenAI API key for embeddings                         |
| `DEEPSEEK_API_KEY`     | DeepSeek API key for LLM responses                    |
| `R2_ACCESS_KEY_ID`     | Cloudflare R2 access key ID                           |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 secret access key                       |
| `R2_ENDPOINT`          | Cloudflare R2 endpoint URL                            |
| `R2_BUCKET_NAME`       | R2 bucket name                                        |

### Optional Variables

| Variable               | Default                 | Description                  |
| ---------------------- | ----------------------- | ---------------------------- |
| `ENVIRONMENT`          | `development`           | Set to `production` in prod  |
| `MONGODB_DATABASE`     | `docurag`               | Database name                |
| `FRONTEND_URL`         | `http://localhost:5173` | Frontend URL for CORS        |
| `GOOGLE_CLIENT_ID`     | —                       | For Google OAuth (optional)  |
| `GOOGLE_CLIENT_SECRET` | —                       | For Google OAuth (optional)  |
| `RESEND_API_KEY`       | —                       | For email service (optional) |

## Contributing

1. Fork the repository
2. Create a feature branch from `main`:
   - `feat/new-feature-name`
   - `fix/bug-description`
   - `chore/tooling-update`
3. Make your changes
4. Open a Pull Request to `main`
5. Address review feedback
6. Your PR will be merged after approval

```bash
git checkout main
git pull origin main
git checkout -b feat/my-feature
# ... make changes ...
git push origin feat/my-feature
# Open PR to main
```

## Security Notes

- **Never commit `.env` files** — they are gitignored by default
- **Rotate keys immediately** if you suspect they have been leaked
- **Use least-privilege API keys** — only grant the permissions your app needs
- **JWT_SECRET_KEY must be strong** — use `openssl rand -base64 32` to generate

## Plan Limits

| Plan    | Tokens        | Chats     | Projects  | Documents |
| ------- | ------------- | --------- | --------- | --------- |
| Free    | 10,000        | 3         | 1         | 3         |
| Pro     | 2,000,000/mo  | Unlimited | 10        | 30        |
| Premium | 15,000,000/mo | Unlimited | Unlimited | Unlimited |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
