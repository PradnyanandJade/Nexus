from app.graph.state import GraphState
from app.prompts.prompt_templates import RAG_REWRITE_QUERY_PROMPT_TEMPLATE
from app.llm.models import rewrite_llm as llm

async def rewrite_rag_query(state: GraphState):
    messages = state["llm_messages"]
    query = messages[-1].content
    prompt = RAG_REWRITE_QUERY_PROMPT_TEMPLATE.invoke({
        "messages": messages,
        "query": query
    })
    result = await llm.ainvoke(prompt)
    return {
        "rewritten_query": result.content
    }
