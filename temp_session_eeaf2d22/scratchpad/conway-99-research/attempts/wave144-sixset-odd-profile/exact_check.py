#!/usr/bin/env python3
"""Exact Wave144 six-set outside-profile enumeration and endpoint replay.

For a fixed induced six-vertex graph H on S, z_P is the number of vertices
outside S whose neighborhood in S is exactly P.  The local feasibility
problem has 64 nonnegative integer variables, but it can be enumerated
without an ILP solver: cells of size at least three are bounded by the pair
equations, pair cells are then forced, singleton cells are forced by the
degree equations, and the empty cell is forced by the total.

The global endpoint certificate is an explicit nonnegative integer table.
No numerical optimization or floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


N = 99
K = 14
LAMBDA = 1
MU = 2
SET_SIZE = 6
OUTSIDE_COUNT = N - SET_SIZE
KNOWN_N3_CAP = 4158
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE21_CHECK = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE141_RESULT = ROOT / "attempts/wave141-bivariate-graph-code/exact-results.json"
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "attempts/wave21-six-vertex-lp/exact_check.py":
        "0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3",
    "attempts/wave21-six-vertex-lp/exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
    "attempts/wave141-bivariate-graph-code/exact_check.py":
        "15378b9a9f807071de0aae5604c4178af5b3cfa067851230781d67d05f2ca204",
    "attempts/wave141-bivariate-graph-code/exact-results.json":
        "351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e",
}

# Explicit integral primal certificate at n3=4158.  Each triple is
# (Wave21 source class, output weight wt(A 1_S), number of six-sets).
# Omitted cells have count zero.
ENDPOINT_CELLS = (
    (2, 56, 8316),
    (3, 56, 4158),
    (4, 56, 8316),
    (5, 46, 16632),
    (6, 50, 83160),
    (7, 46, 41580),
    (8, 46, 158004),
    (9, 46, 37422),
    (10, 46, 74844),
    (11, 40, 681912),
    (12, 40, 213444),
    (13, 42, 359667),
    (14, 36, 3696),
    (15, 54, 20790),
    (16, 50, 83160),
    (17, 50, 166320),
    (18, 50, 149688),
    (19, 52, 110880),
    (20, 48, 831600),
    (21, 48, 307692),
    (22, 44, 748440),
    (23, 44, 1513512),
    (24, 44, 340956),
    (25, 40, 598752),
    (26, 44, 332640),
    (27, 44, 756756),
    (28, 44, 340956),
    (29, 40, 1355508),
    (30, 50, 66528),
    (31, 42, 1995840),
    (32, 42, 1700622),
    (33, 42, 6960492),
    (34, 42, 6286896),
    (35, 42, 6444900),
    (36, 48, 101287494),
    (37, 34, 50894544),
    (37, 46, 19089153),
    (37, 50, 205388169),
    (38, 40, 108559653),
    (38, 44, 79157415),
    (39, 44, 145284678),
    (40, 42, 30345084),
    (41, 42, 95950008),
    (42, 42, 103409460),
    (43, 42, 5069988),
    (44, 40, 2328480),
    (45, 40, 2291058),
    (46, 40, 36124704),
    (47, 44, 8823276),
    (48, 40, 37064412),
    (49, 44, 2461536),
    (50, 42, 3559248),
    (51, 42, 3817044),
    (52, 42, 1704780),
    (53, 42, 1455300),
    (54, 44, 83160),
    (55, 44, 340956),
    (56, 42, 3559248),
    (57, 42, 8279271),
    (58, 40, 17039484),
    (59, 40, 4997916),
    (60, 42, 1363824),
    (61, 40, 7629927),
    (61, 52, 3),
    (62, 42, 365904),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256(ROOT / relative)
        require(actual == expected, f"frozen input drift: {relative}")
        observed[relative] = actual
    return observed


def load_wave21() -> Any:
    spec = importlib.util.spec_from_file_location("wave144_wave21_input", WAVE21_CHECK)
    require(spec is not None and spec.loader is not None, "cannot load Wave21")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def edges() -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(SET_SIZE), 2))


def adjacency(mask: int) -> list[list[int]]:
    matrix = [[0] * SET_SIZE for _ in range(SET_SIZE)]
    for bit, (left, right) in enumerate(edges()):
        if (mask >> bit) & 1:
            matrix[left][right] = matrix[right][left] = 1
    return matrix


def local_parameters(mask: int) -> dict[str, Any]:
    matrix = adjacency(mask)
    degree = [sum(row) for row in matrix]
    pair_rhs = []
    for left, right in edges():
        internal_common = sum(
            matrix[left][vertex] * matrix[right][vertex]
            for vertex in range(SET_SIZE)
        )
        target = LAMBDA if matrix[left][right] else MU
        rhs = target - internal_common
        require(rhs >= 0, "class violates a pair common-neighbor equation")
        pair_rhs.append(rhs)
    return {
        "matrix": matrix,
        "degree": degree,
        "degree_rhs": [K - value for value in degree],
        "pair_rhs": pair_rhs,
        "inside_odd_weight": sum(value % 2 for value in degree),
    }


def sparse_profile(profile: list[int]) -> dict[str, int]:
    return {str(cell): value for cell, value in enumerate(profile) if value}


def verify_profile(mask: int, profile: list[int], claimed_weight: int) -> None:
    require(len(profile) == 1 << SET_SIZE, "profile must have 64 cells")
    require(all(isinstance(value, int) and value >= 0 for value in profile),
            "profile cells must be nonnegative integers")
    params = local_parameters(mask)
    require(sum(profile) == OUTSIDE_COUNT, "outside total equation failed")
    for vertex, rhs in enumerate(params["degree_rhs"]):
        observed = sum(
            profile[cell]
            for cell in range(1 << SET_SIZE)
            if (cell >> vertex) & 1
        )
        require(observed == rhs, f"degree equation failed at vertex {vertex}")
    for pair_index, (left, right) in enumerate(edges()):
        observed = sum(
            profile[cell]
            for cell in range(1 << SET_SIZE)
            if ((cell >> left) & 1) and ((cell >> right) & 1)
        )
        require(
            observed == params["pair_rhs"][pair_index],
            f"pair equation failed at {(left, right)}",
        )
    observed_weight = params["inside_odd_weight"] + sum(
        profile[cell]
        for cell in range(1 << SET_SIZE)
        if cell.bit_count() % 2
    )
    require(observed_weight == claimed_weight, "output-weight equation failed")


def enumerate_local_profiles(mask: int) -> dict[str, Any]:
    """Exhaustively enumerate exact attainable output weights.

    Once all cells of size >=3 are chosen, every remaining cell is forced:
    size-2 cells by the 15 pair equations, size-1 cells by the six degree
    equations, and z_empty by the outside-total equation.
    """

    params = local_parameters(mask)
    edge_list = edges()
    edge_index = {edge: index for index, edge in enumerate(edge_list)}
    remaining = list(params["pair_rhs"])
    high_cells = []
    for size in range(SET_SIZE, 2, -1):
        for vertices in itertools.combinations(range(SET_SIZE), size):
            pair_indices = tuple(
                edge_index[pair]
                for pair in itertools.combinations(vertices, 2)
            )
            if all(remaining[index] > 0 for index in pair_indices):
                cell = sum(1 << vertex for vertex in vertices)
                high_cells.append((cell, vertices, pair_indices))

    vertex_high = [0] * SET_SIZE
    chosen_high: dict[int, int] = {}
    witnesses: dict[int, list[int]] = {}
    node_count = 0
    leaf_count = 0

    def visit(index: int, high_total: int, high_odd: int) -> None:
        nonlocal node_count, leaf_count
        node_count += 1
        if index == len(high_cells):
            leaf_count += 1
            singleton = []
            for vertex in range(SET_SIZE):
                pair_total = sum(
                    remaining[
                        edge_index[tuple(sorted((vertex, other)))]
                    ]
                    for other in range(SET_SIZE)
                    if other != vertex
                )
                value = (
                    params["degree_rhs"][vertex]
                    - vertex_high[vertex]
                    - pair_total
                )
                if value < 0:
                    return
                singleton.append(value)
            empty = (
                OUTSIDE_COUNT
                - high_total
                - sum(remaining)
                - sum(singleton)
            )
            if empty < 0:
                return
            weight = (
                params["inside_odd_weight"]
                + high_odd
                + sum(singleton)
            )
            if weight in witnesses:
                return
            profile = [0] * (1 << SET_SIZE)
            profile[0] = empty
            for vertex, value in enumerate(singleton):
                profile[1 << vertex] = value
            for pair_index, (left, right) in enumerate(edge_list):
                profile[(1 << left) | (1 << right)] = remaining[pair_index]
            for cell, value in chosen_high.items():
                profile[cell] = value
            verify_profile(mask, profile, weight)
            witnesses[weight] = profile
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
    require(witnesses, "local profile system unexpectedly infeasible")
    return {
        "attainable_weights": sorted(witnesses),
        "witnesses": witnesses,
        "high_cell_count": len(high_cells),
        "enumeration_nodes": node_count,
        "terminal_assignments": leaf_count,
    }


def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * math.comb(weight, overlap)
        * math.comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def low_rows_and_moments() -> tuple[dict[int, dict[int, int]], dict[int, int]]:
    payload = json.loads(WAVE141_RESULT.read_text(encoding="utf-8"))
    rows = {
        int(input_weight): {
            int(output_weight): int(count)
            for output_weight, count in row.items()
        }
        for input_weight, row in payload["exact_low_input_rows"].items()
    }
    require(set(rows) >= {0, 1, 2, 3}, "Wave141 low rows are incomplete")
    rhs = {
        degree: sum(
            krawtchouk(6, output_weight) * count
            for output_weight, count in rows[degree].items()
        )
        for degree in range(4)
    }
    return rows, rhs


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def endpoint_certificate(
    wave21: Any,
    supports: dict[int, list[int]],
) -> dict[str, Any]:
    forms = wave21.six_counts()
    endpoint = {(source, weight): count for source, weight, count in ENDPOINT_CELLS}
    require(len(endpoint) == len(ENDPOINT_CELLS), "duplicate endpoint cell")
    require(all(count > 0 for count in endpoint.values()), "nonpositive endpoint cell")

    marginals = {}
    for source in range(1, 63):
        expected = forms[source].evaluate(KNOWN_N3_CAP)
        require(expected.denominator == 1 and expected >= 0,
                f"class {source} endpoint marginal is not a nonnegative integer")
        observed = sum(
            count
            for (cell_source, weight), count in endpoint.items()
            if cell_source == source
        )
        require(observed == expected, f"class {source} marginal mismatch")
        for cell_source, weight in endpoint:
            if cell_source == source:
                require(weight in supports[source],
                        f"unsupported endpoint cell {(source, weight)}")
        marginals[str(source)] = int(expected)

    require(sum(marginals.values()) == math.comb(N, SET_SIZE),
            "six-class marginals do not sum to binom(99,6)")
    _, rhs = low_rows_and_moments()
    lhs = {
        degree: sum(
            krawtchouk(degree, weight) * count
            for (_, weight), count in endpoint.items()
        )
        for degree in range(4)
    }
    require(lhs == rhs, "Krawtchouk reciprocity moment mismatch")

    signed = sum(
        (-1) ** (weight // 2) * count
        for (_, weight), count in endpoint.items()
    )
    expected_signed = Fraction(2024484) + Fraction(512, 3) * KNOWN_N3_CAP
    require(signed == expected_signed, "Wave141 signed row mismatch")

    return {
        "n3": KNOWN_N3_CAP,
        "known_imported_cap": KNOWN_N3_CAP,
        "optimality_logic": (
            "the model imports n3<=4158; this explicit integral primal is "
            "feasible at 4158, so the lifted model optimum is exactly 4158"
        ),
        "variable_domain": "nonnegative integers",
        "nonzero_cells": [
            {"source_class": source, "output_weight": weight, "count": count}
            for source, weight, count in ENDPOINT_CELLS
        ],
        "nonzero_cell_count": len(ENDPOINT_CELLS),
        "class_marginals": marginals,
        "moment_lhs": {str(degree): value for degree, value in lhs.items()},
        "moment_rhs": {str(degree): value for degree, value in rhs.items()},
        "signed_S6": signed,
    }


def build_result() -> dict[str, Any]:
    frozen = verify_frozen_inputs()
    wave21 = load_wave21()
    _, m_mapping = wave21.align_four_five()
    six_mapping = wave21.align_five_six(
        m_mapping,
        wave21.corrected_five_to_six(),
    )
    classes = wave21.locally_admissible_classes(SET_SIZE)
    require(len(classes) == 62 and len(set(six_mapping)) == 62,
            "six-class alignment drift")

    enumerations: dict[int, dict[str, Any]] = {}
    masks: dict[int, int] = {}
    class_records = []
    for source in range(1, 63):
        canonical_index = six_mapping[source - 1]
        mask = classes[canonical_index]
        masks[source] = mask
        local = enumerate_local_profiles(mask)
        enumerations[source] = local
        params = local_parameters(mask)
        class_records.append({
            "source_class": source,
            "canonical_index_zero_based": canonical_index,
            "canonical_mask": mask,
            "edge_count": mask.bit_count(),
            "degrees": params["degree"],
            "degree_rhs": params["degree_rhs"],
            "pair_rhs_in_lex_edge_order": params["pair_rhs"],
            "inside_odd_weight": params["inside_odd_weight"],
            "attainable_weights": local["attainable_weights"],
            "high_cell_count": local["high_cell_count"],
            "enumeration_nodes": local["enumeration_nodes"],
            "terminal_assignments": local["terminal_assignments"],
        })

    supports = {
        source: local["attainable_weights"]
        for source, local in enumerations.items()
    }
    forced = {
        source: supports[source][0]
        for source in range(1, 63)
        if len(supports[source]) == 1
    }
    require(forced == {1: 66, 3: 56, 5: 46, 14: 36},
            f"forced-cell lead mismatch: {forced}")

    endpoint = endpoint_certificate(wave21, supports)
    selected = {
        (entry["source_class"], entry["output_weight"])
        for entry in endpoint["nonzero_cells"]
    }
    selected.update(forced.items())
    selected_witnesses = []
    for source, weight in sorted(selected):
        profile = enumerations[source]["witnesses"][weight]
        verify_profile(masks[source], profile, weight)
        selected_witnesses.append({
            "source_class": source,
            "output_weight": weight,
            "z_by_subset_mask_sparse": sparse_profile(profile),
        })

    return {
        "format": "wave144-sixset-odd-profile-v1",
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "exact six-set outside-neighborhood profile support and four "
            "aggregate Krawtchouk moments; no graph realization"
        ),
        "frozen_inputs_sha256": frozen,
        "parameters": {
            "srg": [N, K, LAMBDA, MU],
            "six_set_size": SET_SIZE,
            "outside_vertex_count": OUTSIDE_COUNT,
            "known_n3_upper_bound": KNOWN_N3_CAP,
        },
        "local_formulation": {
            "variables": "z_P for all 64 subsets P of a fixed six-set S",
            "total": "sum_P z_P=93",
            "degree": "sum_(P contains v) z_P=14-deg_H(v)",
            "pair": (
                "sum_(P contains u,v) z_P="
                "(1 if uv is an edge else 2)-cn_H(u,v)"
            ),
            "output_weight": (
                "number of odd-degree vertices of H plus "
                "sum_(|P| odd) z_P"
            ),
            "exact_enumeration": (
                "enumerate every size>=3 cell within its pair-equation bound; "
                "then pair, singleton, and empty cells are uniquely forced"
            ),
        },
        "class_profiles": class_records,
        "forced_singleton_cells": {
            str(source): weight for source, weight in forced.items()
        },
        "selected_local_integer_witnesses": selected_witnesses,
        "aggregate_endpoint_certificate": endpoint,
        "result": {
            "lifted_model_optimum_n3": KNOWN_N3_CAP,
            "improves_known_n3_cap": False,
            "endpoint_survives": True,
            "interpretation": (
                "null boundary: local profiles plus t=0..3 reciprocity do not "
                "exclude n3=4158"
            ),
        },
        "limitations": [
            "The aggregate table does not assign profiles consistently across overlapping six-sets.",
            "Local integer z_P witnesses are not a 99-vertex graph construction.",
            "Only reciprocity moments t=0,1,2,3 are imposed.",
            "The imported n3<=4158 cap is not reproved here.",
            "No existence, nonexistence, resolution, or novelty claim is made.",
            "Discovery cannot verify itself.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    require(args.write or args.verify, "choose --write or --verify")
    result = build_result()
    if args.verify and args.output.exists():
        observed = json.loads(args.output.read_text(encoding="utf-8"))
        require(observed == result, "sealed exact-results.json drift")
    if args.write:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "status": "PASS",
        "class_count": len(result["class_profiles"]),
        "forced_singleton_cells": result["forced_singleton_cells"],
        "endpoint_n3": result["aggregate_endpoint_certificate"]["n3"],
        "endpoint_integral": True,
        "improves_4158": result["result"]["improves_known_n3_cap"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
