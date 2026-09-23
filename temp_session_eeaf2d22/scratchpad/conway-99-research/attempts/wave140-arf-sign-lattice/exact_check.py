"""Exact Wave140 controls for the binary Arf-sign/lattice question.

The checker separates three levels which must not be conflated:

1. exact binary consequences (symmetric idempotent projection);
2. exact 2-adic spectral/Smith data of the integral adjacency operator;
3. the still-missing entrywise 0/1, zero-diagonal integral realization.

No graph or adjacency matrix is constructed.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


N = 99
RANK_R = 54
RANK_E = 44
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"


def dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def q_even(vector: int) -> int:
    weight = vector.bit_count()
    if weight & 1:
        raise AssertionError("q is defined only on even-weight vectors")
    return (weight // 2) & 1


def gf2_rank(rows: list[int], width: int) -> int:
    work = rows[:]
    rank = 0
    for column in range(width):
        pivot = next(
            (
                candidate
                for candidate in range(rank, len(work))
                if (work[candidate] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for other in range(len(work)):
            if other != rank and ((work[other] >> column) & 1):
                work[other] ^= work[rank]
        rank += 1
    return rank


def gf2_inverse(rows: list[int], size: int) -> list[int]:
    work = [
        row | (1 << (size + index))
        for index, row in enumerate(rows)
    ]
    rank = 0
    for column in range(size):
        pivot = next(
            (
                candidate
                for candidate in range(rank, size)
                if (work[candidate] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            raise ValueError("singular GF(2) matrix")
        work[rank], work[pivot] = work[pivot], work[rank]
        for other in range(size):
            if other != rank and ((work[other] >> column) & 1):
                work[other] ^= work[rank]
        rank += 1
    mask = (1 << size) - 1
    if any((work[index] & mask) != 1 << index for index in range(size)):
        raise AssertionError("GF(2) inverse reduction failed")
    return [(row >> size) & mask for row in work]


def symplectic_pairs(basis: list[int]) -> list[tuple[int, int]]:
    work = basis[:]
    pairs = []
    while work:
        left = work.pop(0)
        pivot = next(
            (
                index
                for index, right in enumerate(work)
                if dot(left, right)
            ),
            None,
        )
        if pivot is None:
            raise ValueError("degenerate alternating space")
        right = work.pop(pivot)
        orthogonal = []
        for vector in work:
            if dot(vector, right):
                vector ^= left
            if dot(vector, left):
                vector ^= right
            orthogonal.append(vector)
        work = orthogonal
        pairs.append((left, right))
    return pairs


def arf_from_basis(basis: list[int]) -> int:
    return sum(
        q_even(left) * q_even(right)
        for left, right in symplectic_pairs(basis)
    ) & 1


def projection_from_basis(basis: list[int]) -> list[int]:
    dimension = len(basis)
    gram = [
        sum(
            dot(left, right) << column
            for column, right in enumerate(basis)
        )
        for left in basis
    ]
    inverse = gf2_inverse(gram, dimension)
    columns = []
    for coordinate in range(N):
        pairing = sum(
            ((vector >> coordinate) & 1) << index
            for index, vector in enumerate(basis)
        )
        coefficients = sum(
            (dot(row, pairing) << index)
            for index, row in enumerate(inverse)
        )
        projected = 0
        for index, vector in enumerate(basis):
            if (coefficients >> index) & 1:
                projected ^= vector
        columns.append(projected)
    rows = [0 for _ in range(N)]
    for column, vector in enumerate(columns):
        for row in range(N):
            if (vector >> row) & 1:
                rows[row] |= 1 << column
    return rows


def projection_audit(rows: list[int]) -> dict:
    mask = (1 << N) - 1
    symmetric = all(
        ((rows[row] >> column) & 1)
        == ((rows[column] >> row) & 1)
        for row in range(N)
        for column in range(N)
    )
    square = []
    for row in rows:
        product_row = 0
        active = row
        while active:
            bit = active & -active
            index = bit.bit_length() - 1
            product_row ^= rows[index]
            active ^= bit
        square.append(product_row)
    packed = b"".join(
        (row & mask).to_bytes(13, "little")
        for row in rows
    )
    return {
        "rank": gf2_rank(rows, N),
        "symmetric": symmetric,
        "idempotent": square == rows,
        "zero_diagonal": all(
            ((rows[index] >> index) & 1) == 0
            for index in range(N)
        ),
        "kills_all_one": all((row & mask).bit_count() % 2 == 0 for row in rows),
        "row_weight_distribution": {
            str(weight): count
            for weight, count in sorted(
                Counter(row.bit_count() for row in rows).items()
            )
        },
        "packed_matrix_sha256": hashlib.sha256(packed).hexdigest(),
    }


def determinant_unit_mod8(e_planes: int, h_planes: int) -> int:
    # det(E)=3 and det(H)=-1=7 modulo 8.
    return (pow(3, e_planes, 8) * pow(7, h_planes, 8)) % 8


def kronecker_two(odd_unit_mod8: int) -> int:
    residue = odd_unit_mod8 % 8
    if residue in (1, 7):
        return 1
    if residue in (3, 5):
        return -1
    raise ValueError("Kronecker (2/d) requires an odd d")


def smith_audit() -> dict:
    smith = [1] * 45 + [3] * 9 + [6] + [12] * 43 + [84]
    determinant = 1
    for value in smith:
        determinant *= value
    spectral_determinant = 14 * (3**54) * (4**44)
    return {
        "invariant_factor_counts": {
            "1": 45,
            "3": 9,
            "6": 1,
            "12": 43,
            "84": 1,
        },
        "all_divide_84": all(84 % value == 0 for value in smith),
        "product_matches_spectrum": determinant == spectral_determinant,
        "rank_mod_2": sum(value % 2 != 0 for value in smith),
        "rank_mod_3": sum(value % 3 != 0 for value in smith),
        "rank_mod_7": sum(value % 7 != 0 for value in smith),
        "two_primary_operator_factors": "1^54,2,4^44",
    }


def main_results() -> dict:
    # f_i=e_i+e_98 is the standard basis of the even-weight hyperplane.
    ambient_basis = [
        (1 << index) | (1 << (N - 1))
        for index in range(N - 1)
    ]
    pairs = symplectic_pairs(ambient_basis)
    typed_pairs = [
        {
            "index": index,
            "left": left,
            "right": right,
            "q_left": q_even(left),
            "q_right": q_even(right),
        }
        for index, (left, right) in enumerate(pairs)
    ]
    e_indices = [
        item["index"]
        for item in typed_pairs
        if item["q_left"] == item["q_right"] == 1
    ]
    h_indices = [
        item["index"]
        for item in typed_pairs
        if item["q_left"] == item["q_right"] == 0
    ]
    if (len(pairs), len(e_indices), len(h_indices)) != (49, 25, 24):
        raise AssertionError("ambient symplectic decomposition drift")

    controls = [
        {
            "name": "epsilon_plus",
            "u_pair_indices": e_indices[:4] + h_indices[:23],
            "expected_epsilon": 1,
        },
        {
            "name": "epsilon_minus",
            "u_pair_indices": e_indices[:3] + h_indices,
            "expected_epsilon": -1,
        },
    ]
    control_results = []
    all_indices = set(range(len(pairs)))
    for control in controls:
        u_indices = control["u_pair_indices"]
        w_indices = sorted(all_indices - set(u_indices))
        u_basis = [
            vector
            for index in u_indices
            for vector in pairs[index]
        ]
        w_basis = [
            vector
            for index in w_indices
            for vector in pairs[index]
        ]
        u_e = sum(index in e_indices for index in u_indices)
        u_h = len(u_indices) - u_e
        w_e = sum(index in e_indices for index in w_indices)
        w_h = len(w_indices) - w_e
        arf_u = arf_from_basis(u_basis)
        arf_w = arf_from_basis(w_basis)
        epsilon_u = -1 if arf_u else 1
        epsilon_w = -1 if arf_w else 1
        det_u = determinant_unit_mod8(u_e, u_h)
        det_w = determinant_unit_mod8(w_e, w_h)
        if epsilon_u != control["expected_epsilon"]:
            raise AssertionError("control Arf sign drift")
        if epsilon_u != kronecker_two(det_u):
            raise AssertionError("2-adic determinant/Arf bridge drift")
        if epsilon_u * epsilon_w != -1:
            raise AssertionError("ambient even-hyperplane sign drift")
        if det_u * det_w % 8 != 3:
            raise AssertionError("ambient determinant unit drift")
        projection = projection_from_basis(u_basis)
        binary_audit = projection_audit(projection)
        if binary_audit != {
            **binary_audit,
            "rank": RANK_R,
            "symmetric": True,
            "idempotent": True,
            "zero_diagonal": True,
            "kills_all_one": True,
        }:
            raise AssertionError("binary projection control failed")
        control_results.append(
            {
                "name": control["name"],
                "U": {
                    "rank": len(u_basis),
                    "E_plane_count": u_e,
                    "H_plane_count": u_h,
                    "Arf": arf_u,
                    "epsilon": epsilon_u,
                    "determinant_unit_mod_8": det_u,
                    "kronecker_2_over_det": kronecker_two(det_u),
                },
                "W": {
                    "rank": len(w_basis),
                    "E_plane_count": w_e,
                    "H_plane_count": w_h,
                    "Arf": arf_w,
                    "epsilon": epsilon_w,
                    "determinant_unit_mod_8": det_w,
                },
                "binary_projection_control": binary_audit,
                "operator_scalars": {
                    "on_U": 3,
                    "on_all_one_line": 14,
                    "on_W": -4,
                },
                "two_primary_adjacency_lattice_discriminant_group": (
                    "Z/4 + (Z/16)^44"
                ),
            }
        )

    scalar_identity_checks = {
        "U": 3**2 == 12 - 3,
        "W": (-4) ** 2 == 12 - (-4),
        "all_one_line": 14**2 == 12 - 14 + 2 * 99,
        "trace_zero": 3 * 54 + 14 - 4 * 44 == 0,
        "two_adic_determinant_valuation": 1 + 2 * 44,
    }
    if not all(
        value is True or key == "two_adic_determinant_valuation"
        for key, value in scalar_identity_checks.items()
    ):
        raise AssertionError("spectral scalar identity drift")

    return {
        "format": "wave140-arf-sign-lattice-v1",
        "claim_labels": {
            "arf_determinant_bridge": "DERIVED",
            "binary_and_two_adic_invariants_force_sign": "REFUTED_BY_CONTROL",
            "full_integral_zero_one_SRG_identities_force_sign": "UNKNOWN",
            "full_two_primary_discriminant_form_would_detect_sign": "DERIVED",
        },
        "frozen_target": {
            "matrix_identities": [
                "A=A^T",
                "diag(A)=0",
                "A*1=14*1",
                "A^2=12I-A+2J",
            ],
            "binary_image_rank": RANK_R,
            "target_Arf_sign": "UNKNOWN",
        },
        "ambient_even_hyperplane": {
            "dimension": N - 1,
            "symplectic_plane_count": len(pairs),
            "E_plane_count": len(e_indices),
            "H_plane_count": len(h_indices),
            "Arf": sum(
                item["q_left"] * item["q_right"]
                for item in typed_pairs
            )
            & 1,
            "epsilon": -1,
            "determinant_unit_mod_8": determinant_unit_mod8(
                len(e_indices), len(h_indices)
            ),
            "expected_99_square_class_mod_8": 3,
        },
        "arf_determinant_bridge": {
            "statement": (
                "For the even unimodular Z_2 lift U of R, "
                "epsilon=(2/det(U)); H has (det,epsilon)=(7,+1), "
                "E has (det,epsilon)=(3,-1)."
            ),
            "missing_target_datum": (
                "det(U) square class in Z_2^x/(Z_2^x)^2, equivalently "
                "which 2-adic even plane type lies in the 3-eigenlattice"
            ),
        },
        "smith_reconstruction": smith_audit(),
        "spectral_operator_control": {
            "scalar_identity_checks": scalar_identity_checks,
            "two_controls_share": [
                "rank(U)=54",
                "rank(W)=44",
                "spectrum 14^1,3^54,(-4)^44",
                "A*1=14*1",
                "A^2=12I-A+2J on the orthogonal decomposition",
                "2-primary Smith factors 1^54,2,4^44",
                "ambient even-hyperplane determinant unit 3 and Arf sign -1",
            ],
            "entrywise_zero_one_zero_diagonal_integral_matrix_supplied": False,
        },
        "opposite_sign_controls": control_results,
        "discriminant_boundary": {
            "group_only": (
                "Both controls give Z/4 + (Z/16)^44 for the 2-primary "
                "discriminant group of the adjacency row lattice."
            ),
            "form_level": (
                "The W determinant units differ (5 versus 1 mod 8), so the "
                "full finite quadratic form can distinguish the controls."
            ),
            "verified_full_target_form_available": False,
        },
        "status": {
            "target_epsilon": "UNKNOWN",
            "binary_code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The opposite-sign controls are exact binary and local 2-adic controls, not 99-by-99 integral adjacency matrices.",
            "They refute sign determination from rank, spectrum, Smith factors, and discriminant-group structure alone.",
            "They do not refute a possible use of the full entrywise 0/1 and zero-diagonal integral constraints.",
            "No unproved lattice self-duality or Type II theorem is used.",
        ],
    }


def main() -> None:
    result = main_results()
    DEFAULT_OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "target_epsilon": result["status"]["target_epsilon"],
        "control_signs": [
            item["U"]["epsilon"]
            for item in result["opposite_sign_controls"]
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
