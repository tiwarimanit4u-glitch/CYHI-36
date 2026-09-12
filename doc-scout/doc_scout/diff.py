import difflib
from typing import List

def generate_diff(original: str, new: str, filename: str) -> str:
    """Return a unified diff (git‑style) between ``original`` and ``new``.

    ``original`` and ``new`` are strings containing the full markdown content.
    ``filename`` is used for the diff header lines.
    The function returns the diff as a single string – empty if the files are identical.
    """
    original_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm="",
    )
    return "\n".join(diff)
