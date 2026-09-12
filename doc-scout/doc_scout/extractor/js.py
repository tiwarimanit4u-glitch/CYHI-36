import re
from pathlib import Path

# Regular expressions to capture exported symbols.
EXPORT_FUNC_RE = re.compile(r'export\s+function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)', re.MULTILINE)
EXPORT_CONST_FUN_RE = re.compile(r'export\s+const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\(?([^=]*?)\)?\s*=>', re.MULTILINE)
EXPORT_CLASS_RE = re.compile(r'export\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', re.MULTILINE)

def extract_symbols(file_path: str):
    """Extract exported symbols from a JavaScript/TypeScript file.

    Returns a list of dicts with the same schema as the Python extractor:
    ``{"name": ..., "type": ..., "signature": ..., "location": ...}``.
    """
    try:
        source = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return []
    symbols = []
    # Exported functions: `export function foo(a, b) {}`
    for match in EXPORT_FUNC_RE.finditer(source):
        name, params = match.group(1), match.group(2).strip()
        signature = f"{name}({params})"
        line = source[:match.start()].count("\n") + 1
        symbols.append({
            "name": name,
            "type": "function",
            "signature": signature,
            "location": f"{file_path}:{line}"
        })
    # Exported const arrow functions: `export const foo = (a, b) => {}`
    for match in EXPORT_CONST_FUN_RE.finditer(source):
        name, params = match.group(1), match.group(2).strip()
        signature = f"{name}({params})"
        line = source[:match.start()].count("\n") + 1
        symbols.append({
            "name": name,
            "type": "function",
            "signature": signature,
            "location": f"{file_path}:{line}"
        })
    # Exported classes: `export class Foo {}`
    for match in EXPORT_CLASS_RE.finditer(source):
        name = match.group(1)
        line = source[:match.start()].count("\n") + 1
        symbols.append({
            "name": name,
            "type": "class",
            "signature": name,
            "location": f"{file_path}:{line}"
        })
    return symbols
