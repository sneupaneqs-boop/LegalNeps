import os

from dotenv import load_dotenv

load_dotenv()


def _list(name: str, default: str) -> list[str]:
    return [m.strip() for m in os.getenv(name, default).split(",") if m.strip()]


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Answer generation: strongest first. Every model has its own quota (the free
# tier allows ~20 requests/day per full "flash" model), so a long chain of
# distinct models multiplies capacity; lite models are the high-volume floor.
GEMINI_MODELS = _list("GEMINI_MODELS", os.getenv("GEMINI_MODEL", "") or
                      "gemini-3.8-flash,gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,"
                      "gemini-3-flash-preview,gemini-flash-latest,gemini-3.5-flash-lite,"
                      "gemini-3.1-flash-lite,gemini-flash-lite-latest,gemini-3.1-flash-lite-preview")
# Query understanding: latency matters more than depth; lite models only.
GEMINI_FAST_MODELS = _list("GEMINI_FAST_MODELS",
                           "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-flash-lite-latest,"
                           "gemini-3.1-flash-lite-preview,gemini-3-flash-preview")
LLM_TIMEOUT_S = int(os.getenv("LLM_TIMEOUT_S", "40"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "8"))
PRECEDENT_K = int(os.getenv("RETRIEVAL_PRECEDENT_K", "3"))
ANSWER_CACHE_SIZE = int(os.getenv("ANSWER_CACHE_SIZE", "512"))
