#!/usr/bin/env python3
"""Exact finite checks for Wave 80.

This script does not assume that an srg(99,14,1,2) exists.  It verifies
parameter-level identities and exhausts the five-coordinate cases used in
the conditional dual-distance argument.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


P = 7
N = 99
K = 44
Q_ENDPOINT = 16
R_ENDPOINT = 28


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rank_mod(matrix: list[list[int]], prime: int = P) -> int:
    a = [[entry % prime for entry in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(rank, rows) if a[row][col] % prime),
            None,
        )
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, prime)
        a[rank] = [(entry * inverse) % prime for entry in a[rank]]
        for row in range(rows):
            if row == rank or a[row][col] == 0:
                continue
            multiple = a[row][col]
            a[row] = [
                (left - multiple * right) % prime
                for left, right in zip(a[row], a[rank])
            ]
        rank += 1
    return rank


def kernel_basis_mod(
    matrix: list[list[int]], prime: int = P
) -> list[list[int]]:
    a = [[entry % prime for entry in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank = 0
    pivots: list[int] = []
    for col in range(cols):
        pivot = next(
            (row for row in range(rank, rows) if a[row][col] % prime),
            None,
        )
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, prime)
        a[rank] = [(entry * inverse) % prime for entry in a[rank]]
        for row in range(rows):
            if row == rank or a[row][col] == 0:
                continue
            multiple = a[row][col]
            a[row] = [
                (left - multiple * right) % prime
                for left, right in zip(a[row], a[rank])
            ]
        pivots.append(col)
        rank += 1

    free = [col for col in range(cols) if col not in pivots]
    basis: list[list[int]] = []
    for free_col in free:
        vector = [0] * cols
        vector[free_col] = 1
        for row, pivot_col in enumerate(pivots):
            vector[pivot_col] = (-a[row][free_col]) % prime
        basis.append(vector)
    return basis


def all_projective_full_support_kernel_vectors(
    matrix: list[list[int]], prime: int = P
) -> list[tuple[int, ...]]:
    basis = kernel_basis_mod(matrix, prime)
    if not basis:
        return []
    vectors: set[tuple[int, ...]] = set()
    for coefficients in itertools.product(range(prime), repeat=len(basis)):
        if not any(coefficients):
            continue
        vector = [
            sum(
                coefficients[index] * basis[index][coordinate]
                for index in range(len(basis))
            )
            % prime
            for coordinate in range(len(matrix))
        ]
        if not all(vector):
            continue
        inverse = pow(vector[0], -1, prime)
        vectors.add(tuple((entry * inverse) % prime for entry in vector))
    return sorted(vectors)


def adjacency_from_mask(order: int, mask: int) -> list[list[int]]:
    adjacency = [[0] * order for _ in range(order)]
    bit = 0
    for left in range(order):
        for right in range(left + 1, order):
            if (mask >> bit) & 1:
                adjacency[left][right] = 1
                adjacency[right][left] = 1
            bit += 1
    return adjacency


def seidel(adjacency: list[list[int]]) -> list[list[int]]:
    return [
        [
            0
            if left == right
            else (1 if adjacency[left][right] else -1)
            for right in range(len(adjacency))
        ]
        for left in range(len(adjacency))
    ]


def locally_srg_admissible(adjacency: list[list[int]]) -> bool:
    """Necessary induced-subgraph conditions from lambda=1 and mu=2."""

    order = len(adjacency)
    for left in range(order):
        for right in range(left + 1, order):
            common = sum(
                adjacency[left][third] and adjacency[right][third]
                for third in range(order)
            )
            if adjacency[left][right] and common > 1:
                return False
            if not adjacency[left][right] and common > 2:
                return False
    return True


def canonical_graph_bits(adjacency: list[list[int]]) -> str:
    order = len(adjacency)
    edges = [
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    ]
    return min(
        "".join(
            str(adjacency[permutation[left]][permutation[right]])
            for left, right in edges
        )
        for permutation in itertools.permutations(range(order))
    )


def outside_patterns(
    coefficients: tuple[int, ...], prime: int = P
) -> list[tuple[int, ...]]:
    """Patterns satisfying the outside-coordinate equation.

    From Sx=0 and S=2A-J+I, an outside vertex with incidence vector p must
    satisfy 2 sum_i p_i x_i = sum_i x_i modulo seven.
    """

    target = sum(coefficients) * pow(2, -1, prime) % prime
    return [
        pattern
        for pattern in itertools.product((0, 1), repeat=len(coefficients))
        if sum(
            incidence * coefficient
            for incidence, coefficient in zip(pattern, coefficients)
        )
        % prime
        == target
    ]


def principal_small_checks() -> dict[str, object]:
    records: dict[str, object] = {}
    for order in (2, 3, 4):
        edge_count = math.comb(order, 2)
        determinants_mod_seven: set[int] = set()
        singular_count = 0
        for mask in range(1 << edge_count):
            matrix = seidel(adjacency_from_mask(order, mask))
            rank = rank_mod(matrix)
            if rank < order:
                singular_count += 1
            # Determinant is needed only modulo seven; elimination rank plus
            # direct permutation expansion is tiny at orders at most four.
            determinant = 0
            for permutation in itertools.permutations(range(order)):
                inversions = sum(
                    permutation[i] > permutation[j]
                    for i in range(order)
                    for j in range(i + 1, order)
                )
                term = -1 if inversions % 2 else 1
                for row in range(order):
                    term *= matrix[row][permutation[row]]
                determinant += term
            determinants_mod_seven.add(determinant % P)
        require(singular_count == 0, f"singular Seidel block at order {order}")
        records[str(order)] = {
            "labelled_sign_patterns": 1 << edge_count,
            "singular_mod_7": singular_count,
            "determinants_mod_7": sorted(determinants_mod_seven),
        }
    return records


def five_support_exhaustion() -> dict[str, object]:
    order = 5
    edge_count = math.comb(order, 2)
    admissible = 0
    singular_with_full_support = 0
    projective_relations = 0
    impossible_outside_relations = 0
    classes: dict[str, dict[str, object]] = {}

    for mask in range(1 << edge_count):
        adjacency = adjacency_from_mask(order, mask)
        if not locally_srg_admissible(adjacency):
            continue
        admissible += 1
        matrix = seidel(adjacency)
        relations = all_projective_full_support_kernel_vectors(matrix)
        if not relations:
            continue
        singular_with_full_support += 1
        canonical = canonical_graph_bits(adjacency)
        degrees = sorted(sum(row) for row in adjacency)
        record = classes.setdefault(
            canonical,
            {
                "canonical_graph_bits": canonical,
                "edge_count": sum(degrees) // 2,
                "degree_sequence": degrees,
                "labelled_count": 0,
                "coefficient_multisets": set(),
            },
        )
        record["labelled_count"] = int(record["labelled_count"]) + 1
        for relation in relations:
            projective_relations += 1
            patterns = outside_patterns(relation)
            if not patterns:
                impossible_outside_relations += 1
            record["coefficient_multisets"].add(tuple(sorted(relation)))

    require(admissible == 683, "five-vertex admissible count drift")
    require(
        singular_with_full_support == 132,
        "five-vertex singular full-support count drift",
    )
    require(len(classes) == 3, "five-vertex isomorphism class count drift")
    require(
        projective_relations == impossible_outside_relations,
        "a five-support relation admits an outside vertex pattern",
    )
    require(
        sorted(int(record["labelled_count"]) for record in classes.values())
        == [12, 60, 60],
        "five-vertex labelled orbit counts drift",
    )

    serial_classes = []
    for canonical in sorted(classes):
        record = classes[canonical]
        serial_classes.append(
            {
                "canonical_graph_bits": canonical,
                "edge_count": record["edge_count"],
                "degree_sequence": record["degree_sequence"],
                "labelled_count": record["labelled_count"],
                "coefficient_multisets": [
                    list(values)
                    for values in sorted(record["coefficient_multisets"])
                ],
                "outside_pattern_count": 0,
            }
        )

    return {
        "all_labelled_graphs": 1 << edge_count,
        "locally_srg_admissible": admissible,
        "singular_with_full_support": singular_with_full_support,
        "projective_full_support_relations": projective_relations,
        "relations_with_no_outside_pattern": impossible_outside_relations,
        "isomorphism_classes": serial_classes,
    }


def six_support_positive_control() -> dict[str, object]:
    """One exact control showing that the support-five argument stops."""

    order = 6
    mask = 36
    adjacency = adjacency_from_mask(order, mask)
    require(
        locally_srg_admissible(adjacency),
        "six-support positive control fails local SRG bounds",
    )
    relations = all_projective_full_support_kernel_vectors(seidel(adjacency))
    require(relations, "six-support positive control lost its kernel")
    relation = relations[0]
    patterns = outside_patterns(relation)
    require(patterns, "six-support positive control lost outside patterns")
    degrees = sorted(sum(row) for row in adjacency)
    return {
        "labelled_graph_mask": mask,
        "canonical_graph_bits": canonical_graph_bits(adjacency),
        "edge_count": sum(degrees) // 2,
        "degree_sequence": degrees,
        "projective_kernel_vector": list(relation),
        "compatible_outside_pattern_count": len(patterns),
        "interpretation": (
            "local lambda/mu, principal-kernel, and one-vertex outside "
            "conditions alone do not exclude support six"
        ),
    }


def code_geometry_rows() -> list[dict[str, object]]:
    rows = []
    for q in range(2, 17, 2):
        r = 44 - q
        required_det_sign = -1 if ((q // 2 + 1) % 2) else 1
        rows.append(
            {
                "q_discriminant_length": q,
                "r_rank_F7_Seidel": r,
                "code_dimension": 44,
                "hull_dimension": r,
                "nondegenerate_quotient_dimension": q,
                "ambient_W_dimension": 99 - 2 * r,
                "one_perp_W0_dimension": 98 - 2 * r,
                "dual_complement_in_W0_dimension": 98 - 2 * r - q,
                "quotient_determinant_legendre_sign": required_det_sign,
                "quotient_orthogonal_type": "minus",
                "quotient_witt_index": q // 2 - 1,
                "dual_complement_orthogonal_type": "plus",
                "dual_complement_witt_index": (10 + q) // 2,
            }
        )
    require(rows[-1]["r_rank_F7_Seidel"] == R_ENDPOINT, "endpoint rank drift")
    require(
        rows[-1]["nondegenerate_quotient_dimension"] == Q_ENDPOINT,
        "endpoint quotient drift",
    )
    return rows


def short_vector_rows() -> list[dict[str, object]]:
    rows = []
    for norm in (14, 16, 18):
        rows.append(
            {
                "K_squared_norm": norm,
                "code_hamming_weight": norm,
                "symbol_composition": {
                    "0": N - norm,
                    "3": norm // 2,
                    "4": norm // 2,
                },
                "code_self_dot_mod_7": (2 * norm) % P,
                "quotient_class": (
                    "isotropic_or_zero" if norm == 14 else "anisotropic"
                ),
            }
        )
    require(
        [row["code_self_dot_mod_7"] for row in rows] == [0, 4, 1],
        "short-vector self-dot drift",
    )
    return rows


def orthogonal_array_slacks() -> list[dict[str, object]]:
    """Compare mandatory known words with OA strength-five moments.

    The 99 pairwise nonproportional Seidel rows give 594 distinct weight-98
    words.  The Wave 71 congruence forces at least one short projective line,
    hence six additional words.  Weight 18 is used for all six in the known
    contribution because it maximizes every tested binomial moment.
    """

    code_size = P**K
    rows = []
    for degree in range(6):
        if degree == 0:
            required = code_size
            known_upper = 1 + 6 * N + 6
        else:
            required = (
                math.comb(N, degree)
                * (P - 1) ** degree
                * P ** (K - degree)
            )
            known_upper = (
                6 * N * math.comb(N - 1, degree)
                + 6 * math.comb(18, degree)
            )
        require(required > known_upper, f"OA moment {degree} has no slack")
        rows.append(
            {
                "degree": degree,
                "required_OA_moment": required,
                "mandatory_known_contribution_upper_control": known_upper,
                "strict_slack": required - known_upper,
            }
        )
    return rows


def build_results() -> dict[str, object]:
    # Parameter algebra controls.
    require((27 % P, 1 % P, -9 % P) == (6, 1, 5), "Gram residues drift")
    require(
        all(
            value % P == 0
            for value in (
                49,  # restricted Seidel eigenvalue squares
                4900,  # principal Seidel eigenvalue square
                63,  # marked-frame scalar
            )
        ),
        "characteristic-seven divisibility drift",
    )
    require((9 % P) == 2, "evaluation-form scale drift")

    return {
        "format": "wave80-f7-overlattice-code-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional finite-field consequences of the Wave66/Wave71 "
            "lattice package and a hypothetical srg(99,14,1,2)"
        ),
        "evaluation_code": {
            "field": "F7",
            "length": N,
            "dimension": K,
            "definition": (
                "C={(<y,v_i>) mod 7 : y in L*/7L*}, v_i=3u_i"
            ),
            "evaluation_map_injective": True,
            "coordinate_sum_zero": True,
            "gram_mod_7": "((<v_i,v_j>))=-S",
            "domain_form": "beta(y,z)=7<y,z> mod 7",
            "code_dot_form": "c(y).c(z)=2 beta(y,z)",
            "radical_preimage": "L/7L*",
            "hull": "C intersect C_perp=row_F7(S)",
            "dual_distance_lower_bound": 6,
            "orthogonal_array_strength": 5,
        },
        "geometry_rows": code_geometry_rows(),
        "endpoint_rank_28": {
            "parameters": "[99,44]_7",
            "hull_dimension": 28,
            "quotient": "O^-(16,7), Witt index 7",
            "ambient_one_perp_quotient": "O^-(42,7), Witt index 20",
            "dual_complement": "O^+(26,7), Witt index 13",
            "dual_parameters": "[99,55]_7",
            "dual_hull_dimension": 28,
        },
        "short_vectors": {
            "rows": short_vector_rows(),
            "theta_count_relation": "N14+N16+N18=2 mod 14",
            "minimum_short_projective_lines": 1,
            "minimum_scalar_closed_codewords": 6,
            "mandatory_scalar_closure_count_mod_42": 6,
            "orthogonal_type_excludes_these_norms": False,
        },
        "dual_distance": {
            "small_principal_checks": principal_small_checks(),
            "five_support_exhaustion": five_support_exhaustion(),
            "six_support_positive_control": six_support_positive_control(),
            "conclusion": "d(C_perp)>=d(row(S)_perp)>=6",
        },
        "macwilliams_control": {
            "OA_strength_five_moments": orthogonal_array_slacks(),
            "contradiction_from_mandatory_lower_counts": False,
            "formal_full_weight_enumerator_constructed": False,
        },
        "endpoint": {
            "rank_28_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Wave80 is discovery and does not verify Wave66 or Wave71.",
            "The code and orthogonal-space profile are necessary conditions, not a graph construction.",
            "Positive slack in low MacWilliams moments is not a formal weight enumerator.",
            "No absence-of-code conclusion is inferred from a bounded search or LP.",
        ],
    }


def main() -> None:
    output_path = Path(__file__).with_name("exact-results.json")
    rendered = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    output_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(output_path),
                "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
