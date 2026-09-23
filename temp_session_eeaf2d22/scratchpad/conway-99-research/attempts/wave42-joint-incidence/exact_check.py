#!/usr/bin/env python3
"""Exact Wave 42 reduction for the canonical rank-33 all-222 lift.

This checker proves necessary reductions for a simultaneous outside incidence
matrix B and validates one complete two-fibre concurrence certificate.  It
does not solve the remaining 60-block three-way matching or construct H.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Sequence

FORMAT = "wave42-joint-incidence-v1"
FROZEN_COMMIT = "ef49b60aafd67f9007f6c218c39fd50392453a1b"
SOURCE = Path("verification/wave41-allquotient-lifts/independent-results.json")
SOURCE_SHA256 = "062785a47ddb8f85ddec10a76a663c262ec9c60c133b681be5228639b022260b"
CORE_EDGE_SHA256 = "b0a9e7cc75d933597d43c9395e0192268b71ad88b93120a82dc662e64585b664"
CANONICAL_MASK = 51739
FIBRES = 3
FIBRE_SIZE = 12
X_SIZE = 36

# Exact Q_01 concurrence-preserving bijection.  Entry i gives the fibre-1
# nonmatching pair assigned to fibre-0 nonmatching pair i, under lexicographic
# pair order.
PAIR_01_CERTIFICATE = (
    57, 53, 28, 8, 21, 45, 38, 30, 50, 55, 46, 40, 47, 39, 31,
    52, 49, 16, 27, 14, 4, 25, 17, 41, 37, 22, 54, 44, 6, 35,
    51, 56, 42, 43, 12, 7, 18, 26, 15, 59, 33, 23, 24, 19, 34,
    13, 3, 48, 9, 58, 32, 2, 0, 1, 36, 11, 10, 29, 5, 20,
)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_source(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if sha256_bytes(raw) != SOURCE_SHA256:
        raise AssertionError("frozen Wave 41 source hash changed")
    result = json.loads(raw)
    witness = result["rank_identity"]["minimum_witness"]
    if witness["mask"] != CANONICAL_MASK:
        raise AssertionError("canonical mask changed")
    if witness["core_edges_sha256"] != CORE_EDGE_SHA256:
        raise AssertionError("canonical core edge hash changed")
    return result


def adjacency_from_edges(edges: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency = [[0] * X_SIZE for _ in range(X_SIZE)]
    seen: set[tuple[int, int]] = set()
    for edge in edges:
        if len(edge) != 2:
            raise AssertionError("malformed core edge")
        left, right = sorted(map(int, edge))
        if not 0 <= left < right < X_SIZE or (left, right) in seen:
            raise AssertionError("bad or duplicate core edge")
        seen.add((left, right))
        adjacency[left][right] = adjacency[right][left] = 1
    if len(seen) != 54 or set(map(sum, adjacency)) != {3}:
        raise AssertionError("core is not cubic on 36 vertices")
    return adjacency


def matrix_square(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(matrix)
    return [
        [
            sum(matrix[left][middle] * matrix[middle][right] for middle in range(size))
            for right in range(size)
        ]
        for left in range(size)
    ]


def forced_gram(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    square = matrix_square(adjacency)
    return [
        [
            (12 if left == right else 0)
            - adjacency[left][right]
            + 2
            - (1 if left // FIBRE_SIZE == right // FIBRE_SIZE else 0)
            - square[left][right]
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]


def components(adjacency: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    unseen = set(range(X_SIZE))
    result: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        seen = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor, value in enumerate(adjacency[vertex]):
                if value and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        unseen -= seen
        result.append(tuple(sorted(seen)))
    return sorted(result, key=lambda component: (len(component), component))


def four_cycle_count(adjacency: Sequence[Sequence[int]]) -> int:
    # Every four-cycle contributes its two opposite pairs to this sum.
    opposite_pair_sum = 0
    for left, right in itertools.combinations(range(X_SIZE), 2):
        common = sum(
            adjacency[left][middle] and adjacency[right][middle]
            for middle in range(X_SIZE)
        )
        opposite_pair_sum += common * (common - 1) // 2
    if opposite_pair_sum % 2:
        raise AssertionError("four-cycle opposite-pair sum has odd parity")
    return opposite_pair_sum // 2


def allowed_pairs(fibre: int, gram: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    start = fibre * FIBRE_SIZE
    return tuple(
        pair
        for pair in itertools.combinations(range(start, start + FIBRE_SIZE), 2)
        if gram[pair[0]][pair[1]] == 1
    )


def mixed_target(
    block: Sequence[int],
    adjacency: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    selected = set(block)
    return tuple(
        2
        - int(vertex in selected)
        - sum(adjacency[vertex][neighbor] for neighbor in selected)
        for vertex in range(X_SIZE)
    )


def candidate_census(
    pair_sets: Sequence[Sequence[tuple[int, int]]],
    gram: Sequence[Sequence[int]],
    adjacency: Sequence[Sequence[int]],
    small_component: frozenset[int],
) -> dict[str, object]:
    support_legal = 0
    component_legal = 0
    mixed_legal = 0
    pattern_counts: Counter[tuple[int, int, int]] = Counter()
    for parts in itertools.product(*pair_sets):
        block = tuple(itertools.chain.from_iterable(parts))
        if not all(
            gram[left][right] > 0
            for left, right in itertools.combinations(block, 2)
        ):
            continue
        support_legal += 1
        pattern = tuple(
            sum(vertex in small_component for vertex in pair)
            for pair in parts
        )
        if sum(pattern) != 2:
            continue
        component_legal += 1
        target = mixed_target(block, adjacency)
        if min(target) < 0:
            continue
        if sum(target) != 48:
            raise AssertionError("mixed target row sum changed")
        mixed_legal += 1
        pattern_counts[pattern] += 1
    return {
        "raw_pair_triples": 60**3,
        "gram_support_legal": support_legal,
        "after_forced_component_equality": component_legal,
        "after_mixed_BH_nonnegativity": mixed_legal,
        "mixed_legal_by_component_pattern": {
            str(pattern): count for pattern, count in sorted(pattern_counts.items())
        },
    }


def pair_concurrence(
    left_pairs: Sequence[tuple[int, int]],
    right_pairs: Sequence[tuple[int, int]],
    certificate: Sequence[int],
) -> list[list[int]]:
    if sorted(certificate) != list(range(60)):
        raise AssertionError("two-fibre certificate is not a permutation")
    result = [[0] * FIBRE_SIZE for _ in range(FIBRE_SIZE)]
    for left_index, right_index in enumerate(certificate):
        for left in left_pairs[left_index]:
            for right in right_pairs[right_index]:
                result[left][right - FIBRE_SIZE] += 1
    return result


def build_results(source_path: Path = SOURCE) -> dict[str, object]:
    source = read_source(source_path)
    witness = source["rank_identity"]["minimum_witness"]
    adjacency = adjacency_from_edges(witness["core_edges"])
    gram = forced_gram(adjacency)
    if gram != [list(row) for row in zip(*gram)]:
        raise AssertionError("forced Gram is not symmetric")
    if set(gram[index][index] for index in range(X_SIZE)) != {10}:
        raise AssertionError("forced Gram diagonal changed")
    if set(map(sum, gram)) != {60} or min(map(min, gram)) < 0:
        raise AssertionError("forced Gram row sums or nonnegativity changed")

    core_components = components(adjacency)
    if [len(component) for component in core_components] != [12, 24]:
        raise AssertionError("canonical core component split changed")
    fibre_balances = [
        [sum(vertex // FIBRE_SIZE == fibre for vertex in component) for fibre in range(3)]
        for component in core_components
    ]
    if fibre_balances != [[4, 4, 4], [8, 8, 8]]:
        raise AssertionError("canonical component fibre balance changed")
    small = frozenset(core_components[0])

    pair_sets = tuple(allowed_pairs(fibre, gram) for fibre in range(3))
    if [len(pairs) for pairs in pair_sets] != [60, 60, 60]:
        raise AssertionError("same-fibre nonmatching-pair census changed")
    same_fibre_values = Counter(
        gram[left][right]
        for fibre in range(3)
        for left, right in itertools.combinations(
            range(fibre * FIBRE_SIZE, (fibre + 1) * FIBRE_SIZE), 2
        )
    )
    if same_fibre_values != Counter({1: 180, 0: 18}):
        raise AssertionError("same-fibre Gram entries changed")

    indicator = [int(vertex in small) for vertex in range(X_SIZE)]
    component_first_moment = 10 * len(small)
    component_second_moment = sum(
        indicator[left] * gram[left][right] * indicator[right]
        for left in range(X_SIZE)
        for right in range(X_SIZE)
    )
    cauchy_floor = component_first_moment**2 // 60
    if (component_first_moment, component_second_moment, cauchy_floor) != (
        120,
        240,
        240,
    ):
        raise AssertionError("component Cauchy equality changed")

    small_pair_count_distributions = []
    for pairs in pair_sets:
        small_pair_count_distributions.append(
            dict(
                sorted(
                    Counter(
                        sum(vertex in small for vertex in pair)
                        for pair in pairs
                    ).items()
                )
            )
        )
    if small_pair_count_distributions != [
        {0: 24, 1: 32, 2: 4},
        {0: 24, 1: 32, 2: 4},
        {0: 24, 1: 32, 2: 4},
    ]:
        raise AssertionError("component pair distribution changed")

    required_block_patterns = {
        "(0, 0, 2)": 4,
        "(0, 1, 1)": 16,
        "(0, 2, 0)": 4,
        "(1, 0, 1)": 16,
        "(1, 1, 0)": 16,
        "(2, 0, 0)": 4,
    }
    census = candidate_census(pair_sets, gram, adjacency, small)
    if (
        census["gram_support_legal"],
        census["after_forced_component_equality"],
        census["after_mixed_BH_nonnegativity"],
    ) != (118718, 49736, 45032):
        raise AssertionError("candidate reduction census changed")

    target_01 = [
        row[FIBRE_SIZE : 2 * FIBRE_SIZE]
        for row in gram[:FIBRE_SIZE]
    ]
    certificate_concurrence = pair_concurrence(
        pair_sets[0], pair_sets[1], PAIR_01_CERTIFICATE
    )
    if certificate_concurrence != target_01:
        raise AssertionError("two-fibre certificate does not realize Q_01")
    pair_pattern_counts = Counter(
        (
            sum(vertex in small for vertex in pair_sets[0][left]),
            sum(vertex in small for vertex in pair_sets[1][right]),
        )
        for left, right in enumerate(PAIR_01_CERTIFICATE)
    )
    expected_pair_patterns = Counter(
        {(0, 0): 4, (0, 1): 16, (0, 2): 4, (1, 0): 16, (1, 1): 16, (2, 0): 4}
    )
    if pair_pattern_counts != expected_pair_patterns:
        raise AssertionError("two-fibre component marginal changed")

    c4 = four_cycle_count(adjacency)
    if c4 != 10:
        raise AssertionError("canonical core four-cycle count changed")
    overlap_counts = {
        "0": 438 + 2 * c4,
        "1": 1044 - 4 * c4,
        "2": 288 + 2 * c4,
    }
    if sum(overlap_counts.values()) != 1770:
        raise AssertionError("block-overlap census does not total C(60,2)")

    certificate_payload = list(PAIR_01_CERTIFICATE)
    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "format": FORMAT,
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Conditional on n3=4158, r3=12, all edges type 222, and the "
            "canonical Wave 41 rank-33 lift mask 51739: exact necessary "
            "simultaneous B/H reduction. No symmetry is assumed."
        ),
        "input": {
            str(source_path).replace("\\", "/"): SOURCE_SHA256,
            "canonical_core_edges_sha256": CORE_EDGE_SHA256,
            "canonical_mask": CANONICAL_MASK,
        },
        "canonical_core": {
            "components": [list(component) for component in core_components],
            "component_sizes": [12, 24],
            "component_fibre_balances": fibre_balances,
            "four_cycle_count": c4,
            "forced_gram_diagonal": 10,
            "forced_gram_row_sum": 60,
            "forced_gram_entry_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(itertools.chain.from_iterable(gram)).items()
                )
            },
        },
        "exhaustive_B_reduction": {
            "same_fibre_gram_distribution": {
                str(value): count for value, count in sorted(same_fibre_values.items())
            },
            "nonmatching_pairs_per_fibre": [60, 60, 60],
            "reason_each_pair_is_used_once": (
                "Every B-column selects two vertices per fibre. Same-fibre "
                "matching pairs have Gram entry 0 and all other pairs have "
                "entry 1, so the 60 nonmatching pairs occur exactly once."
            ),
            "component_Cauchy_equality": {
                "sum_block_intersections": component_first_moment,
                "sum_squared_block_intersections": component_second_moment,
                "Cauchy_floor": cauchy_floor,
                "conclusion": (
                    "All 60 block intersections with the 12-vertex component "
                    "equal 2."
                ),
            },
            "pair_small_component_count_distribution_per_fibre": (
                small_pair_count_distributions
            ),
            "required_60_block_component_patterns": required_block_patterns,
            "candidate_census": census,
            "complete_remaining_model": (
                "Select 60 of the 45032 mixed-legal candidates so every one "
                "of the three fibres' 60 nonmatching pairs is used once and "
                "every cross-fibre point pair has its exact forced Gram "
                "multiplicity. This is an exhaustive three-way matching "
                "formulation, not a restricted symmetry model."
            ),
        },
        "two_fibre_positive_control": {
            "certificate": certificate_payload,
            "certificate_sha256": sha256_bytes(canonical_bytes(certificate_payload)),
            "is_permutation": True,
            "realizes_exact_Q01": True,
            "component_pattern_marginal": {
                str(pattern): count
                for pattern, count in sorted(pair_pattern_counts.items())
            },
            "scope": (
                "Complete X0-X1 pair projection only. It does not select "
                "fibre-2 pairs or provide a 60-column B."
            ),
        },
        "forced_H_boundary_if_B_exists": {
            "block_overlap_pair_counts_0_1_2": overlap_counts,
            "H_edges_by_block_overlap": {"0": 96, "1": 144, "2": 0},
            "H_triangles": 32,
            "H_four_cycles": 171 + c4,
            "identities": {
                "XX": "BB^T=12I-A_X+2J-RR^T-A_X^2",
                "XY": "BH=(J/3-I-A_X)B",
                "YY": "B^TB+H^2=12I-H+2J",
            },
        },
        "bounded_solver_diagnostics_not_evidence": {
            "generic_MILP": (
                "No incumbent in a 45-second run; timeout is not evidence."
            ),
            "one_fixed_two_fibre_stage": (
                "One exact first-stage SAT model had an UNSAT fixed "
                "third-fibre extension, but no proof was retained and other "
                "first-stage models were not exhausted. This is not evidence "
                "of global nonexistence."
            ),
        },
        "status_wall": {
            "canonical_full_B": "UNKNOWN",
            "compatible_8_regular_H": "UNKNOWN",
            "all_264_rank33_lifts": "NOT_CHECKED",
            "all_37378_triangle_free_lifts": "NOT_CHECKED",
            "scoped_branch_excluded": False,
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_results(args.source)
    rendered = canonical_bytes(result)
    if args.verify is not None:
        if args.verify.read_bytes() != rendered:
            raise SystemExit("verification mismatch")
        print("verification: PASS")
        return
    if args.output is not None:
        args.output.write_bytes(rendered)
    else:
        print(rendered.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
