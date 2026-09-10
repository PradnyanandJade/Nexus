# Nexus

Nexus is a full-stack **AI chat assistant** that can have a normal conversation, dig into documents you upload, and search the live web — and it automatically figures out which one of those three things it needs to do for every message you send.

Think of it as your own private ChatGPT-style app, but one that you host yourself, that remembers your past conversations, that can read your PDFs, and that has built-in safety checks so it doesn't get tricked into leaking secrets or doing something it shouldn't.

It has two parts that work together:
- A **backend** (Python/FastAPI) that does all the thinking — talking to AI models, storing your data, searching documents, and streaming answers back word by word.
- A **frontend** (React) that gives you a clean chat interface in the browser.

---

## What Nexus can do

- **Chat like a normal AI assistant** — ask general questions and get a conversational answer, no extra setup needed.
- **Answer questions from your own documents** — upload a PDF, ask a question about it, and Nexus finds the most relevant passages and answers using them (this is called RAG — Retrieval-Augmented Generation).
- **Search the live web** — if a question needs up-to-date information, Nexus automatically searches the web and answers using what it finds.
- **Decide for itself** — for every message, Nexus first figures out whether it should just chat, look in your documents, or search the web. You never have to pick a mode.
- **Stream answers live** — responses appear word by word as they're generated, instead of making you wait for the whole answer.
- **Remember your conversations** — every chat is saved, so you can leave and come back later and pick up where you left off.
- **Keep documents separate per conversation** — you choose which uploaded documents are "in scope" for a given chat.
- **Protect itself and you** — every message and every answer passes through safety checks before it reaches you (more on this below).
- **Support multiple users** — everyone logs in with their own account, and their conversations and documents are private to them.

---

<img width="1536" height="1024" alt="ChatGPT Image Sep 10, 2026, 07_45_39 PM" src="https://github.com/user-attachments/assets/d66d88b1-010f-4f30-bd98-e2de4be7e2d0" />

## How it works, in plain terms

When you send a message, it doesn't just go straight to an AI model. It passes through a pipeline of steps (built using a framework called **LangGraph**, which lets you wire together a sequence of AI-powered steps into a flowchart):

1. **Input safety check** — the message is checked for things like prompt injection (someone trying to trick the AI into ignoring its rules), attempts to leak hidden instructions, or clearly unsafe content. If it's flagged, Nexus refuses politely and stops right there.
2. **Conversation compression** — if the conversation has gotten long, older messages are summarized so the AI doesn't run out of room to "remember" things, while recent messages are kept in full detail.
3. **Routing** — an AI model reads your message and decides which of three paths to take:
   - **Chat** — just answer directly, no extra lookup needed.
   - **RAG** — look this up in your uploaded documents.
   - **Web** — search the internet for this.
4. **Query rewriting** — your question gets rephrased into a cleaner search query (so "what about the second one?" becomes something searchable, using the earlier conversation for context).
5. **Retrieval** — depending on the route:
   - *Documents*: Nexus searches your documents two different ways at once — a "meaning-based" search (finds text with a similar meaning) and a "keyword-based" search (finds exact word matches) — combines the two result sets, and then re-ranks everything so the most relevant chunks float to the top.
   - *Web*: Nexus runs a live web search and pulls back the top results.
6. **Content safety check** — whatever was retrieved (from documents or the web) is scanned for hidden instructions before it's allowed to reach the AI, so a malicious PDF or web page can't hijack the conversation.
7. **Answer generation** — the AI model writes the actual answer, using the conversation history plus whatever context was retrieved, and streams it back to you as it's generated.
8. **Output safety check** — the finished answer is checked one more time before it's shown to you.

If any of the safety checks fail at any point, Nexus stops and sends back a clear, polite refusal instead of the AI's answer.

---
## Retrieval-Augmented Generation (RAG) Architecture 
<img width="1375" height="860" alt="image" src="https://github.com/user-attachments/assets/0d84eeac-8116-41ca-82aa-dcde3599ff3e" />

---
## Document Ingestion Pipeline 
<img width="540" height="785" alt="image" src="https://github.com/user-attachments/assets/1228e030-2e7e-428e-8e0a-80673920d258" />

## Tech Stack
<img width="2172" height="724" alt="ChatGPT Image Sep 10, 2026, 09_01_29 PM" src="https://github.com/user-attachments/assets/bfea4dc0-f3a2-4d10-a79d-02e0aba616f4" />

### Backend & AI

- **FastAPI (Python)** — backend web server and REST API layer
- **LangGraph** — orchestrates the multi-step AI workflow, including routing, RAG, web search, conversation handling, and guardrails
- **OpenAI** — powers query routing, query rewriting, conversation summarization, answer generation, and safety/guardrail checks
- **Hugging Face** — generates document embeddings for semantic retrieval; a Hugging Face chat model is also configured for future use
- **Pinecone** — vector database storing document chunks in **dense and sparse indexes** for hybrid retrieval
- **Cohere Rerank** — reranks retrieved chunks to select the most relevant context for answer generation
- **Tavily** — provides web search for queries routed to the web-search path

