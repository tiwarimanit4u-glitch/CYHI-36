import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """Doc-Scout: AI‑augmented documentation drift detection."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
def scan(path):
    """Scan PATH for public symbols and compare with docs."""
    console.print(f"[bold]Scanning[/] {path} ...")
    # TODO: implement symbol extraction and LLM comparison
    console.print("[green]Scan complete (placeholder).[/]")

@cli.command()
def watch():
    """Watch for changes and run scan periodically."""
    console.print("[yellow]Watch mode not implemented yet.[/]")

@cli.command()
@click.argument('patch_file', type=click.Path(exists=True))
def apply(patch_file):
    """Apply a generated patch file."""
    console.print(f"[blue]Applying patch[/] {patch_file} (placeholder).")

if __name__ == '__main__':
    cli()
