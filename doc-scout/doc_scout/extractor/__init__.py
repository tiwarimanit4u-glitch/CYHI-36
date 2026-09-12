"""doc_scout.extractor package.

This module provides a thin wrapper around the top‑level ``extractor``
package. The public API mirrors ``extractor.extract_symbols`` so that
code within the ``doc_scout`` package can import ``extract_symbols``
directly from ``doc_scout.extractor`` without needing to know about the
external dependency.
"""

from __future__ import annotations

import extractor
from typing import Any

__all__: list[str] = ["extract_symbols"]


def extract_symbols(path: str) -> Any:
    """Extract public symbols from *path*.

    This function simply forwards the call to :func:`extractor.extract_symbols`
    provided by the external ``extractor`` package. The return type is whatever
    the upstream function returns – typically a collection describing the
    discovered symbols.

    Args:
        path: The filesystem path (directory or file) to analyze.

    Returns:
        The result of ``extractor.extract_symbols`` for the given *path*.
    """
    return extractor.extract_symbols(path)
