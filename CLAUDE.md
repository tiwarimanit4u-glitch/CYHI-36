# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Idea: Doc‑Scout (AI‑CLI for Documentation‑Drift Detection)

Doc‑Scout is an AI‑augmented CLI that scans a repository, extracts public symbols across languages, compares them to markdown documentation, and generates precise diff patches. It can run as a one‑shot command, an interactive reviewer, or a background watcher that posts alerts or opens PRs when drift exceeds a confidence threshold. Targeted at the CLI Tools track.

## Common Commands

| Purpose | Command |
|--------|---------|
| Initialise hackathon logging (creates `cyhi-logs/`, installs hooks) | `cyhi-logs/bin/cyhi auto-init --team "<TEAM>" --track <1‑4>` |
| Show current team/track status | `cyhi-logs/bin/cyhi status` |
| Log an action (after each Claude response) | `cyhi-logs/bin/cyhi log --type <type> --summary "<desc>" --files <file1> [<file2> …]` |
| Record a handoff snapshot (≈ every 10 turns) | `cyhi-logs/bin/cyhi handoff <<'EOF'
## Current state
... 
EOF` |
| Render organiser report | `cyhi-logs/bin/cyhi render` |
| Show or set member ID | `cyhi-logs/bin/cyhi whoami` (or `--set <ID>`) |
| Re‑install hooks (rare) | `cyhi-logs/bin/cyhi install-hooks` |
| Help for any sub‑command | `cyhi-logs/bin/cyhi <cmd> --help` |

> **Always log with `cyhi log` immediately after a Claude Code interaction.**

## High‑Level Architecture

- **`cyhi-logs/` (committed)**
  - `turns/<member>.jsonl` – Append‑only logs of prompts (`kind:"prompt"`) and actions (`kind:"action"`). Includes timestamps, session, turn, track, and payload.
  - `state.json` – Team name, selected track, roster, current session ID.
  - `HANDOFF.md` – Free‑form snapshot updated regularly (progress, issues, next steps, “Don’t retry”).
  - `session.md` – Auto‑generated summary (`cyhi render`).
  - `bin/cyhi` – CLI entry‑point.
  - `.local/` (uncommitted) – Machine‑specific IDs, turn counters.

- **`.claude/settings.json`** – Auto‑populated by `auto‑init`; registers a `UserPromptSubmit` hook that captures every Claude prompt verbatim.

- **`.claude/skills/cyhi-skills.md`** – Describes the hackathon workflow, boot sequence, logging discipline, and handoff expectations.

- **`cyhi-skills/`**
  - `install.md` – Manual install instructions (auto‑init handles it).
  - `tracks.md` – Detailed description of the four tracks and constraints.
  - `SKILL.md` & `assets/` – Templates and supporting files.

- **`Problem_statements.md` & `judging.md`** – Provide the overall brief and judging rubric.

- **No build / test system** – The repo is a hackathon framework, not a compiled project.

## Project‑Specific Rules

1. **Prompt Hook** – Do not disable the `UserPromptSubmit` hook; it is required for auditability.
2. **Action Logging** – Every Claude response must be logged with `cyhi log`. Missing logs invalidate the record.
3. **Hand‑off Updates** – Keep `HANDOFF.md` current; include a “Don’t retry” list.
4. **Append‑Only Logs** – Never edit existing lines in `turns/*.jsonl`; always append.
5. **Merge Strategy** – `.gitattributes` uses `union` for JSONL to avoid conflicts.
6. **Track Constraints** – Refer to `cyhi-skills/tracks.md` for hard limits (e.g., input keys for Track 1, self‑hosted models for Track 3, CLI usability for Track 4).

## Quick‑Start Checklist

1. **First‑time setup** (if `cyhi-logs/` missing):
   ```bash
   cyhi-logs/bin/cyhi auto-init --team "MyTeam" --track 4
   ```
2. Verify hooks in `.claude/settings.json`.
3. After each Claude interaction, log the action, e.g.:
   ```bash
   cyhi-logs/bin/cyhi log --type code --summary "Added commander‑based CLI parsing" --files src/cli.js
   ```
4. Every ~10 turns, update `HANDOFF.md` using the template in the skill description.
5. End of session:
   ```bash
   cyhi-logs/bin/cyhi handoff
   cyhi-logs/bin/cyhi render
   ```

Following this workflow ensures a complete audit log, keeps Claude in sync with the session state, and satisfies the hackathon requirements.
