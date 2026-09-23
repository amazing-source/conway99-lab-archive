#!/usr/bin/env python3
"""Exact Wave 32 reductions for the rootless indecomposable endpoint branch.

This checker does not instantiate a Conway graph or prove that the forbidden
three-row motif occurs.  It audits the lattice-generation reduction, the
Wave 31 coordinate-block divisibility wall, the exact n3=708 pair counts,
the unique signed three-row norm-two motif, and a full-size binary hostile
control showing that the mod-two shadow alone is consistent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave31-survivor-proof.md":
        "075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa",
    "verification/wave31-sign-commutant/audit.md":
        "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "agents/2026-07-24-wave28-glue-discriminant.md":
        "3c1354a04f33602c6e339875c8de4f77d1874bd6e8f83dbcb712b91717d6c1ff",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def validate_inputs() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = sha256_file(REPO_ROOT / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        actual[relative] = digest
    return actual


def determinant3(matrix: Sequence[Sequence[int]]) -> int:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def block_support_arithmetic() -> dict[str, Any]:
    """Audit the exact arithmetic used in the support-connectivity reduction."""

    # In an even rootless orthogonal summand, every nonzero component of a
    # norm-four vector has even norm at least four.
    component_partitions = []
    for count in range(1, 6):
        for parts in product((0, 4), repeat=count):
            if sum(parts) == 4:
                component_partitions.append(parts)
    if any(sum(part != 0 for part in parts) != 1
           for parts in component_partitions):
        raise AssertionError("a norm-four row can occupy two rootless blocks")

    # A coordinate block I of the rank-44 projector has rank 4|I|/21,
    # hence 21||I|.  Wave 31 actual-incidence transport gives 33||I|.
    projector_sizes = [b for b in range(232) if b % 21 == 0]
    incidence_sizes = [b for b in range(232) if b % 33 == 0]
    simultaneous = sorted(set(projector_sizes).intersection(incidence_sizes))
    if simultaneous != [0, 231]:
        raise AssertionError(f"unexpected coordinate block sizes: {simultaneous}")

    return {
        "primitive_basis_to_row_generation": (
            "For a primitive rank-44 column lattice X Z^44 in Z^231, "
            "Smith normal form has 44 unit invariant factors. The row "
            "lattice X^T Z^231 is therefore Z^44."
        ),
        "norm_four_block_support": {
            "premises": "even orthogonal summands, each of minimum at least 4",
            "partitions_checked": len(component_partitions),
            "conclusion": "exactly one nonzero orthogonal component per row",
        },
        "support_graph_equivalence": (
            "Because the frame rows generate Z^44, disconnected nonzero "
            "support of M=XSX^T gives an integral orthogonal split; conversely "
            "a rootless integral split makes every row block-supported and "
            "disconnects that support."
        ),
        "coordinate_block_divisibility": {
            "projector_trace": "21 divides |I|",
            "actual_incidence_commutator": "33 divides |I|",
            "simultaneous_sizes_between_0_and_231": simultaneous,
            "proper_nonempty_size_exists": False,
        },
        "consequence": (
            "Under actual target incidence, every surviving rootless endpoint "
            "S-form is necessarily integrally indecomposable."
        ),
        "uses_h_729": False,
    }


def endpoint_pair_counts(n3: int = 708) -> dict[str, Any]:
    if n3 % 3:
        raise AssertionError("n3 must be divisible by three")
    q_sum = 2 * n3 // 3
    ordered_disjoint = {
        "r0_M_plus_1": 4620 + q_sum,
        "r1_M_zero": 41580 - 2 * n3,
        "r2_M_minus_1": 2 * n3,
        "r3_M_minus_2": 2772 - q_sum,
    }
    if sum(ordered_disjoint.values()) != 231 * 212:
        raise AssertionError("ordered disjoint-pair count failed")
    intersecting_unordered = 231 * 18 // 2
    unordered_m = {
        "+1": ordered_disjoint["r0_M_plus_1"] // 2,
        "0": ordered_disjoint["r1_M_zero"] // 2 + intersecting_unordered,
        "-1": ordered_disjoint["r2_M_minus_1"] // 2,
        "-2": ordered_disjoint["r3_M_minus_2"] // 2,
    }
    if sum(unordered_m.values()) != 231 * 230 // 2:
        raise AssertionError("unordered M-pair count failed")
    degree_sums = {
        "+1": 231 * 20 + q_sum,
        "0": 231 * 198 - 3 * q_sum,
        "-1": 3 * q_sum,
        "-2": 231 * 12 - q_sum,
    }
    if any(degree_sums[key] != 2 * unordered_m[key] for key in unordered_m):
        raise AssertionError("degree sums disagree with pair counts")
    return {
        "n3": n3,
        "sum_q": q_sum,
        "ordered_disjoint_pair_counts": ordered_disjoint,
        "intersecting_unordered_M_zero_pairs": intersecting_unordered,
        "all_unordered_M_pair_counts": unordered_m,
        "degree_sums": degree_sums,
    }


def three_row_motif() -> dict[str, Any]:
    """Enumerate every signed sum of three rows over the endpoint alphabet."""

    alphabet = (-2, -1, 0, 1)
    norm_two_hits: list[dict[str, Any]] = []
    all_norms: set[int] = set()
    for m01, m02, m12 in product(alphabet, repeat=3):
        for e1, e2 in product((-1, 1), repeat=2):
            coefficients = (1, e1, e2)  # quotient by global sign
            norm = 12 + 2 * (
                coefficients[0] * coefficients[1] * m01
                + coefficients[0] * coefficients[2] * m02
                + coefficients[1] * coefficients[2] * m12
            )
            all_norms.add(norm)
            if norm == 2:
                norm_two_hits.append({
                    "edge_values": [m01, m02, m12],
                    "sorted_edge_values": sorted((m01, m02, m12)),
                    "coefficients": list(coefficients),
                })
    unique_multisets = sorted({
        tuple(hit["sorted_edge_values"]) for hit in norm_two_hits
    })
    if unique_multisets != [(-2, -2, -1)]:
        raise AssertionError(f"unexpected norm-two motifs: {unique_multisets}")
    if len(norm_two_hits) != 3:
        raise AssertionError(f"unexpected oriented motif count: {len(norm_two_hits)}")

    gram = [
        [4, -2, -2],
        [-2, 4, -1],
        [-2, -1, 4],
    ]
    leading_minors = [4, 12, determinant3(gram)]
    if any(value <= 0 for value in leading_minors):
        raise AssertionError("forbidden motif Gram is not positive definite")
    root_norm = sum(gram[i][j] for i in range(3) for j in range(3))
    if root_norm != 2:
        raise AssertionError("motif row sum is not a root")

    return {
        "alphabet": list(alphabet),
        "signed_combinations_checked": 4 ** 3 * 4,
        "attained_norms": sorted(all_norms),
        "norm_two_hit_count_before_edge_permutation": len(norm_two_hits),
        "unique_norm_two_edge_multiset": list(unique_multisets[0]),
        "canonical_gram": gram,
        "canonical_leading_principal_minors": leading_minors,
        "canonical_sum_vector_norm": root_norm,
        "rootless_consequence": (
            "No three frame rows may have pairwise M-values -2,-2,-1."
        ),
        "graph_class_translation": (
            "For actual target incidence, no r=2 triangle pair may have a "
            "common triangle that is r=3 from both endpoints."
        ),
    }


def matmul(left: Sequence[Sequence[int]],
           right: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def motif_trace_detector() -> dict[str, Any]:
    # One -1 edge {0,1} and two -2 edges {0,2},{1,2}.
    a_minus_1 = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
    a_minus_2 = [[0, 0, 1], [0, 0, 1], [1, 1, 0]]
    square = matmul(a_minus_2, a_minus_2)
    mixed = matmul(a_minus_1, square)
    trace = sum(mixed[i][i] for i in range(3))
    if trace != 2:
        raise AssertionError("motif trace normalization failed")
    return {
        "identity": (
            "tr(A_minus1 A_minus2^2) equals twice the number of unordered "
            "{-2,-2,-1} motifs"
        ),
        "one_motif_hostile_example_trace": trace,
        "rootless_required_value": 0,
        "actual_target_value": "UNKNOWN",
    }


def gf2_rank(rows: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for value in rows:
        row = value
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def swap_hyperbolic_coordinates(value: int, dimension: int = 44) -> int:
    output = 0
    for index in range(0, dimension, 2):
        if value >> index & 1:
            output |= 1 << (index + 1)
        if value >> (index + 1) & 1:
            output |= 1 << index
    return output


def hyperbolic_q(value: int, dimension: int = 44) -> int:
    return sum(
        ((value >> index) & 1) * ((value >> (index + 1)) & 1)
        for index in range(0, dimension, 2)
    ) & 1


def binary_hostile_control() -> dict[str, Any]:
    """Build an exact 231-row, rank-44 mod-two model of all code shadows."""

    singular4 = [
        value for value in range(1, 16)
        if hyperbolic_q(value, 4) == 0
    ]
    if len(singular4) != 9:
        raise AssertionError("four-dimensional singular-vector count failed")

    base_rows: list[int] = []
    for block in range(11):
        base_rows.extend(value << (4 * block) for value in singular4)
    if len(base_rows) != 99:
        raise AssertionError("base row count failed")
    rows = base_rows[:]
    for index in range(66):
        row = base_rows[index % len(base_rows)]
        rows.extend((row, row))
    if len(rows) != 231 or any(row == 0 for row in rows):
        raise AssertionError("binary row padding failed")
    if any(hyperbolic_q(row) for row in rows):
        raise AssertionError("a binary row is nonsingular")
    row_sum = 0
    for row in rows:
        row_sum ^= row
    if row_sum:
        raise AssertionError("binary rows do not sum to zero")

    # X^T X, represented by its 44 bit rows.
    xtx: list[int] = []
    for i in range(44):
        matrix_row = 0
        for j in range(44):
            parity = sum(
                ((row >> i) & 1) * ((row >> j) & 1) for row in rows
            ) & 1
            matrix_row |= parity << j
        xtx.append(matrix_row)
    target_s = [swap_hyperbolic_coordinates(1 << i) for i in range(44)]
    if xtx != target_s:
        raise AssertionError("binary X^T X is not the hyperbolic form")

    transformed = [swap_hyperbolic_coordinates(row) for row in rows]
    m_rows: list[int] = []
    for left in rows:
        m_row = 0
        for j, right_s in enumerate(transformed):
            m_row |= ((left & right_s).bit_count() & 1) << j
        m_rows.append(m_row)
    if any(
        ((m_rows[i] >> j) & 1) != ((m_rows[j] >> i) & 1)
        for i in range(231) for j in range(i)
    ):
        raise AssertionError("binary projector is not symmetric")
    if any((m_rows[i] >> i) & 1 for i in range(231)):
        raise AssertionError("binary projector diagonal is nonzero")
    if any(m_rows[i].bit_count() & 1 for i in range(231)):
        raise AssertionError("binary projector does not kill one")
    if gf2_rank(m_rows) != 44:
        raise AssertionError("binary projector rank failed")
    for i, row in enumerate(m_rows):
        square_row = 0
        bits = row
        while bits:
            low = bits & -bits
            square_row ^= m_rows[low.bit_length() - 1]
            bits ^= low
        if square_row != row:
            raise AssertionError(f"binary projector is not idempotent at row {i}")
    if gf2_rank(rows) != 44:
        raise AssertionError("binary frame rows do not span")

    digest = hashlib.sha256()
    width = (231 + 7) // 8
    for row in m_rows:
        digest.update(row.to_bytes(width, "little"))
    return {
        "dimension": 44,
        "row_count": 231,
        "quadratic_form": "22 hyperbolic planes over F2",
        "base_rows": 99,
        "padding": "66 duplicate pairs",
        "all_rows_nonzero": True,
        "all_rows_quadratically_singular": True,
        "row_sum_zero": True,
        "rank_X": gf2_rank(rows),
        "X_transpose_X": "S_inverse=S, 22 hyperbolic planes",
        "projector_rank": gf2_rank(m_rows),
        "projector_symmetric": True,
        "projector_zero_diagonal": True,
        "projector_kills_one": True,
        "projector_idempotent": True,
        "projector_rows_sha256": digest.hexdigest(),
        "scope": (
            "Finite-field hostile control only. It is not a positive-definite "
            "integral lattice, endpoint M alphabet/profile, incidence object, "
            "or graph."
        ),
    }


def hostile_premise_controls() -> dict[str, Any]:
    # Full rank does not imply primitive row generation.
    nonprimitive_rows = (2, 0)
    generated_gcd = 2
    if generated_gcd == 1:
        raise AssertionError("nonprimitive hostile control accidentally saturated")
    return {
        "drop_primitivity": {
            "X": [[2], [0]],
            "rank_over_Q": 1,
            "row_lattice": "2Z, not Z",
            "conclusion": "full column rank alone does not make rows generate",
        },
        "drop_minimum_four": (
            "A norm-four row may have two orthogonal norm-two components; "
            "block support then fails."
        ),
        "replace_actual_incidence_by_abstract_projector": (
            "The 33-divisibility step and hence support connectivity are lost."
        ),
        "motif_absence": (
            "No current identity proves tr(A_minus1 A_minus2^2)>0; absence "
            "cannot be inferred from the positive global pair counts."
        ),
    }


def build_result() -> dict[str, Any]:
    return {
        "scope": (
            "Exact reductions for the rootless integrally indecomposable "
            "n3=708 endpoint branch; no endpoint or target exclusion."
        ),
        "inputs": validate_inputs(),
        "support_connectivity": block_support_arithmetic(),
        "endpoint_pair_counts": endpoint_pair_counts(),
        "forbidden_three_row_motif": three_row_motif(),
        "motif_trace_reduction": motif_trace_detector(),
        "binary_hostile_control": binary_hostile_control(),
        "hostile_premise_controls": hostile_premise_controls(),
        "status": {
            "rootless_decomposable_actual_endpoint": "IMPOSSIBLE_BY_WAVE31",
            "surviving_rootless_endpoint_must_be_indecomposable": "DERIVED",
            "minus2_minus2_minus1_motif_forbidden_if_rootless": "DERIVED",
            "actual_incidence_forces_forbidden_motif": "UNKNOWN",
            "rootless_indecomposable_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "uses_h_729": False,
    }


def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(value), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    arguments = parser.parse_args()
    result = build_result()
    if arguments.stdout:
        print(render(result), end="")
    else:
        write_json(arguments.output, result)
        print(json.dumps({
            "output": str(arguments.output),
            "sha256": hashlib.sha256(render(result).encode("utf-8")).hexdigest(),
            "status": result["status"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
