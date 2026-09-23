"""Clean-room verifier for the Wave 187 proof-B hostile relaxation.

The discovery checker is frozen as an input file but is never imported or
executed here.  All transforms and quadratic counts are reconstructed from
their mathematical definitions with exact integer/Fraction arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
N = 231
DIMENSION = 11
CODE_SIZE = 3**DIMENSION
PROJECTIVE_SIZE = (CODE_SIZE - 1) // 2


def qstr(value: Fraction | int) -> str:
    return str(Fraction(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        entries.append((match.group(1).lower(), match.group(2)))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def verify_frozen_inputs() -> dict[str, Any]:
    expected_paths = {
        "agents/2026-07-29-wave187-code-geometry-proof-b.md",
        "attempts/wave187-code-geometry-proof-b/exact_check.py",
        "verification/wave171-pq-centered-code/verification-report.md",
        "verification/wave173-complete-enumerator-lift/verification-report.md",
        "verification/wave174-no-weight3-dual/verification-report.md",
        "verification/wave175-polar-cap-boundary/audit.md",
        "agents/2026-07-29-wave186-nonedge-relation-dimension-proof-a.md",
        "verification/wave188-affine-star-word-amplification-verifier/audit.md",
    }
    entries = parse_hash_list(INPUT_FREEZE)
    actual_paths = {relative.replace("\\", "/") for _, relative in entries}
    if actual_paths != expected_paths:
        raise AssertionError(
            f"unexpected frozen input set: {sorted(actual_paths ^ expected_paths)}"
        )

    failures: list[dict[str, str]] = []
    for expected, relative in entries:
        target = (ROOT / relative).resolve()
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {
                    "path": relative,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return {
        "passed": not failures,
        "files_checked": len(entries),
        "failures": failures,
        "discovery_checker_imported_or_executed": False,
    }


# Each mass is a projective scalar-pair mass.  A cell (a,b) contributes the
# two word compositions (a,b) and (b,a), including twice the same monomial
# when a=b.
TYPE_CELL_MASSES: dict[str, dict[tuple[int, int], Fraction]] = {
    "singular": {
        (0, 81): Fraction(1, 1700),
        (6, 24): Fraction(45334, 697),
        (36, 162): Fraction(231),
        (72, 81): Fraction(2142276162781519, 576217218500),
        (75, 78): Fraction(2368455943056339, 144054304625),
        (78, 78): Fraction(226718, 25),
    },
    "norm_plus": {
        (0, 120): Fraction(1663, 84),
        (0, 228): Fraction(81673674496579188347, 3569527376475060000),
        (33, 195): Fraction(1459598804117088331, 100114860628282500),
        (75, 78): Fraction(12502563, 425),
        (102, 102): Fraction(160341, 952),
        (114, 114): Fraction(59981815805188283, 23787060262812000),
    },
    "norm_minus": {
        (0, 114): Fraction(445838499187, 2044229600),
        (0, 120): Fraction(957613632057, 3212360800),
        (72, 78): Fraction(2033920953923, 292032800),
        (78, 78): Fraction(8822683455071, 408845920),
        (108, 111): Fraction(481518113773, 1405407850),
    },
}


def aggregate_pair_masses() -> dict[tuple[int, int], Fraction]:
    aggregate: dict[tuple[int, int], Fraction] = {}
    for cells in TYPE_CELL_MASSES.values():
        for cell, mass in cells.items():
            aggregate[cell] = aggregate.get(cell, Fraction()) + mass
    return aggregate


PAIR_MASSES = aggregate_pair_masses()


def mass_certificate() -> dict[str, Any]:
    assert all(mass > 0 for cells in TYPE_CELL_MASSES.values() for mass in cells.values())
    type_totals = {
        name: sum(cells.values(), Fraction())
        for name, cells in TYPE_CELL_MASSES.items()
    }
    assert type_totals == {
        "singular": Fraction(29524),
        "norm_plus": Fraction(29646),
        "norm_minus": Fraction(29403),
    }
    assert sum(type_totals.values(), Fraction()) == PROJECTIVE_SIZE
    assert TYPE_CELL_MASSES["singular"][(36, 162)] == 231

    serialized = {
        name: {
            f"{a},{b}": qstr(mass)
            for (a, b), mass in sorted(cells.items())
        }
        for name, cells in TYPE_CELL_MASSES.items()
    }
    return {
        "typed_scalar_pair_masses": serialized,
        "all_masses_strictly_positive": True,
        "type_totals": {name: qstr(value) for name, value in type_totals.items()},
        "projective_scalar_pair_total": PROJECTIVE_SIZE,
        "marked_family": {
            "type": "singular",
            "composition": [36, 162],
            "weight": 198,
            "mass": 231,
            "counts_scalar_pairs_not_individual_words": True,
        },
    }


def complete_moment_column(ones: int, twos: int) -> tuple[Fraction, ...]:
    weight = ones + twos
    difference = ones - twos
    x = Fraction(2 * N - 3 * weight, 2)
    return (
        Fraction(1),
        2 * x,
        x * x - x - Fraction(3, 4) * difference * difference,
        2 * x * x + Fraction(3, 2) * difference * difference - 2 * N,
        x**3
        - x**2
        - 2 * (N - 1) * x
        + Fraction(3, 4) * (x + 1) * difference * difference,
        x**3 / 3
        - x**2
        + Fraction(2 * N, 3)
        - Fraction(3, 4) * (x + 1) * difference * difference,
    )


def complete_strength_three_certificate() -> dict[str, Any]:
    totals = tuple(
        sum(
            mass * complete_moment_column(*cell)[index]
            for cell, mass in PAIR_MASSES.items()
        )
        for index in range(6)
    )
    targets = (
        Fraction(PROJECTIVE_SIZE),
        Fraction(-N),
        Fraction(-comb(N, 2)),
        Fraction(-N * (N - 1)),
        Fraction(-3 * comb(N, 3)),
        Fraction(-comb(N, 3)),
    )
    assert totals == targets
    return {
        "labels": ["sum_t", "K10", "K20", "K11", "K21", "K30"],
        "totals": [qstr(value) for value in totals],
        "zero_word_cancellation_targets": [qstr(value) for value in targets],
        "all_equal": True,
    }


def ordinary_krawtchouk(degree: int, primal_weight: int) -> int:
    return sum(
        (-1) ** h
        * 2 ** (degree - h)
        * comb(primal_weight, h)
        * comb(N - primal_weight, degree - h)
        for h in range(degree + 1)
    )


def ordinary_certificate() -> dict[str, Any]:
    primal = [Fraction() for _ in range(N + 1)]
    primal[0] = 1
    for (ones, twos), mass in PAIR_MASSES.items():
        primal[ones + twos] += 2 * mass
    assert sum(primal, Fraction()) == CODE_SIZE

    dual = [
        sum(
            primal[weight] * ordinary_krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        / CODE_SIZE
        for degree in range(N + 1)
    ]
    slacks = [dual[index] - primal[index] for index in range(N + 1)]
    assert dual[:4] == [1, 0, 0, 0]
    assert all(value >= 0 for value in primal)
    assert all(value >= 0 for value in dual)
    assert all(value >= 0 for value in slacks)

    expected_b4 = Fraction(126079749915623, 131414760)
    expected_short = Fraction(721437869830147204193861, 3066344400)
    assert dual[4] == expected_b4
    assert sum(dual[4:10], Fraction()) == expected_short

    return {
        "primal_support": {
            str(index): qstr(value)
            for index, value in enumerate(primal)
            if value
        },
        "primal_total": qstr(sum(primal, Fraction())),
        "dual_coefficients_checked": len(dual),
        "B0_through_B9": [qstr(value) for value in dual[:10]],
        "B1_B2_B3": [qstr(value) for value in dual[1:4]],
        "all_A_nonnegative": True,
        "all_B_nonnegative": True,
        "all_B_at_least_A": True,
        "minimum_B": qstr(min(dual)),
        "minimum_B_minus_A": qstr(min(slacks)),
        "B4": qstr(dual[4]),
        "B4_through_B9": qstr(sum(dual[4:10], Fraction())),
        "B4_exceeds_18018": dual[4] > 18018,
    }


# Cyclotomic integer a+b*omega, omega^2+omega+1=0.
Eisenstein = tuple[int, int]
ONE: Eisenstein = (1, 0)
OMEGA: Eisenstein = (0, 1)
OMEGA2: Eisenstein = (-1, -1)


def emul(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def epow(value: Eisenstein, exponent: int) -> Eisenstein:
    result = ONE
    base = value
    power = exponent
    while power:
        if power & 1:
            result = emul(result, base)
        base = emul(base, base)
        power //= 2
    return result


def linear_power(
    exponent: int,
    u_phase: Eisenstein,
    v_phase: Eisenstein,
    degree_limit: int,
) -> dict[tuple[int, int], Eisenstein]:
    coefficients: dict[tuple[int, int], Eisenstein] = {}
    for u_degree in range(degree_limit + 1):
        for v_degree in range(degree_limit + 1 - u_degree):
            if u_degree + v_degree > exponent:
                continue
            scalar = comb(exponent, u_degree) * comb(
                exponent - u_degree, v_degree
            )
            phase = emul(epow(u_phase, u_degree), epow(v_phase, v_degree))
            coefficients[(u_degree, v_degree)] = (
                scalar * phase[0],
                scalar * phase[1],
            )
    return coefficients


def polynomial_product(
    left: dict[tuple[int, int], Eisenstein],
    right: dict[tuple[int, int], Eisenstein],
    degree_limit: int,
) -> dict[tuple[int, int], Eisenstein]:
    result: dict[tuple[int, int], Eisenstein] = {}
    for (i, j), left_value in left.items():
        for (r, s), right_value in right.items():
            if i + j + r + s > degree_limit:
                continue
            key = i + r, j + s
            term = emul(left_value, right_value)
            previous = result.get(key, (0, 0))
            result[key] = previous[0] + term[0], previous[1] + term[1]
    return result


@lru_cache(maxsize=None)
def scalar_pair_complete_column(
    ones: int, twos: int, degree_limit: int
) -> dict[tuple[int, int], int]:
    zeros = N - ones - twos
    polynomial = linear_power(zeros, ONE, ONE, degree_limit)
    polynomial = polynomial_product(
        polynomial,
        linear_power(ones, OMEGA, OMEGA2, degree_limit),
        degree_limit,
    )
    polynomial = polynomial_product(
        polynomial,
        linear_power(twos, OMEGA2, OMEGA, degree_limit),
        degree_limit,
    )

    # Swapping ones and twos is cyclotomic conjugation.  The trace of
    # a+b*omega is 2a-b and is the coefficient from both scalar words.
    return {key: 2 * value[0] - value[1] for key, value in polynomial.items()}


def complete_dual_coefficients(degree_limit: int) -> dict[tuple[int, int], Fraction]:
    coefficients = {
        (ones, twos): Fraction(
            comb(N, ones) * comb(N - ones, twos), CODE_SIZE
        )
        for ones in range(degree_limit + 1)
        for twos in range(degree_limit + 1 - ones)
    }
    for (ones, twos), mass in PAIR_MASSES.items():
        column = scalar_pair_complete_column(ones, twos, degree_limit)
        for cell, value in column.items():
            coefficients[cell] += mass * value / CODE_SIZE
    return coefficients


def complete_certificate() -> dict[str, Any]:
    coefficients = complete_dual_coefficients(7)
    by_degree: dict[str, Any] = {}
    for degree in range(8):
        values = [coefficients[(ones, degree - ones)] for ones in range(degree + 1)]
        by_degree[str(degree)] = {
            "coefficients_B_r_degree_minus_r": [qstr(value) for value in values],
            "negative_count": sum(value < 0 for value in values),
            "zero_count": sum(value == 0 for value in values),
        }

    assert all(
        coefficients[(ones, degree - ones)] >= 0
        for degree in range(7)
        for ones in range(degree + 1)
    )
    expected_degree_four = [
        Fraction(0),
        Fraction(0),
        Fraction(126079749915623, 131414760),
        Fraction(0),
        Fraction(0),
    ]
    assert [coefficients[(ones, 4 - ones)] for ones in range(5)] == expected_degree_four

    negative = Fraction(-10151603437954385741, 508426957500)
    assert coefficients[(7, 0)] == coefficients[(0, 7)] == negative
    assert sum(
        coefficients[(ones, 7 - ones)] < 0 for ones in range(8)
    ) == 2

    return {
        "maximum_certified_nonnegative_total_degree": 6,
        "degrees": by_degree,
        "degree_four_order": ["B_04", "B_13", "B_22", "B_31", "B_40"],
        "degree_four_row": [qstr(value) for value in expected_degree_four],
        "first_negative_total_degree": 7,
        "negative_degree_seven_cells": {
            "B_70": qstr(negative),
            "B_07": qstr(negative),
        },
        "degree_nine_float_work_performed": False,
    }


def quadratic_form(vector: tuple[int, ...]) -> int:
    return (
        vector[0] * vector[0]
        + sum(vector[2 * index - 1] * vector[2 * index] for index in range(1, 6))
    ) % 3


def bilinear(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return (
        2 * left[0] * right[0]
        + sum(
            left[2 * index - 1] * right[2 * index]
            + left[2 * index] * right[2 * index - 1]
            for index in range(1, 6)
        )
    ) % 3


@lru_cache(maxsize=1)
def projective_points() -> tuple[tuple[int, ...], ...]:
    points: list[tuple[int, ...]] = []
    for first_nonzero in range(DIMENSION):
        prefix = (0,) * first_nonzero + (1,)
        for tail in product(range(3), repeat=DIMENSION - first_nonzero - 1):
            points.append(prefix + tail)
    assert len(points) == PROJECTIVE_SIZE
    return tuple(points)


def basis_e(index: int) -> tuple[int, ...]:
    return tuple(1 if coordinate == 2 * index - 1 else 0 for coordinate in range(11))


def basis_f(index: int) -> tuple[int, ...]:
    return tuple(1 if coordinate == 2 * index else 0 for coordinate in range(11))


def vector_add(*vectors: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(entries) % 3 for entries in zip(*vectors))


def vector_scale(scalar: int, vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(scalar * entry % 3 for entry in vector)


def complement_type_counts(
    spanning: tuple[tuple[int, ...], ...]
) -> tuple[int, int, int]:
    counts = Counter(
        quadratic_form(point)
        for point in projective_points()
        if all(bilinear(point, vector) == 0 for vector in spanning)
    )
    return counts[0], counts[1], counts[2]


def gram_matrix(vectors: tuple[tuple[int, ...], ...]) -> list[list[int]]:
    return [[bilinear(left, right) for right in vectors] for left in vectors]


def determinant_three(matrix: list[list[int]]) -> int:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    ) % 3


@lru_cache(maxsize=1)
def quadratic_geometry_certificate() -> dict[str, Any]:
    class_sizes = Counter(quadratic_form(point) for point in projective_points())
    assert class_sizes == Counter({0: 29524, 1: 29646, 2: 29403})

    e1, e2, e3 = basis_e(1), basis_e(2), basis_e(3)
    f1, f2 = basis_f(1), basis_f(2)
    canonical = {
        "three_orthogonal_pairs": (e1, e2, e3),
        "two_orthogonal_pairs": (e1, f1, e2),
        "one_orthogonal_pair": (e1, e2, vector_add(f1, f2)),
        "no_orthogonal_plus": (
            e1,
            vector_add(f1, e2),
            vector_add(f1, f2),
        ),
        "no_orthogonal_minus": (
            e1,
            vector_add(f1, e2),
            vector_add(f1, vector_scale(2, f2)),
        ),
    }
    assert all(
        quadratic_form(vector) == 0
        for vectors in canonical.values()
        for vector in vectors
    )

    one_counts = complement_type_counts((e1,))
    orthogonal_pair = complement_type_counts((e1, e2))
    nonorthogonal_pair = complement_type_counts((e1, f1))
    triple_counts = {
        name: complement_type_counts(vectors) for name, vectors in canonical.items()
    }
    grams = {name: gram_matrix(vectors) for name, vectors in canonical.items()}
    determinants = {
        name: determinant_three(gram)
        for name, gram in grams.items()
        if name.startswith("no_orthogonal")
    }

    assert one_counts == (9841, 9963, 9720)
    assert orthogonal_pair == (3280, 3402, 3159)
    assert nonorthogonal_pair == (3280, 3321, 3240)
    assert triple_counts == {
        "three_orthogonal_pairs": (1093, 1215, 972),
        "two_orthogonal_pairs": (1093, 1134, 1053),
        "one_orthogonal_pair": (1093, 1134, 1053),
        "no_orthogonal_plus": (1066, 1107, 1107),
        "no_orthogonal_minus": (1120, 1080, 1080),
    }
    assert determinants == {"no_orthogonal_plus": 2, "no_orthogonal_minus": 1}

    return {
        "projective_points_enumerated": len(projective_points()),
        "class_sizes_S_plus_minus": [
            class_sizes[0],
            class_sizes[1],
            class_sizes[2],
        ],
        "one_singular_orthogonal_complement_S_plus_minus": list(one_counts),
        "orthogonal_pair_complement_S_plus_minus": list(orthogonal_pair),
        "nonorthogonal_pair_complement_S_plus_minus": list(nonorthogonal_pair),
        "triple_complement_S_plus_minus": {
            name: list(values) for name, values in triple_counts.items()
        },
        "canonical_triple_gram_matrices": grams,
        "no_orthogonal_determinants_mod3": determinants,
    }


def typed_moment_certificate() -> dict[str, Any]:
    moments: dict[str, tuple[Fraction, ...]] = {}
    for type_name, cells in TYPE_CELL_MASSES.items():
        moments[type_name] = tuple(
            sum(
                mass * comb(N - ones - twos, degree)
                for (ones, twos), mass in cells.items()
            )
            for degree in range(4)
        )
    expected = {
        "singular": (29524, 2273271, 87133200, 2233980128),
        "norm_plus": (29646, 2301453, 88521741, 2242872288),
        "norm_minus": (29403, 2245320, 85771224, 2174315184),
    }
    assert moments == {
        name: tuple(Fraction(value) for value in values)
        for name, values in expected.items()
    }

    geometry = quadratic_geometry_certificate()
    one = {
        "singular": geometry["one_singular_orthogonal_complement_S_plus_minus"][0],
        "norm_plus": geometry["one_singular_orthogonal_complement_S_plus_minus"][1],
        "norm_minus": geometry["one_singular_orthogonal_complement_S_plus_minus"][2],
    }
    pair_orth = {
        "singular": geometry["orthogonal_pair_complement_S_plus_minus"][0],
        "norm_plus": geometry["orthogonal_pair_complement_S_plus_minus"][1],
        "norm_minus": geometry["orthogonal_pair_complement_S_plus_minus"][2],
    }
    pair_nonorth = {
        "singular": geometry["nonorthogonal_pair_complement_S_plus_minus"][0],
        "norm_plus": geometry["nonorthogonal_pair_complement_S_plus_minus"][1],
        "norm_minus": geometry["nonorthogonal_pair_complement_S_plus_minus"][2],
    }
    for type_name in moments:
        assert moments[type_name][1] == N * one[type_name]
        assert moments[type_name][2] == (
            3696 * pair_orth[type_name] + 22869 * pair_nonorth[type_name]
        )
    assert sum(values[3] for values in moments.values()) == comb(N, 3) * 3280

    return {
        "factorial_moment_order": ["M0", "M1", "M2", "M3"],
        "typed_factorial_moments": {
            name: [qstr(value) for value in values]
            for name, values in moments.items()
        },
        "orthogonal_selected_pairs": 3696,
        "nonorthogonal_selected_pairs": 22869,
        "third_moment_total": qstr(sum(values[3] for values in moments.values())),
        "third_moment_required_total": comb(N, 3) * 3280,
    }


def triple_census_certificate() -> dict[str, Any]:
    census = {
        "three_orthogonal_pairs": 38192,
        "two_orthogonal_pairs": 0,
        "one_orthogonal_pair": 731808,
        "no_orthogonal_plus": 302968,
        "no_orthogonal_minus": 954827,
    }
    geometry = quadratic_geometry_certificate()
    complements = {
        name: tuple(values)
        for name, values in geometry["triple_complement_S_plus_minus"].items()
    }
    derived = tuple(
        sum(census[name] * complements[name][type_index] for name in census)
        for type_index in range(3)
    )
    expected_m3 = (2233980128, 2242872288, 2174315184)

    assert all(isinstance(value, int) and value >= 0 for value in census.values())
    assert sum(census.values()) == comb(N, 3)
    assert (
        3 * census["three_orthogonal_pairs"]
        + 2 * census["two_orthogonal_pairs"]
        + census["one_orthogonal_pair"]
        == 3696 * (N - 2)
    )
    assert (
        3 * census["three_orthogonal_pairs"]
        + census["two_orthogonal_pairs"]
        == N * comb(32, 2)
    )
    assert derived == expected_m3

    return {
        "integral_nonnegative_census": census,
        "triple_total": sum(census.values()),
        "required_triple_total": comb(N, 3),
        "orthogonal_pair_incidence": 3696 * (N - 2),
        "wedge_incidence": N * comb(32, 2),
        "derived_typed_M3_S_plus_minus": list(derived),
        "matches_typed_moments": True,
        "realizable_point_set_asserted": False,
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave187-proof-b-clean-room-verification-v1",
        "verdict": "VERIFIED_RELAXATION_BOUNDARY",
        "integrity": integrity,
        "masses": mass_certificate(),
        "complete_strength_three": complete_strength_three_certificate(),
        "ordinary_macwilliams": ordinary_certificate(),
        "complete_macwilliams": complete_certificate(),
        "quadratic_geometry": quadratic_geometry_certificate(),
        "typed_moments": typed_moment_certificate(),
        "triple_gram_census": triple_census_certificate(),
        "boundary": {
            "rational_relaxation_only": True,
            "linear_code_constructed": False,
            "projective_point_set_constructed": False,
            "endpoint_excluded": False,
            "rank_11_excluded": False,
            "upper_bound_below_18018_obtained": False,
            "certified_complete_degree": 6,
            "first_failure_degree": 7,
            "float_degree_nine_work_performed": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            print("FAIL Wave 187 proof-B clean-room verification")
            return 1
        print(f"PASS Wave 187 proof-B clean-room verification: {args.verify}")
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
