#!/usr/bin/env python3
"""Scout whether the Wave144 endpoint witness extends to the order-seven deck.

This is deliberately a fixed-witness diagnostic.  It does not decide the
full six/seven coupling: the Wave144 aggregate table and its selected local
z_P witnesses are held fixed, while the 208 order-seven class counts and
h11/4 are allowed to vary.

For a six-set S and x outside S, the pair

    (G[S], orbit_Aut(G[S])(N(x) intersect S))

is a rooted order-seven extension type.  Summing the selected Wave144 local
profiles gives its required multiplicity.  Every order-seven class supplies
seven such rooted types, one for each deleted vertex.  The scout adds these
exact incidence equations to the Wave43 order-seven count system.

A solver result is discovery guidance only.  A rounded incumbent is checked
with exact integer arithmetic; an infeasibility status is not a certificate.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
WAVE21_PATH = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE22_PATH = ROOT / "attempts/wave22-full-seven-deck/exact_check.py"
WAVE43_PATH = ROOT / "attempts/wave43-seven-deck-endpoint/endpoint_deck.py"
WAVE144_RESULT = ROOT / "attempts/wave144-sixset-odd-profile/exact-results.json"
SEVEN_SUPPORT_PATH = (
    ROOT / "attempts/wave146-six-seven-coupling/seven_extendable_support.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(
        specification is not None and specification.loader is not None,
        f"cannot load {path}",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def transform_subset(subset: int, permutation: tuple[int, ...]) -> int:
    result = 0
    for vertex in range(len(permutation)):
        if subset >> vertex & 1:
            result |= 1 << permutation[vertex]
    return result


def canonical_root_pattern(
    wave22: Any,
    card: int,
    canonical_card: int,
    pattern: int,
) -> int:
    """Canonicalize a subset while mapping a six-card to its representative."""

    candidates = []
    for permutation, bit_map in zip(
        itertools.permutations(range(6)),
        wave22.permutation_bit_maps(6),
    ):
        if wave22.transform_mask(card, bit_map) == canonical_card:
            candidates.append(transform_subset(pattern, permutation))
    require(candidates, "no isomorphism maps a six-card to its canonical form")
    return min(candidates)


def canonical_profile_pattern(wave22: Any, mask: int, pattern: int) -> int:
    return canonical_root_pattern(wave22, mask, mask, pattern)


def deleted_pattern(wave22: Any, mask: int, deleted: int) -> tuple[int, int]:
    """Return the compressed six-card and deleted vertex's neighbor subset."""

    remaining = [vertex for vertex in range(7) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(remaining)}
    adjacency = wave22.adjacency_rows(mask, 7)
    pattern = 0
    for old in remaining:
        if adjacency[deleted] >> old & 1:
            pattern |= 1 << relabel[old]
    return wave22.delete_vertex(mask, 7, deleted), pattern


def source_masks(wave21: Any) -> tuple[int, ...]:
    _, five_mapping = wave21.align_four_five()
    six_mapping = wave21.align_five_six(
        five_mapping,
        wave21.corrected_five_to_six(),
    )
    classes = wave21.locally_admissible_classes(6)
    masks = tuple(classes[index] for index in six_mapping)
    require(len(masks) == 62 and len(set(masks)) == 62, "six-class map drift")
    return masks


def fixed_required_extensions(
    wave22: Any,
    source_mask_by_index: tuple[int, ...],
) -> Counter[tuple[int, int]]:
    payload = json.loads(WAVE144_RESULT.read_text(encoding="utf-8"))
    support_module = load_module("wave146_seven_support", SEVEN_SUPPORT_PATH)
    repaired = support_module.build_result()
    cells = {
        (int(record["source_class"]), int(record["output_weight"])): int(record["count"])
        for record in payload["aggregate_endpoint_certificate"]["nonzero_cells"]
    }
    profiles = {
        (int(record["source_class"]), int(record["output_weight"])): {
            int(pattern): int(count)
            for pattern, count in record["z_by_subset_mask_sparse"].items()
        }
        for record in repaired["selected_seven_extendable_local_witnesses"]
    }
    require(set(cells) <= set(profiles), "a positive Wave144 cell has no local profile")

    required: Counter[tuple[int, int]] = Counter()
    for (source, weight), six_count in cells.items():
        mask = source_mask_by_index[source - 1]
        for pattern, local_count in profiles[(source, weight)].items():
            orbit = canonical_profile_pattern(wave22, mask, pattern)
            required[(source, orbit)] += six_count * local_count

    total_six_sets = sum(cells.values())
    require(total_six_sets == math.comb(99, 6), "Wave144 six-set total drift")
    require(
        sum(required.values()) == 93 * total_six_sets,
        "rooted extension total drift",
    )
    return required


