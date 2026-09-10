from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from app.config import settings

router_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    temperature=0,
    max_completion_tokens=settings.ROUTER_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY
)

rewrite_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    temperature=0,
    max_completion_tokens=settings.REWRITE_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY
)

answer_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    temperature=0.2,
    max_completion_tokens=settings.ANSWER_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY,
    streaming=True
)

guardrail_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    temperature=0,
    max_completion_tokens=settings.GUARDRAIL_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY
)

summary_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    temperature=0,
    max_completion_tokens=settings.SUMMARY_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY
)


endpoint_huggingface = HuggingFaceEndpoint(
    repo_id=settings.HUGGINGFACE_MODEL_NAME,
    task="text-generation",
    huggingfacehub_api_token=settings.HF_TOKEN
)

llm_huggingface = ChatHuggingFace(
    llm=endpoint_huggingface
)

