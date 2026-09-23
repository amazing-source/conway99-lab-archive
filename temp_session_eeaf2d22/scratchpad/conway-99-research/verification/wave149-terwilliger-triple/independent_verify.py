#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave149 triangle-root Gram projection.

This file does not import or execute discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave149-terwilliger-triple"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
DISCOVERY_RESULTS = DISCOVERY / "exact-results.json"
EXPECTED_MANIFEST_SHA256 = (
    "84bea47182b6a59b69f5df29d4f7a8cdf71bff63cfbc47947b1e65013d09d70f"
)
EXPECTED_RESULTS_SHA256 = (
    "6fed4da32fbeefce54d1802136dc8c9a328f112bb0f295a86230f0e6175f5ee6"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_discovery_manifest() -> dict[str, object]:
    require(
        sha256_file(DISCOVERY_MANIFEST) == EXPECTED_MANIFEST_SHA256,
        "discovery manifest-file hash drift",
    )
    checked = []
    for line in DISCOVERY_MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.is_file(), f"missing discovery artifact {relative}")
        actual = sha256_file(path)
        require(actual == digest, f"discovery artifact hash drift: {relative}")
        checked.append({"path": relative, "sha256": actual})
    require(
        sha256_file(DISCOVERY_RESULTS) == EXPECTED_RESULTS_SHA256,
        "discovery result hash drift",
    )
    return {
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "entries_checked": len(checked),
        "entries": checked,
    }


def identity(order: int) -> list[list[int]]:
    return [[int(row == column) for column in range(order)] for row in range(order)]


def all_ones(rows: int, columns: int | None = None) -> list[list[int]]:
    columns = rows if columns is None else columns
    return [[1] * columns for _ in range(rows)]


