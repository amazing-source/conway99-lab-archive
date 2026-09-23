#!/usr/bin/env python3
"""Exhaustively scan a decoded candidate and emit exact prism blocking cuts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from complete_endpoint import (
    FULL_VERTEX_COUNT,
    cut_catalog,
    validate_cut_catalog,
)


def no_duplicate_object_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_candidate(path: Path) -> tuple[int, tuple[tuple[int, int], ...]]:
    data = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=no_duplicate_object_keys,
    )
    if not isinstance(data, dict) or set(data) != {"format", "vertices", "edges"}:
        raise ValueError("candidate must have exactly format, vertices, and edges")
    if data["format"] != "srg-edge-list-v1":
        raise ValueError("candidate format must be srg-edge-list-v1")
    if data["vertices"] != FULL_VERTEX_COUNT:
        raise ValueError("candidate must declare exactly 99 vertices")
    if not isinstance(data["edges"], list):
        raise ValueError("candidate edges must be a list")
    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for index, raw_edge in enumerate(data["edges"]):
        if (
            not isinstance(raw_edge, list)
            or len(raw_edge) != 2
            or any(type(vertex) is not int for vertex in raw_edge)
        ):
            raise ValueError(f"candidate edge {index} is malformed")
        first, second = sorted(raw_edge)
        if not 0 <= first < second < FULL_VERTEX_COUNT:
            raise ValueError(f"candidate edge {index} is invalid")
        edge = (first, second)
        if edge in seen:
            raise ValueError(f"candidate edge {index} is duplicated")
        seen.add(edge)
        edges.append(edge)
    return FULL_VERTEX_COUNT, tuple(sorted(edges))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="bind a complete existing catalog to the supplied candidate",
    )
    args = parser.parse_args()

    if args.verify_only:
        if args.candidate is None:
            raise SystemExit("--verify-only requires --candidate")
        _, edges = load_candidate(args.candidate)
        raw = json.loads(
            args.catalog.read_text(encoding="utf-8"),
            object_pairs_hook=no_duplicate_object_keys,
        )
        cuts = validate_cut_catalog(
            raw,
            candidate_edges=edges,
            require_complete=True,
        )
        print(
            json.dumps(
                {
                    "status": "PASS_COMPLETE_CATALOG_BOUND_TO_CANDIDATE",
                    "cut_count": len(cuts),
                },
                sort_keys=True,
            )
        )
        return 0

    if args.candidate is None:
        raise SystemExit("--candidate is required")
    vertex_count, edges = load_candidate(args.candidate)
    result = cut_catalog(vertex_count, edges)
    args.catalog.parent.mkdir(parents=True, exist_ok=True)
    args.catalog.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    validate_cut_catalog(
        result,
        candidate_edges=edges,
        require_complete=True,
    )
    print(
        json.dumps(
            {
                "status": (
                    "PRISM_FREE_CANDIDATE"
                    if result["prism_witness_count"] == 0
                    else "CUTS_EMITTED"
                ),
                "prism_witness_count": result["prism_witness_count"],
                "deduplicated_cut_count": result["deduplicated_cut_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
