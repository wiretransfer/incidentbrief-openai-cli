import argparse
import json
import sys
from pathlib import Path

from .schemas import DEFAULT_MODEL, EXAMPLE_TEXT
from .workflow import render_markdown, run_incidentbrief


def read_input(args) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return " ".join(args.text)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide an incident log as arguments, with --file, or through stdin.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn incident logs into response briefs.")
    parser.add_argument("text", nargs="*", help="Incident log or notes to process.")
    parser.add_argument("--file", help="Read incident notes from a UTF-8 text file.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use.")
    parser.add_argument("--example", action="store_true", help="Run against a bundled incident example.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    text = EXAMPLE_TEXT if args.example else read_input(args)
    result = run_incidentbrief(text, model=args.model)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
