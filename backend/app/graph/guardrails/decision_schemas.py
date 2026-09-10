from pydantic import BaseModel
from typing import Literal

class InputGuardrailDecision(BaseModel):
    category: Literal[
        "safe",
        "prompt_injection",
        "prompt_leakage",
        "sensitive_data"
    ]

class OutputGuardrailDecision(BaseModel):
    category: Literal[
        "safe",
        "unsafe_content",
        "sensitive_data",
        "prompt_leakage"
    ]

class ContentSecurityDecision(BaseModel):
    category: Literal[
        "safe",
        "indirect_prompt_injection"
    ]