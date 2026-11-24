from __future__ import annotations

import argparse
import sys
from pathlib import Path

from algo_agent import OptimizationError, Optimizer
from algo_agent.llm import GroqClient
from algo_agent.optimizer import save_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Optimize C, C++, Python, or JavaScript source code using the Groq API."
        )
    )
    parser.add_argument("source", help="Path to the source-code file")
    parser.add_argument(
        "--language",
        choices=["c", "cpp", "python", "javascript"],
        help="Specify language explicitly if the file extension is unsupported",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Groq model name (overrides GROQ_MODEL in .env)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for optimized source and JSON report (default: output)",
    )
    parser.add_argument(
        "--validation-timeout",
        type=float,
        default=15.0,
        help="Maximum seconds allowed for each syntax check (default: 15)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_path = Path(args.source)

    if not source_path.is_file():
        print(f"ERROR: Source file not found: {source_path}", file=sys.stderr)
        return 2

    if args.validation_timeout <= 0:
        print("ERROR: --validation-timeout must be greater than zero.", file=sys.stderr)
        return 2

    try:
        source = source_path.read_text(encoding="utf-8-sig")
        client = GroqClient(model=args.model)
        optimizer = Optimizer(
            client=client,
            validation_timeout_s=args.validation_timeout,
        )

        print("\nStarting optimization...")
        print(f"Input file: {source_path}")
        print(f"Model: {client.model}")

        result = optimizer.optimize(
            source,
            filename=source_path.name,
            language=args.language,
        )
        code_path, report_path = save_result(result, args.output_dir)

        print("\n" + "=" * 58)
        print("                 OPTIMIZATION RESULT")
        print("=" * 58)
        print(f"Language: {result.language}")
        print(f"Candidate accepted: {'Yes' if result.validation.get('candidate_accepted') else 'No'}")
        print(f"Code changed: {'Yes' if result.optimized else 'No'}")
        print(f"Time complexity: {result.time_complexity_before} -> {result.time_complexity_after}")
        print(f"Space complexity: {result.space_complexity_before} -> {result.space_complexity_after}")
        print(f"Summary: {result.summary}")

        if result.changes:
            print("\nChanges:")
            for item in result.changes:
                print(f"  - {item}")

        print("\nValidation:")
        for item in result.validation.get("checks", []):
            print(f"  [PASS] {item}")
        for item in result.validation.get("warnings", []):
            print(f"  [SKIP/LIMITATION] {item}")
        for item in result.validation.get("errors", []):
            print(f"  [ERROR] {item}")

        for warning in result.warnings:
            print(f"WARNING: {warning}")

        print(f"\nElapsed time: {result.elapsed_seconds:.3f} seconds")
        print(f"Optimized source: {code_path}")
        print(f"JSON report: {report_path}")
        print("=" * 58)

        if not result.validation.get("checks"):
            print(
                "NOTE: No external compiler/runtime syntax check ran. "
                "Review the validation warnings above."
            )
        print(
            "NOTE: Syntax validation does not prove behavioral equivalence. "
            "Complexity values are AI estimates, not measured benchmarks."
        )
        return 0

    except (OSError, UnicodeError, OptimizationError) as exc:
        print(f"\nOPTIMIZATION ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(
            f"\nUNEXPECTED ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
