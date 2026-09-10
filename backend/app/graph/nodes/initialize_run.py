from app.graph.state import GraphState

async def initialize_run(state: GraphState):
    return {
        "llm_messages": [],
        "route": "",
        "rewritten_query": "",
        "context": "",
        "context_documents": [],
        "guardrail": ""
    }