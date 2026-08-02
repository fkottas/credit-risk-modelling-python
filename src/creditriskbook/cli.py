"""Command-line entry point for the reference workflow."""

from __future__ import annotations

import argparse
import json

from creditriskbook.data.datasets import available_datasets
from creditriskbook.workflows import run_end_to_end, write_run_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the tested credit-risk teaching workflow")
    parser.add_argument("--dataset", choices=available_datasets(), default="synthetic_retail")
    parser.add_argument("--data-path", default=None, help="Local CSV path for a manual dataset adapter")
    parser.add_argument("--cache-dir", default="data/raw")
    parser.add_argument("--rows", type=int, default=5_000, help="Rows for the synthetic dataset")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-defects", action="store_true")
    parser.add_argument("--output", default="artifacts/demo/run_manifest.json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_end_to_end(
        args.dataset,
        data_path=args.data_path,
        cache_dir=args.cache_dir,
        n_rows=args.rows,
        seed=args.seed,
        inject_defects=not args.no_defects,
    )
    write_run_manifest(result, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

