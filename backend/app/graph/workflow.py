from langgraph.graph import StateGraph,START,END
from app.graph.state import GraphState
from app.graph.nodes.initialize_run import initialize_run
from app.graph.nodes.compress_conversation_history import compress_conversation_history
from app.graph.nodes.route import route
from app.graph.nodes.create_retriever import create_retriever
from app.graph.nodes.web_search import web_search
from app.graph.nodes.rewrite_rag_query import rewrite_rag_query
from app.graph.nodes.rewrite_web_query import rewrite_web_query
from app.graph.nodes.ask_llm import ask_llm
from app.graph.guardrails.guardrails import input_guardrail,output_guardrail,blocked_node,content_security_guardrail
from app.graph.router import query_route_decision,guardrail_decision

def build_graph(checkpointer, retriever):
    graph = StateGraph(GraphState)

    context_retriever = create_retriever(retriever)

    graph.add_node("initialize_run",initialize_run)
    graph.add_node('input_guardrail',input_guardrail)
    graph.add_node("compress_conversation_history",compress_conversation_history)
    graph.add_node("route",route)
    graph.add_node("rewrite_rag_query",rewrite_rag_query)
    graph.add_node("rewrite_web_query",rewrite_web_query)
    graph.add_node("context_retriever",context_retriever)
    graph.add_node("web_search",web_search)
    graph.add_node("content_security_guardrail",content_security_guardrail)
    graph.add_node("ask_llm",ask_llm)
    graph.add_node('output_guardrail',output_guardrail)
    graph.add_node("blocked_node",blocked_node)


    graph.add_edge(START,"initialize_run")
    graph.add_edge("initialize_run","input_guardrail")
    graph.add_conditional_edges("input_guardrail",guardrail_decision,{
        "safe":"compress_conversation_history",
        "unsafe":"blocked_node"
    })
    graph.add_edge("compress_conversation_history","route")
    graph.add_conditional_edges("route",query_route_decision,{
        "rag":"rewrite_rag_query",
        "web":"rewrite_web_query",
        "chat":"ask_llm"
    })
    graph.add_edge("rewrite_rag_query","context_retriever")
    graph.add_edge("rewrite_web_query","web_search")
    graph.add_edge("context_retriever","content_security_guardrail")
    graph.add_edge("web_search","content_security_guardrail")
    graph.add_conditional_edges("content_security_guardrail",guardrail_decision,{
        "safe":"ask_llm",
        "unsafe":"blocked_node"
    })
    graph.add_edge("ask_llm","output_guardrail")
    graph.add_conditional_edges("output_guardrail",guardrail_decision,{
        "safe":END,
        "unsafe":"blocked_node"
    })
    graph.add_edge("blocked_node",END)
    return graph.compile(checkpointer=checkpointer)

