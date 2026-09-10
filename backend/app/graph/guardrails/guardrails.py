from app.prompts.prompt_templates import INPUT_GUARDRAIL_PROMPT_TEMPLATE,OUTPUT_GUARDRAIL_PROMPT_TEMPLATE,CONTENT_SECURITY_GUARDRAIL_PROMPT_TEMPLATE
from app.llm.models import guardrail_llm as llm
from app.graph.state import GraphState
from langchain_core.messages import AIMessage
from app.graph.guardrails.decision_schemas import InputGuardrailDecision,OutputGuardrailDecision,ContentSecurityDecision


async def input_guardrail(state: GraphState):
    message = state['messages'][-1].content
    prompt = INPUT_GUARDRAIL_PROMPT_TEMPLATE.invoke({"query":message})
    result = await llm.with_structured_output(InputGuardrailDecision).ainvoke(prompt)
    return {
        "guardrail":result.category
    }

async def output_guardrail(state: GraphState):
    message = state["messages"][-1].content
    prompt = OUTPUT_GUARDRAIL_PROMPT_TEMPLATE.invoke({"response":message})
    result = await llm.with_structured_output(OutputGuardrailDecision).ainvoke(prompt)
    return {
        "guardrail":result.category
    }

async def content_security_guardrail(state: GraphState):
    context = state.get("context", "")
    prompt = CONTENT_SECURITY_GUARDRAIL_PROMPT_TEMPLATE.invoke({"context": context})
    result = await llm.with_structured_output(ContentSecurityDecision).ainvoke(prompt)
    return {
        "guardrail": result.category
    }

async def blocked_node(state: GraphState):
    category = state["guardrail"]
    messages = {
        "prompt_injection": "I can't help with attempts to bypass my instructions.",
        "prompt_leakage": "I can't provide hidden system or developer instructions.",
        "sensitive_data": "I can't provide private or sensitive information.",
        "unsafe_content": "I can't provide that content.",
        "indirect_prompt_injection": "I found instructions in the retrieved content that I can't follow."
    }
    return {"messages": [AIMessage(content=messages.get(category,"I can't process that request."))]}


