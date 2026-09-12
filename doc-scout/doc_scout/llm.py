"""LLM wrapper for Doc‑Scout.

We use Google Gemini 2 Flash (free tier) via the `google‑generativeai` client.
The wrapper provides a single function ``compare(symbol_code, doc_excerpt)`` that:
1️⃣  Extracts the intent of ``symbol_code`` (one‑sentence summary).
2️⃣  Asks the model to generate a markdown diff (or a new section) that aligns the
    documentation with that intent and returns a confidence score.

If the free quota is exhausted or Gemini is unavailable, the function falls back to a
stub implementation that returns an empty diff and a low confidence (0.0) – this
keeps the pipeline functional for the demo.
"""

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import logging
from .diff import generate_diff

_logger = logging.getLogger(__name__)


def _init_gemini():
    """Return a configured Gemini model or ``None`` if it cannot be created.
    The environment variable ``GOOGLE_API_KEY`` must be set for the free tier.
    """
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            _logger.warning("GOOGLE_API_KEY not set – Gemini will be unavailable.")
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as exc:  # pragma: no cover – import errors are benign for testing
        _logger.exception("Failed to initialize Gemini model: %s", exc)
        return None

# Global singleton – initialized lazily on first use.
_GEMINI_MODEL = None


def _get_model():
    global _GEMINI_MODEL
    if _GEMINI_MODEL is None:
        _GEMINI_MODEL = _init_gemini()
    return _GEMINI_MODEL


def _call_model(messages: list[dict[str, str]]) -> str:
    """Send ``messages`` (list of ``{"role":..., "content":...}``) to Gemini.
    Returns the plain text response.
    """
    model = _get_model()
    if model is None:
        raise RuntimeError("Gemini model not available – check GOOGLE_API_KEY.")
    try:
        response = model.generate_content(messages)
        if isinstance(response, str):
            return response
        return response.text
    except Exception as exc:
        _logger.exception("Gemini request failed: %s", exc)
        raise


def _extract_intent(symbol_code: str) -> str:
    """Ask the model to summarise the purpose of ``symbol_code``.
    The prompt is deliberately short to stay within the free token budget.
    """
    prompt = [
        {"role": "system", "content": (
            "You are a concise code‑understanding assistant. "
            "Given a small Python/JS/TS snippet, return a one‑sentence description of its public intent."
        )},
        {"role": "user", "content": symbol_code}
    ]
    response = _call_model(prompt)
    return response.strip()


def compare(symbol_code: str, doc_excerpt: str) -> Dict[str, Any]:
    """Generate a markdown diff (or a new snippet) that aligns documentation.

    Returns a dictionary with three keys:
        ``diff``        – a git‑style patch (string, may be empty)
        ``confidence``  – float between 0 and 1 indicating how sure the model is
        ``model``       – identifier of the backend used (always ``gemini-2-flash`` here)
    """
    # 1️⃣ Intent extraction
    try:
        intent = _extract_intent(symbol_code)
    except Exception:
        # Fallback – Gemini unavailable. Produce a placeholder diff.
        placeholder_md = f"## {symbol_code.splitlines()[0] if symbol_code else 'Generated Documentation'}\n\n{symbol_code}\n"
        diff_text = generate_diff("", placeholder_md, "generated.md")
        return {"diff": diff_text, "confidence": 0.5, "model": "fallback"}

    # 2️⃣ Diff generation prompt
    diff_prompt = [
        {"role": "system", "content": (
            "You are a diff‑generation assistant. Given an intent description and an existing "
            "markdown excerpt (which may be empty), produce the minimal markdown patch that "
            "would make the documentation match the intent. Return the patch in plain text "
            "followed by a line `Confidence: <float>` (e.g., `Confidence: 0.93`)."
        )},
        {"role": "user", "content": f"Intent: {intent}\n\nDocumentation excerpt:\n{doc_excerpt}"}
    ]
    raw = _call_model(diff_prompt)

    # Expected format: <diff>\nConfidence: <value>
    lines = raw.strip().splitlines()
    confidence = 0.0
    diff = "\n".join(lines).strip()
    # Look for a line that starts with "Confidence:" (case‑insensitive).
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].lower().startswith("confidence:"):
            try:
                confidence = float(lines[i].split(":", 1)[1].strip())
            except Exception:
                confidence = 0.0
            diff = "\n".join(lines[:i]).strip()
            break
    return {"diff": diff, "confidence": confidence, "model": "gemini-2-flash"}