### Data & Storage

- **Vercel Postgres (PostgreSQL)** — stores users, documents, conversations, messages, document metadata, and LangGraph conversation checkpoints
- **AWS S3** — stores the original uploaded documents securely
- **Pinecone** — stores indexed document representations and metadata for retrieval

### Authentication & Security

- **JWT (JSON Web Tokens)** — authentication using short-lived access tokens and longer-lived refresh tokens
- **Input Guardrails** — detect potentially unsafe or malicious user input
- **Context Security Guardrails** — inspect retrieved document/web content for malicious or unsafe instructions
- **Output Guardrails** — validate generated responses before returning them to the user

### Frontend

- **React 19** — frontend web application
- **Vite** — frontend build tool and development server
- **react-markdown** — renders AI responses as Markdown
- **remark-gfm** — supports GitHub-Flavored Markdown such as tables, lists, and task lists
- **CSS** — application styling
- **Nginx** — serves the production React application

### Deployment & Infrastructure

- **Docker** — containerizes the frontend and backend
- **Docker Compose** — orchestrates the application containers
- **AWS EC2** — production hosting environment
  - **React + Nginx container** — serves the frontend
  - **FastAPI + LangGraph container** — runs the backend and AI pipeline
  - **Docker Compose** — manages the containers
- **AWS S3** — cloud object storage for uploaded documents
- **Vercel Postgres** — managed PostgreSQL database for application data and LangGraph state
  
---

## Project structure

```
Nexus/
├── backend/
│   ├── app/
│   │   ├── api/routes/       → API endpoints (auth, conversations, documents)
│   │   ├── graph/            → the LangGraph pipeline: nodes, router, guardrails
│   │   │   ├── nodes/        → each individual step in the pipeline
│   │   │   └── guardrails/   → the input/output/content safety checks
│   │   ├── database/         → SQLAlchemy models and DB connection setup
│   │   ├── llm/              → AI model configuration
│   │   ├── rag/              → hybrid document retriever (Pinecone + reranker)
│   │   ├── services/         → business logic (auth, documents, chat, S3, etc.)
│   │   ├── schemas/          → request/response data shapes (Pydantic)
│   │   ├── streaming/        → server-sent-events (SSE) streaming logic
│   │   ├── prompts/          → the prompt templates used by each AI step
│   │   ├── utils/            → security helpers, logging setup
│   │   └── main.py           → FastAPI app entry point, wires everything together on startup
│   ├── run.py                 → convenience script to start the server
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       → React components (chat panel, sidebar, document library, auth page, etc.)
│   │   ├── services/         → API calls to the backend (auth, conversations, documents, streaming)
│   │   └── App.jsx           → main app component
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml          → runs frontend + backend together
```

---

## API overview

All backend routes live under `/api`.

**Authentication** (`/api/auth`)
| Method | Endpoint | What it does |
|---|---|---|
| POST | `/register` | Create a new account |
| POST | `/login` | Log in and receive access/refresh tokens |
| POST | `/refresh` | Get a new access token using a refresh token |
| POST | `/logout` | Log out of the current session |
| POST | `/logout-all` | Log out of every device |
| GET | `/me` | Get the logged-in user's info |

**Conversations** (`/api/conversations`)
| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | List all your conversations |
| POST | `/` | Start a new conversation |
| GET | `/{id}` | Get one conversation |
| PUT | `/{id}` | Rename/update a conversation |
| DELETE | `/{id}` | Delete a conversation |
| GET | `/{id}/messages` | Get the message history for a conversation |
| POST | `/{id}/chat` | Send a message and get a full response |
| POST | `/{id}/stream-chat` | Send a message and get the response streamed back live |
| GET / POST | `/{id}/documents` | View or attach documents to a conversation |

**Documents** (`/api/documents`)
| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | List your uploaded documents |
| GET | `/{id}` | Get one document's details |
| POST | `/upload` | Upload and index a new document |
| POST | `/urls` | Get shareable/download URLs for documents |
| DELETE | `/delete/{id}` | Delete a document |

---

## Getting started

### Prerequisites

