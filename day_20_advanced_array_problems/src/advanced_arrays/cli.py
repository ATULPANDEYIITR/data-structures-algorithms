"""Command-line interface for the advanced array algorithms."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from typing import Any

from .algorithms import (
    find_duplicate,
    find_majority_element,
    find_missing_number,
    longest_consecutive_sequence,
    max_subarray_sum,
    product_except_self,
    rearrange_alternating,
    rotate_array,
    three_sum,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run advanced array algorithms from the command line."
    )
    parser.add_argument(
        "operation",
        choices=[
            "max-subarray",
            "majority",
            "missing",
            "duplicate",
            "rotate",
            "product-except-self",
            "alternate",
            "longest-consecutive",
            "three-sum",
        ],
    )
    parser.add_argument("values", help="JSON array, for example [2,-1,3,-4,5]")
    parser.add_argument("--k", type=int, default=0, help="Rotation amount.")
    parser.add_argument("--target", type=int, default=0, help="Target for three-sum.")
    return parser


def _load_values(raw: str) -> list[int]:
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("values must be valid JSON") from exc

    if not isinstance(values, list):
        raise ValueError("values must be a JSON array")

    return values


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    values = _load_values(args.values)

    operations: dict[str, Callable[[], Any]] = {
        "max-subarray": lambda: max_subarray_sum(values),
        "majority": lambda: find_majority_element(values),
        "missing": lambda: find_missing_number(values),
        "duplicate": lambda: find_duplicate(values),
        "rotate": lambda: rotate_array(values, args.k),
        "product-except-self": lambda: product_except_self(values),
        "alternate": lambda: rearrange_alternating(values),
        "longest-consecutive": lambda: longest_consecutive_sequence(values),
        "three-sum": lambda: three_sum(values, args.target),
    }

    try:
        result = operations[args.operation]()
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(result))


if __name__ == "__main__":
    main()
