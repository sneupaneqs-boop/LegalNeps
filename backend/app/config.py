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
# Model chains per tier as "provider/model". With a gateway (OPENAI_BASE_URL,
# e.g. OmniRoute) the whole ID goes to the gateway. Without one, each entry is
# called directly on that provider's OpenAI-compatible API using the keys
# below (several keys per provider rotate, multiplying free-tier quota);
# entries whose provider has no key are skipped. Strongest-that-has-quota
# first; rate-limited model/key pairs are skipped instantly and cooled down.
OPENAI_MODELS = _list("OPENAI_MODELS",
                      "groq/openai/gpt-oss-120b,gemini/gemini-3.8-flash,gemini/gemini-3.6-flash,"
                      "gemini/gemini-3-flash-preview,groq/qwen/qwen3.8-27b,gemini/gemini-3.7-flash,"
                      "gemini/gemini-3.5-flash,cohere/command-a-plus-05-2026,mistral/mistral-medium-latest,"
                      "openrouter/z-ai/glm-5.2:free,openrouter/google/gemma-4-31b-it:free,"
                      "cohere/command-a-03-2025,gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite,auto/chat")
# Query analysis runs on different providers than the answer where possible
# (Groq's per-minute token limit is shared by both otherwise). Measured on 40
# eval questions: gemini-3.5-flash-lite MRR 0.88 at 1.2s median, 3.1-flash-lite
# hit@8 0.98; OpenRouter free models are often rate-limited upstream.
OPENAI_FAST_MODELS = _list("OPENAI_FAST_MODELS",
                           "gemini/gemini-3.5-flash-lite,gemini/gemini-3.1-flash-lite,groq/openai/gpt-oss-120b,"
                           "gemini/gemini-flash-lite-latest,cohere/command-a-03-2025,groq/qwen/qwen3.8-27b,"
                           "groq/openai/gpt-oss-20b,mistral/mistral-small-latest,"
                           "openrouter/qwen/qwen3.8-27b:free,auto/fast")


def _keys(*names: str) -> list[str]:
    """All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or GROQ_API_KEY=k)."""
    out: list[str] = []
    for n in names:
        out += [k.strip() for k in os.getenv(n, "").split(",") if k.strip() and k.strip() not in out]
    return out


# Direct providers (OpenAI-compatible endpoints) used when no gateway is set.
DIRECT_PROVIDERS = {
    name: (base, keys) for name, base, keys in (
        ("groq", "https://api.groq.com/openai/v1", _keys("GROQ_API_KEYS", "GROQ_API_KEY")),
        ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai",
         _keys("GEMINI_API_KEYS", "GEMINI_API_KEY")),
        ("openrouter", "https://openrouter.ai/api/v1", _keys("OPENROUTER_API_KEYS", "OPENROUTER_API_KEY")),
        ("cohere", "https://api.cohere.ai/compatibility/v1", _keys("COHERE_API_KEYS", "COHERE_API_KEY")),
        ("mistral", "https://api.mistral.ai/v1", _keys("MISTRAL_API_KEYS", "MISTRAL_API_KEY")),
        ("cerebras", "https://api.cerebras.ai/v1", _keys("CEREBRAS_API_KEYS", "CEREBRAS_API_KEY")),
    ) if keys
}
if not GEMINI_API_KEY and "gemini" in DIRECT_PROVIDERS:
    GEMINI_API_KEY = DIRECT_PROVIDERS["gemini"][1][0]
if not GROQ_API_KEY and "groq" in DIRECT_PROVIDERS:
    GROQ_API_KEY = DIRECT_PROVIDERS["groq"][1][0]

# Hard time budgets (seconds) so a slow/rate-limited provider can't hang the UI.
LLM_TIMEOUT_S = int(os.getenv("LLM_TIMEOUT_S", "60"))            # whole streamed answer
LLM_CALL_TIMEOUT_S = float(os.getenv("LLM_CALL_TIMEOUT_S", "20"))  # one attempt on one model
ANALYZE_BUDGET_S = float(os.getenv("ANALYZE_BUDGET_S", "8"))       # question understanding
ANSWER_BUDGET_S = float(os.getenv("ANSWER_BUDGET_S", "40"))        # non-streamed answer
FIRST_TOKEN_BUDGET_S = float(os.getenv("FIRST_TOKEN_BUDGET_S", "30"))  # streamed answer must start by then
MODEL_FIRST_TOKEN_S = float(os.getenv("MODEL_FIRST_TOKEN_S", "8"))    # ...and each model gets this long to start

