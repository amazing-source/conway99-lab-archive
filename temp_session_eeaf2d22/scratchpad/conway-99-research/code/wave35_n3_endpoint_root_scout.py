#!/usr/bin/env python3
"""Reproduce the exact rooted ``P=0`` reduction and bounded branch scout.

For every root triangle ``(o,a,b)`` and every other root neighbor ``r``, the
three fixed incidence edges

    o--r, a--{a,r}, b--{b,r}

show that the residual edge ``{a,r}--{b,r}`` closes a triangular prism.
Consequently ``P=0`` adds exactly 7*12 negative units to the rooted target
model.

The cited-and-derived N3 normalization has a separately verified 12-way joint
matching cover.  Seven branches clash with an endpoint unit immediately; only
branches 4, 5, 8, 10, and 12 require a solver call.  Solver results from this
program are discovery-only unless an exported formula and proof are checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from matching_orbits import n3_joint_branch_decisions
from root_model import RootModel
from sat_model import EncodedRootModel, solve_model


SURVIVING_BRANCHES = (4, 5, 8, 10, 12)


def endpoint_edges(root: RootModel) -> tuple[tuple[int, int], ...]:
    indices = root.label_index()
    edges: set[tuple[int, int]] = set()
    for pair in range(7):
        first_coordinate = 2 * pair
        second_coordinate = first_coordinate + 1
        for other in range(14):
            if other in (first_coordinate, second_coordinate):
                continue
            first_label = indices[tuple(sorted((first_coordinate, other)))]
            second_label = indices[tuple(sorted((second_coordinate, other)))]
            edges.add(tuple(sorted((first_label, second_label))))
    result = tuple(sorted(edges))
    if len(result) != 84:
        raise AssertionError("endpoint reduction did not produce 84 unique units")
    return result


def endpoint_edge_sha256(edges: Sequence[tuple[int, int]]) -> str:
    payload = json.dumps([list(edge) for edge in edges], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def branch_mate_profile(
    root: RootModel, edges: set[tuple[int, int]]
) -> dict[int, int]:
    profile = {}
    for branch in range(1, 13):
        decisions = n3_joint_branch_decisions(root, branch)
        positive = {edge for edge, present in decisions.items() if present}
        profile[branch] = len(positive.intersection(edges))
    survivors = tuple(branch for branch, count in profile.items() if count == 0)
    if survivors != SURVIVING_BRANCHES:
        raise AssertionError(f"unexpected endpoint branch survivors: {survivors}")
    return profile


def build_branch(branch: int) -> tuple[EncodedRootModel, tuple[int, ...]]:
    if branch not in SURVIVING_BRANCHES:
        raise ValueError(f"branch {branch} is not an endpoint survivor")
    encoded = EncodedRootModel.build(
        7, variant="compact", cardinality_backend="native"
    )
    units = tuple(encoded.edge_variables[edge] for edge in endpoint_edges(encoded.root))
    for literal in units:
        encoded.cnf.append([-literal])
    encoded.add_n3_normalization()
    encoded.add_n3_joint_branch(branch)
    return encoded, units


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--conflict-budget", type=int, default=100_000)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = RootModel.build(7)
    edges = endpoint_edges(root)
    edge_set = set(edges)
    profile = branch_mate_profile(root, edge_set)
    results = []

    for branch in SURVIVING_BRANCHES:
        encoded, units = build_branch(branch)
        status = "NOT_RUN"
        solver_record = None
        if args.solve:
            result, _, solver_record = solve_model(
                encoded, "minicard", conflict_budget=args.conflict_budget
            )
            status = (
                "SAT_CANDIDATE"
                if result is True
                else "UNSAT_UNVERIFIED"
                if result is False
                else "BUDGET_UNKNOWN"
            )
        results.append(
            {
                "branch": branch,
                "status": status,
                "endpoint_unit_count": len(set(units)),
                "encoding": encoded.statistics(),
                "solver": solver_record,
            }
        )

    record = {
        "format": "wave35-n3-endpoint-root-scout-v1",
        "claim_label": "UNKNOWN",
        "scope": (
            "full rooted compact target model with theorem-forced N3, "
            "verified joint branch cover, and the necessary P=0 units"
        ),
        "endpoint": {
            "unit_count": len(edges),
            "edge_catalog_sha256": endpoint_edge_sha256(edges),
            "branch_mate_positive_counts": {
                str(branch): count for branch, count in profile.items()
            },
            "immediate_conflict_branches": [
                branch for branch, count in profile.items() if count > 0
            ],
            "solver_branches": list(SURVIVING_BRANCHES),
        },
        "results": results,
        "limitations": [
            "a budget stop has no mathematical evidentiary value",
            "a solver UNSAT needs an exported formula and independently checked proof",
            "a SAT assignment needs decoding and independent SRG verification",
        ],
    }
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
