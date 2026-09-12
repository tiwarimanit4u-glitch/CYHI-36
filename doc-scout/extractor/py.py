import ast
from pathlib import Path

def _signature(node: ast.FunctionDef) -> str:
    """Return a simple signature string ``name(arg1, arg2, ...)``.
    It ignores defaults, *args, **kwargs for simplicity.
    """
    args = [arg.arg for arg in node.args.args]
    return f"{node.name}({', '.join(args)})"

def extract_symbols(file_path: str):
    """Extract public functions and classes from a Python source file.

    Returns a list of dictionaries with the shape:
    {
        "name": <symbol name>,
        "type": "function" | "class",
        "signature": <human‑readable signature>,
        "location": "<file_path>:<lineno>"
    }
    Private members (those starting with an underscore) are ignored.
    """
    try:
        source = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path)
    except Exception:
        # If parsing fails we simply return an empty list – the caller can decide what to do.
        return []

    symbols = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("_"):
                continue
            symbols.append({
                "name": node.name,
                "type": "function",
                "signature": _signature(node),
                "location": f"{file_path}:{node.lineno}"
            })
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            symbols.append({
                "name": node.name,
                "type": "class",
                "signature": node.name,
                "location": f"{file_path}:{node.lineno}"
            })
    return symbols
