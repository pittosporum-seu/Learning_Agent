from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LABS_ROOT = REPO_ROOT / "labs"


def iter_lab_dirs(selected_lab: str | None) -> list[Path]:
    if selected_lab:
        lab_dir = LABS_ROOT / selected_lab
        if not lab_dir.exists():
            raise FileNotFoundError(f"Lab not found: {lab_dir}")
        return [lab_dir]

    return sorted(
        path
        for path in LABS_ROOT.iterdir()
        if path.is_dir() and path.name != "shared" and not path.name.startswith(".")
    )


def discover_lab_suite(lab_dir: Path) -> unittest.TestSuite | None:
    tests_dir = lab_dir / "tests"
    if not tests_dir.exists():
        return None

    loader = unittest.TestLoader()
    return loader.discover(start_dir=str(tests_dir), pattern="test*.py")


def build_suite(selected_lab: str | None) -> tuple[unittest.TestSuite, list[str]]:
    suite = unittest.TestSuite()
    discovered_labs: list[str] = []

    for lab_dir in iter_lab_dirs(selected_lab):
        lab_suite = discover_lab_suite(lab_dir)
        if lab_suite is None:
            continue
        suite.addTests(lab_suite)
        discovered_labs.append(lab_dir.name)

    return suite, discovered_labs


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tests for one lab or all labs.")
    parser.add_argument("--lab", help="Lab directory name, for example 01-strategy-intake.")
    parser.add_argument("--verbose", action="store_true", help="Use verbose unittest output.")
    args = parser.parse_args()

    suite, discovered_labs = build_suite(args.lab)
    if suite.countTestCases() == 0:
        target = args.lab or "all labs"
        print(f"No tests discovered for {target}.", file=sys.stderr)
        return 1

    print(f"Discovered labs: {', '.join(discovered_labs)}")
    print(f"Discovered tests: {suite.countTestCases()}")

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
