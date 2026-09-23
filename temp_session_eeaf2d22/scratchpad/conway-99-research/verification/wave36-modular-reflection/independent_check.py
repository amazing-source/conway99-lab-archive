#!/usr/bin/env python3
"""Independent exact checks for the Wave 36 modular-reflection claims.

This module deliberately imports no discovery-side code and does not read the
submitted result JSON.  It reconstructs the finite arithmetic from the frozen
endpoint premises:

    C^2 = 441 I_231,
    diag(C) = -13,
    C_ij in {0, +2, -2},
    per-row off-diagonal counts (+2, -2, 0) = (32, 36, 162),
    rank_Q(M) = 44,
    C = 2M - 21I,

together with the previously verified projector-index formula and congruence

    h = 3^(44-r3) 7^(44-r7),  h == 1 (mod 4).

The program checks finite consequences; the general linear-algebra lemmas are
recorded explicitly in the result and justified in the verifier audit.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


N = 231
RATIONAL_RANK = 44
ROW_ZERO_COUNT = 162
ROW_NORM_SQUARED = 441
PROPORTIONAL_FALSE_NORM = 450
DISTINCT_ROW_COMBINATION_NORM = 882
PRIMES = (3, 7)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_projective_vectors(field: int, dimension: int) -> Iterable[tuple[int, ...]]:
    """Yield one representative of each nonzero projective point.

    The first nonzero coordinate is normalized to one.  This routine is
    generic, although the verifier uses it only over F_3.
    """

    require(field == 3, "this independent enumerator is specialized to F_3")
    for vector in itertools.product(range(field), repeat=dimension):
        try:
            first = next(index for index, value in enumerate(vector) if value)
        except StopIteration:
            continue
        inverse = pow(vector[first], -1, field)
        normalized = tuple((inverse * value) % field for value in vector)
        if normalized == vector:
            yield vector


def diagonal_quadratic_norm(vector: tuple[int, ...], final_coefficient: int) -> int:
    require(final_coefficient in (1, 2), "invalid F_3 determinant class")
    if len(vector) == 1:
        return (final_coefficient * vector[0] * vector[0]) % 3
    return (
        sum(value * value for value in vector[:-1])
        + final_coefficient * vector[-1] * vector[-1]
    ) % 3


def ternary_norm2_projective_count(dimension: int, final_coefficient: int) -> int:
    return sum(
        diagonal_quadratic_norm(vector, final_coefficient) == 2
        for vector in canonical_projective_vectors(3, dimension)
    )


def ternary_count_table(max_dimension: int = 7) -> dict[str, list[int]]:
    return {
        str(dimension): [
            ternary_norm2_projective_count(dimension, 1),
            ternary_norm2_projective_count(dimension, 2),
        ]
        for dimension in range(1, max_dimension + 1)
    }


def row_proportionality_check() -> dict[str, object]:
    """Reconstruct the two impossible integer row combinations.

    Equal factor rows modulo 3 make the corresponding C rows congruent.
    Residue injectivity on {0,+2,-2}, with diag(C) congruent to +2, forces
    row_i-row_j = -15(e_i-e_j).  Antipodal factor rows similarly force
    row_i+row_j = -15(e_i+e_j).
    """

    alphabet = (0, 2, -2)
    residues = {value % 3 for value in alphabet}
    require(len(residues) == len(alphabet), "off-diagonal residues not injective")
    require((-13) % 3 == 2 % 3, "diagonal/+2 residue relation failed")
    require((-13 - 2) ** 2 * 2 == PROPORTIONAL_FALSE_NORM, "false norm mismatch")
    require(2 * ROW_NORM_SQUARED == DISTINCT_ROW_COMBINATION_NORM, "true norm mismatch")
    require(
        PROPORTIONAL_FALSE_NORM != DISTINCT_ROW_COMBINATION_NORM,
        "proportional-row contradiction disappeared",
    )
    return {
        "off_diagonal_residues_are_distinct": True,
        "diagonal_residue_equals_plus_two": True,
        "forced_equal_case": "-15(e_i-e_j)",
        "forced_antipodal_case": "-15(e_i+e_j)",
        "forced_combination_norm_squared": PROPORTIONAL_FALSE_NORM,
        "orthogonal_row_combination_norm_squared": DISTINCT_ROW_COMBINATION_NORM,
        "projective_points_distinct": True,
    }


def mod3_rank_floor() -> dict[str, object]:
    table = ternary_count_table()
    maximum_through_six = max(max(table[str(dimension)]) for dimension in range(1, 7))
    six_space_maximum = max(table["6"])
    seven_space_minimum = min(table["7"])
    require(maximum_through_six < N, "dimension <=6 unexpectedly accommodates all points")
    require(seven_space_minimum >= N, "a determinant class in dimension 7 is too small")
    require(ROW_ZERO_COUNT > six_space_maximum, "rank-seven orthogonal-complement step failed")
    return {
        "canonical_projective_norm2_counts": table,
        "dimension_at_least_seven_from_total_points": True,
        "six_space_maximum": six_space_maximum,
        "orthogonal_companions_per_point": ROW_ZERO_COUNT,
        "rank_seven_excluded": True,
        "rank_lower_bound": 8,
    }


def symmetric_cube_dimension(dimension: int) -> int:
    """Dimension of Sym^3(V), equivalently symmetric 3-tensors in char > 3."""

    return math.comb(dimension + 2, 3)


def mod7_cubic_check() -> dict[str, object]:
    diagonal = (-13) % 7
    off_diagonal = (0, 2, -2 % 7)
    require(diagonal == 1, "unexpected diagonal residue modulo seven")

    checks: dict[str, dict[str, int]] = {}
    for integer_label, residue in (("0", 0), ("+2", 2), ("-2", -2 % 7)):
        cube = pow(residue, 3, 7)
        rhs = (4 * residue) % 7
        require(cube == rhs, f"off-diagonal cubic identity failed at {integer_label}")
        checks[integer_label] = {"cube": cube, "four_times_entry": rhs}

    diagonal_cube = pow(diagonal, 3, 7)
    diagonal_rhs = (4 * (1 + diagonal)) % 7
    require(diagonal_cube == diagonal_rhs, "diagonal cubic isolator failed")
    require((1 + 0) * (1 - 0) % 7 == 1, "formal nilpotent inverse scalar failed")

    dim10 = symmetric_cube_dimension(10)
    dim11 = symmetric_cube_dimension(11)
    require(dim10 < N <= dim11, "symmetric-cube dimension boundary changed")
    return {
        "symmetric_tensor_model": (
            "Symmetric tensors in V tensor V tensor V; pure cubes v tensor v tensor v"
        ),
        "dimension_formula": "binom(r+2,3)",
        "diagonal_residue": diagonal,
        "entry_checks": checks,
        "diagonal_check": {"cube": diagonal_cube, "four_times_I_plus_C": diagonal_rhs},
        "gram_identity": "C^(o3)=4(I+C) mod 7",
        "nilpotent_inverse": "(I+C)^(-1)=I-C because C^2=0",
        "dimension_at_rank_10": dim10,
        "dimension_at_rank_11": dim11,
        "rank_lower_bound": 11,
    }


def valuation_profile(rank_mod_p: int) -> list[int]:
    require(0 <= rank_mod_p <= N // 2, "rank incompatible with reciprocal pairing")
    return (
        [0] * rank_mod_p
        + [1] * (N - 2 * rank_mod_p)
        + [2] * rank_mod_p
    )


def smith_factors(r3: int, r7: int) -> list[int]:
    e3 = valuation_profile(r3)
    e7 = valuation_profile(r7)
    factors = [3**a * 7**b for a, b in zip(e3, e7)]
    require(all(factors[index] <= factors[index + 1] for index in range(N - 1)),
            "combined invariant factors are not ordered")
    require(all(441 % factor == 0 for factor in factors), "factor does not divide 441")
    require(
        all(factors[index] * factors[N - 1 - index] == 441 for index in range(N)),
        "reciprocal Smith pairing failed",
    )
    require(sum(factor % 3 != 0 for factor in factors) == r3, "F_3 rank mismatch")
    require(sum(factor % 7 != 0 for factor in factors) == r7, "F_7 rank mismatch")
    require(factors[N // 2] == 21, "odd central invariant factor is not 21")
    return factors


def run_length_encoding(values: list[int]) -> list[list[int]]:
    encoded: list[list[int]] = []
    for value in values:
        if encoded and encoded[-1][0] == value:
            encoded[-1][1] += 1
        else:
            encoded.append([value, 1])
    return encoded


def smith_and_survivor_check() -> dict[str, object]:
    survivors = [
        [r3, r7]
        for r3 in range(8, RATIONAL_RANK + 1)
        for r7 in range(11, RATIONAL_RANK + 1)
        if (r3 + r7) % 2 == 0
    ]
    require(len(survivors) == 629, "survivor count mismatch")

    # Check every arithmetic survivor, not just representative boundaries.
    for r3, r7 in survivors:
        factors = smith_factors(r3, r7)
        h = 3 ** (RATIONAL_RANK - r3) * 7 ** (RATIONAL_RANK - r7)
        require(h % 4 == 1, "parity-compatible pair has wrong index congruence")
        require(math.prod(factors) == 21**N, "Smith determinant magnitude mismatch")

    hostile_odd_pair = (8, 11)
    hostile_h = (
        3 ** (RATIONAL_RANK - hostile_odd_pair[0])
        * 7 ** (RATIONAL_RANK - hostile_odd_pair[1])
    )
    require(hostile_h % 4 == 3, "odd rank-sum hostile parity control failed")

    representatives = {}
    for r3, r7 in ((8, 12), (9, 11), (44, 44), (11, 11), (12, 8)):
        representatives[f"r3={r3},r7={r7}"] = run_length_encoding(smith_factors(r3, r7))

    return {
        "reciprocal_pairing": "d_i*d_(232-i)=441",
        "no_zero_invariant_factors": "C^2=441I makes C nonsingular",
        "valuation_profile": "0^r_p,1^(231-2r_p),2^r_p",
        "central_factor": 21,
        "all_629_shapes_checked": True,
        "representative_smith_shapes": representatives,
        "rank_sum_even": True,
        "hostile_odd_pair": list(hostile_odd_pair),
        "hostile_odd_pair_h_mod_4": hostile_h % 4,
        "admissible_rank_pair_count": len(survivors),
        "admissible_rank_pairs": survivors,
        "v3_h_upper_bound": RATIONAL_RANK - 8,
        "v7_h_upper_bound": RATIONAL_RANK - 11,
    }


def build_result() -> dict[str, object]:
    mod3 = mod3_rank_floor()
    mod7 = mod7_cubic_check()
    smith = smith_and_survivor_check()
    proportionality = row_proportionality_check()

    require(mod3["rank_lower_bound"] == 8, "mod-three floor mismatch")
    require(mod7["rank_lower_bound"] == 11, "mod-seven floor mismatch")
    return {
        "schema_version": 1,
        "role": "verifier",
        "scope": "conditional n3=4158 modular-reflection consequences only",
        "frozen_public_head": "697cc02bcbe16b69aaf08822298e03c66329c64c",
        "premises": {
            "C_definition": "C=2M-21I",
            "C_squared": "441I",
            "C_diagonal": -13,
            "C_off_diagonal_alphabet": [0, 2, -2],
            "C_off_diagonal_row_counts": {"+2": 32, "-2": 36, "0": 162},
            "rank_Q_M": RATIONAL_RANK,
            "index_formula": "h=3^(44-r3)*7^(44-r7)",
            "index_mod_4": 1,
        },
        "general_lemmas_audited": {
            "symmetric_rank_factorization": (
                "For symmetric A of rank r over an odd field, A=VHV^T "
                "with V full column rank and H symmetric nonsingular."
            ),
            "square_zero_frame": (
                "If additionally A^2=0, multiplication by left/right inverses "
                "of V and V^T gives V^T V=0."
            ),
            "symmetric_cube_independence": (
                "An invertible Gram matrix of pure symmetric cubes makes those "
                "cubes linearly independent; no nondegeneracy of the restricted "
                "tensor form is needed."
            ),
            "smith_reciprocity": (
                "C^2=441I implies exponent(coker C) divides 441 and the Smith "
                "form of C=441C^-1 is the reverse list 441/d_i."
            ),
        },
        "mod3": {**proportionality, **mod3},
        "mod7": mod7,
        "smith_and_index": smith,
        "verdict": {
            "mod3_rank_floor": "VERIFIED",
            "mod7_rank_floor": "VERIFIED",
            "reciprocal_smith_form": "VERIFIED",
            "parity_and_629_census": "VERIFIED",
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "conway_99": "UNKNOWN",
            "novelty": "NOT_ASSESSED",
        },
        "limitations": [
            "The endpoint matrix and graph are neither constructed nor excluded.",
            "The 629 pairs are arithmetic survivors, not realizable matrices.",
            "The finite checker accompanies the human factorization, tensor, and Smith arguments.",
            "No literature novelty claim is assessed.",
        ],
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    result = build_result()
    text = canonical_json(result)
    if args.verify is not None:
        require(args.verify.read_text(encoding="utf-8") == text, "stored result differs")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    if args.output is None and args.verify is None:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
