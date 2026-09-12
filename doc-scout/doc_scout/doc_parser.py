import os
from pathlib import Path

def parse_docs(root_path: str):
    """Parse markdown files under ``root_path`` and return a mapping
    ``symbol_name -> excerpt``. For each top‑level heading (``## <name>``) we
    capture the first non‑empty paragraph that follows it. This is a very
    lightweight heuristic – it works for the simple docs we expect in the
    hackathon demo.
    """
    mapping = {}
    for root, dirs, files in os.walk(root_path):
        for fname in files:
            if not fname.lower().endswith('.md'):
                continue
            full_path = os.path.join(root, fname)
            try:
                text = Path(full_path).read_text(encoding='utf-8')
            except Exception:
                continue
            lines = text.splitlines()
            cur_heading = None
            paragraph = []
            for line in lines:
                if line.startswith('## '):
                    # Save previous heading's paragraph, if any
                    if cur_heading and paragraph:
                        mapping[cur_heading] = '\n'.join(paragraph).strip()
                        paragraph = []
                    cur_heading = line[3:].strip()
                elif line.strip() == '':
                    # Blank line ends current paragraph
                    if paragraph:
                        if cur_heading and cur_heading not in mapping:
                            mapping[cur_heading] = '\n'.join(paragraph).strip()
                        paragraph = []
                else:
                    paragraph.append(line)
            # End‑of‑file capture
            if cur_heading and paragraph and cur_heading not in mapping:
                mapping[cur_heading] = '\n'.join(paragraph).strip()
    return mapping
