#!/usr/bin/env python3
"""Merge the latest origin/main into the current branch."""

import argparse
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        check=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch origin and merge origin/main into a branch."
    )
    parser.add_argument(
        "branch",
        nargs="?",
        help="branch to check out before merging (defaults to the current branch)",
    )
    args = parser.parse_args()

    try:
        if args.branch:
            run_git("checkout", args.branch)
        run_git("fetch", "origin")
        run_git("merge", "origin/main")
    except subprocess.CalledProcessError as error:
        return error.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
