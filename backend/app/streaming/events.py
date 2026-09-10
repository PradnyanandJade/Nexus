def context_event(context, documents, route):
    return {
        "type": "context",
        "context": context,
        "documents": documents,
        "route": route,
    }


def status_event(message: str):
    return {
        "type": "status",
        "message": message
    }


def answer_event(content: str):
    return {
        "type": "answer",
        "content": content
    }


def guardrail_block_event(message: str):
    return {
        "type": "guardrail_block",
        "message": message,
    }


def done_event():
    return {
        "type": "done"
    }


def error_event(message: str):
    return {
        "type": "error",
        "message": message
    }