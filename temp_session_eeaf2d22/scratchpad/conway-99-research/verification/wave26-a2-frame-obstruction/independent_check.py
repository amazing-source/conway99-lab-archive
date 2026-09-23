#!/usr/bin/env python3
"""Independent exact checker for the Wave 26 A2 frame obstruction.

This file uses only Python's standard library and public, frozen Wave
20/21/24/25 artifacts.  It deliberately does not import discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


PUBLIC_BASE_COMMIT = "1f22323a2805e3e24f7848d53f2f4813e236fae9"
REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
}

A2 = ((2, -1), (-1, 2))
ORIGINAL_OFF_DIAGONALS = (-2, -1, 0, 1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    actual = {
        relative: sha256_file(REPO_ROOT / relative)
        for relative in sorted(EXPECTED_INPUTS)
    }
    if actual != dict(sorted(EXPECTED_INPUTS.items())):
        mismatches = {
            relative: {
                "expected": EXPECTED_INPUTS[relative],
                "actual": actual.get(relative),
            }
            for relative in sorted(EXPECTED_INPUTS)
            if actual.get(relative) != EXPECTED_INPUTS[relative]
        }
        raise RuntimeError(f"frozen public input mismatch: {mismatches}")
    return actual


def transpose(matrix: Sequence[Sequence[object]]) -> list[list[object]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[object]],
    right: Sequence[Sequence[object]],
) -> list[list[object]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def block_diagonal(blocks: Sequence[Sequence[Sequence[int]]]) -> list[list[int]]:
    size = sum(len(block) for block in blocks)
    result = [[0 for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        width = len(block)
        if any(len(row) != width for row in block):
            raise ValueError("blocks must be square")
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[offset + i][offset + j] = value
        offset += width
    return result


def quadratic(vector: Sequence[int], gram: Sequence[Sequence[int]]) -> int:
    return sum(
        vector[i] * gram[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def inner(
    left: Sequence[int],
    right: Sequence[int],
    gram: Sequence[Sequence[int]],
) -> int:
    return sum(
        left[i] * gram[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    )


def determinant_bareiss(matrix: Sequence[Sequence[int]]) -> int:
    work = [list(map(int, row)) for row in matrix]
    n = len(work)
    if n == 0:
        return 1
    if any(len(row) != n for row in work):
        raise ValueError("matrix must be square")
    sign = 1
    previous = 1
    for column in range(n - 1):
        pivot_row = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot_row is None:
            return 0
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            sign *= -1
        pivot = work[column][column]
        for i in range(column + 1, n):
            for j in range(column + 1, n):
                numerator = work[i][j] * pivot - work[i][column] * work[column][j]
                if numerator % previous:
                    raise ArithmeticError("Bareiss division was not exact")
                work[i][j] = numerator // previous
        previous = pivot
        for i in range(column + 1, n):
            work[i][column] = 0
    return sign * work[-1][-1]


def inverse_two(matrix: Sequence[Sequence[int]]) -> list[list[Fraction]]:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("singular two-by-two matrix")
    return [
        [Fraction(d, determinant), Fraction(-b, determinant)],
        [Fraction(-c, determinant), Fraction(a, determinant)],
    ]


def a2_norm(vector: Sequence[int]) -> int:
    return quadratic(vector, A2)


def enumerate_a2_roots() -> tuple[tuple[int, int], ...]:
    # If 2(a^2-ab+b^2)=2, completing the square bounds |b|<2 and,
    # symmetrically, |a|<2.  The slightly wider box is a hostile margin.
    roots = {
        (a, b)
        for a in range(-2, 3)
        for b in range(-2, 3)
        if a2_norm((a, b)) == 2
    }
    return tuple(sorted(roots))


def a2_norm_four_residue_obstruction() -> dict[str, object]:
    # Norm four would require a^2-ab+b^2=2.  Modulo three the form only
    # represents zero or one, proving that no integer vector has norm four.
    represented = sorted(
        {
            (a * a - a * b + b * b) % 3
            for a in range(3)
            for b in range(3)
        }
    )
    return {
        "form_modulus": 3,
        "represented_residues": represented,
        "forbidden_half_norm_residue": 2,
        "has_norm_four": 2 in represented,
    }


def frame_energy_data() -> dict[str, object]:
    inverse = inverse_two(A2)
    coordinate_second_moment = [
        [21 * inverse[i][j] for j in range(2)]
        for i in range(2)
    ]
    if any(value.denominator != 1 for row in coordinate_second_moment for value in row):
        raise ArithmeticError("21 A2^-1 unexpectedly nonintegral")
    coordinate_second_moment_int = [
        [int(value) for value in row] for row in coordinate_second_moment
    ]
    energy_matrix = matmul(A2, coordinate_second_moment_int)
    energy = sum(energy_matrix[i][i] for i in range(2))
    return {
        "coordinate_second_moment": coordinate_second_moment_int,
        "a2_energy": energy,
        "root_norm": 2,
        "root_rows_forced": energy // 2,
    }


def same_oriented_root_fiber_data(
    allowed_off_diagonals: Iterable[int] = ORIGINAL_OFF_DIAGONALS,
) -> dict[str, object]:
    raw_residual = sorted({value - 2 for value in allowed_off_diagonals})
    cauchy_feasible = [value for value in raw_residual if -2 <= value <= 2]
    if not cauchy_feasible:
        cap = 1
        four_sum_norm_upper = None
    else:
        largest_pair_inner = max(cauchy_feasible)
        four_sum_norm_upper = 4 * 2 + 2 * 6 * largest_pair_inner
        cap = 3 if four_sum_norm_upper < 0 else None
    return {
        "same_a2_root_inner_product": 2,
        "raw_residual_inner_products": raw_residual,
        "cauchy_feasible_residual_inner_products": cauchy_feasible,
        "four_vector_sum_norm_upper": four_sum_norm_upper,
        "fiber_cap": cap,
    }


def shared_root_edge_cases() -> dict[str, object]:
    root = (1, 0)
    opposite = (-1, 0)
    residual_triple = ((1, 0), (0, 1), (-1, -1))
    residual_gram = [
        [inner(left, right, A2) for right in residual_triple]
        for left in residual_triple
    ]
    total_off_diagonals = sorted(
        {
            2 + residual_gram[i][j]
            for i in range(3)
            for j in range(i + 1, 3)
        }
    )
    opposite_total = inner(root, opposite, A2) + inner(root, root, A2)
    return {
        "three_same_oriented_roots_are_locally_possible": {
            "residual_gram": residual_gram,
            "total_off_diagonals": total_off_diagonals,
            "passes_original_set": set(total_off_diagonals).issubset(
                set(ORIGINAL_OFF_DIAGONALS)
            ),
        },
        "opposite_orientations_must_be_separate_fibers": {
            "a2_inner": inner(root, opposite, A2),
            "residual_inner": inner(root, root, A2),
            "total_inner": opposite_total,
            "passes_original_set": opposite_total in ORIGINAL_OFF_DIAGONALS,
        },
    }


def plus_two_hostile_relaxation() -> dict[str, object]:
    # Four rows share one A2 root.  Their residual components are four
    # orthogonal A1 roots, so every off-diagonal total is +2.
    residual_gram = [[2 if i == j else 0 for j in range(4)] for i in range(4)]
    total_gram = [
        [2 + residual_gram[i][j] for j in range(4)]
        for i in range(4)
    ]
    off_diagonals = sorted(
        {
            total_gram[i][j]
            for i in range(4)
            for j in range(4)
            if i != j
        }
    )
    return {
        "row_count_same_oriented_root": 4,
        "total_gram": total_gram,
        "off_diagonals": off_diagonals,
        "accepted_if_plus_two_added": set(off_diagonals).issubset(
            set(ORIGINAL_OFF_DIAGONALS) | {2}
        ),
        "accepted_originally": set(off_diagonals).issubset(
            set(ORIGINAL_OFF_DIAGONALS)
        ),
    }


def missing_frame_hostile_relaxation() -> dict[str, object]:
    # T=A2 orthogonal_sum A1^4.  Four local norm-four rows have zero A2
    # component and mutually zero inner products.  They satisfy the local
    # row-Gram alphabet but not Y^T Y=21T^-1, whose A2 block is nonzero.
    residual_gram = [[2 if i == j else 0 for j in range(4)] for i in range(4)]
    residual_rows = (
        (1, 1, 0, 0),
        (1, -1, 0, 0),
        (0, 0, 1, 1),
        (0, 0, 1, -1),
    )
    local_gram = [
        [
            inner(residual_rows[i], residual_rows[j], residual_gram)
            for j in range(4)
        ]
        for i in range(4)
    ]
    local_off_diagonals = {
        local_gram[i][j]
        for i in range(4)
        for j in range(4)
        if i != j
    }
    return {
        "local_gram": local_gram,
        "local_norms": [local_gram[i][i] for i in range(4)],
        "local_off_diagonals": sorted(local_off_diagonals),
        "local_projector_row_conditions_pass": (
            all(local_gram[i][i] == 4 for i in range(4))
            and local_off_diagonals.issubset(set(ORIGINAL_OFF_DIAGONALS))
        ),
        "actual_a2_energy": 0,
        "required_a2_energy": frame_energy_data()["a2_energy"],
        "frame_identity_pass": False,
    }


def basis_invariance_toy_check() -> dict[str, object]:
    # X has Gram 21*A2^-1.  A unimodular congruence on S must be paired with
    # the contragredient column change Y=X*P^-T.
    x_rows = (
        ((1, 1),) * 7
        + ((1, 0),) * 7
        + ((0, 1),) * 7
    )
    x = [list(row) for row in x_rows]
    g = matmul(transpose(x), x)
    expected_g = frame_energy_data()["coordinate_second_moment"]
    p = [[1, 1], [0, 1]]
    p_inverse = [[1, -1], [0, 1]]
    p_inverse_t = transpose(p_inverse)
    t = matmul(matmul(transpose(p), A2), p)
    y = matmul(x, p_inverse_t)
    m_original = matmul(matmul(x, A2), transpose(x))
    m_transformed = matmul(matmul(y, t), transpose(y))
    y_gram = matmul(transpose(y), y)
    t_inverse = inverse_two(t)
    expected_y_gram = [
        [21 * t_inverse[i][j] for j in range(2)]
        for i in range(2)
    ]
    return {
        "unimodular_change": p,
        "original_gram": g,
        "original_gram_is_21_s_inverse": g == expected_g,
        "M_factorization_preserved": m_original == m_transformed,
        "transformed_frame_identity": y_gram == expected_y_gram,
        "transformed_T": t,
        "transformed_Y_gram": y_gram,
    }


def survivor_check() -> dict[str, object]:
    path = REPO_ROOT / "verification/wave24-n3-708-index/survivor-certificate.json"
    certificate = json.loads(path.read_text(encoding="utf-8"))
    matrices = certificate["matrices"]
    a2 = matrices["A2"]
    e8 = matrices["E8"]
    s = matrices["S"]
    expected_s = block_diagonal([e8] * 5 + [a2] * 2)
    return {
        "rank": len(s),
        "A2_matches_verifier_convention": a2 == [list(row) for row in A2],
        "det_A2": determinant_bareiss(a2),
        "det_E8": determinant_bareiss(e8),
        "S_is_exact_E8_5_orthogonal_A2_2": s == expected_s,
        "has_orthogonal_A2_summand": (
            a2 == [list(row) for row in A2] and s == expected_s
        ),
        "abstract_coordinate_lattice_preserved": True,
        "projector_frame_realization_excluded": (
            a2 == [list(row) for row in A2] and s == expected_s
        ),
    }


def build_result() -> dict[str, object]:
    frozen_hashes = verify_frozen_inputs()
    roots = enumerate_a2_roots()
    norm_four = a2_norm_four_residue_obstruction()
    frame = frame_energy_data()
    fiber = same_oriented_root_fiber_data()
    root_capacity = len(roots) * int(fiber["fiber_cap"])
    contradiction = int(frame["root_rows_forced"]) > root_capacity
    if not contradiction:
        raise AssertionError("expected A2 root-capacity contradiction")
    survivor = survivor_check()
    if not survivor["has_orthogonal_A2_summand"]:
        raise AssertionError("frozen Wave 24 survivor lost its A2 summand")
    return {
        "base_commit": PUBLIC_BASE_COMMIT,
        "claim": {
            "label": "VERIFIED",
            "verdict": "PASS_SCOPED_A2_FRAME_OBSTRUCTION",
            "statement": (
                "A 231-row projector frame with M=YTY^T, "
                "Y^TY=21T^-1, diagonal 4, and off-diagonal alphabet "
                "{0,1,-1,-2} cannot have T even positive definite with "
                "an orthogonal A2 summand."
            ),
        },
        "frozen_input_sha256": frozen_hashes,
        "basis_invariance": basis_invariance_toy_check(),
        "a2_arithmetic": {
            "gram": [list(row) for row in A2],
            "roots": [list(root) for root in roots],
            "oriented_root_count": len(roots),
            "norm_four_residue_obstruction": norm_four,
        },
        "frame_count": {
            **frame,
            "fiber_cap_per_oriented_root": fiber["fiber_cap"],
            "total_root_capacity": root_capacity,
            "forced_root_rows_exceed_capacity": contradiction,
        },
        "same_oriented_root_fiber": fiber,
        "shared_a2_edge_cases": shared_root_edge_cases(),
        "hostile_controls": {
            "allow_plus_two": plus_two_hostile_relaxation(),
            "omit_frame_identity": missing_frame_hostile_relaxation(),
        },
        "wave24_survivor": survivor,
        "scope": {
            "exact_E8_5_orthogonal_A2_2_projector_frame": "EXCLUDED",
            "abstract_E8_5_orthogonal_A2_2_coordinate_lattice": "PRESERVED",
            "arbitrary_primitive_embedding_without_projector_frame": "UNKNOWN",
            "all_h_equals_9_forms": "UNKNOWN",
            "n3_equals_708": "NOT_EXCLUDED",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = build_result()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
