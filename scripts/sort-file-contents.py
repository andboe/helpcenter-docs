#!/usr/bin/env python3
"""Alphabetize the lines of a file in place."""

import argparse
from pathlib import Path
from typing import Iterable, Tuple


def sort_key(line: str) -> Tuple[str, str]:
    stripped = line.strip()
    if stripped.startswith(":") and ":" in stripped[1:]:
        attribute = stripped[1:].split(":", 1)[0]
        return (attribute.casefold(), line.casefold())
    return (line.casefold(), line.casefold())


def sort_file(path: Path, dry_run: bool = False) -> bool:
    """Return True if file contents changed."""
    text = path.read_text()
    lines = text.splitlines()
    sorted_lines = sorted(lines, key=sort_key)
    if lines == sorted_lines:
        return False
    suffix = "\n" if text.endswith("\n") or not lines else ""
    if dry_run:
        return True
    path.write_text("\n".join(sorted_lines) + suffix)
    return True


def run(paths: Iterable[Path], dry_run: bool) -> None:
    for file_path in paths:
        file_path = file_path.resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")
        updated = sort_file(file_path, dry_run=dry_run)
        status = "would update" if dry_run else "updated"
        if updated:
            print(f"{status}: {file_path}")
        else:
            print(f"already sorted: {file_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Alphabetize lines in one or more files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Files whose lines should be sorted alphabetically.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which files would change without rewriting them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.files, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
