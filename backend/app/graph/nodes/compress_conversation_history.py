import tiktoken
from langchain_core.messages import SystemMessage
from app.llm.models import summary_llm as llm
from app.graph.state import GraphState
from app.config import settings
from app.prompts.prompt_templates import SUMMARIZE_CONVERSATION_HISTORY_PROMPT_TEMPLATE

def count_message_tokens(messages) -> int:
    try:
        encoding = tiktoken.encoding_for_model(
            settings.OPENAI_MODEL_NAME
        )
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    text = "\n".join(message.content for message in messages if isinstance(message.content, str))
    return len(encoding.encode(text))


async def compress_conversation_history(state: GraphState):
    messages = state["messages"]
    if not messages:
        return {
            "llm_messages": []
        }
    token_count = count_message_tokens(messages)
    if token_count <= settings.MAX_HISTORY_TOKENS:
        return {
            "llm_messages": messages
        }
    old_messages = messages[:-settings.RECENT_MESSAGE_COUNT]
    recent_messages = messages[-settings.RECENT_MESSAGE_COUNT:]
    conversation = "\n".join(
        f"{message.type}: {message.content}"
        for message in old_messages
        if isinstance(message.content, str)
    )
    
    prompt = SUMMARIZE_CONVERSATION_HISTORY_PROMPT_TEMPLATE.invoke({"conversation":conversation})
    response = await llm.ainvoke(prompt)
    summary_message = SystemMessage(
        content=f"""
Previous conversation summary:
{response.content}
"""
    )

    llm_messages = [
        summary_message,
        *recent_messages
    ]
    return {
        "llm_messages": llm_messages
    }