from app.graph.state import GraphState
from pydantic import BaseModel
from typing import Literal
from app.llm.models import router_llm as llm


class RouteDecision(BaseModel):
    route: Literal["chat", "rag", "web"]

router_llm = llm.with_structured_output(RouteDecision)

async def route(state: GraphState):
    messages = state["llm_messages"]
    result = await router_llm.ainvoke([
        {
            "role": "system",
            "content": """
            Decide which route should handle the user's request.

            chat:
            Use for normal conversation, greetings, casual questions,
            explanations, coding questions, etc. that do not require
            uploaded documents or current web information.

            rag:
            Use when the user is asking about information contained
            in their uploaded documents.

            web:
            Use when the user needs current or external internet information,
            such as latest news, current prices, recent events, etc.
            """
        },
        *messages
    ])
    return {
        "route": result.route
    }
