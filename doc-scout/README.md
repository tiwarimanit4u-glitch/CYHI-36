# Doc‑Scout

AI‑augmented CLI tool that detects documentation drift by extracting public symbols from code and comparing them against markdown documentation using an LLM.

## Install

```bash
# Assuming you have Python 3 and pip
pip install doc-scout-cli  # placeholder for future packaging
```

## Usage

```bash
# Scan a repository
./doc-scout-cli scan /path/to/repo

# Watch mode (not yet implemented)
./doc-scout-cli watch

# Apply a generated patch
./doc-scout-cli apply change.patch
```

## Development

Run the project directly:
```bash
python -m doc_scout.cli scan .
```

## License

MIT
