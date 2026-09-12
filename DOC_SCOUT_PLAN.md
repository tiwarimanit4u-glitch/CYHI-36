# Doc‑Scout Implementation Plan (19‑hour Hackathon)

## Overview
Doc‑Scout is an AI‑augmented command‑line tool that automatically detects documentation drift in a codebase. It extracts public symbols (functions, classes, CLI commands, API routes) across multiple languages, compares them with existing markdown documentation, and generates precise markdown diff patches. The tool can be run as a one‑shot scanner, an interactive reviewer, or a lightweight watcher that posts alerts or opens a PR when drift exceeds a confidence threshold. This condensed plan fits into a 19‑hour hackathon, targeting the **CLI Tools** track.

## Why Use an LLM Instead of a Pure Diff?
- **Semantic understanding** – The LLM infers the purpose of a symbol and checks whether the documentation still matches that intent, something a plain line‑by‑line diff cannot do.
- **Missing documentation** – When a new public API has no entry, the LLM can synthesize a sensible markdown block from the code itself.
- **Cross‑language flexibility** – By feeding a normalized JSON schema to the LLM, the same prompt works for JavaScript, Python, Go, etc., without writing language‑specific diff logic.
- **Confidence scoring** – The LLM returns a confidence level for each suggested change, allowing us to gate automatic PR creation or ask the user for confirmation only when the score is high.
- **Style‑aware output** – A short style guide embedded in the prompt ensures generated markdown follows the project’s conventions.

## High‑Level Architecture
- **CLI Front‑End** (`click` for Python) – parses sub‑commands (`scan`, `watch`, `apply`).
- **Language Extractors** – small modules that parse source files and emit a normalized list of public symbols:
  - JavaScript/TypeScript → `@babel/parser`
  - Python → built‑in `ast`
  - (Go support deferred to post‑hackathon)
- **Documentation Parser** – reads all `*.md` files, extracts headings and code‑block annotations to build a map of documented symbols.
- **LLM Prompt Engine** – wraps the Claude SDK (or OpenAI) with a two‑step prompt:
  1. *Extract intent* – “Given this symbol definition … what is its purpose?”
  2. *Diff request* – “Compare the extracted intent with this markdown excerpt and produce a minimal markdown diff.”
- **Diff Generator** – uses `difflib` (Python) to format the LLM‑produced changes as a git‑style patch.
- **Interactive Reviewer** – colour‑coded UI that lets the user accept, reject, or edit the patch before committing.
- **Automation Layer (optional)** – a lightweight `watch` mode that runs every few minutes, posts a Slack summary, and can auto‑create a PR via `gh pr create`.
- **CI Integration** – a minimal GitHub Action (`doc-scout.yml`) runs `doc-scout scan --ci` on each push and fails the build if drift confidence > 80 %.
- **Packaging** – publish as a single‑file binary (`pyinstaller`) installable with `pipx install doc-scout`.

## Development Steps (ordered)
0. **Initialize Hackathon Logging** (0‑0.5 h)
   - Run `cyhi-logs/bin/cyhi auto-init --team "<TEAM>" --track 4` to create `cyhi-logs/` and install hooks.
   - Verify `.claude/settings.json` contains the `UserPromptSubmit` hook for automatic prompt capture.
   - After each Claude interaction, log the action with `cyhi-logs/bin/cyhi log --type <type> --summary "<desc>" --files <files>`.
   - Update `HANDOFF.md` roughly every 10 turns using `cyhi-logs/bin/cyhi handoff`.

1. **Bootstrap Project** (0 – 1 h)
   - `poetry new doc-scout`
   - Add `click`, `rich`, and the Claude SDK as dependencies (difflib is built‑in).
2. **CLI Skeleton** (1 – 2 h)
   - Implement `doc-scout scan <path>` (file walk, list symbols).
   - Stub `watch` and `apply` sub‑commands.
3. **Language Extractors** (2 – 5 h)
   - Implement `extractor/js.ts` and `extractor/py.py` (covers the majority of participants).
   - Export a common JSON schema `{name, type, signature, location}`.
4. **Documentation Parser** (5 – 7 h)
   - Walk all `*.md` files, build `symbol → markdown excerpt` map.
   - Support front‑matter tag `@doc‑symbol` for explicit mapping.
5. **LLM Wrapper** (7 – 9 h)
   - Function `compare(symbol, docExcerpt) → {diff, confidence}`.
   - Two‑step prompt template; simple in‑memory cache to avoid duplicate calls.
6. **Diff Generation** (9 – 11 h)
   - Convert LLM output into a git‑style patch.
   - Add `--dry‑run` flag to preview without applying.
7. **Interactive Reviewer** (11 – 13 h)
   - Use `prompt‑toolkit` (Python) for colourised diff.
   - On acceptance: `git apply --check` then `git commit -am "🤖 Fix docs drift"`.
8. **Watch Mode & CI (light)** (13 – 15 h)
   - Implement a minimal `watch` that re‑scans every 5 min and posts to Slack (configurable webhook URL).
   - Create `doc-scout.yml` GitHub Action that runs `doc-scout scan --ci` and fails on confidence > 80 %.
9. **Testing** (15 – 17 h)
   - Unit tests for both extractors using small fixture files.
   - Mock LLM responses to verify diff pipeline.
   - End‑to‑end test on a tiny repo with known drift.
10. **Documentation & Demo** (17 – 18 h)
    - Write concise `README.md` with install command, usage examples, and a 3‑minute demo script.
    - Record a short screencast showing `doc-scout scan`, diff preview, acceptance, and PR creation.
11. **Packaging & Release** (18 – 19 h)
    - Build single‑file binary (`pyinstaller`).
    - Publish to PyPI and tag the repo.

## Timeline (19 h total)
| Hour | Milestone |
|------|-----------|
| 0‑1  | Project bootstrap, CLI skeleton, version‑control set‑up |
| 1‑5  | Language extractors for JS/TS and Python |
| 5‑7  | Documentation parser & symbol‑to‑doc mapping |
| 7‑9  | LLM wrapper + prompt templates, basic caching |
| 9‑11 | Diff generation, `--dry‑run` flag |
|11‑13 | Interactive reviewer UI (coloured diff, accept/reject) |
|13‑15 | Minimal watch mode + Slack webhook stub, CI GitHub Action |
|15‑17 | Unit & integration tests (mock LLM) |
|17‑18 | README, demo script, record screencast |
|18‑19 | Binary build, pip packaging, final commit |

## Risks & Mitigations (shortened)
- **LLM latency / rate limits** – In‑memory caching per symbol; fallback stub for the demo.
- **Parsing complexity** – Focus on JS/TS and Python; Go postponed.
- **False positives** – Confidence threshold ≥ 0.8; `--force` flag for manual override.
- **Time pressure** – Prioritise core scan → diff → apply flow; watch mode and CI are minimal.

## Future Extensions (post‑hackathon)
- Add Go, Rust, Java, C++ extractors.
- Implement a local semantic‑similarity filter before hitting the LLM.
- VS Code extension to run Doc‑Scout on file save.
- Documentation‑coverage metrics.
- Custom prompt templates for different doc styles.

---
*Prepared for a 19‑hour hackathon. Adjust milestones as needed based on team size and familiarity with the language stack.*
