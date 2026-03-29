from __future__ import annotations

import argparse
import json

from .config import load_config
from .pipeline import discover_inputs, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Task 2 pancreas cross-species OCR mapping pipeline')
    subparsers = parser.add_subparsers(dest='command', required=True)

    discover_parser = subparsers.add_parser('discover', help='Locate configured inputs and print them as JSON')
    discover_parser.add_argument('--config', required=True, help='Path to YAML configuration file')

    run_parser = subparsers.add_parser('run', help='Run the Task 2 pipeline')
    run_parser.add_argument('--config', required=True, help='Path to YAML configuration file')
    run_parser.add_argument('--skip-mapping', action='store_true', help='Prepare standardized OCR outputs but do not run HAL mapping')
    run_parser.add_argument('--skip-annotation', action='store_true', help='Skip nearest-gene and promoter/distal annotation')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == 'discover':
        print(json.dumps(discover_inputs(config), indent=2))
        return 0

    outputs = run_pipeline(config, skip_mapping=args.skip_mapping, skip_annotation=args.skip_annotation)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))
    return 0
