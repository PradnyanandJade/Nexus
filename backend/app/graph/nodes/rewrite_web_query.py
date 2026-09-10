from app.graph.state import GraphState
from app.prompts.prompt_templates import WEB_REWRITE_QUERY_PROMPT_TEMPLATE
from app.llm.models import rewrite_llm as llm

async def rewrite_web_query(state: GraphState):
    messages = state["llm_messages"]
    query = messages[-1].content
    prompt = WEB_REWRITE_QUERY_PROMPT_TEMPLATE.invoke({
        "messages": messages,
        "query": query
    })
    result = await llm.ainvoke(prompt)
    return {
        "rewritten_query": result.content
    }
