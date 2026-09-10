from app.graph.state import GraphState
from app.prompts.prompt_templates import ASK_LLM_PROMPT_TEMPLATE
from app.llm.models import answer_llm as llm


async def ask_llm(state:GraphState):
    messages = state["messages"]
    context = state.get("context","")
    # use the actual query user asked not rewritten query
    query = messages[-1].content 
    prompt = ASK_LLM_PROMPT_TEMPLATE.invoke({
        "messages": messages,
        "context": context,
        "query": query
    }) 
    response = await llm.ainvoke(prompt)
    return {
        "messages":[response]
    }