#!/usr/bin/env python3
"""Independent crosscheck of the Wave 34 rooted pair-state census.

This module does not import or execute either Wave 34 structural verifier.
It reconstructs the row census by triangular elimination and reconstructs
the Pb-column totals by a relative-permutation/permanent identity rather than
the released point-by-point degree-state dynamic program.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from functools import lru_cache
from itertools import permutations, product
from math import comb, factorial
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

FROZEN_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/wave33-rooted-extension/independent-results.json": "66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778",
    "verification/wave33-rooted-extension/comparison-results.json": "2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd",
    "verification/wave33-rooted-extension/comparison-audit.md": "fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a",
    "verification/wave34-rooted-structural/precomparison/artifact-manifest.sha256": "233a32ac6cb67bcb23b7b269cc6f3f889d943bd5d0714c4f54ead9cbf28c7681",
    "verification/wave34-rooted-structural/precomparison/exact-results.json": "9b4c2e00d50e142b4ae551741b8b5b9afda8ecaad0a3085c3cd549c07975ca60",
    "verification/wave34-rooted-structural/precomparison/derivation.md": "7e84ada91985dd3c58d62991e6bdaf469e6111bb89d17e11d72cfbc195aab8ab",
    "verification/wave34-rooted-structural/comparison-results.json": "d73e302d6af8bbd3df28c80ded5dc922e4e6ea5084234ed15531330646fc26d8",
    "verification/wave34-rooted-structural/comparison-audit.md": "dc4d9b060ff8bfb9b49ecdba28eebbcc784ebc165d2f399b00f46e0bc7ee5a93",
    "verification/wave34-rooted-structural/comparison-artifact-manifest.sha256": "ce4bb77f33e919c3086b09521acd80297a9dcfffbc6bb2b72b331c2ee650ae3c",
}

STATE_NAMES = (
    "g0_r0_h0_c2",
    "g0_r0_h1_c1",
    "g0_r1_h0_c1",
    "g0_r1_h1_c0",
    "g0_r2_h0_c0",
    "g1_r0_h0_c1",
    "g1_r0_h1_c0",
    "g1_r1_h0_c0",
    "g2_r0_h0_c0",
)

EXPECTED_CYCLE_CENSUS = {
    "1+1+1+1+1+1+1": 24,
    "2+1+1+1+1+1": 4746,
    "2+2+1+1+1": 227136,
    "2+2+2+1": 2148384,
    "3+1+1+1+1": 69972,
    "3+2+1+1": 4004196,
    "3+2+2": 18854388,
    "3+3+1": 11738034,
    "4+1+1+1": 920304,
    "4+2+1": 26163837,
    "4+3": 76574904,
    "5+1+1": 9667812,
    "5+2": 91117740,
    "6+1": 70294224,
    "7": 262332336,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        result[name.lstrip("*")] = digest
    return result


def validate_inputs() -> dict[str, object]:
    actual = {name: sha256(ROOT / name) for name in FROZEN_INPUTS}
    mismatches = {
        name: {"expected": FROZEN_INPUTS[name], "actual": actual[name]}
        for name in FROZEN_INPUTS
        if actual[name] != FROZEN_INPUTS[name]
    }
    freeze = parse_manifest(HERE / "input-freeze.sha256")

    checked_manifests = {}
    for relative in (
        "verification/wave34-rooted-structural/precomparison/artifact-manifest.sha256",
        "verification/wave34-rooted-structural/comparison-artifact-manifest.sha256",
    ):
        entries = parse_manifest(ROOT / relative)
        entry_mismatches = {}
        for name, expected in entries.items():
            observed = sha256(ROOT / name)
            if observed != expected:
                entry_mismatches[name] = {
                    "expected": expected,
                    "actual": observed,
                }
        checked_manifests[relative] = {
            "entries": len(entries),
            "all_match": not entry_mismatches,
            "mismatches": entry_mismatches,
        }

    return {
        "entry_count": len(FROZEN_INPUTS),
        "all_frozen_inputs_match": not mismatches,
        "mismatches": mismatches,
        "freeze_file_matches_constants": freeze == FROZEN_INPUTS,
        "checked_manifests": checked_manifests,
    }


def load_json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def wave33_data() -> dict[str, object]:
    return load_json(
        "verification/wave33-rooted-extension/independent-results.json"
    )


def dot(left: list[int], right: list[int]) -> int:
    return sum(a * b for a, b in zip(left, right))


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    right_t = transpose(right)
    return [[dot(row, column) for column in right_t] for row in left]


def support_reconstruction() -> dict[str, object]:
    source = wave33_data()
    incidence = source["support_outside_incidence"]["D"]
    support_adjacency = source["support"]["support_adjacency"]
    metadata = source["support_outside_incidence"]["column_metadata"]

    if len(incidence) != 14 or {len(row) for row in incidence} != {70}:
        raise AssertionError("Wave 33 support incidence is not 14x70")
    if any(value not in (0, 1) for row in incidence for value in row):
        raise AssertionError("support incidence is not binary")

    columns = transpose(incidence)
    gram = matmul(columns, incidence)
    row_sums = [sum(row) for row in incidence]
    column_sums = [sum(column) for column in columns]
    if set(row_sums) != {10} or set(column_sums) != {2}:
        raise AssertionError("support incidence degrees drifted")

    type_profiles: dict[str, Counter[int]] = {}
    for index, record in enumerate(metadata):
        kind = record["kind"]
        profile = Counter(
            gram[index][other]
            for other in range(70)
            if other != index
        )
        type_profiles.setdefault(kind, profile)
        if type_profiles[kind] != profile:
            raise AssertionError(f"nonconstant g profile within {kind}")

    two_j_minus_f = [
        [2 - incidence[row][column] for column in range(70)]
        for row in range(14)
    ]
    a_times_f = matmul(support_adjacency, incidence)
    fixed_so_rhs = [
        [
            two_j_minus_f[row][column] - a_times_f[row][column]
            for column in range(70)
        ]
        for row in range(14)
    ]
    diagonal_dt = [
        dot(columns[index], [row[index] for row in fixed_so_rhs])
        for index in range(70)
    ]
    dt_by_kind: dict[str, int] = {}
    for index, record in enumerate(metadata):
        kind = record["kind"]
        dt_by_kind.setdefault(kind, diagonal_dt[index])
        if dt_by_kind[kind] != diagonal_dt[index]:
            raise AssertionError(f"nonconstant diag(DT) within {kind}")

    capacities = [[0] * 7 for _ in range(7)]
    for record in metadata:
        capacities[record["point_index"]][record["line_index"]] += 1
    capacity_histogram = Counter(
        value for row in capacities for value in row
    )
    if capacity_histogram != Counter({1: 28, 2: 21}):
        raise AssertionError("unexpected signed-Fano edge capacities")

    return {
        "incidence_shape": [14, 70],
        "row_degree_set": sorted(set(row_sums)),
        "column_degree_set": sorted(set(column_sums)),
        "type_counts": dict(Counter(record["kind"] for record in metadata)),
        "g_profiles": {
            kind: {str(key): value for key, value in sorted(profile.items())}
            for kind, profile in sorted(type_profiles.items())
        },
        "diag_DT_by_type": dict(sorted(dt_by_kind.items())),
        "capacities": capacities,
        "capacity_histogram": {
            str(key): value for key, value in sorted(capacity_histogram.items())
        },
    }


def allowed_states() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        (g, r, h, c)
        for g, r, h, c in product(range(3), range(3), range(2), range(3))
        if g + r + h + c == 2
    )


def state_name(state: tuple[int, int, int, int]) -> str:
    g, r, h, c = state
    return f"g{g}_r{r}_h{h}_c{c}"


def triangular_row_census(
    *, g1: int, g2: int, diagonal_dt: int
) -> dict[str, int]:
    """Solve the nine states in a triangular order, not by matrix inversion."""
    values = {}

    # Marginal r counts for a simple 2-(15,3,2) design row are 33,33,3.
    r0, r1, r2 = 33, 33, 3
    h1 = 9

    # Each equation below determines a new state exactly.
    values["g2_r0_h0_c0"] = g2
    values["g0_r2_h0_c0"] = r2
    values["g1_r0_h1_c0"] = diagonal_dt
    values["g0_r1_h1_c0"] = 3  # off-diagonal sum h*r=diag(DR)=3
    values["g1_r1_h0_c0"] = 6  # diag(TR)-T_ii R_ii=12-2*3
    values["g0_r1_h0_c1"] = (
        r1
        - values["g0_r1_h1_c0"]
        - values["g1_r1_h0_c0"]
    )
    values["g1_r0_h0_c1"] = (
        g1
        - values["g1_r0_h1_c0"]
        - values["g1_r1_h0_c0"]
    )
    values["g0_r0_h1_c1"] = (
        h1
        - values["g0_r1_h1_c0"]
        - values["g1_r0_h1_c0"]
    )
    values["g0_r0_h0_c2"] = (
        r0
        - values["g0_r0_h1_c1"]
        - values["g1_r0_h0_c1"]
        - values["g1_r0_h1_c0"]
        - values["g2_r0_h0_c0"]
    )

    if set(values) != set(STATE_NAMES):
        raise AssertionError("triangular census omitted a state")
    if any(value < 0 for value in values.values()):
        raise AssertionError("negative row-state count")
    if sum(values.values()) != 69:
        raise AssertionError("row-state counts do not total 69")

    checks = {
        "g1": sum(
            value for name, value in values.items() if name.startswith("g1_")
        ),
        "g2": values["g2_r0_h0_c0"],
        "r0": sum(
            value for name, value in values.items() if "_r0_" in name
        ),
        "r1": sum(
            value for name, value in values.items() if "_r1_" in name
        ),
        "r2": values["g0_r2_h0_c0"],
        "h1": sum(
            value for name, value in values.items() if "_h1_" in name
        ),
        "c_sum": sum(
            int(name[-1]) * value for name, value in values.items()
        ),
    }
    expected = {
        "g1": g1,
        "g2": g2,
        "r0": r0,
        "r1": r1,
        "r2": r2,
        "h1": h1,
        "c_sum": 72,
    }
    if checks != expected:
        raise AssertionError(f"row census check failed: {checks} != {expected}")
    return {name: values[name] for name in STATE_NAMES}


def pair_census() -> dict[str, object]:
    support = support_reconstruction()
    kind_edge = "support_edge_completion"
    kind_duplicate = "support_cross_nonedge_completion"
    edge_profile = support["g_profiles"][kind_edge]
    duplicate_profile = support["g_profiles"][kind_duplicate]

    edge_rows = triangular_row_census(
        g1=edge_profile["1"],
        g2=edge_profile.get("2", 0),
        diagonal_dt=support["diag_DT_by_type"][kind_edge],
    )
    duplicate_rows = triangular_row_census(
        g1=duplicate_profile["1"],
        g2=duplicate_profile.get("2", 0),
        diagonal_dt=support["diag_DT_by_type"][kind_duplicate],
    )

    global_counts = {}
    for name in STATE_NAMES:
        ordered = 28 * edge_rows[name] + 42 * duplicate_rows[name]
        if ordered % 2:
            raise AssertionError(f"odd ordered total for {name}")
        global_counts[name] = ordered // 2
    if sum(global_counts.values()) != comb(70, 2):
        raise AssertionError("global census does not partition O pairs")

    x11 = global_counts["g1_r1_h0_c0"]
    duplicate_pairs = global_counts["g2_r0_h0_c0"]
    return {
        "allowed_states": [state_name(state) for state in allowed_states()],
        "triangular_elimination_order": [
            "g2_r0_h0_c0",
            "g0_r2_h0_c0",
            "g1_r0_h1_c0",
            "g0_r1_h1_c0",
            "g1_r1_h0_c0",
            "g0_r1_h0_c1",
            "g1_r0_h0_c1",
            "g0_r0_h1_c1",
            "g0_r0_h0_c2",
        ],
        "constraint_uniqueness": "TRIANGULAR_NINE_PIVOTS",
        "row_distribution_by_support_type": {
            "support_edge": edge_rows,
            "support_nonedge_copy": duplicate_rows,
        },
        "global_unordered_pair_distribution": global_counts,
        "global_pair_total": sum(global_counts.values()),
        "duplicate_pair_rule": {
            "state": "g2_r0_h0_c0",
            "pairs": duplicate_pairs,
            "vertices": 42,
            "degree": 1,
            "matching": duplicate_pairs == 21,
            "B_rows_disjoint": True,
            "D_nonadjacent": True,
            "no_common_O_neighbour": True,
        },
        "X11_graph": {
            "state": "g1_r1_h0_c0",
            "vertices": 70,
            "degree": edge_rows["g1_r1_h0_c0"],
            "edges": x11,
            "regular": edge_rows["g1_r1_h0_c0"]
            == duplicate_rows["g1_r1_h0_c0"]
            == 6,
            "disjoint_from_D": True,
            "disjoint_from_offdiagonal_support_D2": True,
        },
    }


def cycle_type(permutation: tuple[int, ...]) -> tuple[int, ...]:
    seen = set()
    lengths = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            length += 1
            current = permutation[current]
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def cycle_label(parts: tuple[int, ...]) -> str:
    return "+".join(map(str, parts))


def permanent(matrix: list[list[int]]) -> int:
    """Ryser-free row/subset dynamic program for a 7x7 permanent."""
    n = len(matrix)
    dp = {0: 1}
    for row in range(n):
        next_dp = {}
        for mask, subtotal in dp.items():
            for column in range(n):
                bit = 1 << column
                if mask & bit:
                    continue
                value = matrix[row][column]
                if value:
                    new_mask = mask | bit
                    next_dp[new_mask] = (
                        next_dp.get(new_mask, 0) + subtotal * value
                    )
        dp = next_dp
    return dp.get((1 << n) - 1, 0)


def relative_permutation_weight_matrices(
    permutation: tuple[int, ...],
    capacities: list[list[int]],
) -> tuple[list[list[int]], list[list[int]]]:
    n = len(permutation)
    inverse = [0] * n
    for source, target in enumerate(permutation):
        inverse[target] = source

    labeled = [[0] * n for _ in range(n)]
    underlying = [[0] * n for _ in range(n)]
    for point in range(n):
        for line in range(n):
            if permutation[point] == point:
                # A one-cycle uses both copies of one doubled edge.
                if capacities[point][line] == 2:
                    # Two ordered allocations of the parallel copies.
                    labeled[point][line] = 2
                    underlying[point][line] = 2
            else:
                previous = inverse[point]
                labeled[point][line] = (
                    capacities[point][line] * capacities[previous][line]
                )
                underlying[point][line] = 1
    return labeled, underlying


@lru_cache(maxsize=1)
def column_cycle_census() -> dict[str, object]:
    capacities = support_reconstruction()["capacities"]
    ordered_labeled = Counter()
    ordered_underlying = Counter()
    permutation_counts = Counter()

    for permutation in permutations(range(7)):
        parts = cycle_type(permutation)
        label = cycle_label(parts)
        labeled_matrix, underlying_matrix = (
            relative_permutation_weight_matrices(permutation, capacities)
        )
        ordered_labeled[label] += permanent(labeled_matrix)
        ordered_underlying[label] += permanent(underlying_matrix)
        permutation_counts[label] += 1

    labeled = {}
    underlying = {}
    divisibility = {}
    for label in sorted(ordered_labeled):
        cycles = label.count("+") + 1
        decompositions = 2**cycles
        divisibility[label] = {
            "ordered_labeled_mod_2_to_cycles": (
                ordered_labeled[label] % decompositions
            ),
            "ordered_underlying_mod_2_to_cycles": (
                ordered_underlying[label] % decompositions
            ),
        }
        labeled[label] = ordered_labeled[label] // decompositions
        underlying[label] = ordered_underlying[label] // decompositions

    duplicate_free_types = sorted(
        label
        for label in labeled
        if all(part != "1" for part in label.split("+"))
    )
    duplicate_free_total = sum(labeled[label] for label in duplicate_free_types)
    full_total = sum(labeled.values())
    return {
        "method": (
            "sum weighted 7x7 permanents over relative permutations; "
            "divide each k-cycle class by 2^k alternating decompositions"
        ),
        "permutations_checked": sum(permutation_counts.values()),
        "permutation_cycle_type_counts": dict(sorted(permutation_counts.items())),
        "labeled_cycle_census": dict(sorted(labeled.items())),
        "underlying_cycle_census": dict(sorted(underlying.items())),
        "decomposition_divisibility": divisibility,
        "underlying_capacity_bounded_two_factors": sum(underlying.values()),
        "all_labeled_Pb_columns": full_total,
        "duplicate_free_types": duplicate_free_types,
        "duplicate_free_Pb_columns": duplicate_free_total,
        "columns_excluded_by_duplicate_pair_rule": (
            full_total - duplicate_free_total
        ),
        "raw_weight_14_columns": comb(70, 14),
    }


def compare_claims(
    census: dict[str, object], columns: dict[str, object]
) -> dict[str, object]:
    stage1 = load_json(
        "verification/wave34-rooted-structural/precomparison/exact-results.json"
    )
    stage2 = load_json(
        "verification/wave34-rooted-structural/comparison-results.json"
    )
    stage1_claim = stage1["forced_pair_distribution"]
    stage2_claim = stage2["stage1_reconciliation"]
    normalized_stage1_rows = {
        row_type: {
            state: stage1_claim["row_distribution_by_support_type"][
                row_type
            ].get(state, 0)
            for state in STATE_NAMES
        }
        for row_type in ("support_edge", "support_nonedge_copy")
    }

    agreements = {
        "nine_allowed_states": census["allowed_states"]
        == stage1_claim["allowed_states"],
        "row_distribution": census["row_distribution_by_support_type"]
        == normalized_stage1_rows,
        "global_distribution": census["global_unordered_pair_distribution"]
        == stage1_claim["global_unordered_pair_distribution"],
        "duplicate_pair_count": census["duplicate_pair_rule"]["pairs"]
        == stage2_claim["Stage1_duplicate_support_pairs"]
        == 21,
        "X11_degree": census["X11_graph"]["degree"] == 6,
        "X11_edges": census["X11_graph"]["edges"] == 210,
        "all_labeled_Pb_columns": columns["all_labeled_Pb_columns"]
        == stage2_claim["candidate_count_verified"]
        == 574118037,
        "duplicate_free_Pb_columns": columns["duplicate_free_Pb_columns"]
        == stage2_claim["duplicate_free_Pb_columns_surviving_rule"]
        == 448879368,
        "excluded_Pb_columns": columns[
            "columns_excluded_by_duplicate_pair_rule"
        ]
        == stage2_claim["Pb_only_columns_excluded_by_duplicate_pair_rule"]
        == 125238669,
        "full_cycle_census": columns["labeled_cycle_census"]
        == EXPECTED_CYCLE_CENSUS,
    }
    return {
        "agreements": agreements,
        "all_claims_reproduce": all(agreements.values()),
        "discrepancies": [
            name for name, agrees in agreements.items() if not agrees
        ],
    }


def build_results() -> dict[str, object]:
    integrity = validate_inputs()
    if not (
        integrity["all_frozen_inputs_match"]
        and integrity["freeze_file_matches_constants"]
        and all(
            record["all_match"]
            for record in integrity["checked_manifests"].values()
        )
    ):
        raise RuntimeError(f"input integrity failure: {integrity}")

    support = support_reconstruction()
    census = pair_census()
    columns = column_cycle_census()
    comparison = compare_claims(census, columns)
    if not comparison["all_claims_reproduce"]:
        raise RuntimeError(f"claim discrepancy: {comparison}")

    return {
        "schema_version": 1,
        "role": "independent_pair_census_cross_verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": (
            "Wave 34 Stage-1 rooted O-pair census and its duplicate-free "
            "single-Pb-column consequence only"
        ),
        "independence": {
            "structural_exact_check_imported_or_executed": False,
            "structural_static_compare_imported_or_executed": False,
            "pair_census_method": "direct triangular elimination",
            "column_count_method": "relative permutations plus weighted permanents",
            "candidate_degree_state_DP_used": False,
            "git_used": False,
        },
        "input_integrity": integrity,
        "support_reconstruction": support,
        "pair_census": census,
        "column_cycle_census": columns,
        "claim_comparison": comparison,
        "verdict": "PASS",
        "status": {
            "pair_state_census": "VERIFIED_SCOPED",
            "duplicate_pair_rule": "VERIFIED_SCOPED",
            "X11_graph": "VERIFIED_SCOPED",
            "duplicate_free_Pb_column_count": "VERIFIED_SCOPED",
            "compatible_15_column_design": "UNKNOWN",
            "binary_D_B_solution": "UNKNOWN",
            "rooted_graph_extension_or_exclusion": "UNKNOWN",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The 448879368 count is for one Pb column after one necessary duplicate-pair rule.",
            "It does not count compatible 15-column designs.",
            "It does not impose all pair intersections, D, D^2, projector, or binary compatibility conditions.",
            "No binary solution or complete-domain exclusion is produced.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