def seven_extension_vectors(
    wave22: Any,
    classes: Iterable[int],
    source_mask_by_index: tuple[int, ...],
) -> tuple[tuple[Counter[tuple[int, int]], ...], tuple[tuple[int, int], ...]]:
    source_by_mask = {
        mask: source for source, mask in enumerate(source_mask_by_index, start=1)
    }
    vectors = []
    keys: set[tuple[int, int]] = set()
    for mask in classes:
        vector: Counter[tuple[int, int]] = Counter()
        for deleted in range(7):
            card, pattern = deleted_pattern(wave22, mask, deleted)
            canonical_card = wave22.canonical_mask(card, 6)
            source = source_by_mask[canonical_card]
            orbit = canonical_root_pattern(
                wave22,
                card,
                canonical_card,
                pattern,
            )
            vector[(source, orbit)] += 1
        require(sum(vector.values()) == 7, "seven-class root total drift")
        vectors.append(vector)
        keys.update(vector)
    return tuple(vectors), tuple(sorted(keys))


def build_model() -> dict[str, Any]:
    wave21 = load_module("wave146_wave21", WAVE21_PATH)
    wave22 = load_module("wave146_wave22", WAVE22_PATH)
    wave43 = load_module("wave146_wave43", WAVE43_PATH)
    endpoint = wave43.build_endpoint_model()
    masks = source_masks(wave21)
    required = fixed_required_extensions(wave22, masks)
    vectors, all_keys = seven_extension_vectors(wave22, endpoint["classes"], masks)
    missing_keys = tuple(sorted(set(required) - set(all_keys)))
    return {
        "wave43": endpoint,
        "required": required,
        "vectors": vectors,
        "keys": all_keys,
        "missing_keys": missing_keys,
    }


def sparse_constraints(model: dict[str, Any]) -> tuple[Any, np.ndarray, list[str]]:
    endpoint = model["wave43"]
    classes = endpoint["classes"]
    y_index = len(classes)
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    targets: list[float] = []
    labels: list[str] = []

    def append_row(entries: Iterable[tuple[int, int]], target: int, label: str) -> None:
        row = len(targets)
        for column, coefficient in entries:
            if coefficient:
                row_indices.append(row)
                column_indices.append(column)
                values.append(float(coefficient))
        targets.append(float(target))
        labels.append(label)

    for index, (coefficients, target) in enumerate(
        zip(endpoint["matrix_rows"], endpoint["deck_rhs"])
    ):
        append_row(
            ((column, coefficient) for column, coefficient in enumerate(coefficients)),
            int(target),
            f"deck:{index + 1}",
        )

    for equation in endpoint["h_equations"]:
        entries = [(int(equation["class_index"]), 1)]
        if equation["y_coefficient"]:
            entries.append((y_index, -int(equation["y_coefficient"])))
        append_row(
            entries,
            int(equation["constant"]),
            f"hamiltonian:{equation['source_index']}",
        )

    for key in model["keys"]:
        append_row(
            (
                (column, vector.get(key, 0))
                for column, vector in enumerate(model["vectors"])
            ),
            int(model["required"].get(key, 0)),
            f"root:{key[0]}:{key[1]}",
        )

    matrix = coo_array(
        (
            np.asarray(values, dtype=np.float64),
            (
                np.asarray(row_indices, dtype=np.int32),
                np.asarray(column_indices, dtype=np.int32),
            ),
        ),
        shape=(len(targets), len(classes) + 1),
    ).tocsr()
    return matrix, np.asarray(targets, dtype=np.float64), labels


def exact_residuals(model: dict[str, Any], values: list[int]) -> dict[str, Any]:
    endpoint = model["wave43"]
    counts = values[:-1]
    y_value = values[-1]
    failures = []
    for index, (row, target) in enumerate(
        zip(endpoint["matrix_rows"], endpoint["deck_rhs"])
    ):
        actual = sum(coefficient * count for coefficient, count in zip(row, counts))
        if actual != target:
            failures.append(f"deck:{index + 1}:{actual - target}")
    for equation in endpoint["h_equations"]:
        actual = counts[equation["class_index"]]
        target = equation["constant"] + equation["y_coefficient"] * y_value
        if actual != target:
            failures.append(f"hamiltonian:{equation['source_index']}:{actual - target}")
    for key in model["keys"]:
        actual = sum(
            count * vector.get(key, 0)
            for count, vector in zip(counts, model["vectors"])
        )
        target = model["required"].get(key, 0)
        if actual != target:
            failures.append(f"root:{key[0]}:{key[1]}:{actual - target}")
    return {
        "pass": not failures,
        "failure_count": len(failures),
        "first_failures": failures[:20],
        "h11": 4 * y_value,
        "positive_seven_classes": sum(count > 0 for count in counts),
    }


