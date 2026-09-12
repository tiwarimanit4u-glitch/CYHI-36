import click
import os
from pathlib import Path
from rich.console import Console
from . import extractor
from . import doc_parser
from . import llm
from . import diff
from . import reviewer
import subprocess
# Resolve the path to the `cyhi` CLI script regardless of the current working directory.
CYHI_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cyhi-logs", "bin", "cyhi"))


console = Console()

@click.group()
def cli():
    """Doc-Scout: AI‑augmented documentation drift detection."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
@click.option('--ci', is_flag=True, default=False, help='Exit with non‑zero status if any high‑confidence drift is found (for CI).')
def scan(path, ci):
    """Scan PATH for public symbols and compare with docs."""
    console.print(f"[bold]Scanning[/] {path} ...")
    # Walk the directory tree and collect symbols from supported files
    all_symbols = []
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname.endswith(('.py', '.js', '.ts')):
                full_path = os.path.join(root, fname)
                symbols = extractor.extract_symbols(full_path)
                all_symbols.extend(symbols)
    console.print(f"[green]Found {len(all_symbols)} public symbols (placeholder).[/]")
    # Simple doc lookup – just show whether a symbol has a matching heading
    docs = doc_parser.parse_docs(path)
    matched = sum(1 for sym in all_symbols if sym["name"] in docs)
    console.print(f"[blue]Documentation coverage:[/] {matched}/{len(all_symbols)} symbols have a heading in the markdown docs.")

    # Process symbols without documentation
    for sym in all_symbols:
        name = sym["name"]
        if name in docs:
            continue  # already documented
        console.print(f"[magenta]Generating doc for missing symbol:[/] {name}")
        # Use the LLM to produce a diff (or a new markdown snippet)
        llm_res = llm.compare(sym["signature"], "")
        diff_text = llm_res.get("diff", "")
        confidence = llm_res.get("confidence", 0.0)
        if not diff_text:
            console.print(f"[yellow]LLM returned empty diff for {name} (confidence {confidence:.2f})[/]")
            continue
        console.print(f"[cyan]Confidence:[/] {confidence:.2f}")
        # Let the user review the diff before applying
        if reviewer.review_diff(diff_text):
            target_path = os.path.join(path, f"{name}.md")
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(diff_text)
            console.print(f"[green]Created documentation file:[/] {target_path}")
            # Stage and commit the change (optional – only if repo uses git)
            try:
                subprocess.run(["git", "add", target_path], check=True)
                subprocess.run(["git", "commit", "-m", f"doc‑scout: add docs for {name}"], check=True)
                console.print(f"[green]Committed {target_path} to git.[/]")
                # Log action via cyhi
                subprocess.run([
                    CYHI_BIN, "log",
                    "--type", "code",
                    "--summary", f"Generated docs for {name}",
                    "--files", target_path
                ], check=False)
            except Exception as exc:
                console.print(f"[red]Git commit failed:[/] {exc}")
        # CI handling – after processing all symbols
        if ci:
            # Determine if any generated diff had confidence >= 0.8 for symbols without docs.
            high_conf = any(
                llm.compare(sym["signature"], "").get("confidence", 0.0) >= 0.8
                for sym in all_symbols if sym["name"] not in docs
            )
            if high_conf:
                console.print("[red]High‑confidence documentation drift detected – failing CI.[/]")
                import sys
                sys.exit(1)
            else:
                console.print("[green]No high‑confidence drift detected – CI passes.[/]")
    # Update handoff snapshot after scan
    subprocess.run([CYHI_BIN, "hand-off"], check=False)



@cli.command()
def watch():
    """Watch for changes and run scan periodically."""
    try:
        from .watch import watch as _watch
    except Exception:
        console.print("[red]Watch module not available.[/]")
        return
    # Default interval 300 seconds (5 min); can be overridden via env var.
    interval = int(os.getenv("DOCSCOUT_WATCH_INTERVAL", "300"))
    console.print(f"[yellow]Starting watch mode – scanning every {interval}s[/]")
    _watch(path='.', interval=interval)


@cli.command()
@click.argument('patch_file', type=click.Path(exists=True))
def apply(patch_file):
    """Apply a generated patch file."""
    console.print(f"[blue]Applying patch[/] {patch_file} (placeholder).")

if __name__ == '__main__':
    cli()