def permutation_matrix(permutation: Sequence[int]) -> list[list[int]]:
    order = len(permutation)
    require(sorted(permutation) == list(range(order)), "not a permutation")
    return [
        [int(column == permutation[row]) for column in range(order)]
        for row in range(order)
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def add(*matrices: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [sum(matrix[row][column] for matrix in matrices) for column in range(len(matrices[0][0]))]
        for row in range(len(matrices[0]))
    ]


def scale(coefficient: int, matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [[coefficient * value for value in row] for row in matrix]


def multiply(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def block_matrix(blocks: Sequence[Sequence[Sequence[Sequence[int]]]]) -> list[list[int]]:
    result = []
    for block_row in blocks:
        height = len(block_row[0])
        for local_row in range(height):
            result.append(
                [
                    value
                    for block in block_row
                    for value in block[local_row]
                ]
            )
    return result


def exact_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            multiple = work[row][column]
            work[row] = [
                value - multiple * pivot_entry
                for value, pivot_entry in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def fixed_points(permutation: Sequence[int]) -> int:
    return sum(index == image for index, image in enumerate(permutation))


def compose(*permutations: Sequence[int]) -> tuple[int, ...]:
    """Permutation encoded by a product of row-convention matrices P1 P2 ... ."""
    order = len(permutations[0])
    result = tuple(range(order))
    for permutation in permutations:
        result = tuple(permutation[result[index]] for index in range(order))
    return result


def partition_derivation() -> dict[str, object]:
    v, k, lam, mu = 99, 14, 1, 2
    root_size = 3
    fibre_size = k - 2
    residual_size = v - root_size - 3 * fibre_size
    ai_to_root = 1
    ai_internal = lam
    ai_to_each_other_fibre = mu - 1
    ai_to_b = k - ai_to_root - ai_internal - 2 * ai_to_each_other_fibre
    b_to_each_ai = mu
    b_internal = k - 3 * b_to_each_ai
    require(
        (fibre_size, residual_size, ai_to_b, b_internal) == (12, 60, 10, 8),
        "partition arithmetic",
    )
    require(fibre_size * ai_to_b == residual_size * b_to_each_ai, "incidence total")
    return {
        "root_triangle": root_size,
        "fibres": [fibre_size] * 3,
        "residual": residual_size,
        "outside_vertex_cannot_meet_two_roots": (
            "otherwise a root edge has the third root and the outside vertex "
            "as two common neighbors, contradicting lambda=1"
        ),
        "Ai_internal_degree": ai_internal,
        "Ai_to_each_other_Aj": ai_to_each_other_fibre,
        "Ai_to_B": ai_to_b,
        "B_to_each_Ai": b_to_each_ai,
        "B_internal_degree": b_internal,
        "incidence_balance_per_fibre": fibre_size * ai_to_b,
    }


def character_certificate() -> tuple[list[dict[str, int]], Counter[int], int]:
    cases = [
        # m, p, j, multiplicity
        (1, 1, 12, 1),
        (1, 1, 0, 2),
        (1, -1, 0, 3),
        (-1, 1, 0, 3),
        (-1, -1, 0, 3),
    ]
    records = []
    spectrum: Counter[int] = Counter()
    rank = 0
    for m, p, j, multiplicity in cases:
        d = 9 - m + j
        a = 2 * j - 1 - 2 * m - p
        b = 2 * j - 1 - p - 2 * m * p
        antisymmetric = d - b
        symmetric_trace = 2 * d + b
        symmetric_determinant = d * (d + b) - 2 * a * a
        discriminant = b * b + 8 * a * a
        square_root = math.isqrt(discriminant)
        require(square_root * square_root == discriminant, "nonsquare discriminant")
        require((symmetric_trace + square_root) % 2 == 0, "nonintegral eigenvalue")
        symmetric_high = (symmetric_trace + square_root) // 2
        symmetric_low = (symmetric_trace - square_root) // 2
        eigenvalues = [antisymmetric, symmetric_high, symmetric_low]
        require(all(value >= 0 for value in eigenvalues), "negative exact eigenvalue")
        require(symmetric_determinant == symmetric_high * symmetric_low, "determinant")
        rank_contribution = sum(value > 0 for value in eigenvalues)
        rank += multiplicity * rank_contribution
        for value in eigenvalues:
            spectrum[value] += multiplicity
        records.append(
            {
                "m": m,
                "p": p,
                "j": j,
                "multiplicity": multiplicity,
                "d": d,
                "a": a,
                "b": b,
                "antisymmetric_eigenvalue": antisymmetric,
                "symmetric_trace": symmetric_trace,
                "symmetric_determinant": symmetric_determinant,
                "symmetric_eigenvalues": [symmetric_high, symmetric_low],
                "rank_contribution_per_character": rank_contribution,
            }
        )
    require(sum(spectrum.values()) == 36, "spectrum dimension")
    return records, spectrum, rank


def build_result() -> dict[str, object]:
    manifest = verify_discovery_manifest()
    stored = json.loads(DISCOVERY_RESULTS.read_text(encoding="utf-8"))
    partition = partition_derivation()

    order = 12
    mate = tuple(index ^ 1 for index in range(order))
    shift = tuple((index + 6) % order for index in range(order))
    ident = tuple(range(order))
    require(compose(mate, mate) == ident, "M not involution")
    require(compose(shift, shift) == ident, "P not involution")
    require(compose(mate, shift) == compose(shift, mate), "M,P do not commute")
    require(fixed_points(mate) == fixed_points(shift) == 0, "fixed point")
    require(fixed_points(compose(mate, shift)) == 0, "MP fixed point")

    f01, f02, f12 = ident, ident, shift
    f20 = f02  # identity is its own inverse
    prism_composition = compose(f01, f12, f20)
    rooted_prisms = fixed_points(prism_composition)
    require(rooted_prisms == 0, "witness contains rooted prism")

    i12 = identity(order)
    j12 = all_ones(order)
    m = permutation_matrix(mate)
    p = permutation_matrix(shift)
    mp = multiply(m, p)
    require(multiply(m, m) == i12, "M matrix involution")
    require(multiply(p, p) == i12, "P matrix involution")
    require(mp == multiply(p, m), "matrix commutation")

    diagonal = add(scale(9, i12), scale(-1, m), j12)
    cross_equal = add(scale(2, j12), scale(-1, i12), scale(-2, m), scale(-1, p))
    cross_shift = add(scale(2, j12), scale(-1, i12), scale(-1, p), scale(-2, mp))
    gram = block_matrix(
        (
            (diagonal, cross_equal, cross_equal),
            (transpose(cross_equal), diagonal, cross_shift),
            (transpose(cross_equal), transpose(cross_shift), diagonal),
        )
    )

    require(gram == transpose(gram), "Gram not symmetric")
    require(all(gram[index][index] == 10 for index in range(36)), "diagonal")
    require(all(sum(row) == 60 for row in gram), "row sum")
    entries = Counter(value for row in gram for value in row)
    off_diagonal = [
        gram[row][column]
        for row in range(36)
        for column in range(36)
        if row != column
    ]
    require(min(off_diagonal) == 0 and max(off_diagonal) == 2, "entry bounds")
    gram_sha256 = hashlib.sha256(canonical_bytes(gram)).hexdigest()

    records, spectrum, character_rank = character_certificate()
    rational_rank = exact_rank(gram)
    require(character_rank == rational_rank == 32, "rank disagreement")
    require(rational_rank <= 60, "factor-dimension rank obstruction")
    require(sum(value * multiplicity for value, multiplicity in spectrum.items()) == 360, "trace")

    witness = stored["minimal_surviving_witness"]
    require(tuple(witness["M0_M1_M2_permutation"]) == mate, "stored M mismatch")
    require(tuple(witness["F01_permutation"]) == f01, "stored F01 mismatch")
    require(tuple(witness["F02_permutation"]) == f02, "stored F02 mismatch")
    require(tuple(witness["F12_permutation"]) == f12, "stored F12 mismatch")
    require(witness["gram_rows"] == gram, "stored Gram mismatch")
    require(witness["gram_sha256"] == gram_sha256, "stored Gram hash mismatch")
    require(witness["gram_rank"] == rational_rank, "stored rank mismatch")
    require(witness["rooted_prism_fixed_points"] == rooted_prisms, "stored prism trace")

    return {
        "format": "wave149-independent-terwilliger-triple-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": (
            "triangle-root partition, matching prism trace, explicit "
            "prism-free witness, and first forced 36x36 Gram projection"
        ),
        "discovery_manifest": manifest,
        "partition": partition,
        "matching_witness": {
            "M": list(mate),
            "P": list(shift),
            "F01": list(f01),
            "F02": list(f02),
            "F12": list(f12),
            "composition": list(prism_composition),
            "rooted_prism_fixed_points": rooted_prisms,
            "commuting_involutions": True,
        },
        "gram": {
            "order": 36,
            "sha256": gram_sha256,
            "minimum_entry": min(entries),
            "maximum_entry": max(entries),
            "off_diagonal_minimum": min(off_diagonal),
            "off_diagonal_maximum": max(off_diagonal),
            "entry_multiplicities": {
                str(value): multiplicity for value, multiplicity in sorted(entries.items())
            },
            "diagonal": 10,
            "row_sum": 60,
            "exact_rational_rank": rational_rank,
            "available_factor_dimension": 60,
            "rank_condition_passes": rational_rank <= 60,
            "rows": gram,
        },
        "psd_character_certificate": {
            "joint_character_multiplicity_derivation": (
                "M,P generate three regular V4 orbits, hence every joint "
                "character has multiplicity 3; the (+,+) space splits into "
                "the all-ones j=12 line and two j=0 lines"
            ),
            "records": records,
            "exact_spectrum": {
                str(value): multiplicity
                for value, multiplicity in sorted(spectrum.items())
            },
            "all_eigenvalues_nonnegative": True,
            "rank_from_characters": character_rank,
        },
        "comparison": {
            "stored_witness_matrix_exact_match": True,
            "stored_gram_hash_exact_match": True,
            "stored_rank_exact_match": True,
            "discovery_code_imported_or_executed": False,
        },
        "verdict": {
            "projection_feasible": "VERIFIED_SCOPED",
            "forces_a_prism": False,
            "binary_incidence_factor": "UNKNOWN",
            "graph_realization": False,
            "strict_n3_upper_bound": "NOT_IMPROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "The verified object is a 36x36 Gram matrix, not a binary 36x60 incidence factor.",
            "No compatible 60-vertex residual adjacency block is produced.",
            "Compatibility between different root triangles is not enforced.",
            "No graph, strict bound, target resolution, or novelty claim follows.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == expected, "stored independent result mismatch")
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
                },
                sort_keys=True,
            )
        )
        return
    output = args.output or HERE / "independent-results.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "WROTE",
                "path": str(output),
                "sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
