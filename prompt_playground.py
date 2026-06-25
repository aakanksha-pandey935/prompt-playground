"""
Prompt Playground — loads templates from prompt-templates.md,
fills placeholders interactively, calls Claude, and logs every run.
"""

import json
import re
import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic

TEMPLATES_FILE = Path(__file__).parent / "prompt-templates.md"
RUNS_LOG = Path(__file__).parent / "runs.jsonl"
MODEL = "claude-opus-4-8"


def parse_templates(path: Path) -> dict[str, str]:
    """Extract named templates from the markdown file.

    Looks for code blocks immediately after an '## N. Name' heading,
    skipping the 'Example' blocks (which follow '**Example:**').
    """
    text = path.read_text(encoding="utf-8")
    templates: dict[str, str] = {}

    # Split on top-level section headings (## 1. Role, ## 2. Few-Shot …)
    sections = re.split(r"(?m)^## \d+\.\s+", text)

    for section in sections[1:]:  # skip preamble
        first_line, _, body = section.partition("\n")
        name = first_line.strip()

        # Find the first fenced code block that is NOT preceded by "**Example"
        # Strategy: split on ```  pairs and take the first one whose preceding
        # text does not contain "**Example"
        parts = re.split(r"```(?:\w*\n?)", body)
        # parts alternates: [before_block, block_content, between, block_content, …]
        chosen = None
        for i, part in enumerate(parts):
            if i % 2 == 1:  # odd indices are inside a fenced block
                preceding = parts[i - 1]
                if "**Example" not in preceding:
                    chosen = part.rstrip("\n")
                    break

        if chosen:
            templates[name] = chosen

    return templates


def find_placeholders(template: str) -> list[str]:
    """Return all unique {{placeholder}} names, preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for ph in re.findall(r"\{\{(\w+)\}\}", template):
        if ph not in seen:
            seen.add(ph)
            result.append(ph)
    return result


def fill_template(template: str, values: dict[str, str]) -> str:
    for key, val in values.items():
        template = template.replace("{{" + key + "}}", val)
    return template


def call_claude(prompt: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(
        (block.text for block in response.content if block.type == "text"), ""
    )


def log_run(template_name: str, filled_prompt: str, response: str) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "template": template_name,
        "prompt": filled_prompt,
        "response": response,
        "model": MODEL,
    }
    with RUNS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def pick_template(templates: dict[str, str]) -> tuple[str, str]:
    names = list(templates.keys())
    print("\nAvailable templates:")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    print()

    while True:
        raw = input("Pick a template (number or name): ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(names):
                name = names[idx]
                return name, templates[name]
            print(f"  Enter a number between 1 and {len(names)}.")
        else:
            # fuzzy name match
            matches = [n for n in names if raw.lower() in n.lower()]
            if len(matches) == 1:
                return matches[0], templates[matches[0]]
            elif len(matches) > 1:
                print(f"  Ambiguous — matches: {matches}")
            else:
                print("  No match found.")


def main() -> None:
    if not TEMPLATES_FILE.exists():
        print(f"Template file not found: {TEMPLATES_FILE}")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY before running.")
        return

    templates = parse_templates(TEMPLATES_FILE)
    if not templates:
        print("No templates parsed — check prompt-templates.md format.")
        return

    print("=== Prompt Playground ===")

    while True:
        template_name, template_body = pick_template(templates)
        print(f"\n--- Template: {template_name} ---")
        print(template_body)

        placeholders = find_placeholders(template_body)
        values: dict[str, str] = {}

        if placeholders:
            print(f"\nFill in {len(placeholders)} placeholder(s):")
            for ph in placeholders:
                val = input(f"  {{{{ {ph} }}}}: ").strip()
                values[ph] = val

        filled = fill_template(template_body, values)

        print("\n--- Filled prompt ---")
        print(filled)
        print("\nSending to Claude...\n")

        response = call_claude(filled)
        print("--- Response ---")
        print(response)

        log_run(template_name, filled, response)
        print(f"\n(Run logged to {RUNS_LOG.name})")

        again = input("\nTry another template? [y/N]: ").strip().lower()
        if again != "y":
            break

    print("Done.")


if __name__ == "__main__":
    main()
