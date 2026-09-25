import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# Unit tests must never call a real LLM.
for key in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY"):
    os.environ[key] = ""