# V3: the answer is one JSON object (generate, then verify), so it is not streamed from the model.
# Devanagari costs ~3x the tokens of English and JSON adds keys/quotes; a cut-off object is salvaged
# sentence by sentence, never shown half-written.
ANSWER_MAX_TOKENS_EN = int(os.getenv("ANSWER_MAX_TOKENS_EN", "3200"))
ANSWER_MAX_TOKENS_NE = int(os.getenv("ANSWER_MAX_TOKENS_NE", "6000"))
ANSWER_JSON_BUDGET_S = float(os.getenv("ANSWER_JSON_BUDGET_S", "50"))       # whole structured generation
ANSWER_JSON_CALL_TIMEOUT_S = float(os.getenv("ANSWER_JSON_CALL_TIMEOUT_S", "35"))  # one attempt on one model
# Optional LLM entailment pass over the surviving rule sentences (off on the free tier: quota); paid tiers always run it.
ENTAILMENT_CHECK = os.getenv("ENTAILMENT_CHECK", "0").lower() in ("1", "true", "yes")
# Progressive streaming of the model's JSON with per-sentence verification (V3.1). STREAM_VERIFIED=0 restores the
# single non-streamed call. Nothing is shown until STREAM_MIN_RULES rule/deadline/penalty sentences verified
# (2 = the document-level minimum, so the extractive fallback almost never replaces already-shown text).
STREAM_VERIFIED = os.getenv("STREAM_VERIFIED", "1").lower() in ("1", "true", "yes")
STREAM_MIN_RULES = int(os.getenv("STREAM_MIN_RULES", "2"))
STREAM_JSON_FIRST_TOKEN_S = float(os.getenv("STREAM_JSON_FIRST_TOKEN_S", "15"))  # then the non-streamed fallback
# Simulated streaming of the verified answer (seconds between ~40-char chunks; capped per answer)
STREAM_CHUNK_DELAY_S = float(os.getenv("STREAM_CHUNK_DELAY_S", "0.01"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
# Vercel production + preview URLs of the frontend project
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"https://kanooni-sathi(-[a-z0-9-]+)?\.vercel\.app")
TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "6"))
PRECEDENT_K = int(os.getenv("RETRIEVAL_PRECEDENT_K", "2"))
# chars of each passage sent to the model (the best-matching window)
PASSAGE_CHARS = int(os.getenv("PASSAGE_CHARS", "700"))
ANSWER_CACHE_SIZE = int(os.getenv("ANSWER_CACHE_SIZE", "512"))

# S5: Supabase (auth + user data - the legal corpus itself stays file-based).
# SUPABASE_SERVICE_ROLE_KEY bypasses RLS - used only server-side for cache/
# quota writes and for validating a user's own token; never sent to the
# frontend (which uses its own anon key directly, set as a separate env var
# in Vercel, not read by this backend at all).
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
DAILY_QUOTA_FREE = int(os.getenv("DAILY_QUOTA_FREE", "50"))  # answers/day for a logged-in free user
IP_RATE_LIMIT_PER_HOUR = int(os.getenv("IP_RATE_LIMIT_PER_HOUR", "30"))  # per IP, anonymous or not

# S12: Compliance Radar reminder emails (Resend free tier - 100 emails/day,
# 3000/month, no card required). Unset in dev/test: the reminder job then
# fails open (logs and skips sending) same as every other optional integration.
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "Kanooni Sathi <reminders@kanoonisathi.com>")
COMPLIANCE_REMINDER_DAYS_AHEAD = int(os.getenv("COMPLIANCE_REMINDER_DAYS_AHEAD", "7"))

# S13: AI gateway v2 - plan-based tier routing (STRATEGY.md §2: free chain for
# free users, Haiku 4.5 for paid structured answers, Sonnet 5.5 only for paid
# drafting/contract review). Model IDs and $/1M-token pricing per Anthropic's
# first-party rates (checked 2026-09-25) - update MODEL_PRICING_PER_1M if
# either model's price changes, so cost-per-query stays accurate rather than
# silently stale.
PAID_HAIKU_MODEL = os.getenv("PAID_HAIKU_MODEL", "claude-haiku-4-5")
PAID_SONNET_MODEL = os.getenv("PAID_SONNET_MODEL", "claude-sonnet-5-5")
MODEL_PRICING_PER_1M = {
    PAID_HAIKU_MODEL: {"input": 1.00, "output": 5.00},
    PAID_SONNET_MODEL: {"input": 2.00, "output": 10.00},
}
# Per-plan daily answer quotas (STRATEGY.md §5 pricing table). DAILY_QUOTA_FREE
# above already existed pre-S13 (default 50) for the only plan that existed
# then; STRATEGY's own pricing table specifies 5/day for the free plan, but
# this code doesn't silently override whatever value is already configured
# in production - see docs/PROGRESS.md's S13 entry.
DAILY_QUOTA_INDIVIDUAL = int(os.getenv("DAILY_QUOTA_INDIVIDUAL", "40"))
DAILY_QUOTA_PROFESSIONAL = int(os.getenv("DAILY_QUOTA_PROFESSIONAL", "200"))
DAILY_QUOTA_FIRM = int(os.getenv("DAILY_QUOTA_FIRM", "200"))
