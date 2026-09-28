# DocAI

DocAI is an AI-powered document knowledge base API built with **Python and FastAPI**. It allows authenticated users to upload PDF documents and ask questions about their content using a Retrieval-Augmented Generation (RAG) pipeline.

The project focuses on building an AI backend system with document processing, vector search, conversational retrieval, and real-time LLM streaming.

## Features

* 🔐 JWT authentication
* 🔑 Google OAuth authentication
* 📄 PDF document upload and text extraction
* ✂️ Text chunking with overlapping chunks
* 🧠 OpenAI embeddings
* 🔎 Semantic vector search using PostgreSQL and pgvector
* 💬 Conversational question answering
* 🔄 Conversational query rewriting for follow-up questions
* 📚 Source retrieval with document and chunk metadata
* ⚡ Real-time LLM response streaming using Server-Sent Events (SSE)
* 💾 Conversation and message persistence
* 👤 User-scoped documents and conversations
* 🛡️ Error handling during streaming
* 🐘 PostgreSQL database

## Architecture

DocAI follows a RAG-based architecture:

```text
                         ┌──────────────────┐
                         │      Client      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    FastAPI API   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             Document Upload               Chat Request
                    │                           │
                    ▼                           ▼
              PDF Extraction             Query Rewriting
                    │                           │
                    ▼                           ▼
               Text Chunking              Embedding
                    │                           │
                    ▼                           ▼
              OpenAI Embedding         Vector Search
                    │                           │
                    ▼                           ▼
              PostgreSQL +               Relevant
                pgvector                  Chunks
                                                │
                                                ▼
                                           LLM Context
                                                │
                                                ▼
                                          OpenAI LLM
                                                │
                                                ▼
                                           SSE Stream
                                                │
                                                ▼
                                             Client
```

## RAG Pipeline

When a document is uploaded:

```text
PDF
 ↓
Text Extraction
 ↓
Text Chunking
 ↓
OpenAI Embeddings
 ↓
PostgreSQL + pgvector
```

When a user asks a question:

```text
Question
 ↓
Query Rewriting
 ↓
Query Embedding
 ↓
Vector Similarity Search
 ↓
Relevant Document Chunks
 ↓
Context Construction
 ↓
LLM
 ↓
Streaming Response + Sources
```

## Conversational Retrieval

DocAI supports follow-up questions that depend on previous conversation context.

For example:

```text
User:
What authentication methods does the document describe?

Assistant:
The document describes JWT and OAuth authentication.

User:
Can you give me an example of each?
```

The second question is not sufficiently specific for semantic search by itself.

DocAI therefore rewrites the follow-up question into a standalone retrieval query while preserving the original question for the final LLM response.

```text
Conversation History
        +
Latest Question
        ↓
Query Rewriting
        ↓
Standalone Search Query
        ↓
Vector Retrieval
```

## Real-Time Streaming

The LLM response is streamed to the client using **Server-Sent Events (SSE)**.

The API sends different event types:

### Token

```text
event: token
data: {"text":"FastAPI"}
```

### Sources

```text
event: sources
data: [...]
```

### Completion

```text
event: done
data: {"message":"completed"}
```

### Error

```text
event: error
data: {"message":"Something went wrong while generating the answer."}
```

This allows the client to display the answer incrementally instead of waiting for the complete LLM response.

## Authentication

DocAI supports two authentication methods:

### JWT Authentication

Users can register and log in using email/password authentication.

JWT access tokens are used to authenticate protected API endpoints.

### Google OAuth

Users can also authenticate through Google OAuth.

Protected resources are scoped to the authenticated user, preventing users from accessing documents or conversations belonging to other users.

## Database

DocAI uses **PostgreSQL** with **pgvector** for storing both application data and document embeddings.

Main entities include:

```text
User
 │
 ├── Documents
 │      └── Document Chunks
 │             └── Embedding
 │
 └── Conversations
        └── Messages
```

### Document Chunks

Each document is divided into chunks containing:

* Document ID
* Chunk index
* Text content
* Vector embedding
* Creation timestamp

Embeddings are generated using OpenAI's embedding model and stored using the PostgreSQL `vector` type.

## Project Structure

```text
DocAI/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── oauth.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── document.py
│   │       ├── document_chunk.py
│   │       ├── conversation.py
│   │       └── message.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   └── message.py
│   │
│   ├── services/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── retrieval.py
│   │   └── llm.py
│   │
│   └── api/
│       ├── deps.py
│       └── routes/
│           ├── auth.py
│           ├── documents.py
│           ├── conversations.py
│           └── chat.py
│
├── uploads/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

## Tech Stack

### Backend

* Python
* FastAPI
* SQLModel
* Pydantic

### AI / LLM

* OpenAI API
* OpenAI Embeddings
* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Vector Search

### Database

* PostgreSQL
* pgvector

### Authentication

* JWT
* Google OAuth
* Argon2 password hashing

### Document Processing

* pypdf

### Development

* uv
* Git
* Docker
* Postman

## Getting Started

### Prerequisites

Make sure you have:

* Python 3.10+
* PostgreSQL
* PostgreSQL with the `pgvector` extension
* An OpenAI API key
* Google OAuth credentials if Google login is enabled

### 1. Clone the repository

```bash
git clone https://github.com/Abdulwadood0/DocAI.git
cd DocAI
```

### 2. Install dependencies

This project uses `uv`.

```bash
uv sync
```

Or install dependencies with:

```bash
uv run fastapi dev app/main.py
```

### 3. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/docai

OPENAI_API_KEY=your_openai_api_key

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

Never commit your `.env` file.

### 4. Enable pgvector

Make sure the PostgreSQL `vector` extension is enabled:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Run the application

```bash
uv run fastapi dev app/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Main API Endpoints

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/google
GET  /auth/google/callback
GET  /auth/me
```

### Documents

```text
POST /documents/
```

Uploads a PDF, extracts its text, creates chunks, generates embeddings, and stores the document and vectors.

### Conversations

```text
POST /conversations/
GET  /conversations/
GET  /conversations/{conversation_id}/messages
```

### Chat

```text
POST /chat/{conversation_id}
```

Returns an SSE stream containing generated tokens, document sources, and completion status.

## Example RAG Flow

A question such as:

```text
What are the main authentication methods described in the document?
```

is converted into an embedding and compared against stored document embeddings.

The most relevant chunks are retrieved and provided as context to the LLM.

The model then generates an answer based on the retrieved document context rather than relying only on its general knowledge.

The response also includes the document chunks used to generate the answer.

## Design Decisions

### Why PostgreSQL + pgvector?

Using PostgreSQL with pgvector allows application data and vector embeddings to be stored in the same database, simplifying the architecture while supporting semantic similarity search.

### Why query rewriting?

Follow-up questions often depend on previous conversation context. Rewriting them into standalone search queries improves retrieval quality without changing the original question sent to the final LLM.

### Why SSE?

Server-Sent Events provide a simple way to stream generated LLM output from the backend to the client over a persistent HTTP connection.

### Why asynchronous streaming?

LLM generation can take several seconds. Streaming allows the client to receive generated content incrementally rather than waiting for the entire response.
