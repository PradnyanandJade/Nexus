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

## Tech stack

**Backend**
- **FastAPI** (Python) — the web server and API
- **LangGraph** — orchestrates the multi-step pipeline described above
- **OpenAI models** — power the routing, query rewriting, answering, summarizing, and safety-check steps
- **Hugging Face** — used for generating document embeddings (the "meaning-based" search representations); a Hugging Face chat model is also configured for future use
- **Pinecone** — the search index that stores document chunks two ways (meaning-based and keyword-based) for hybrid search
- **Cohere** — re-ranks search results so the best matches come out on top
- **Tavily** — the web search provider
- **PostgreSQL** — stores users, conversations, messages, and document records, and also stores the AI pipeline's own conversation checkpoints (so it can resume/replay a conversation's state)
- **AWS S3** — stores the actual uploaded document files
- **JWT (JSON Web Tokens)** — handles login sessions, with short-lived access tokens and longer-lived refresh tokens
- **Docker** — both backend and frontend ship with their own Dockerfiles, plus a `docker-compose.yml` to run everything together
- **AWS EC2 — Hosting***

**Frontend**
- **React 19** with **Vite** as the build tool
- **react-markdown** + **remark-gfm** — renders the AI's answers as nicely formatted Markdown (including tables, lists, etc.)
- Plain CSS for styling, served in production through **Nginx**

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
