"""Find directories that have input-trident.txt but no output or not-found marker."""

import os
import sys


def find_orphan_trident(dir_path: str) -> list[str]:
    """Return paths that have input-trident.txt but no output-*.overpassql or not-found.txt."""
    results: list[str] = []
    for root, dirs, files in os.walk(dir_path):
        if (
            "input-trident.txt" in files
            and "not-found.txt" not in files
            and not any(f.startswith("output-") and f.endswith(".overpassql") for f in files)
        ):
            results.append(root)
    return results


if __name__ == "__main__":
    dir_path: str = sys.argv[1]
    for path in find_orphan_trident(dir_path):
        print(path)
