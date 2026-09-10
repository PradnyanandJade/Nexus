from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.graph.workflow import build_graph 
from app.utils.logging_config import setup_logging
from app.config import settings
from pinecone import Pinecone
from app.rag.HybridRetriever import HybridRetriever
from app.rag.embedding import embedding
from pinecone_text.sparse import BM25Encoder
from app.api.routes import auth,conversations,documents
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from pathlib import Path
from app.database.database import create_tables
import cohere

BASE_DIR = Path(__file__).resolve().parent

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("0. Creating Tables")
#     await create_tables()

#     print("1. Logging")
#     setup_logging()

#     print("2. BM25")
#     bm25_path = (BASE_DIR / "rag" / "bm25_params" / "msmarco_bm25_params.json")
#     bm25_encoder = BM25Encoder()
#     bm25_encoder.load(str(bm25_path))

#     print("3. Pinecone")
#     pc = Pinecone(
#         api_key=settings.PINECONE_API_KEY,
#     )
#     dense_index = pc.Index(
#         settings.PINECONE_DENSE_INDEX_NAME
#     )
#     sparse_index = pc.Index(
#         settings.PINECONE_SPARSE_INDEX_NAME
#     )

#     print("4. Reranker")
#     cohere_client = cohere.ClientV2(
#         api_key = settings.COHERE_API_KEY
#     )
#     # reranker = CrossEncoder("BAAI/bge-reranker-base")
#     reranker = cohere_client

#     print("5. Retriever")
#     retriever = HybridRetriever(
#         dense_index=dense_index,
#         sparse_index=sparse_index,
#         embedding=embedding,
#         sparse_encoder=bm25_encoder,
#         reranker=reranker
#     )

#     print("6. Checkpointer")
#     async with AsyncPostgresSaver.from_conn_string(settings.CHECKPOINTER_POSTGRES_URL) as checkpointer:
#         print("7. Checkpointer setup")
#         await checkpointer.setup()
#         print("8. Build graph")
#         graph = build_graph(
#             checkpointer=checkpointer,
#             retriever=retriever
#         )
#         print("9. Yield")
#         app.state.dense_index = dense_index
#         app.state.sparse_index = sparse_index
#         app.state.bm25_encoder = bm25_encoder
#         app.state.embedding = embedding
#         app.state.retriever = retriever
#         app.state.graph = graph
#         yield
#         app.state.dense_index = None
#         app.state.sparse_index = None
#         app.state.bm25_encoder = None
#         app.state.embedding = None
#         app.state.retriever = None
#         app.state.graph = None

# app = FastAPI(lifespan=lifespan)

# app.include_router(auth.router, prefix="/api")
# app.include_router(conversations.router, prefix="/api")
# app.include_router(documents.router, prefix="/api")

# @app.get("/")
# def default_route():
#     return {"message": "Welcome to Nexus 2.0 Backend ...!"}



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("0. Creating Tables")
    await create_tables()

    print("1. Logging")
    setup_logging()

    print("2. BM25")
    bm25_path = (BASE_DIR / "rag" / "bm25_params" / "msmarco_bm25_params.json")
    bm25_encoder = BM25Encoder()
    bm25_encoder.load(str(bm25_path))

    print("3. Pinecone")
    pc = Pinecone(
        api_key=settings.PINECONE_API_KEY,
    )
    dense_index = pc.Index(
        settings.PINECONE_DENSE_INDEX_NAME
    )
    sparse_index = pc.Index(
        settings.PINECONE_SPARSE_INDEX_NAME
    )

    print("4. Reranker")
    cohere_client = cohere.ClientV2(
        api_key = settings.COHERE_API_KEY
    )
    # reranker = CrossEncoder("BAAI/bge-reranker-base")
    reranker = cohere_client

    print("5. Retriever")
    retriever = HybridRetriever(
        dense_index=dense_index,
        sparse_index=sparse_index,
        embedding=embedding,
        sparse_encoder=bm25_encoder,
        reranker=reranker
    )

    print("6. Checkpointer")
    pool = AsyncConnectionPool(
        conninfo=settings.CHECKPOINTER_POSTGRES_URL,
        min_size=1,
        max_size=5,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "sslmode": "require",
        },
        check=AsyncConnectionPool.check_connection,
        max_lifetime=1800,
        open=False
    )
    await pool.open()
    checkpointer = AsyncPostgresSaver(pool)
    print("7. Checkpointer setup")
    await checkpointer.setup()
    print("8. Build graph")
    graph = build_graph(
        checkpointer=checkpointer,
        retriever=retriever
    )
    print("9. Yield")
    app.state.dense_index = dense_index
    app.state.sparse_index = sparse_index
    app.state.bm25_encoder = bm25_encoder
    app.state.embedding = embedding
    app.state.retriever = retriever
    app.state.graph = graph
    yield
    app.state.dense_index = None
    app.state.sparse_index = None
    app.state.bm25_encoder = None
    app.state.embedding = None
    app.state.retriever = None
    app.state.graph = None

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
def default_route():
    return {"message": "Welcome to Nexus 2.0 Backend ...!"}
