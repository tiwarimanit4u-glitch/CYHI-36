import os
from .py import extract_symbols as extract_python
# Optional JS/TS extractor – fallback if not present.
try:
    from .js import extract_symbols as extract_js_ts
except ImportError:  # pragma: no cover
    def extract_js_ts(_path):  # type: ignore
        """Fallback stub for missing JS/TS extractor."""
        return []

def extract_symbols(path):
    """Dispatch extraction based on file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        return extract_python(path)
    elif ext in (".js", ".ts"):
        return extract_js_ts(path)
    else:
        return []
