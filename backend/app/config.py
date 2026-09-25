import os

from dotenv import load_dotenv

load_dotenv()


def _list(name: str, default: str) -> list[str]:
    return [m.strip() for m in os.getenv(name, default).split(",") if m.strip()]


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
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
# OpenAI-compatible gateway, tried first when set. For OmniRoute:
#   OPENAI_BASE_URL=http://localhost:20128/v1  OPENAI_API_KEY=<OmniRoute API key>
# "auto/fast" and "auto" let OmniRoute pick the provider per tier.
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Ordered per tier (OmniRoute model IDs). Strongest-that-has-quota first;
# rate-limited models are skipped instantly and cooled down. Plain "auto" is
# kept only as the last resort because it can pick unsuitable models.
OPENAI_MODELS = _list("OPENAI_MODELS",
                      "gemini/gemini-3.8-flash,groq/openai/gpt-oss-120b,gemini/gemini-3.6-flash,"
                      "groq/qwen/qwen3.8-27b,gemini/gemini-3-flash-preview,mistral/mistral-medium-latest,"
                      "gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite,auto/chat")
OPENAI_FAST_MODELS = _list("OPENAI_FAST_MODELS",
                           "groq/qwen/qwen3.8-27b,groq/openai/gpt-oss-20b,gemini/gemini-3.1-flash-lite,"
                           "gemini/gemini-3.5-flash-lite,mistral/mistral-small-latest,auto/fast")

# Hard time budgets (seconds) so a slow/rate-limited provider can't hang the UI.
LLM_TIMEOUT_S = int(os.getenv("LLM_TIMEOUT_S", "60"))            # whole streamed answer
LLM_CALL_TIMEOUT_S = float(os.getenv("LLM_CALL_TIMEOUT_S", "20"))  # one attempt on one model
ANALYZE_BUDGET_S = float(os.getenv("ANALYZE_BUDGET_S", "8"))       # question understanding
ANSWER_BUDGET_S = float(os.getenv("ANSWER_BUDGET_S", "40"))        # non-streamed answer
FIRST_TOKEN_BUDGET_S = float(os.getenv("FIRST_TOKEN_BUDGET_S", "30"))  # streamed answer must start by then
MODEL_FIRST_TOKEN_S = float(os.getenv("MODEL_FIRST_TOKEN_S", "8"))    # ...and each model gets this long to start

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "6"))
PRECEDENT_K = int(os.getenv("RETRIEVAL_PRECEDENT_K", "2"))
# chars of each passage sent to the model (the best-matching window)
PASSAGE_CHARS = int(os.getenv("PASSAGE_CHARS", "700"))
ANSWER_CACHE_SIZE = int(os.getenv("ANSWER_CACHE_SIZE", "512"))
