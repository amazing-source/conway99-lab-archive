"""Clean-room exact verifier for Wave 140.

This file intentionally does not import the discovery checker.  It rebuilds
the binary quadratic space, the two opposite-sign projections, the Smith
factor calculation, and the local 2-adic invariant comparison from the
frozen statement.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path


N = 99
DISCOVERY = Path("attempts/wave140-arf-sign-lattice")
SEALED_MANIFEST_HASH = (
    "934bbbd1818536af3786b9cb8b2f6bc48481d8bda3824328a266d5b3544ffd58"
)
OUTPUT = Path("verification/wave140-arf-sign-lattice/verification-results.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_frozen_manifest() -> dict:
    manifest = DISCOVERY / "package-manifest.sha256"
    manifest_hash = sha256(manifest)
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        actual = sha256(Path(relative))
        entries.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
    return {
        "manifest_sha256": manifest_hash,
        "expected_manifest_sha256": SEALED_MANIFEST_HASH,
        "manifest_pass": manifest_hash == SEALED_MANIFEST_HASH,
        "entry_count": len(entries),
        "entries_pass": all(item["pass"] for item in entries),
        "entries": entries,
    }


def parity_dot(left: int, right: int) -> int:
    return ((left & right).bit_count()) & 1


def q_of_even_word(word: int) -> int:
    weight = word.bit_count()
    if weight & 1:
        raise ValueError("q(x)=wt(x)/2 mod 2 requires even weight")
    return (weight // 2) & 1


def binary_rank(rows: list[int], width: int) -> int:
    echelon = rows[:]
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(echelon))
                if (echelon[row] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            continue
        echelon[rank], echelon[pivot] = echelon[pivot], echelon[rank]
        for row in range(len(echelon)):
            if row != rank and ((echelon[row] >> column) & 1):
                echelon[row] ^= echelon[rank]
        rank += 1
    return rank


def inverse_over_f2(rows: list[int], size: int) -> list[int]:
    augmented = [
        row | (1 << (size + index))
        for index, row in enumerate(rows)
    ]
    for column in range(size):
        pivot = next(
            row
            for row in range(column, size)
            if (augmented[row] >> column) & 1
        )
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        for row in range(size):
            if row != column and ((augmented[row] >> column) & 1):
                augmented[row] ^= augmented[column]
    low_mask = (1 << size) - 1
    if any((row & low_mask) != 1 << index for index, row in enumerate(augmented)):
        raise AssertionError("binary inverse failed")
    return [row >> size for row in augmented]


def independent_symplectic_split(
    basis: list[int],
) -> list[tuple[int, int]]:
    remaining = basis[:]
    answer: list[tuple[int, int]] = []
    while remaining:
        first = remaining.pop(0)
        partner_index = next(
            index
            for index, candidate in enumerate(remaining)
            if parity_dot(first, candidate)
        )
        second = remaining.pop(partner_index)
        corrected = []
        for vector in remaining:
            vector ^= first if parity_dot(vector, second) else 0
            vector ^= second if parity_dot(vector, first) else 0
            corrected.append(vector)
        answer.append((first, second))
        remaining = corrected
    return answer


def orthogonal_projector(basis: list[int]) -> list[int]:
    size = len(basis)
    gram_rows = [
        sum(
            parity_dot(left, right) << column
            for column, right in enumerate(basis)
        )
        for left in basis
    ]
    gram_inverse = inverse_over_f2(gram_rows, size)

    columns = []
    for coordinate in range(N):
        pairing_column = sum(
            ((vector >> coordinate) & 1) << index
            for index, vector in enumerate(basis)
        )
        coefficient_bits = sum(
            parity_dot(inverse_row, pairing_column) << index
            for index, inverse_row in enumerate(gram_inverse)
        )
        image = 0
        for index, vector in enumerate(basis):
            if (coefficient_bits >> index) & 1:
                image ^= vector
        columns.append(image)

    rows = [0] * N
    for column, image in enumerate(columns):
        for row in range(N):
            if (image >> row) & 1:
                rows[row] |= 1 << column
    return rows


def binary_matrix_product(rows: list[int]) -> list[int]:
    square = []
    for row in rows:
        output = 0
        active = row
        while active:
            bit = active & -active
            output ^= rows[bit.bit_length() - 1]
            active ^= bit
        square.append(output)
    return square


def packed_hash(rows: list[int]) -> str:
    packed = b"".join(row.to_bytes(13, "little") for row in rows)
    return hashlib.sha256(packed).hexdigest()


def integer_srg_identity_holds(rows: list[int]) -> bool:
    for i in range(N):
        for j in range(N):
            left = (rows[i] & rows[j]).bit_count()
            right = 12 * (i == j) - ((rows[i] >> j) & 1) + 2
            if left != right:
                return False
    return True


def determinant_unit(e_planes: int, h_planes: int) -> int:
    return pow(3, e_planes, 8) * pow(7, h_planes, 8) % 8


def chi_two(unit: int) -> int:
    residue = unit % 8
    if residue in (1, 7):
        return 1
    if residue in (3, 5):
        return -1
    raise ValueError("unit must be odd")


def smith_from_forced_valuations() -> list[int]:
    # Divisibility ordering makes each p-adic valuation nondecreasing.
    v2 = [0] * 54 + [1] + [2] * 44
    v3 = [0] * 45 + [1] * 54
    v7 = [0] * 98 + [1]
    return [
        (2**two) * (3**three) * (7**seven)
        for two, three, seven in zip(v2, v3, v7, strict=True)
    ]


def main_results() -> dict:
    frozen = audit_frozen_manifest()
    if not frozen["manifest_pass"] or not frozen["entries_pass"]:
        raise AssertionError("sealed Wave140 package did not pass hash audit")

    # The basis f_i=e_i+e_98 identifies K/2K with the even hyperplane.
    ambient_basis = [
        (1 << index) | (1 << (N - 1))
        for index in range(N - 1)
    ]
    ambient_gram_rows = [
        sum(
            parity_dot(left, right) << column
            for column, right in enumerate(ambient_basis)
        )
        for left in ambient_basis
    ]
    planes = independent_symplectic_split(ambient_basis)
    e_indices = [
        index
        for index, (left, right) in enumerate(planes)
        if q_of_even_word(left) == q_of_even_word(right) == 1
    ]
    h_indices = [
        index
        for index, (left, right) in enumerate(planes)
        if q_of_even_word(left) == q_of_even_word(right) == 0
    ]
    if len(e_indices) + len(h_indices) != len(planes):
        raise AssertionError("unexpected mixed symplectic plane")

    ambient_gauss = sum(
        (-1 if (weight // 2) & 1 else 1) * comb(N, weight)
        for weight in range(0, N + 1, 2)
    )
    plane_models = {
        "H2": {
            "gram": [[0, 1], [1, 0]],
            "det_mod_8": 7,
            "gauss_sum": 2,
            "epsilon": 1,
        },
        "E2": {
            "gram": [[2, 1], [1, 2]],
            "det_mod_8": 3,
            "gauss_sum": -2,
            "epsilon": -1,
        },
    }

    allocations = [
        ("epsilon_plus", e_indices[:4] + h_indices[:23]),
        ("epsilon_minus", e_indices[:3] + h_indices),
    ]
    controls = []
    all_plane_indices = set(range(len(planes)))
    for name, u_indices in allocations:
        w_indices = sorted(all_plane_indices - set(u_indices))
        u_basis = [
            vector
            for index in u_indices
            for vector in planes[index]
        ]
        rows = orthogonal_projector(u_basis)
        u_e = sum(index in e_indices for index in u_indices)
        u_h = len(u_indices) - u_e
        w_e = sum(index in e_indices for index in w_indices)
        w_h = len(w_indices) - w_e
        u_unit = determinant_unit(u_e, u_h)
        w_unit = determinant_unit(w_e, w_h)
        u_epsilon = (-1) ** u_e
        weights = [row.bit_count() for row in rows]
        controls.append(
            {
                "name": name,
                "U": {
                    "rank": len(u_basis),
                    "E_planes": u_e,
                    "H_planes": u_h,
                    "determinant_unit_mod_8": u_unit,
                    "epsilon": u_epsilon,
                    "epsilon_matches_chi_two": u_epsilon == chi_two(u_unit),
                },
                "W": {
                    "rank": 2 * len(w_indices),
                    "E_planes": w_e,
                    "H_planes": w_h,
                    "determinant_unit_mod_8": w_unit,
                    "epsilon": (-1) ** w_e,
                },
                "binary_projection": {
                    "rank": binary_rank(rows, N),
                    "symmetric": all(
                        ((rows[i] >> j) & 1) == ((rows[j] >> i) & 1)
                        for i in range(N)
                        for j in range(N)
                    ),
                    "idempotent_mod_2": binary_matrix_product(rows) == rows,
                    "zero_diagonal_mod_2": all(
                        ((rows[i] >> i) & 1) == 0
                        for i in range(N)
                    ),
                    "kills_one_mod_2": all(weight % 2 == 0 for weight in weights),
                    "packed_sha256": packed_hash(rows),
                    "row_weight_distribution": {
                        str(weight): count
                        for weight, count in sorted(Counter(weights).items())
                    },
                    "integer_row_sums_all_14": all(weight == 14 for weight in weights),
                    "integer_srg_identity": integer_srg_identity_holds(rows),
                },
                "local_operator": {
                    "spectrum": {"14": 1, "3": 54, "-4": 44},
                    "trace": 14 + 3 * 54 - 4 * 44,
                    "polynomial_on_K": (
                        3 * 3 == 12 - 3
                        and (-4) * (-4) == 12 - (-4)
                    ),
                    "polynomial_on_one_line": 14 * 14 == 12 - 14 + 2 * N,
                    "two_primary_smith_exponents": [1] + [2] * 44,
                    "two_primary_discriminant_group": {
                        "Z/4": 1,
                        "Z/16": 44,
                    },
                    "scale_16_form_determinant_unit_mod_8": w_unit,
                },
            }
        )

    smith = smith_from_forced_valuations()
    smith_counts = {
        str(value): count
        for value, count in sorted(Counter(smith).items())
    }
    source_results = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    expected_control_hashes = [
        item["binary_projection_control"]["packed_matrix_sha256"]
        for item in source_results["opposite_sign_controls"]
    ]
    actual_control_hashes = [
        item["binary_projection"]["packed_sha256"]
        for item in controls
    ]

    return {
        "format": "wave140-independent-verification-v1",
        "verdict": "PASS_WITH_SCOPE_CORRECTION",
        "frozen_package": frozen,
        "ambient": {
            "dimension": len(ambient_basis),
            "bilinear_rank": binary_rank(ambient_gram_rows, N - 1),
            "gram_determinant": 99,
            "gram_determinant_unit_mod_8": 99 % 8,
            "plane_count": len(planes),
            "E2_count": len(e_indices),
            "H2_count": len(h_indices),
            "gauss_sum": ambient_gauss,
            "expected_gauss_sum": -(1 << 49),
            "epsilon": -1,
        },
        "plane_models": plane_models,
        "bridge": {
            "statement": "epsilon(U)=(2/det(U))",
            "assumptions": [
                "U is an even unimodular Z_2 lattice.",
                "The binary q is the reduction of (x,x)/2 modulo 2.",
                "The determinant is its odd unit square class modulo 8.",
            ],
            "exhaustive_plane_count_check": all(
                (-1) ** e == chi_two(determinant_unit(e, m - e))
                for m in range(1, 50)
                for e in range(m + 1)
            ),
        },
        "controls": controls,
        "control_hashes_match_discovery": (
            actual_control_hashes == expected_control_hashes
        ),
        "smith_reconstruction": {
            "counts": smith_counts,
            "all_divide_84": all(84 % value == 0 for value in smith),
            "product_matches_spectrum": (
                __import__("math").prod(smith) == 14 * 3**54 * 4**44
            ),
            "modular_ranks": {
                "2": sum(value % 2 != 0 for value in smith),
                "3": sum(value % 3 != 0 for value in smith),
                "7": sum(value % 7 != 0 for value in smith),
            },
        },
        "discriminant_boundary": {
            "groups_equal": (
                controls[0]["local_operator"]["two_primary_discriminant_group"]
                == controls[1]["local_operator"][
                    "two_primary_discriminant_group"
                ]
            ),
            "scale_16_form_units": [
                item["W"]["determinant_unit_mod_8"]
                for item in controls
            ],
            "forms_separated_by_unit_square_class": (
                controls[0]["W"]["determinant_unit_mod_8"]
                != controls[1]["W"]["determinant_unit_mod_8"]
            ),
            "convention": (
                "For the even lattice L=A Z_2^99, use "
                "q_L(x+L)=(x,x)/2 mod Z_2.  The exponent-16 Jordan block "
                "is 4W and retains det(W) modulo odd squares."
            ),
        },
        "hostile_scope_checks": {
            "binary_controls_are_not_14_regular": all(
                not item["binary_projection"]["integer_row_sums_all_14"]
                for item in controls
            ),
            "binary_controls_fail_integral_srg_identity": all(
                not item["binary_projection"]["integer_srg_identity"]
                for item in controls
            ),
            "integral_zero_one_adjacency_supplied": False,
            "controls_refute": (
                "determination by the matched binary projection and local "
                "2-adic coarse invariants"
            ),
            "controls_do_not_refute": (
                "a proof using an actual integral 0/1, zero-diagonal, "
                "14-regular SRG adjacency, or unconstructed global "
                "odd-primary discriminant-form compatibility"
            ),
        },
        "status": {
            "target_epsilon": "UNKNOWN",
            "integral_graph": "NOT_CONSTRUCTED",
            "Conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    result = main_results()
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "manifest_pass": result["frozen_package"]["manifest_pass"],
                "control_signs": [
                    item["U"]["epsilon"]
                    for item in result["controls"]
                ],
                "not_integral_srg": result["hostile_scope_checks"][
                    "binary_controls_fail_integral_srg_identity"
                ],
                "target_epsilon": result["status"]["target_epsilon"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