def run(time_limit: float) -> dict[str, Any]:
    model = build_model()
    if model["missing_keys"]:
        missing = [
            {
                "source_class": source,
                "canonical_pattern": pattern,
                "required_count": model["required"][(source, pattern)],
            }
            for source, pattern in model["missing_keys"]
        ]
        return {
            "format": "wave146-fixed-six-seven-coupling-scout-v1",
            "scope": (
                "fixed Wave144 endpoint table and selected local profiles coupled "
                "to locally admissible rooted order-seven extensions"
            ),
            "model": {
                "seven_vertex_classes": len(model["vectors"]),
                "available_root_extension_types": len(model["keys"]),
                "required_root_extension_types": len(model["required"]),
                "missing_required_root_extension_types": len(missing),
                "missing_required_ordered_pairs": sum(
                    record["required_count"] for record in missing
                ),
            },
            "solver": {
                "status": "NOT_RUN_EXACT_PRECHECK_REFUTED_FIXED_WITNESS",
                "infeasibility_status_is_not_a_certificate": True,
            },
            "fixed_witness_exact_replay": {
                "pass": False,
                "reason": (
                    "the selected Wave144 local profiles assign positive mass "
                    "to rooted seven-vertex types excluded by the exact local "
                    "lambda/mu common-neighbor conditions"
                ),
                "missing_types": missing,
            },
            "conclusion": "FIXED_WAVE144_WITNESS_REFUTED",
            "limitations": [
                "This refutes only the selected Wave144 endpoint witness, not all profiles with the same aggregate table.",
                "It does not prove a strict n3 upper bound or decide Conway-99.",
                "No automorphism of the putative 99-vertex graph is assumed.",
            ],
        }
    matrix, targets, labels = sparse_constraints(model)
    variable_count = matrix.shape[1]
    lower = np.zeros(variable_count, dtype=np.float64)
    upper = np.full(variable_count, np.inf, dtype=np.float64)
    lower[-1] = math.ceil(2 * 4158 / 4)
    upper[-1] = 4158
    result = milp(
        c=np.zeros(variable_count, dtype=np.float64),
        integrality=np.ones(variable_count, dtype=np.uint8),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(matrix, targets, targets),
        options={
            "disp": False,
            "presolve": True,
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
        },
    )
    candidate = None
    maximum_rounding_error = None
    if result.x is not None:
        rounded = [int(round(float(value))) for value in result.x]
        maximum_rounding_error = max(
            abs(float(value) - integer)
            for value, integer in zip(result.x, rounded)
        )
        candidate = exact_residuals(model, rounded)
    return {
        "format": "wave146-fixed-six-seven-coupling-scout-v1",
        "scope": (
            "fixed Wave144 endpoint table and selected local profiles coupled "
            "to the complete Wave43 order-seven count system"
        ),
        "model": {
            "integer_variables": variable_count,
            "equalities": int(matrix.shape[0]),
            "nonzeros": int(matrix.nnz),
            "root_extension_types": len(model["keys"]),
            "positive_required_root_types": len(model["required"]),
            "labels_sha256_note": "labels retained in memory only for diagnostics",
        },
        "solver": {
            "status": int(result.status),
            "message": str(result.message),
            "success": bool(result.success),
            "time_limit_seconds": time_limit,
            "maximum_rounding_error": maximum_rounding_error,
            "infeasibility_status_is_not_a_certificate": True,
        },
        "candidate_exact_replay": candidate,
        "conclusion": (
            "EXACT_INTEGER_EXTENSION_WITNESS"
            if candidate and candidate["pass"]
            else "UNKNOWN"
        ),
        "limitations": [
            "Only the one fixed Wave144 witness and its selected local profiles are tested.",
            "Aggregate seven-class counts still do not impose global overlapping-subset consistency.",
            "A solver infeasibility status is not negative evidence without an exact certificate.",
            "No automorphism of the putative 99-vertex graph is assumed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=300.0)
    arguments = parser.parse_args()
    require(1 <= arguments.time_limit <= 1800, "invalid time limit")
    print(json.dumps(run(arguments.time_limit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
