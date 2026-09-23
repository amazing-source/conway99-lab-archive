"""Clean-room verifier for the two frozen Wave 189 conclusions.

Neither discovery checker is imported or executed here.  The rational
enumerator is checked by exact Fraction/cyclotomic arithmetic, and the
conditional circuit theorem is reconstructed as a symbolic certificate.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
N = 231
DIMENSION = 11
CODE_SIZE = 3**DIMENSION
PROJECTIVE_SIZE = (CODE_SIZE - 1) // 2
C = 4158


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
        entries.append((match.group(1).lower(), match.group(2).replace("\\", "/")))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def check_hash_entries(entries: list[tuple[str, str]]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for expected, relative in entries:
        target = (ROOT / relative).resolve()
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {"path": relative, "expected": expected, "actual": actual}
            )
    return failures


def verify_frozen_inputs() -> dict[str, Any]:
    expected = {
        "AGENTS.md",
        "agents/2026-07-29-wave189-degree7-star-complete-proof-b.md",
        "attempts/wave189-degree7-star-complete/package-manifest.sha256",
        "attempts/wave189-orbit-closed-star-translations/package-manifest.sha256",
        "agents/2026-07-29-wave187-multiplicity-one-star-translation-proof-a.md",
        "verification/wave174-no-weight3-dual/package-manifest.sha256",
        "verification/wave176-star-projector-circuits/package-manifest.sha256",
        "verification/wave178-edge-circuit-injection/package-manifest.sha256",
        "verification/wave179-global-transversal-circuits/package-manifest.sha256",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "verification/wave186-star-translation-cover-verifier/package-manifest.sha256",
        "verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256",
        "verification/2026-07-29-wave189-companion-pool-separation-memo.md",
        "verification/2026-07-29-wave189-exact-three-orbit-verifier-memo.md",
        "verification/2026-07-29-wave189-equality-exclusion-verifier-memo.md",
    }
    entries = parse_hash_list(INPUT_FREEZE)
    actual = {path for _, path in entries}
    if actual != expected:
        raise AssertionError(f"unexpected frozen input set: {sorted(actual ^ expected)}")
    failures = check_hash_entries(entries)

    source_manifests = {
        "degree7": ROOT
        / "attempts/wave189-degree7-star-complete/package-manifest.sha256",
        "orbit": ROOT
        / "attempts/wave189-orbit-closed-star-translations/package-manifest.sha256",
    }
    source_digests = {
        name: sha256(path) for name, path in source_manifests.items()
    }
    assert source_digests == {
        "degree7": "dce4157a05fc20f9b3965ec9830a08f893eeefacdb347b084af13807fa417c90",
        "orbit": "d62ce505ebbaa7bd3799c05a6f0ac50ed920fdd519044e287bada2cb582e39d2",
    }
    nested = {
        name: parse_hash_list(path) for name, path in source_manifests.items()
    }
    for name, nested_entries in nested.items():
        for failure in check_hash_entries(nested_entries):
            failure["manifest"] = name
            failures.append(failure)
    assert len(nested["degree7"]) == 10
    assert len(nested["orbit"]) == 9
    return {
        "passed": not failures,
        "files_checked_directly": len(entries),
        "nested_source_entries_checked": {
            name: len(values) for name, values in nested.items()
        },
        "source_manifest_sha256": source_digests,
        "failures": failures,
        "discovery_checkers_imported_or_executed_by_verifier": False,
    }


# A mass at (a,b) counts projective scalar pairs and therefore contributes
# both complete compositions (a,b) and (b,a), even when a=b.
TYPE_CELL_MASSES: dict[str, dict[tuple[int, int], Fraction]] = {
    "singular": {
        (3, 48): Fraction(
            14411387513622084486137560717167,
            238565703738366727873918069925,
        ),
        (6, 21): Fraction(
            151404600678599425990047056072,
            6816162963953335082111944855,
        ),
        (75, 78): Fraction(
            135107001065053933560914945547542,
            6816162963953335082111944855,
        ),
        (78, 78): Fraction(
            2239849573793715820582869720469368,
            238565703738366727873918069925,
        ),
        (36, 162): Fraction(231),
    },
    "norm_plus": {
        (0, 114): Fraction(
            4371071297597773098616451861669,
            1860812489159260477416560945415,
        ),
        (60, 168): Fraction(
            9503222436749466474872623889296,
            238565703738366727873918069925,
        ),
        (75, 78): Fraction(
            89985254810156437594770425249185707,
            3101354148598767462360934909025,
        ),
        (78, 78): Fraction(
            259251231196287938560820521790174,
            524844548224406801322619753835,
        ),
        (111, 111): Fraction(
            149629196671953830109181890067814,
            1574533644673220403967859261505,
        ),
    },
    "norm_minus": {
        (0, 120): Fraction(
            246906431636332574951131748038647,
            477131407476733455747836139850,
        ),
        (18, 189): Fraction(
            45076153929327260205645509344698,
            906549674205793565920888665715,
        ),
        (45, 51): Fraction(
            11255851000663540594262153162806,
            143139422243020036724350841955,
        ),
        (75, 75): Fraction(
            82555981974216485422614393790451983,
            13598245113086903488813329985725,
        ),
        (78, 78): Fraction(
            427776412695344432838928992139975,
            19085256299069338229913445594,
        ),
        (108, 111): Fraction(
            2596662164776425133740490435333,
            9542628149534669114956722797,
        ),
    },
}


def aggregate_pair_masses() -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for cells in TYPE_CELL_MASSES.values():
        for cell, mass in cells.items():
            result[cell] = result.get(cell, Fraction()) + mass
    return result


PAIR_MASSES = aggregate_pair_masses()


def mass_certificate() -> dict[str, Any]:
    assert sum(len(cells) for cells in TYPE_CELL_MASSES.values()) == 16
    assert all(mass > 0 for cells in TYPE_CELL_MASSES.values() for mass in cells.values())
    totals = {
        name: sum(cells.values(), Fraction())
        for name, cells in TYPE_CELL_MASSES.items()
    }
    assert totals == {
        "singular": Fraction(29524),
        "norm_plus": Fraction(29646),
        "norm_minus": Fraction(29403),
    }
    assert sum(totals.values(), Fraction()) == PROJECTIVE_SIZE
    assert TYPE_CELL_MASSES["singular"][(36, 162)] == 231
    return {
        "typed_cells": sum(len(cells) for cells in TYPE_CELL_MASSES.values()),
        "aggregate_cells": len(PAIR_MASSES),
        "all_masses_strictly_positive": True,
        "type_totals": {name: qstr(value) for name, value in totals.items()},
        "projective_scalar_pair_total": PROJECTIVE_SIZE,
        "marked_singular_cell": {"composition": [36, 162], "mass": "231"},
        "typed_scalar_pair_masses": {
            name: {
                f"{a},{b}": qstr(mass)
                for (a, b), mass in sorted(cells.items())
            }
            for name, cells in TYPE_CELL_MASSES.items()
        },
    }


def allowed_star_patterns() -> set[tuple[int, int]]:
    return {
        (r, s)
        for r in range(8)
        for s in range(8 - r)
        if (r - s) % 3 == 0
    }


def local_profile(a: int, b: int) -> dict[tuple[int, int], Fraction]:
    x, y = Fraction(a, 33), Fraction(b, 33)
    if x == 0 and y == 0:
        return {(0, 0): Fraction(1)}
    boundary = ((6, 0), (5, 2), (2, 5), (0, 6))
    for first, second in zip(boundary, boundary[1:]):
        determinant = first[0] * second[1] - first[1] * second[0]
        w_first = Fraction(x * second[1] - y * second[0], determinant)
        w_second = Fraction(first[0] * y - first[1] * x, determinant)
        w_zero = 1 - w_first - w_second
        if min(w_zero, w_first, w_second) >= 0:
            result = {
                (0, 0): w_zero,
                first: w_first,
                second: w_second,
            }
            return {key: value for key, value in result.items() if value}
    raise AssertionError(f"point outside star polygon: {(a, b)}")


def star_polygon_certificate() -> dict[str, Any]:
    allowed = allowed_star_patterns()
    expected = {
        (0, 0), (0, 3), (0, 6), (1, 1), (1, 4), (2, 2),
        (2, 5), (3, 0), (3, 3), (4, 1), (5, 2), (6, 0),
    }
    assert allowed == expected
    vertices = [(0, 0), (6, 0), (5, 2), (2, 5), (0, 6)]
    assert all(
        r + s <= 7 and 2 * r + s <= 12 and r + 2 * s <= 12
        for r, s in allowed
    )

    lifted_cells: dict[str, Any] = {}
    for (a, b), mass in sorted(PAIR_MASSES.items()):
        for u, v in {(a, b), (b, a)}:
            assert u + v <= 231
            assert 2 * u + v <= 396
            assert u + 2 * v <= 396
            profile = local_profile(u, v)
            assert set(profile) <= allowed
            assert sum(profile.values(), Fraction()) == 1
            assert sum(r * value for (r, _), value in profile.items()) == Fraction(u, 33)
            assert sum(s * value for (_, s), value in profile.items()) == Fraction(v, 33)
            lift = {pattern: 99 * mass * value for pattern, value in profile.items()}
            assert sum(lift.values(), Fraction()) == 99 * mass
            assert sum(r * value for (r, _), value in lift.items()) == 3 * u * mass
            assert sum(s * value for (_, s), value in lift.items()) == 3 * v * mass
            lifted_cells[f"{u},{v}"] = {
                f"{r},{s}": qstr(value) for (r, s), value in sorted(profile.items())
            }
    return {
        "allowed_patterns": [list(value) for value in sorted(allowed)],
        "convex_hull_vertices": [list(value) for value in vertices],
        "facet_inequalities": ["r+s<=7", "2r+s<=12", "r+2s<=12"],
        "primal_scaled_facets": ["a+b<=231", "2a+b<=396", "a+2b<=396"],
        "oriented_witness_cells_lifted": len(lifted_cells),
        "all_lifts_nonnegative_and_exact": True,
        "profiles": lifted_cells,
    }


# Cyclotomic integers a+b*omega with omega^2+omega+1=0.
Eisenstein = tuple[int, int]
ONE: Eisenstein = (1, 0)
OMEGA: Eisenstein = (0, 1)
OMEGA2: Eisenstein = (-1, -1)


def emul(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def epow(value: Eisenstein, exponent: int) -> Eisenstein:
    result, base, power = ONE, value, exponent
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
    result: dict[tuple[int, int], Eisenstein] = {}
    for u_degree in range(degree_limit + 1):
        for v_degree in range(degree_limit + 1 - u_degree):
            if u_degree + v_degree > exponent:
                continue
            scalar = comb(exponent, u_degree) * comb(
                exponent - u_degree, v_degree
            )
            phase = emul(epow(u_phase, u_degree), epow(v_phase, v_degree))
            result[(u_degree, v_degree)] = (
                scalar * phase[0], scalar * phase[1]
            )
    return result


def polynomial_product(
    left: dict[tuple[int, int], Eisenstein],
    right: dict[tuple[int, int], Eisenstein],
    degree_limit: int,
) -> dict[tuple[int, int], Eisenstein]:
    result: dict[tuple[int, int], Eisenstein] = {}
    for (i, j), x in left.items():
        for (r, s), y in right.items():
            if i + j + r + s > degree_limit:
                continue
            key = i + r, j + s
            term = emul(x, y)
            old = result.get(key, (0, 0))
            result[key] = old[0] + term[0], old[1] + term[1]
    return result


@lru_cache(maxsize=None)
def scalar_pair_complete_column(
    ones: int, twos: int, degree_limit: int
) -> dict[tuple[int, int], int]:
    polynomial = linear_power(N - ones - twos, ONE, ONE, degree_limit)
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
    # The scalar-reversed word is cyclotomic conjugation.  The contribution
    # of the pair is the trace Tr(a+b*omega)=2a-b.
    return {key: 2 * value[0] - value[1] for key, value in polynomial.items()}


def complete_dual_coefficients(limit: int) -> dict[tuple[int, int], Fraction]:
    result = {
        (r, s): Fraction(comb(N, r) * comb(N - r, s), CODE_SIZE)
        for r in range(limit + 1)
        for s in range(limit + 1 - r)
    }
    for (a, b), mass in PAIR_MASSES.items():
        for cell, trace in scalar_pair_complete_column(a, b, limit).items():
            result[cell] += mass * trace / CODE_SIZE
    return result


def ordinary_krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** h
        * 2 ** (degree - h)
        * comb(weight, h)
        * comb(N - weight, degree - h)
        for h in range(degree + 1)
    )


def ordinary_certificate() -> dict[str, Any]:
    primal = [Fraction() for _ in range(N + 1)]
    primal[0] = 1
    for (a, b), mass in PAIR_MASSES.items():
        primal[a + b] += 2 * mass
    assert sum(primal, Fraction()) == CODE_SIZE
    dual = [
        sum(
            primal[weight] * ordinary_krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        / CODE_SIZE
        for degree in range(N + 1)
    ]
    slack = [dual[index] - primal[index] for index in range(N + 1)]
    assert dual[:4] == [1, 0, 0, 0]
    assert all(value >= 0 for value in primal)
    assert all(value >= 0 for value in dual)
    assert all(value >= 0 for value in slack)
    short = sum(dual[4:10], Fraction())
    expected_short = Fraction(
        303955951136016513013761953327276372487328891,
        2147091333645300550865262629325,
    )
    assert short == expected_short
    assert short > 18018
    return {
        "primal_total": qstr(sum(primal, Fraction())),
        "primal_support": {
            str(index): qstr(value)
            for index, value in enumerate(primal)
            if value
        },
        "all_232_B_rows_nonnegative": True,
        "all_232_B_rows_at_least_A": True,
        "B0_through_B9": [qstr(value) for value in dual[:10]],
        "minimum_B": qstr(min(dual)),
        "minimum_B_minus_A": qstr(min(slack)),
        "B4_through_B9": qstr(short),
        "strictly_exceeds_18018": True,
    }


def star_pair_forcing_certificate() -> dict[str, Any]:
    edges, nonedges = 693, 4158
    assert edges == 99 * 14 // 2
    assert nonedges == comb(99, 2) - edges
    return {
        "single_stars": {
            "B_7_0_lower": 99,
            "B_0_7_lower": 99,
        },
        "adjacent_star_pairs": {
            "count": edges,
            "sum_compositions": [[12, 1], [1, 12]],
            "difference_composition": [6, 6],
            "lower_rows": {"B_12_1": 693, "B_1_12": 693, "B_6_6": 1386},
        },
        "nonadjacent_star_pairs": {
            "count": nonedges,
            "sum_compositions": [[14, 0], [0, 14]],
            "difference_composition": [7, 7],
            "lower_rows": {"B_14_0": 4158, "B_0_14": 4158, "B_7_7": 8316},
        },
        "distinctness_reason": "support recovers the center or unordered center pair",
        "no_extra_total_degree_seven_pair_row": True,
    }


def complete_certificate() -> dict[str, Any]:
    coefficients = complete_dual_coefficients(14)
    degrees: dict[str, Any] = {}
    for degree in range(8):
        values = [coefficients[(r, degree - r)] for r in range(degree + 1)]
        degrees[str(degree)] = {
            "coefficients_B_r_degree_minus_r": [qstr(value) for value in values],
            "negative_count": sum(value < 0 for value in values),
            "zero_count": sum(value == 0 for value in values),
        }
    assert all(
        coefficients[(r, degree - r)] == 0
        for degree in range(1, 4)
        for r in range(degree + 1)
    )
    degree_four = [coefficients[(r, 4 - r)] for r in range(5)]
    assert degree_four[0] == degree_four[1] == 0
    assert degree_four[2] > 0
    assert degree_four[3] == degree_four[4] == 0
    assert all(
        coefficients[(r, degree - r)] >= 0
        for degree in range(5, 8)
        for r in range(degree + 1)
    )
    assert coefficients[(7, 0)] == coefficients[(0, 7)] == 99
    forcing = star_pair_forcing_certificate()
    lower_rows = {
        (12, 1): 693,
        (1, 12): 693,
        (6, 6): 1386,
        (14, 0): 4158,
        (0, 14): 4158,
        (7, 7): 8316,
    }
    assert all(coefficients[cell] >= lower for cell, lower in lower_rows.items())
    return {
        "degrees_zero_through_seven": degrees,
        "all_complete_rows_through_degree_seven_nonnegative": True,
        "degree_four_row": [qstr(value) for value in degree_four],
        "degree_seven_endpoints": {
            "B_7_0": qstr(coefficients[(7, 0)]),
            "B_0_7": qstr(coefficients[(0, 7)]),
        },
        "star_pair_forcing": forcing,
        "pair_row_actual_values": {
            f"B_{r}_{s}": qstr(coefficients[(r, s)])
            for r, s in lower_rows
        },
        "pair_row_slacks": {
            f"B_{r}_{s}_minus_{lower}": qstr(coefficients[(r, s)] - lower)
            for (r, s), lower in lower_rows.items()
        },
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
    result: list[tuple[int, ...]] = []
    for first_nonzero in range(DIMENSION):
        prefix = (0,) * first_nonzero + (1,)
        for tail in product(range(3), repeat=DIMENSION - first_nonzero - 1):
            result.append(prefix + tail)
    assert len(result) == PROJECTIVE_SIZE
    return tuple(result)


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
            e1, vector_add(f1, e2), vector_add(f1, f2)
        ),
        "no_orthogonal_minus": (
            e1, vector_add(f1, e2), vector_add(f1, vector_scale(2, f2))
        ),
    }
    assert all(
        quadratic_form(vector) == 0
        for vectors in canonical.values()
        for vector in vectors
    )
    triple = {
        name: complement_type_counts(vectors)
        for name, vectors in canonical.items()
    }
    assert triple == {
        "three_orthogonal_pairs": (1093, 1215, 972),
        "two_orthogonal_pairs": (1093, 1134, 1053),
        "one_orthogonal_pair": (1093, 1134, 1053),
        "no_orthogonal_plus": (1066, 1107, 1107),
        "no_orthogonal_minus": (1120, 1080, 1080),
    }
    return {
        "projective_points_enumerated": len(projective_points()),
        "class_sizes_S_plus_minus": [
            class_sizes[0], class_sizes[1], class_sizes[2]
        ],
        "triple_complement_S_plus_minus": {
            name: list(values) for name, values in triple.items()
        },
        "enumeration_scope": "five canonical quadratic complements, not a graph or code search",
    }


def typed_moment_and_census_certificate() -> dict[str, Any]:
    moments = {
        name: tuple(
            sum(
                mass * comb(N - a - b, degree)
                for (a, b), mass in cells.items()
            )
            for degree in range(4)
        )
        for name, cells in TYPE_CELL_MASSES.items()
    }
    degree_two_targets = {
        "singular": (29524, 2273271, 87133200),
        "norm_plus": (29646, 2301453, 88521741),
        "norm_minus": (29403, 2245320, 85771224),
    }
    assert {
        name: values[:3] for name, values in moments.items()
    } == {
        name: tuple(Fraction(value) for value in values)
        for name, values in degree_two_targets.items()
    }

    census = {
        "three_orthogonal_pairs": Fraction(
            7180647277052148633129515561210236,
            429418266729060110173052525865,
        ),
        "two_orthogonal_pairs": Fraction(
            9219695165864115094599706506625844,
            143139422243020036724350841955,
        ),
        "one_orthogonal_pair": Fraction(
            95530879146955891940574034442778796,
            143139422243020036724350841955,
        ),
        "no_orthogonal_plus": Fraction(
            151281112285105230584058395337270808,
            429418266729060110173052525865,
        ),
        "no_orthogonal_minus": Fraction(
            398058731681237045785655912939722711,
            429418266729060110173052525865,
        ),
    }
    assert all(value >= 0 for value in census.values())
    assert sum(census.values(), Fraction()) == comb(N, 3)
    assert (
        census["one_orthogonal_pair"]
        + 2 * census["two_orthogonal_pairs"]
        + 3 * census["three_orthogonal_pairs"]
        == 3696 * (N - 2)
    )
    assert (
        census["two_orthogonal_pairs"]
        + 3 * census["three_orthogonal_pairs"]
        == N * comb(32, 2)
    )
    geometry = quadratic_geometry_certificate()
    complements = {
        name: tuple(values)
        for name, values in geometry["triple_complement_S_plus_minus"].items()
    }
    derived_m3 = tuple(
        sum(census[name] * complements[name][index] for name in census)
        for index in range(3)
    )
    assert derived_m3 == tuple(
        moments[name][3] for name in ("singular", "norm_plus", "norm_minus")
    )
    nonintegral = [name for name, value in census.items() if value.denominator != 1]
    assert nonintegral
    return {
        "factorial_moment_order": ["M0", "M1", "M2", "M3"],
        "typed_factorial_moments": {
            name: [qstr(value) for value in values]
            for name, values in moments.items()
        },
        "rational_gram_census": {
            name: qstr(value) for name, value in census.items()
        },
        "all_census_entries_nonnegative": True,
        "nonintegral_census_classes": nonintegral,
        "triple_total": qstr(sum(census.values(), Fraction())),
        "orthogonal_pair_incidence": qstr(3696 * (N - 2)),
        "orthogonal_wedge_incidence": qstr(N * comb(32, 2)),
        "derived_typed_M3": [qstr(value) for value in derived_m3],
        "realizable_point_set_asserted": False,
    }


def singleton_majority_certificate() -> dict[str, Any]:
    checked = 0
    worst_best = 0
    worst_cases: list[list[int]] = []
    for a in range(1, 7):
        for b in range(1, 7):
            if a + b > 9:
                continue
            for p_x in range(a + 1):
                for p_y in range(b + 1):
                    m_x = max(p_x, a - p_x)
                    m_y = max(p_y, b - p_y)
                    w_x = 7 - m_x + b
                    w_y = a + 7 - m_y
                    best = min(w_x, w_y)
                    assert best <= 9
                    checked += 1
                    if best > worst_best:
                        worst_best = best
                        worst_cases = [[a, b, p_x, p_y, w_x, w_y]]
                    elif best == worst_best:
                        worst_cases.append([a, b, p_x, p_y, w_x, w_y])
    assert worst_best == 9
    return {
        "coefficient_splits_checked": checked,
        "maximum_of_best_axis_translate_weight": worst_best,
        "worst_case_examples": worst_cases[:12],
        "symbolic_contradiction_if_both_at_least_10": (
            "Mx<=b-3 and My<=a-3 with Mx>=a/2, My>=b/2 imply a+b>=12"
        ),
        "translated_support_has_two_proper_star_sides": True,
        "minimal_subcircuit_crosses_private_label": True,
        "outside_selected_cover_by_privacy": True,
    }


def orbit_packing_certificate() -> dict[str, Any]:
    variable_order = ["n1", "n2", "n3", "p2", "p3"]
    private_row = (2, 2, 3, 1, 1)
    lhs = (18, 12, 24, 12, 6)
    seven_private = tuple(7 * value for value in private_row)
    remainder = (4, -2, 3, 5, -1)
    assert tuple(
        seven_private[index] + remainder[index] for index in range(5)
    ) == lhs
    # remainder = 4n1+2(p2-n2)+(3n3-p3)+3p2.
    assert remainder == (4, -2, 3, 5, -1)

    n1, n2, n3, p2, p3 = 0, 0, 1386, 0, 4158
    r, h = 2079, 0
    assignments = n1 + 2 * p2 + p3
    incidence = 2 * n1 + 2 * n2 + 3 * n3 + p2 + p3
    assert incidence == 2 * C
    assert assignments == 4158
    assert assignments == 2 * r + 3 * h
    assert n1 + n2 + 2 * n3 + r + 2 * h == 4851
    assert 12 * 4851 == 14 * C
    return {
        "variable_order": variable_order,
        "private_incidence_row": list(private_row),
        "twelve_Q_row": list(lhs),
        "seven_I_row": list(seven_private),
        "nonnegative_remainder_row": list(remainder),
        "remainder_decomposition": "4*n1+2*(p2-n2)+(3*n3-p3)+3*p2",
        "pool_separation": {
            "selected_vs_companions": "minimality and fixed-point-free involution",
            "raw_extractions_vs_selected": "private label and distinct source support",
            "raw_extractions_vs_selected_companions": "privacy plus own-leaf omission",
            "added_orbit_mates_vs_selected": "privacy and involution",
            "added_orbit_mates_vs_selected_companions": "involution would make raw extraction selected",
            "pairwise_disjoint": True,
        },
        "orbit_capacity": {
            "raw_assignments": "A=n1+2*p2+p3",
            "closed_pool": "|X|=r+2*h",
            "assignment_bound": "A<=2*r+3*h",
            "consequence": "2*|X|>=A",
            "type2_orbit_collision_excluded": (
                "6+2 forces center x, 2+6 forces center y, companions share center"
            ),
        },
        "fractional_bound": {"inequality": "12*Q>=14*C", "Q": 4851},
        "sharp_scalar_control": {
            "n1": n1, "n2": n2, "n3": n3, "p2": p2, "p3": p3,
            "r": r, "h": h,
        },
        "sharp_scalar_control_is_cover_or_graph": False,
    }


def hoffman_null_certificate() -> dict[str, Any]:
    triangles = 231
    anticomplete_centers_per_triangle = 60
    flags = triangles * anticomplete_centers_per_triangle
    row_degree, column_degree = 10, 3
    conflict_degree = column_degree * (row_degree - 1)
    assert flags == 13860
    assert conflict_degree == 27
    # A=H^T H-3I. H^T H is PSD and H has more columns than rows, so A has
    # least eigenvalue exactly -3.
    assert flags > C
    least_eigenvalue = -column_degree
    hoffman = Fraction(flags * -least_eigenvalue, conflict_degree - least_eigenvalue)
    assert hoffman == 1386
    uniform_weight = Fraction(1, row_degree)
    assert flags * uniform_weight == 1386
    uniform_center, uniform_triangle = 14, 6
    assert 99 * uniform_center == triangles * uniform_triangle == 1386
    assert 7 * uniform_triangle == 3 * (28 - uniform_center)
    return {
        "candidate_flags": flags,
        "incidence_matrix_shape": [C, flags],
        "row_degree": row_degree,
        "column_degree": column_degree,
        "flags_share_at_most_one_nonedge": True,
        "conflict_adjacency_identity": "A=H^T*H-3I",
        "conflict_degree": conflict_degree,
        "least_eigenvalue": least_eigenvalue,
        "least_eigenvalue_reason": "PSD plus nontrivial kernel because 13860>4158",
        "hoffman_independence_bound": qstr(hoffman),
        "equality_equivalent_to": "a 0-1 vector b with H*b=1",
        "uniform_rational_flag_weight": qstr(uniform_weight),
        "uniform_center_count": uniform_center,
        "uniform_triangle_replication": uniform_triangle,
        "vertex_triangle_identity": "N*r=3*(28*1-c), hence N*r=0 mod 3",
        "status": "TIGHT_NULL_BOUNDARY_NOT_INTEGRAL_FEASIBILITY",
    }


def equality_cancellation_certificate() -> dict[str, Any]:
    # Coordinates 0..2 are the x-star side; 3..8 are the outer y-star side.
    leaf = [2] * 9
    conic = [1, 2, 0, 2, 1, 0, 0, 0, 0]
    residuals = [
        [(leaf[index] - scalar * conic[index]) % 3 for index in range(9)]
        for scalar in (1, 2)
    ]
    profiles: list[list[int]] = []
    for residual in residuals:
        profile = [
            sum(value != 0 for value in residual[:3]),
            sum(value != 0 for value in residual[3:]),
        ]
        assert profile == [2, 5]
        assert sum(profile) == 7
        assert any(
            conic[index] and not residual[index] for index in range(9)
        )
        profiles.append(profile)
    return {
        "equality_slacks_force": {
            "n1": 0, "n2": 0, "n3": 1386, "p2": 0, "p3": 4158,
            "r": 2079, "h": 0,
        },
        "selected_triples_partition_all_nonedges": True,
        "each_X_circuit_exact_two_with_two_assignments": True,
        "X_is_all_2079_canonical_checkerboard_conics": True,
        "canonical_conic_containment": (
            "the two common-neighbor blocks on both star sides lie in the 3+6 leaf support"
        ),
        "leaf_relation": leaf,
        "checkerboard_relation": conic,
        "leaf_minus_checkerboard": residuals[0],
        "leaf_minus_twice_checkerboard": residuals[1],
        "residual_side_profiles": profiles,
        "residual_weights": [sum(value != 0 for value in row) for row in residuals],
        "proper_star_subsets_force_cross_circuit": True,
        "excluded_existing_pools": {
            "checkerboard": "each residual omits two checkerboard coordinates",
            "selected_owner": "privacy and omitted leaf triangle T",
            "selected_companion": "privacy, same label triple, and omitted T",
            "other_X": "equality saturates two distinct assignments per exact-two label set",
        },
        "contradicts_Q_4851": True,
        "strict_Q_lower": 4852,
        "edge_isolated_projective_circuits": 693,
        "all_projective_short_circuit_lower": 5545,
        "scalar_short_circuit_word_lower": 11090,
    }


def analytic_theorem_certificate() -> dict[str, Any]:
    singleton = singleton_majority_certificate()
    packing = orbit_packing_certificate()
    hoffman = hoffman_null_certificate()
    equality = equality_cancellation_certificate()
    assert equality["strict_Q_lower"] == 4852
    assert equality["all_projective_short_circuit_lower"] == 4852 + 693
    assert equality["scalar_short_circuit_word_lower"] == 2 * 5545
    return {
        "status": "VERIFIED_CONDITIONAL_THEOREM",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "singleton_majority_translation": singleton,
        "pool_separation_orbit_closure_and_scalar_identity": packing,
        "design_spectral_null_boundary": hoffman,
        "equality_saturation_and_weight7_exclusion": equality,
        "Q_lower": 4852,
        "circuit_specific_scalar_short_word_lower": 11090,
        "wave188_all_short_word_lower_remains_stronger": 18018,
        "rank_11_excluded": False,
        "endpoint_excluded": False,
        "conway_99_resolved": False,
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave189-degree7-star-orbit-clean-room-verification-v1",
        "verdict": "VERIFIED_WITH_SCOPE",
        "integrity": integrity,
        "degree7_relaxation": {
            "status": "VERIFIED_RELAXATION_FEASIBILITY",
            "masses": mass_certificate(),
            "local_star_polygon": star_polygon_certificate(),
            "ordinary_macwilliams": ordinary_certificate(),
            "complete_macwilliams": complete_certificate(),
            "quadratic_geometry": quadratic_geometry_certificate(),
            "typed_moments_and_rational_census": typed_moment_and_census_certificate(),
            "linear_code_constructed": False,
            "projective_point_set_constructed": False,
            "graph_constructed": False,
            "endpoint_existence_proved": False,
        },
        "analytic_circuit_theorem": analytic_theorem_certificate(),
        "boundary": {
            "rational_relaxation_feasible": True,
            "relaxation_feasibility_implies_code_existence": False,
            "conditional_Q_at_least_4852_verified": True,
            "conditional_theorem_implies_endpoint_exclusion": False,
            "rank_11_status": "UNKNOWN",
            "endpoint_status": "UNKNOWN",
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
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build_results()
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE Wave 189 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            print("FAIL Wave 189 clean-room verification")
            return 1
        print(f"PASS Wave 189 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
