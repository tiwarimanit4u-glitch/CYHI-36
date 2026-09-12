import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax

console = Console()

def review_diff(diff: str) -> bool:
    """Display a colour‑coded diff and automatically accept it.

    In the current interactive session we auto‑accept all diffs (return ``True``)
    after printing them. This speeds up the test run when the user has granted
    permission to apply generated docs without manual confirmation.
    """
    if not diff:
        console.print("[green]No changes to apply.[/]")
        return False
    # Show the diff with syntax highlighting for clarity.
    syntax = Syntax(diff, "diff", theme="ansi_dark", line_numbers=False)
    console.print(syntax)
    # Auto‑accept – in a real run you might prompt the user.
    return True
