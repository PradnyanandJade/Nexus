import json
from app.streaming.events import (status_event, answer_event, done_event, error_event, context_event, guardrail_block_event)
from app.streaming.status_messages import STATUS_MESSAGES
import logging

logger = logging.getLogger(__name__)

def serialize_documents(documents):
    return [
        {
            "content": document.page_content,
            "metadata": document.metadata
        }
        for document in documents
    ]

async def stream_graph(graph, initial_state, config):
    final_answer = None
    output_guardrail_result = None
    context = ""
    context_documents = []
    context_route = None

    try:
        async for chunk in graph.astream(
            initial_state,
            config,
            stream_mode="updates"
        ):
            for node_name, update in chunk.items():
                status = STATUS_MESSAGES.get(node_name)
                if status:
                    yield status_event(status)
                if node_name in {"context_retriever", "web_search"}:
                    context = update.get("context", "")
                    context_documents = update.get(
                        "context_documents",
                        []
                    )
                    context_route = "web" if node_name == "web_search" else "rag"
                if node_name == "content_security_guardrail":
                    guardrail_result = update.get("guardrail")
                    if guardrail_result != "safe":
                        yield guardrail_block_event(
                            "The retrieved content could not be safely processed."
                        )
                        yield done_event()
                        return
                    yield context_event(
                        context=context,
                        documents=serialize_documents(context_documents),
                        route=context_route,
                    )
                if node_name == "ask_llm":
                    messages = update.get("messages", [])
                    if messages:
                        final_answer = messages[-1].content
                if node_name == "output_guardrail":
                    output_guardrail_result = update.get("guardrail")

                if node_name == "blocked_node":
                    messages = update.get("messages", [])
                    blocked_message = messages[-1].content if messages else "I can't process that request."
                    yield guardrail_block_event(blocked_message)
                    yield done_event()
                    return

        if output_guardrail_result != "safe":
            yield error_event(
                "I can't provide that response."
            )
            return

        yield answer_event(final_answer)
        yield done_event()

    except Exception as e:
        print("STREAM ERROR:", repr(e))
        logger.exception("STREAM ERROR")
        yield error_event(
            "Something went wrong while processing your request."
        )