You'll need accounts/API keys for the following services, since Nexus relies on them:
- An **OpenAI** API key
- A **Hugging Face** access token
- A **Pinecone** account (with a dense and a sparse index created)
- A **Cohere** API key (for re-ranking)
- A **Tavily** API key (for web search)
- An **AWS** account with an **S3** bucket (for storing uploaded files)
- A **PostgreSQL** database (used both for app data and for the AI pipeline's checkpoints)

You'll also need **Python 3.10+**, **Node.js**, and optionally **Docker**.

### Option A: Run with Docker (recommended)

1. Open `docker-compose.yml` and fill in all the placeholder values (`...`) with your real API keys, database URLs, and secrets.
2. From the project root, run:
   ```bash
   docker-compose up --build
   ```
3. The frontend will be available at `http://localhost` and the backend API at `http://localhost:8000`.

### Option B: Run manually

**Backend**
```bash
cd backend
pip install -r requirements.txt
```
Create a `.env` file inside `backend/` with the following variables (see the table below for what each one is for), then start the server:
```bash
python run.py
```
The API will be available at `http://localhost:8000`.

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173` (Vite's default dev port).

---
---
## RAG Index Setup

Before running the Nexus backend, initialize the required resources for the RAG pipeline.

### 1. Download BM25 Encoder

Downloads the BM25 encoder configuration required for sparse/keyword-based retrieval.

Run from the `backend` directory:

python app/scripts/download_bm25.py

### 2. Create Pinecone Dense Index

Creates the Pinecone dense index used for semantic/vector-based retrieval.

Run:

python app/scripts/create_pinecone_dense_index.py

### 3. Create Pinecone Sparse Index

Creates the Pinecone sparse index used for keyword-based retrieval with BM25.

Run:

python app/scripts/create_pinecone_sparse_index.py

These resources are required for Nexus's hybrid RAG retrieval, which combines:

Dense Retrieval — semantic/meaning-based search
Sparse Retrieval (BM25) — keyword-based search
Reciprocal Rank Fusion (RRF) — combines dense and sparse results
Cohere Reranking — selects the most relevant document chunks
Running the Backend on Windows

When running FastAPI on Windows, Uvicorn multiprocessing can sometimes cause process-related errors.

Use the provided run.py entry point:

python run.py

Run this command from the backend directory.

---
---

### Environment variables (backend `.env`)

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY`, `OPENAI_MODEL_NAME`, `OPENAI_EMBEDDING_MODEL_NAME` | OpenAI access and model choice |
| `ROUTER_MAX_TOKENS`, `REWRITE_MAX_TOKENS`, `SUMMARY_MAX_TOKENS`, `ANSWER_MAX_TOKENS`, `GUARDRAIL_MAX_TOKENS` | Token limits for each pipeline step |
| `HUGGINGFACE_MODEL_NAME`, `HUGGINGFACE_EMBEDDING_MODEL_NAME`, `HF_TOKEN` | Hugging Face access and models |
| `PINECONE_API_KEY`, `PINECONE_DIMENSION`, `PINECONE_DENSE_INDEX_NAME`, `PINECONE_SPARSE_INDEX_NAME` | Pinecone vector search setup |
| `COHERE_API_KEY` | Re-ranking search results |
| `TAVILY_API_KEY` | Web search |
| `CHECKPOINTER_POSTGRES_URL` | Postgres connection string for LangGraph's conversation checkpoints |
| `SQL_ALCHEMY_POSTGRES_URL` | Postgres connection string for the main app database |
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | How documents are split into chunks before indexing |
| `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRATION_MINUTES`, `REFRESH_TOKEN_EXPIRATION_DAYS` | Login/session security |
| `MAX_HISTORY_TOKENS`, `RECENT_MESSAGE_COUNT` | Controls when/how conversation history gets summarized |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET` | Storage for uploaded document files |



---

## In Summary

Nexus brings together the following technologies and capabilities:

1. **LLM-based intelligent routing**
2. **Conversation-aware query rewriting**
3. **Hybrid dense + sparse retrieval**
4. **Pinecone vector search**
5. **Reciprocal Rank Fusion (RRF)**
6. **Cohere reranking**
7. **Live web search with Tavily**
8. **Multi-document RAG**
9. **Conversation compression**
10. **Persistent conversation history**
11. **LangGraph state and checkpoint management**
12. **Input, context, and output guardrails**
13. **Prompt-injection protection**
14. **Source-aware responses**
15. **Real-time response streaming**
16. **JWT-based authentication**
17. **AWS S3 document storage**
18. **PostgreSQL persistent storage**
19. **Dockerized deployment on AWS EC2**

Together, these components make Nexus a **full-stack, production-oriented AI assistant** capable of intelligently switching between general conversation, private document retrieval, and live web search while maintaining conversation context, providing grounded responses, and enforcing security checks throughout the workflow.

---

## A typical flow, end to end

1. You register/log in on the frontend.
2. You start a new conversation and (optionally) upload a PDF.
3. You ask a question.
4. The backend runs your message through the safety-checked, routed pipeline described above.
5. If it needed your document or the web, it retrieves the relevant information first.
6. The answer streams into the chat window in real time, formatted as Markdown.
7. Everything — your message, the answer, and which document(s) were used — is saved, so it's all still there next time you open that conversation.

---

## Notes for new contributors

- Each step of the AI pipeline lives as its own small file under `backend/app/graph/nodes/`, which makes it easy to find and modify one part of the flow (e.g. just the web search step) without touching the rest.
- The overall pipeline is wired together in `backend/app/graph/workflow.py` — that file is the best starting point for understanding how a message flows from start to finish.
- Safety checks (guardrails) are intentionally separate from the "thinking" steps, so they can be audited and adjusted independently.
- The frontend talks to the backend only through the `services/` folder, so all API logic is centralized in one place rather than scattered across components.


