from app.graph.state import GraphState
from typing import Literal

def query_route_decision(state: GraphState) -> Literal["rag", "web", "chat"]:
    return state["route"]

def guardrail_decision(state : GraphState) -> Literal["safe","unsafe"]:
    guardrail = state["guardrail"]
    if guardrail == "safe":
        return "safe"
    else :
        return "unsafe"