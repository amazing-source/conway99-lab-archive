#!/usr/bin/env python3
"""Exact six-set profiles using only locally admissible seventh vertices.

Wave144 imposed the SRG equations on pairs wholly inside a fixed six-set S.
For a cell P=N(x) intersect S, an actual outside vertex x must also satisfy
the lambda/mu common-neighbor cap for every pair (x,u), u in S.  This script
adds those exact per-cell restrictions and re-enumerates all attainable
weights with integer arithmetic.

The result is a local support calculation only.  Profiles for different
six-sets are not coupled.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WAVE144_PATH = ROOT / "attempts/wave144-sixset-odd-profile/exact_check.py"
WAVE144_RESULT = ROOT / "attempts/wave144-sixset-odd-profile/exact-results.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_wave144() -> Any:
    specification = importlib.util.spec_from_file_location(
        "wave146_wave144",
        WAVE144_PATH,
    )
    require(
        specification is not None and specification.loader is not None,
        "cannot load Wave144",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def root_pattern_allowed(wave144: Any, mask: int, pattern: int) -> bool:
    """Check all common-neighbor caps for pairs (new root, old vertex)."""

    matrix = wave144.adjacency(mask)
    for vertex in range(6):
        common_inside = sum(
            matrix[vertex][other]
            for other in range(6)
            if pattern >> other & 1
        )
        target = 1 if pattern >> vertex & 1 else 2
        if common_inside > target:
            return False
    return True


def enumerate_profiles(
    wave144: Any,
    mask: int,
    statistic_patterns: set[int] | None = None,
) -> dict[str, Any]:
    params = wave144.local_parameters(mask)
    edge_list = wave144.edges()
    edge_index = {edge: index for index, edge in enumerate(edge_list)}
    allowed = [
        root_pattern_allowed(wave144, mask, pattern)
        for pattern in range(1 << 6)
    ]
    remaining = list(params["pair_rhs"])
    high_cells = []
    for size in range(6, 2, -1):
        for vertices in itertools.combinations(range(6), size):
            cell = sum(1 << vertex for vertex in vertices)
            if not allowed[cell]:
                continue
            pair_indices = tuple(
                edge_index[pair]
                for pair in itertools.combinations(vertices, 2)
            )
            if all(remaining[index] > 0 for index in pair_indices):
                high_cells.append((cell, vertices, pair_indices))

    vertex_high = [0] * 6
    chosen_high: dict[int, int] = {}
    witnesses: dict[int, list[int]] = {}
    statistic_values: dict[int, set[int]] = {}
    node_count = 0
    leaf_count = 0

    def visit(index: int, high_total: int, high_odd: int) -> None:
        nonlocal node_count, leaf_count
        node_count += 1
        if index == len(high_cells):
            leaf_count += 1
            pair_values = [0] * len(edge_list)
            for pair_index, (left, right) in enumerate(edge_list):
                cell = (1 << left) | (1 << right)
                if allowed[cell]:
                    pair_values[pair_index] = remaining[pair_index]
                elif remaining[pair_index]:
                    return

            singletons = []
            for vertex in range(6):
                pair_total = sum(
                    pair_values[
                        edge_index[tuple(sorted((vertex, other)))]
                    ]
                    for other in range(6)
                    if other != vertex
                )
                value = (
                    params["degree_rhs"][vertex]
                    - vertex_high[vertex]
                    - pair_total
                )
                if value < 0:
                    return
                if value and not allowed[1 << vertex]:
                    return
                singletons.append(value)

            empty = (
                wave144.OUTSIDE_COUNT
                - high_total
                - sum(pair_values)
                - sum(singletons)
            )
            if empty < 0 or (empty and not allowed[0]):
                return
            weight = params["inside_odd_weight"] + high_odd + sum(singletons)
            if weight in witnesses and statistic_patterns is None:
                return
            profile = [0] * (1 << 6)
            profile[0] = empty
            for vertex, value in enumerate(singletons):
                profile[1 << vertex] = value
            for pair_index, (left, right) in enumerate(edge_list):
                profile[(1 << left) | (1 << right)] = pair_values[pair_index]
            for cell, value in chosen_high.items():
                profile[cell] = value
            wave144.verify_profile(mask, profile, weight)
            require(
                all(not value or allowed[cell] for cell, value in enumerate(profile)),
                "forbidden rooted type has positive mass",
            )
            witnesses.setdefault(weight, profile)
            if statistic_patterns is not None:
                statistic_values.setdefault(weight, set()).add(
                    sum(profile[cell] for cell in statistic_patterns)
                )
            return

        cell, vertices, pair_indices = high_cells[index]
        capacity = min(remaining[pair_index] for pair_index in pair_indices)
        for value in range(capacity + 1):
            if value:
                chosen_high[cell] = value
            for pair_index in pair_indices:
                remaining[pair_index] -= value
            for vertex in vertices:
                vertex_high[vertex] += value
            visit(
                index + 1,
                high_total + value,
                high_odd + (value if len(vertices) % 2 else 0),
            )
            for pair_index in pair_indices:
                remaining[pair_index] += value
            for vertex in vertices:
                vertex_high[vertex] -= value
            chosen_high.pop(cell, None)

    visit(0, 0, 0)
    return {
        "attainable_weights": sorted(witnesses),
        "witnesses": witnesses,
        "allowed_pattern_count": sum(allowed),
        "forbidden_patterns": [
            pattern for pattern, is_allowed in enumerate(allowed) if not is_allowed
        ],
        "enumeration_nodes": node_count,
        "terminal_assignments": leaf_count,
        "statistic_values_by_weight": {
            weight: sorted(values)
            for weight, values in statistic_values.items()
        },
    }


def build_result() -> dict[str, Any]:
    wave144 = load_wave144()
    wave21 = wave144.load_wave21()
    _, five_mapping = wave21.align_four_five()
    six_mapping = wave21.align_five_six(
        five_mapping,
        wave21.corrected_five_to_six(),
    )
    classes = wave21.locally_admissible_classes(6)
    prior = json.loads(WAVE144_RESULT.read_text(encoding="utf-8"))
    prior_support = {
        int(record["source_class"]): list(map(int, record["attainable_weights"]))
        for record in prior["class_profiles"]
    }

    records = []
    supports = {}
    witnesses = {}
    for source in range(1, 63):
        mask = classes[six_mapping[source - 1]]
        local = enumerate_profiles(wave144, mask)
        supports[source] = local["attainable_weights"]
        witnesses[source] = local["witnesses"]
        records.append(
            {
                "source_class": source,
                "canonical_mask": mask,
                "allowed_pattern_count": local["allowed_pattern_count"],
                "forbidden_pattern_count": len(local["forbidden_patterns"]),
                "forbidden_patterns": local["forbidden_patterns"],
                "wave144_attainable_weights": prior_support[source],
                "seven_extendable_attainable_weights": local["attainable_weights"],
                "removed_weights": sorted(
                    set(prior_support[source]) - set(local["attainable_weights"])
                ),
                "enumeration_nodes": local["enumeration_nodes"],
                "terminal_assignments": local["terminal_assignments"],
            }
        )

    cells = {
        (int(record["source_class"]), int(record["output_weight"])): int(record["count"])
        for record in prior["aggregate_endpoint_certificate"]["nonzero_cells"]
    }
    unsupported = [
        {
            "source_class": source,
            "output_weight": weight,
            "count": count,
        }
        for (source, weight), count in sorted(cells.items())
        if weight not in supports[source]
    ]
    selected_witnesses = [
        {
            "source_class": source,
            "output_weight": weight,
            "z_by_subset_mask_sparse": wave144.sparse_profile(
                witnesses[source][weight]
            ),
        }
        for source, weight in sorted(cells)
        if weight in supports[source]
    ]
    return {
        "format": "wave146-seven-extendable-six-support-v1",
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "exact local six-set outside profiles after imposing all induced "
            "seven-vertex lambda/mu common-neighbor caps"
        ),
        "class_profiles": records,
        "summary": {
            "classes": len(records),
            "classes_with_removed_weights": sum(
                bool(record["removed_weights"]) for record in records
            ),
            "total_removed_weight_cells": sum(
                len(record["removed_weights"]) for record in records
            ),
            "wave144_endpoint_positive_cells": len(cells),
            "wave144_endpoint_unsupported_cells": len(unsupported),
        },
        "wave144_endpoint_unsupported_cells": unsupported,
        "selected_seven_extendable_local_witnesses": selected_witnesses,
        "limitations": [
            "The calculation is local to one six-set at a time.",
            "It does not couple profiles on overlapping six-sets.",
            "Endpoint support survival would not be a graph construction.",
            "No automorphism of a putative graph is assumed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    arguments = parser.parse_args()
    result = build_result()
    if arguments.compact:
        print(json.dumps(result["summary"], sort_keys=True))
        print(
            json.dumps(
                result["wave144_endpoint_unsupported_cells"],
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
