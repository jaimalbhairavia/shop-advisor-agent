import logging
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-4-20250514"


def model_use(name: str, temperature: float = 0.7):

    lowered = name.lower()

    if any(k in lowered for k in ("gpt", "openai", "open ai", "o1", "o3", "o4")):
        return ChatOpenAI(model=name, temperature=temperature)

    if any(k in lowered for k in ("claude", "anthropic")):
        return ChatAnthropic(model_name=name, temperature=temperature)

    logger.warning(
        "Unknown model '%s' — falling back to default model '%s'.", name, DEFAULT_MODEL
    )
    return ChatAnthropic(model_name=DEFAULT_MODEL, temperature=temperature)
