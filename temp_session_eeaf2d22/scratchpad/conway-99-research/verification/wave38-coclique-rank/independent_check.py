#!/usr/bin/env python3
"""Independent verifier for the Wave 38 coclique/rank implication.

The checker uses only the frozen SRG parameters and previously verified
incidence/projector premises.  It does not import or execute the discovery
implementation under ``attempts/wave38-coclique-rank``.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Sequence


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "independent-results.json"
PUBLIC_BASE_COMMIT = "3014f3b1c010cdde1687b8878d4ec58d2bb90f03"
TARGET = {"v": 99, "k": 14, "lambda": 1, "mu": 2}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("result must be a JSON object")
    return value


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[tuple[tuple[int, int], ...]]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for tail in perfect_matchings(remainder):
            yield ((first, second),) + tail


def local_structure(
    *,
    k: int = 14,
    lam: int = 1,
    mu: int = 2,
    triangle_mate_extra_neighbors: int | None = None,
) -> dict[str, Any]:
    """Derive the exact structure around an edge xy and its triangle mate z."""

    require(k == 14 and lam == 1 and mu == 2, "wrong frozen SRG parameters")
    side_size = k - 2

    # For u in N(x), neighbors of u inside N(x) are exactly the common
    # neighbors of the adjacent pair x,u.  Thus G[N(x)] is lambda-regular.
    neighborhood_internal_degree = lam
    require(neighborhood_internal_degree == 1, "local graph is not a matching")

    # The edge xz has exactly lambda common neighbors.  Vertex y is already
    # one, so z has lambda-1 other neighbors in N(x).  The symmetric statement
    # holds with x and y interchanged.
    derived_extra = lam - 1
    if triangle_mate_extra_neighbors is not None:
        require(
            triangle_mate_extra_neighbors == derived_extra,
            "triangle mate has an impossible extra side neighbor",
        )
    require(derived_extra == 0, "triangle mate is not isolated from the side sets")

    # For u in X=N(x)\\{y,z}, u is nonadjacent to y; otherwise u would be a
    # second common neighbor of xy.  The pair u,y therefore has mu common
    # neighbors.  One is x, z is unavailable by the preceding paragraph, and
    # the remaining mu-1 vertices lie in Y.  Symmetry gives the column degree.
    cross_degree = mu - 1
    require(cross_degree == 1, "cross relation is not a perfect matching")

    return {
        "side_size": side_size,
        "two_side_sets_are_disjoint": True,
        "neighborhood_internal_degree": neighborhood_internal_degree,
        "local_matching_edges_per_side": side_size // 2,
        "triangle_mate_extra_neighbors_per_side": derived_extra,
        "cross_degree_each_direction": cross_degree,
        "cross_relation": "perfect matching",
        "induced_side_union_degree": neighborhood_internal_degree + cross_degree,
    }


def normalized_cycle_lengths(
    pulled_back_y_matching: tuple[tuple[int, int], ...],
) -> tuple[int, ...]:
    """Return cycles in the normalized 24-point three-matching union.

    Relabel X so its local matching is (0,1),(2,3),..., and relabel Y through
    the cross matching, making the cross edges x_i--y_i.  The pulled-back
    local Y matching is then an arbitrary perfect matching on 0,...,11.
    """

    vertices = tuple(range(24))
    adjacency = {vertex: set() for vertex in vertices}

    def add_edge(left: int, right: int) -> None:
        require(left != right, "loop in normalized local model")
        adjacency[left].add(right)
        adjacency[right].add(left)

    for left in range(0, 12, 2):
        add_edge(left, left + 1)
    for index in range(12):
        add_edge(index, 12 + index)
    for left, right in pulled_back_y_matching:
        add_edge(12 + left, 12 + right)

    require(
        all(len(adjacency[vertex]) == 2 for vertex in vertices),
        "three matching families do not form a 2-regular graph",
    )

    seen: set[int] = set()
    lengths: list[int] = []
    for start in vertices:
        if start in seen:
            continue
        previous: int | None = None
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            length += 1
            first, second = sorted(adjacency[current])
            following = first if first != previous else second
            previous, current = current, following
        require(current == start, "2-regular component traversal did not close")
        require(length % 4 == 0, "local/cross cycle length is not divisible by four")
        lengths.append(length)
    require(sum(lengths) == 24, "cycle decomposition does not cover both sides")
    require(sum(length // 2 for length in lengths) == 12, "wrong cycle coclique size")
    return tuple(sorted(lengths, reverse=True))


@lru_cache(maxsize=1)
def cycle_partition_census() -> dict[str, int]:
    census: Counter[str] = Counter()
    count = 0
    for matching in perfect_matchings(tuple(range(12))):
        lengths = normalized_cycle_lengths(matching)
        census["+".join(str(length) for length in lengths)] += 1
        count += 1
    require(count == 10_395, "wrong perfect-matching census")
    expected = {
        "24": 3840,
        "20+4": 2304,
        "16+8": 1440,
        "16+4+4": 720,
        "12+12": 640,
        "12+8+4": 960,
        "12+4+4+4": 160,
        "8+8+8": 120,
        "8+8+4+4": 180,
        "8+4+4+4+4": 30,
        "4+4+4+4+4+4": 1,
    }
    require(dict(census) == expected, "normalized cycle-partition census changed")
    return dict(sorted(census.items()))


def solve_projector_coefficients() -> tuple[Fraction, Fraction, Fraction]:
    """Solve P=alpha I+beta A+gamma J for the A=-4 projector."""

    rows = [
        [Fraction(1), Fraction(14), Fraction(99), Fraction(0)],
        [Fraction(1), Fraction(3), Fraction(0), Fraction(0)],
        [Fraction(1), Fraction(-4), Fraction(0), Fraction(1)],
    ]
    for column in range(3):
        pivot = next(index for index in range(column, 3) if rows[index][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [entry / scale for entry in rows[column]]
        for index in range(3):
            if index == column:
                continue
            scale = rows[index][column]
            rows[index] = [
                left - scale * right
                for left, right in zip(rows[index], rows[column])
            ]
    result = tuple(rows[index][3] for index in range(3))
    require(
        result == (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63)),
        "minus-four projector coefficients changed",
    )
    return result


def check_incidence_identity(coefficients: Sequence[int] = (27, -9, 1)) -> dict[str, Any]:
    """Check N(21E0)N^T = 27I-9A+J on all adjacency eigenspaces."""

    require(tuple(coefficients) == (27, -9, 1), "incidence identity was tampered")
    adjacency_eigenvalues = (14, 3, -4)
    multiplicities = (1, 54, 44)
    j_eigenvalues = (99, 0, 0)
    nn_eigenvalues = tuple(7 + value for value in adjacency_eigenvalues)
    require(nn_eigenvalues == (21, 10, 3), "NN^T spectrum changed")

    # Since N^T N=3I+Gamma, E0=proj(ker Gamma) is the spectral projector
    # of N^T N for eigenvalue 3.  Singular-value transport gives
    # N E0 N^T = 3 P_-4.
    ne0nt = (0, 0, 3)
    left = tuple(21 * value for value in ne0nt)
    right = tuple(
        coefficients[0]
        + coefficients[1] * adjacency
        + coefficients[2] * j_value
        for adjacency, j_value in zip(adjacency_eigenvalues, j_eigenvalues)
    )
    require(left == right == (0, 0, 63), "incidence identity eigenspaces disagree")

    alpha, beta, gamma = solve_projector_coefficients()
    require(
        (63 * alpha, 63 * beta, 63 * gamma)
        == tuple(Fraction(value) for value in coefficients),
        "projector scaling does not give the integer identity",
    )
    return {
        "adjacency_spectrum": [
            {"eigenvalue": value, "multiplicity": multiplicity}
            for value, multiplicity in zip(adjacency_eigenvalues, multiplicities)
        ],
        "NNt_eigenvalues": list(nn_eigenvalues),
        "NE0Nt_eigenvalues": list(ne0nt),
        "NMNt_eigenvalues": list(left),
        "integer_coefficients_I_A_J": list(coefficients),
        "identity": "N M N^T = 27I - 9A + J",
        "transport_reason": (
            "E0 projects to the eigenvalue-3 space of N^T N=3I+Gamma; "
            "singular-value transport maps it through N to the eigenvalue-3 "
            "space of NN^T=7I+A, namely the A=-4 eigenspace"
        ),
    }


def coclique_gram(size: int = 13) -> list[list[int]]:
    require(size == 13, "coclique size was tampered")
    return [
        [28 if row == column else 1 for column in range(size)]
        for row in range(size)
    ]


def determinant_bareiss(matrix: Sequence[Sequence[int]]) -> int:
    work = [list(row) for row in matrix]
    n = len(work)
    require(n > 0 and all(len(row) == n for row in work), "matrix is not square")
    sign = 1
    denominator = 1
    for column in range(n - 1):
        pivot = next(
            (index for index in range(column, n) if work[index][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, n):
            for other in range(column + 1, n):
                numerator = (
                    work[row][other] * pivot_value
                    - work[row][column] * work[column][other]
                )
                require(numerator % denominator == 0, "Bareiss division was not exact")
                work[row][other] = numerator // denominator
        denominator = pivot_value
    return sign * work[-1][-1]


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(value * inverse) % prime for value in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    (left - scale * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def coclique_rank_data(size: int = 13, residue: int = 5) -> dict[str, Any]:
    gram = coclique_gram(size)
    determinant = determinant_bareiss(gram)
    expected = 27 ** 12 * 40
    require(determinant == expected, "coclique Gram determinant changed")
    actual_residue = determinant % 7
    require(residue == actual_residue == 5, "determinant residue was tampered")
    rank = rank_mod_prime(gram, 7)
    require(rank == 13, "coclique Gram lost full rank modulo seven")
    return {
        "size": size,
        "gram": "27I_13 + J_13",
        "diagonal": 28,
        "off_diagonal": 1,
        "eigenvalues": {"27": 12, "40": 1},
        "determinant": determinant,
        "determinant_factorization": "27^12*40",
        "determinant_mod_7": actual_residue,
        "rank_mod_7": rank,
    }


def admissible_endpoint_pairs() -> list[list[int]]:
    return [
        [r3, r7]
        for r3 in range(12, 45)
        for r7 in range(13, 45)
        if (r3 + r7) % 2 == 0
    ]


def compute_results() -> dict[str, Any]:
    local = local_structure()
    cycle_census = cycle_partition_census()
    incidence = check_incidence_identity()
    rank_data = coclique_rank_data()
    pairs = admissible_endpoint_pairs()
    r3_twelve = [r7 for r3, r7 in pairs if r3 == 12]
    require(r3_twelve == list(range(14, 45, 2)), "r3=12 parity boundary changed")
    require(len(pairs) == 528, "endpoint rank-pair count changed")

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "universal 13-coclique implication for a putative "
            "srg(99,14,1,2), its characteristic-seven M-rank consequence, "
            "and the conditional n3=4158 reflection/parity update"
        ),
        "target_parameters": TARGET,
        "coclique": {
            "size": 13,
            "construction": (
                "one alternating color class from the induced 24-point "
                "three-matching union, together with the triangle mate z"
            ),
            "local_derivation": local,
            "triangle_mate_nonadjacent_to_all_24": True,
            "cycle_argument": {
                "cross_matching_normalized_to_identity": True,
                "pulled_back_second_local_matching_count": 10_395,
                "cycle_partition_frequencies": cycle_census,
                "all_cycle_lengths_divisible_by_four": True,
                "alternating_color_class_size": 12,
            },
            "completed_graph_automorphism_assumed": False,
        },
        "incidence_projector": {
            "N_shape": [99, 231],
            "triangle_incidence_identity": "N N^T = 7I + A",
            "triangle_graph_identity": "N^T N = 3I + Gamma",
            "M_definition": "M=21E0, E0=orthogonal projector onto ker(Gamma)",
            **incidence,
        },
        "coclique_gram": rank_data,
        "rank_transfer": {
            "factorization": "N_I M N_I^T",
            "field": "F_7",
            "inequality": "rank(N_I M N_I^T) <= rank(M)",
            "claim_type": "LOWER_BOUND_ONLY",
            "rank_F7_M_lower_bound": 13,
            "rank_F7_M_exact": None,
        },
        "endpoint": {
            "conditional_on": "n3=4158",
            "C_definition": "C=2M-21I",
            "C_mod_7": "C=2M",
            "scalar_two_is_invertible_mod_7": True,
            "rank_F7_C_equals_rank_F7_M": True,
            "r7_lower_bound": 13,
            "previously_verified_r3_lower_bound": 12,
            "previously_verified_parity": "r3+r7 is even",
            "if_r3_equals_12": {
                "r7_parity": "even",
                "r7_lower_bound": 14,
                "admissible_r7_values": r3_twelve,
            },
            "admissible_rank_pair_count_after_update": len(pairs),
        },
        "status": {
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "strongest_general_upper_bound_on_n3": 4158,
            "upper_bound_improved_below_4158": False,
            "novelty_status": "UNKNOWN",
        },
        "attribution": {
            "novelty_claimed": False,
            "coclique_prior_public_attribution": (
                "REPORTED_BY_DISCOVERY_NOT_REAUDITED_IN_THIS_VERIFIER"
            ),
            "scope": "mathematical verification only, not literature priority",
        },
        "limitations": [
            "The proof is a universal implication and does not construct a graph.",
            "The rank conclusion is only rank_F7(M)>=13, not an exact rank.",
            "The endpoint reflection and parity consequences remain compatible with many rank pairs.",
            "No endpoint exclusion or improved n3 upper bound follows.",
            "The reported public attribution was not independently researched; novelty remains UNKNOWN.",
        ],
    }


def validate_results(result: dict[str, Any]) -> None:
    require(result.get("claim_label") == "VERIFIED", "wrong scoped claim label")
    require(result["coclique"]["size"] == 13, "coclique size was tampered")
    require(
        result["coclique"]["triangle_mate_nonadjacent_to_all_24"] is True,
        "triangle-mate nonadjacency was removed",
    )
    require(
        result["incidence_projector"]["identity"]
        == "N M N^T = 27I - 9A + J",
        "incidence identity text was tampered",
    )
    require(
        result["coclique_gram"]["determinant_mod_7"] == 5,
        "determinant residue was tampered",
    )
    require(
        result["rank_transfer"]["claim_type"] == "LOWER_BOUND_ONLY"
        and result["rank_transfer"]["rank_F7_M_exact"] is None,
        "rank lower bound was promoted to an exact rank",
    )
    require(
        result["rank_transfer"]["rank_F7_M_lower_bound"] == 13,
        "rank lower bound changed",
    )
    require(
        result["endpoint"]["if_r3_equals_12"]["r7_lower_bound"] == 14,
        "r3=12 parity consequence changed",
    )
    require(
        result["attribution"]["novelty_claimed"] is False
        and result["attribution"]["coclique_prior_public_attribution"]
        == "REPORTED_BY_DISCOVERY_NOT_REAUDITED_IN_THIS_VERIFIER",
        "attribution or novelty status was inflated",
    )
    status = result["status"]
    require(
        status
        == {
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "strongest_general_upper_bound_on_n3": 4158,
            "upper_bound_improved_below_4158": False,
            "novelty_status": "UNKNOWN",
        },
        "target, bound, or novelty status was inflated",
    )
    require(result == compute_results(), "result differs from independent reconstruction")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify:
        validate_results(load_json(args.verify))
        print(f"PASS independent coclique-rank verification: {args.verify}")
        return 0
    result = compute_results()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    output = args.output or DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
