from typing import TypedDict,Annotated,Literal
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class GraphState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]
    document_ids: list[int]
    llm_messages: list[BaseMessage]
    route : Literal['chat','rag','web']
    guardrail : str
    rewritten_query : str
    context_documents : list[Document]
    context : str
