import argparse
import json
import sys
from typing import Sequence

from .agent import build_literature_summary, export_papers, import_papers, list_papers, store_papers
from .springer import SpringerClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research assistant for scholarly paper discovery")
    parser.add_argument("query", help="Search query for papers")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--api-key", default=None, help="Springer API key")
    parser.add_argument("--db-path", default="papers.db", help="Path to the local SQLite database")
    parser.add_argument("--summary", action="store_true", help="Generate a literature review summary")
    parser.add_argument(
        "--export",
        nargs="?",
        const="papers_export.json",
        default=None,
        help="Export the database contents to a JSON file; defaults to papers_export.json",
    )
    parser.add_argument(
        "--import-from",
        nargs="?",
        const="papers_import.json",
        default=None,
        help="Import papers from a JSON file into the database; defaults to papers_import.json",
    )
    parser.add_argument("--list", action="store_true", help="List stored papers from the database")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.list:
            papers = list_papers(args.db_path)
            print(json.dumps(papers, indent=2))
            return 0

        if args.import_from is not None:
            import_path = args.import_from if args.import_from != "papers_import.json" else "papers_import.json"
            import_papers(args.db_path, import_path, query=args.query)
            print(f"Imported papers from {import_path} into {args.db_path}")
            return 0

        client = SpringerClient(api_key=args.api_key)
        papers = client.search(args.query, max_results=args.max_results)
        store_papers(args.db_path, papers, query=args.query)

        if args.export:
            export_papers(args.db_path, args.export)
            print(f"Exported papers to {args.export}")

        if args.summary:
            print(build_literature_summary(papers, query=args.query))
        else:
            print(json.dumps(papers, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
