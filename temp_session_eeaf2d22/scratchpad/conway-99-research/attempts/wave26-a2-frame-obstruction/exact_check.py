#!/usr/bin/env python3
"""Exact Wave 26 checks for the A2 projector-frame obstruction.

The checker proves a finite arithmetic/combinatorial lemma.  If the
scaled-dual form of an actual 231-row projector package has an orthogonal
A2 summand, its frame identity forces 21 rows incident with that summand.
The permitted projector off-diagonal entries allow at most 18.

The conclusion is deliberately narrow: it excludes the required projector
origin of the frozen Wave 24 survivor, not arbitrary primitive embeddings,
all h=9 lattices, or n3=708.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "1f22323a2805e3e24f7848d53f2f4813e236fae9"
AMBIENT_ROWS = 231
LATTICE_RANK = 44
FRAME_CONSTANT = 21
ROW_NORM = 4
ACTUAL_OFF_DIAGONALS = {-2, -1, 0, 1}
A2 = [[2, -1], [-1, 2]]

INPUTS = {
    "verification/wave21-lattice-extension/"
    "2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/"
    "2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
    "verification/wave25-n3-708-strictness/"
    "2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
}

Number = int | Fraction
Matrix = list[list[Number]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = list(zip(*right))
    return [
        [sum(x * y for x, y in zip(row, column)) for column in columns]
        for row in left
    ]


def scale(matrix: Matrix, scalar: Number) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def inverse(matrix: Matrix) -> Matrix:
    """Exact inverse by Fraction Gauss-Jordan elimination."""
    size = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(int(row_index == col)) for col in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for col in range(size):
        pivot = next(
            (row for row in range(col, size) if work[row][col]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [value / pivot_value for value in work[col]]
        for row in range(size):
            if row == col:
                continue
            multiplier = work[row][col]
            if multiplier:
                work[row] = [
                    value - multiplier * pivot_entry
                    for value, pivot_entry in zip(work[row], work[col])
                ]
    return [row[size:] for row in work]


def as_integral(matrix: Matrix) -> list[list[int]]:
    result: list[list[int]] = []
    for row in matrix:
        converted: list[int] = []
        for value in row:
            fraction = Fraction(value)
            if fraction.denominator != 1:
                raise ValueError("matrix is not integral")
            converted.append(fraction.numerator)
        result.append(converted)
    return result


def standard_gram(rows: Matrix) -> Matrix:
    return matmul(transpose(rows), rows)


def form_inner(left: Sequence[int], form: Matrix, right: Sequence[int]) -> int:
    value = sum(
        left[row] * form[row][col] * right[col]
        for row in range(len(form))
        for col in range(len(form))
    )
    fraction = Fraction(value)
    if fraction.denominator != 1:
        raise ValueError("nonintegral inner product")
    return fraction.numerator


def form_gram(rows: list[list[int]], form: Matrix) -> list[list[int]]:
    return [
        [form_inner(left, form, right) for right in rows]
        for left in rows
    ]


def outer_sum(rows: list[list[int]]) -> list[list[int]]:
    if not rows:
        return []
    size = len(rows[0])
    return [
        [sum(row[i] * row[j] for row in rows) for j in range(size)]
        for i in range(size)
    ]


def block(matrix: Matrix, start: int, size: int) -> Matrix:
    return [
        row[start:start + size]
        for row in matrix[start:start + size]
    ]


def is_orthogonal_block(matrix: Matrix, start: int, target: Matrix) -> bool:
    size = len(target)
    if block(matrix, start, size) != target:
        return False
    indices = set(range(start, start + size))
    return all(
        matrix[i][j] == 0
        for i in indices
        for j in range(len(matrix))
        if j not in indices
    )


def frozen_survivor() -> tuple[Matrix, Matrix]:
    certificate = load_json(
        ROOT / "verification/wave24-n3-708-index/survivor-certificate.json"
    )
    matrices = certificate["matrices"]
    return matrices["S"], matrices["A2"]


def frozen_survivor_structure() -> dict[str, object]:
    s, frozen_a2 = frozen_survivor()
    if frozen_a2 != A2:
        raise AssertionError("frozen A2 block changed")
    starts = [
        start
        for start in range(len(s) - 1)
        if is_orthogonal_block(s, start, A2)
    ]
    if starts != [40, 42]:
        raise AssertionError(f"unexpected orthogonal A2 blocks: {starts}")
    return {
        "rank": len(s),
        "A2_block_starts_zero_based": starts,
        "orthogonal_A2_block_count": len(starts),
        "scaled_dual_form": "E8^5 orthogonal_sum A2^2",
    }


def a2_norm(vector: Sequence[int]) -> int:
    return form_inner(vector, A2, vector)


def a2_representation_certificate() -> dict[str, object]:
    # q(a,b)-(a^2+b^2)=(a-b)^2, so q<=4 implies |a|,|b|<=2.
    vectors = list(product(range(-2, 3), repeat=2))
    roots = [list(vector) for vector in vectors if a2_norm(vector) == 2]
    norm_four = [list(vector) for vector in vectors if a2_norm(vector) == 4]
    expected_roots = [
        [-1, -1],
        [-1, 0],
        [0, -1],
        [0, 1],
        [1, 0],
        [1, 1],
    ]
    if roots != expected_roots:
        raise AssertionError("unexpected A2 root enumeration")
    if norm_four:
        raise AssertionError("A2 unexpectedly represents four")
    residue_values = sorted(
        {
            (a * a - a * b + b * b) % 3
            for a, b in product(range(3), repeat=2)
        }
    )
    if residue_values != [0, 1]:
        raise AssertionError("unexpected A2 norm residues modulo three")
    return {
        "form": A2,
        "norm_formula": "2*(a^2-a*b+b^2)",
        "search_box_complete_because": (
            "q(a,b)-(a^2+b^2)=(a-b)^2, so q<=4 implies "
            "|a|<=2 and |b|<=2"
        ),
        "norm_two_vectors": roots,
        "oriented_root_count": len(roots),
        "norm_four_vectors": norm_four,
        "norm_four_absent_mod_3": True,
        "mod_3_values_of_a2_minus_ab_plus_b2": residue_values,
    }


def basis_invariance_certificate() -> dict[str, object]:
    """Exact 2-dimensional model of the contragredient basis change."""
    # These 21 rows have Gram H=21*A2^-1.
    y: Matrix = [[1, 1]] * 7 + [[1, 0]] * 7 + [[0, 1]] * 7
    h = standard_gram(y)
    t: Matrix = A2
    if h != scale(inverse(t), FRAME_CONSTANT):
        raise AssertionError("synthetic H=21*T^-1 identity failed")

    # If P^T*T*P is the desired representative, the lattice basis changes
    # by A=P^-T.  The projector matrix Y*T*Y^T is invariant.
    p: Matrix = [[1, 1], [0, 1]]
    a = as_integral(transpose(inverse(p)))
    y_prime = matmul(y, a)
    t_prime = matmul(transpose(p), matmul(t, p))
    h_prime = standard_gram(y_prime)
    m = matmul(y, matmul(t, transpose(y)))
    m_prime = matmul(y_prime, matmul(t_prime, transpose(y_prime)))
    if m != m_prime:
        raise AssertionError("projector Gram changed under basis change")
    if h_prime != scale(inverse(t_prime), FRAME_CONSTANT):
        raise AssertionError("transformed H=21*T^-1 identity failed")

    return {
        "general_identities": {
            "H": "Y^T*Y",
            "T": "21*H^-1",
            "M": "Y*T*Y^T",
            "second_moment": "Y^T*Y=21*T^-1",
        },
        "basis_change": {
            "isometry_matrix_P": p,
            "lattice_basis_matrix_A_equals_P_inverse_transpose": a,
            "transformed_T": as_integral(t_prime),
            "M_unchanged": m == m_prime,
            "second_moment_covariant": (
                h_prime == scale(inverse(t_prime), FRAME_CONSTANT)
            ),
            "Y_dimensions": [len(y), len(y[0])],
        },
    }


def frame_obstruction_certificate() -> dict[str, object]:
    a2 = a2_representation_certificate()
    block_energy = FRAME_CONSTANT * len(A2)
    forced_incident_rows = block_energy // 2

    # Two rows in one oriented-root fiber have inner product 2+c, where c
    # is the inner product of two norm-two complement vectors.  Cauchy gives
    # -2<=c<=2.
    complement_inner_products = sorted(
        value - 2
        for value in ACTUAL_OFF_DIAGONALS
        if -2 <= value - 2 <= 2
    )
    if complement_inner_products != [-2, -1]:
        raise AssertionError("unexpected complement inner products")

    bounds = {
        size: 2 * size - size * (size - 1)
        for size in range(1, 8)
    }
    fiber_capacity = max(size for size, bound in bounds.items() if bound >= 0)
    total_capacity = a2["oriented_root_count"] * fiber_capacity
    if fiber_capacity != 3 or total_capacity != 18:
        raise AssertionError("unexpected A2 fiber capacity")

    return {
        "frame_identity": "sum_i x_i*x_i^T=21*S^-1",
        "A2_block_second_moment": "sum_i a_i*a_i^T=21*A2^-1",
        "A2_block_energy": block_energy,
        "energy_trace_identity": "sum_i q_A2(a_i)=21*rank(A2)=42",
        "possible_A2_component_norms_for_a_norm_four_row": [0, 2],
        "forced_A2_incident_rows": forced_incident_rows,
        "oriented_A2_root_count": a2["oriented_root_count"],
        "actual_projector_off_diagonals": sorted(ACTUAL_OFF_DIAGONALS),
        "same_root_fiber_complement_inner_products": complement_inner_products,
        "fiber_sum_norm_upper_bounds": bounds,
        "fiber_capacity_per_oriented_root": fiber_capacity,
        "total_A2_incident_row_capacity": total_capacity,
        "contradiction_gap": forced_incident_rows - total_capacity,
        "contradiction": forced_incident_rows > total_capacity,
    }


def shared_a2_row_certificate() -> dict[str, object]:
    """A row meeting both A2 blocks is covered by each block argument."""
    s, _ = frozen_survivor()
    row = [0] * LATTICE_RANK
    row[40] = 1
    row[42] = 1
    first = row[40:42]
    second = row[42:44]
    return {
        "full_row_norm": form_inner(row, s, row),
        "first_A2_component": first,
        "first_A2_component_norm": a2_norm(first),
        "second_A2_component": second,
        "second_A2_component_norm": a2_norm(second),
        "counting_rule": (
            "The row is counted once in each summand's separate energy "
            "identity; relative to either block, the other root is the "
            "norm-two complement vector."
        ),
    }


def plus_two_hostile_control() -> dict[str, object]:
    """Four rows defeat the fiber cap if off-diagonal +2 is admitted."""
    s, _ = frozen_survivor()
    rows: list[list[int]] = []
    for e8_block in range(4):
        row = [0] * LATTICE_RANK
        row[40] = 1  # the same oriented root in the first A2 block
        row[8 * e8_block] = 1  # norm-two simple root in its E8 block
        rows.append(row)
    gram = form_gram(rows, s)
    diagonal = [gram[i][i] for i in range(len(rows))]
    off_diagonal = sorted(
        {
            gram[i][j]
            for i in range(len(rows))
            for j in range(i)
        }
    )
    return {
        "construction": (
            "One fixed A2 root plus four mutually orthogonal norm-two "
            "simple roots in four distinct E8 blocks."
        ),
        "fiber_size": len(rows),
        "Gram": gram,
        "diagonal": diagonal,
        "off_diagonal_values": off_diagonal,
        "valid_if_plus_two_is_allowed": (
            diagonal == [4] * 4 and off_diagonal == [2]
        ),
        "valid_for_actual_off_diagonals": set(off_diagonal).issubset(
            ACTUAL_OFF_DIAGONALS
        ),
        "scope": "Local hostile control, not a complete projector frame.",
    }


def omitted_frame_identity_control() -> dict[str, object]:
    """Eighteen locally valid rows when the tight-frame identity is omitted."""
    s, _ = frozen_survivor()
    central_roots = a2_representation_certificate()["norm_two_vectors"]
    complement_starts = [0, 8, 16, 24, 32, 42]
    rows: list[list[int]] = []

    for central_root, start in zip(central_roots, complement_starts):
        # In every selected E8/A2 block, the first two displayed basis
        # vectors span A2.  This is its three-root zero-sum triple.
        triple = ([1, 0], [0, 1], [-1, -1])
        for pair in triple:
            row = [0] * LATTICE_RANK
            row[40], row[41] = central_root
            row[start], row[start + 1] = pair
            rows.append(row)

    gram = form_gram(rows, s)
    diagonal = [gram[i][i] for i in range(len(rows))]
    off_diagonal = sorted(
        {
            gram[i][j]
            for i in range(len(rows))
            for j in range(i)
        }
    )
    central_components = [row[40:42] for row in rows]
    central_moment = outer_sum(central_components)
    required_central_moment = as_integral(scale(inverse(A2), FRAME_CONSTANT))
    return {
        "construction": (
            "Each of the six oriented roots in the first A2 block is paired "
            "with a three-root, pairwise-inner-product-minus-one triple in "
            "one distinct orthogonal complement block."
        ),
        "row_count": len(rows),
        "diagonal": diagonal,
        "off_diagonal_values": off_diagonal,
        "all_local_row_constraints_hold": (
            diagonal == [4] * 18
            and set(off_diagonal).issubset(ACTUAL_OFF_DIAGONALS)
        ),
        "central_A2_second_moment": central_moment,
        "required_frame_second_moment": required_central_moment,
        "frame_identity_holds_on_central_A2": (
            central_moment == required_central_moment
        ),
        "central_A2_energy": sum(
            a2_norm(component) for component in central_components
        ),
        "scope": (
            "Local 18-row hostile configuration only. It proves that the "
            "entry and norm constraints do not replace the frame identity."
        ),
    }


def build_results() -> dict[str, object]:
    frozen_inputs = {
        path: {
            "expected_sha256": expected,
            "actual_sha256": sha256(ROOT / path),
            "matches": sha256(ROOT / path) == expected,
        }
        for path, expected in INPUTS.items()
    }
    if not all(row["matches"] for row in frozen_inputs.values()):
        raise AssertionError("frozen input hash mismatch")

    structure = frozen_survivor_structure()
    basis = basis_invariance_certificate()
    a2 = a2_representation_certificate()
    obstruction = frame_obstruction_certificate()
    shared = shared_a2_row_certificate()
    controls = {
        "allow_plus_two": plus_two_hostile_control(),
        "omit_frame_identity": omitted_frame_identity_control(),
    }
    if not obstruction["contradiction"]:
        raise AssertionError("A2 frame contradiction was not obtained")
    if not controls["allow_plus_two"]["valid_if_plus_two_is_allowed"]:
        raise AssertionError("+2 hostile control failed")
    if controls["allow_plus_two"]["valid_for_actual_off_diagonals"]:
        raise AssertionError("+2 hostile control passed the actual premise")
    if not controls["omit_frame_identity"]["all_local_row_constraints_hold"]:
        raise AssertionError("omitted-frame local control failed")
    if controls["omit_frame_identity"]["frame_identity_holds_on_central_A2"]:
        raise AssertionError("omitted-frame control accidentally became tight")

    return {
        "status": "DERIVED_EXACT_REPLAY_PENDING_INDEPENDENT_VERIFIER",
        "public_base_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "Necessary projector-frame obstruction for scaled-dual forms "
            "with an orthogonal A2 summand."
        ),
        "frozen_inputs": frozen_inputs,
        "projector_package": {
            "ambient_rows": AMBIENT_ROWS,
            "lattice_rank": LATTICE_RANK,
            "frame_constant": FRAME_CONSTANT,
            "row_norm": ROW_NORM,
            "off_diagonal_values": sorted(ACTUAL_OFF_DIAGONALS),
        },
        "basis_invariance": basis,
        "frozen_survivor_structure": structure,
        "A2_arithmetic": a2,
        "frame_obstruction": obstruction,
        "row_meeting_both_A2_blocks": shared,
        "hostile_controls": controls,
        "conclusion": {
            "general_necessary_result": (
                "An actual projector frame cannot have a scaled-dual form "
                "with an orthogonal A2 summand."
            ),
            "wave24_exact_survivor_projector_origin": "REFUTED",
            "wave24_exact_survivor_arbitrary_primitive_embedding": "UNKNOWN",
            "all_h9_lattices_excluded": False,
            "h9_arithmetic_row_excluded": False,
            "n3_708_excluded": False,
            "target_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    args = parser.parse_args()
    payload = build_results()
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["conclusion"], sort_keys=True))


if __name__ == "__main__":
    main()
