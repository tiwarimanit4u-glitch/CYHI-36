import time
import os
from pathlib import Path
from . import extractor
from . import doc_parser
from . import llm
from . import diff
from . import reviewer
from rich.console import Console

console = Console()

def watch(path: str, interval: int = 300, slack_webhook: str | None = None) -> None:
    """Continuously watch ``path`` for documentation drift.

    Every ``interval`` seconds the repository is rescanned. If any symbol lacks
    documentation, we generate an LLM‑driven diff and, when the confidence is
    high (≥ 0.8), print it and optionally post it to a Slack webhook.
    """
    while True:
        console.print(f"[bold cyan]Scanning {path}…[/]")
        # Collect symbols across supported files
        symbols = []
        for root, _, files in os.walk(path):
            for fname in files:
                if fname.endswith(('.py', '.js', '.ts')):
                    full = os.path.join(root, fname)
                    symbols.extend(extractor.extract_symbols(full))
        docs = doc_parser.parse_docs(path)
        for sym in symbols:
            name = sym["name"]
            if name in docs:
                continue  # already documented
            # Use the symbol signature as the new markdown content
            new_md = f"## {name}\n\n{sym['signature']}\n"
            old_md = ""
            patch = diff.generate_diff(old_md, new_md, f"{name}.md")
            if not patch:
                continue
            # Ask the LLM for a confidence score
            llm_res = llm.compare(sym['signature'], "")
            conf = llm_res.get("confidence", 0.0)
            if conf >= 0.8:
                console.print(f"[red]High‑confidence suggestion for {name} (confidence {conf:.2f})[/]")
                console.print(patch)
                if slack_webhook:
                    try:
                        import requests
                        payload = {"text": f"Doc‑Scout found drift for *{name}* (confidence {conf:.2f})\n```diff\n{patch}\n```"}
                        requests.post(slack_webhook, json=payload)
                    except Exception as exc:
                        console.print(f"[yellow]Failed to post to Slack: {exc}[/]")
        console.print(f"[green]Watch cycle complete – sleeping {interval}s[/]")
        time.sleep(interval)
