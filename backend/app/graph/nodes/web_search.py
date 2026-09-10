from app.graph.state import GraphState
from langchain_core.documents import Document
from tavily import AsyncTavilyClient
from app.config import settings

tavily_client = AsyncTavilyClient(
    api_key=settings.TAVILY_API_KEY
)

async def web_search(state: GraphState):
    query = state["rewritten_query"]
    response = await tavily_client.search(query=query,max_results=5)
    documents = []
    for result in response["results"]:
        document = Document(
            page_content=result["content"],
            metadata={
                "title": result["title"],
                "url": result["url"],
                "score": result["score"],
                "source": "web",
            }
        )
        documents.append(document)
    context = "\n\n".join(document.page_content for document in documents)
    return {
        "context_documents": documents,
        "context": context
    }