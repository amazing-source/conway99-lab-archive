#!/usr/bin/env python3
"""Clean-room exact-face verifier for Wave135.

Only the frozen Wave134 mathematical statement is used.  No Wave135
discovery implementation is imported or inspected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Sequence


N = 99
PRIMAL_SIZE = 2**109
DUAL_SIZE = 2**89
RANK_CERTIFICATE_PRIME = 1_000_000_007
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE134_RESULTS = (
    ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
    / "exact-results.json"
)
EXPECTED_WAVE134_RESULTS_SHA256 = (
    "8d3e39c4360341f7d3d6b8ac496853c0ae19e546ab8655cc6939b36edbddb1a2"
)
DISCOVERY = ROOT / "attempts" / "wave135-z4-exact-face"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "6f466d96036d7fe48a1ab3be6590683fa46648a6fae5582913f9e4721e541f1a"
)
EXPECTED_DISCOVERY_MANIFEST_ENTRIES = 16
DISCOVERY_FACE = DISCOVERY / "face-rank.json"
EXPECTED_DISCOVERY_FACE_SHA256 = (
    "55cf42ef789b1a3d4c57a9018072e09e49a0b27d766738d8f820e253a0c99af2"
)
DISCOVERY_STATUS = DISCOVERY / "search-status.json"
EXPECTED_DISCOVERY_STATUS_SHA256 = (
    "4b1e9603edf933edae664346bb5271e59964a0879c358ad7f2582bd37e1321f1"
)
DISCOVERY_SHIFTED_TRACE = DISCOVERY / "row-generation.json"
EXPECTED_DISCOVERY_SHIFTED_TRACE_SHA256 = (
    "66d79880bd55aebb138e9d7daad0c16cfc33f5e6c308ce62c6e524d023e1b3b9"
)
DISCOVERY_UNSHIFTED_TRACE = DISCOVERY / "row-generation-unshifted.json"
EXPECTED_DISCOVERY_UNSHIFTED_TRACE_SHA256 = (
    "4a5de2e24c43cd8ea3044e5195e4360a18f224a8eb0fa6fdf9b278b14a33b87e"
)
MODEL_BASE = "wave135-identity-size-face-v1"
MODEL_TORSION = "wave135-identity-size-torsion-face-v1"

Composition = tuple[int, int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_rational(value: object) -> Fraction:
    require(not isinstance(value, bool), "Boolean is not a rational encoding")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        require(value.strip() == value and value, "noncanonical rational string")
        return Fraction(value)
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) and not isinstance(item, bool)
                for item in value)
    ):
        require(value[1] > 0, "rational denominator must be positive")
        return Fraction(value[0], value[1])
    raise AssertionError(f"unsupported exact rational encoding: {value!r}")


def composition_key(composition: Composition) -> str:
    return ",".join(str(value) for value in composition)


def swap_zero_two(composition: Composition) -> Composition:
    zeros, odd, twos = composition
    return twos, odd, zeros


def all_orbit_representatives() -> list[Composition]:
    """Even-residue zero/two orbit representatives, with n0 >= n2."""

    output = []
    for odd in range(0, N + 1, 2):
        for twos in range((N - odd) // 2 + 1):
            zeros = N - odd - twos
            require(zeros > twos, "degree 99 has no fixed even-residue orbit")
            output.append((zeros, odd, twos))
    require(len(output) == 1_275, "even-residue orbit count")
    return output


def primal_orbits() -> list[Composition]:
    """The 1,119 structurally admissible primal coefficient orbits."""

    output = []
    for composition in all_orbit_representatives():
        _zeros, odd, twos = composition
        allowed = (
            twos not in range(1, 7)
            if odd == 0
            else 8 <= odd <= 92
        )
        if allowed:
            output.append(composition)
    require(len(output) == 1_119, "primal orbit count")
    return output


def dual_orbits(*, allowed: bool) -> list[Composition]:
    """The 1,114 allowed or 161 zero dual coefficient orbits."""

    output = []
    for composition in all_orbit_representatives():
        _zeros, odd, twos = composition
        is_allowed = (
            twos not in range(1, 8)
            if odd == 0
            else 8 <= odd <= 90
        )
        if is_allowed == allowed:
            output.append(composition)
    expected = 1_114 if allowed else 161
    require(len(output) == expected, "dual orbit partition")
    return output


@lru_cache(maxsize=None)
def krawtchouk(total: int, negative: int, degree: int) -> int:
    """Coefficient [t^degree](1+t)^(total-negative)(1-t)^negative."""

    require(0 <= negative <= total <= N, "bad Krawtchouk parameters")
    if degree < 0 or degree > total:
        return 0
    positive = total - negative
    return sum(
        (-1) ** from_negative
        * math.comb(negative, from_negative)
        * math.comb(positive, degree - from_negative)
        for from_negative in range(
            max(0, degree - positive), min(negative, degree) + 1
        )
    )


def reduced_face_entry(source: Composition, target: Composition) -> int:
    """Zero-row coefficient after removing a nonzero common power of two.

    The full coefficient of one expanded source is

      2^r K_r(a,c) K_s(99-r,b),

    where source=(a,b,c) and target=(*,r,s).  A source orbit contains its
    zero/two swap with the same coefficient because r is even, adding another
    common factor two.  Removing 2^(r+1) preserves every rational zero row.
    """

    zeros, odd, twos = source
    _target_zeros, target_odd, target_twos = target
    require(target_odd % 2 == 0, "face row must have even odd-symbol count")
    first = krawtchouk(zeros + twos, twos, target_odd)
    if first == 0 or odd > N - target_odd:
        return 0
    second = krawtchouk(N - target_odd, odd, target_twos)
    return first * second


@lru_cache(maxsize=1)
def face_matrix() -> tuple[list[Composition], list[Composition], list[list[int]]]:
    sources = primal_orbits()
    zero_targets = dual_orbits(allowed=False)
    matrix = [
        [reduced_face_entry(source, target) for source in sources]
        for target in zero_targets
    ]
    require(len(matrix) == 161, "zero-row matrix height")
    require(all(len(row) == 1_119 for row in matrix),
            "zero-row matrix width")
    return sources, zero_targets, matrix


def matrix_sha256(matrix: Sequence[Sequence[int]]) -> str:
    digest = hashlib.sha256()
    for row in matrix:
        digest.update(",".join(str(value) for value in row).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def modular_rank_and_pivots(
    matrix: Sequence[Sequence[int]], prime: int
) -> tuple[int, list[int]]:
    require(prime > 2, "rank prime")
    if not matrix:
        return 0, []
    rows = [[value % prime for value in row] for row in matrix]
    height = len(rows)
    width = len(rows[0])
    pivot_row = 0
    pivots: list[int] = []
    for column in range(width):
        selected = next(
            (row for row in range(pivot_row, height) if rows[row][column]),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row]
        inverse = pow(pivot[column], prime - 2, prime)
        pivot[column:] = [
            value * inverse % prime for value in pivot[column:]
        ]
        for row_index in range(height):
            if row_index == pivot_row:
                continue
            factor = rows[row_index][column]
            if not factor:
                continue
            row = rows[row_index]
            row[column:] = [
                (left - factor * right) % prime
                for left, right in zip(
                    row[column:], pivot[column:], strict=True
                )
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row, pivots


def determinant_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "determinant square")
    rows = [[value % prime for value in row] for row in matrix]
    determinant = 1
    for column in range(size):
        selected = next(
            (row for row in range(column, size) if rows[row][column]),
            None,
        )
        if selected is None:
            return 0
        if selected != column:
            rows[column], rows[selected] = rows[selected], rows[column]
            determinant = -determinant
        pivot = rows[column][column]
        determinant = determinant * pivot % prime
        inverse = pow(pivot, prime - 2, prime)
        for row_index in range(column + 1, size):
            factor = rows[row_index][column] * inverse % prime
            if not factor:
                continue
            rows[row_index][column:] = [
                (left - factor * right) % prime
                for left, right in zip(
                    rows[row_index][column:],
                    rows[column][column:],
                    strict=True,
                )
            ]
    return determinant % prime


def block_rank_upper_bound(
    sources: Sequence[Composition],
    targets: Sequence[Composition],
) -> tuple[int, list[dict[str, object]]]:
    """Prove the row-rank upper bound shell by shell.

    For fixed target odd count r, a matrix entry factors as

      K_r(99-b,c) K_s(99-r,b).

    Within a fixed source odd count b, the first factor only rescales
    columns, so the row block is spanned by at most one vector per active b.
    """

    records = []
    total_upper = 0
    for target_odd in sorted({target[1] for target in targets}):
        block = [target for target in targets if target[1] == target_odd]
        active_source_odds = sorted(
            {
                source[1]
                for source in sources
                if source[1] <= N - target_odd
            }
        )
        upper = min(len(block), len(active_source_odds))
        total_upper += upper
        records.append(
            {
                "target_odd_count": target_odd,
                "rows": len(block),
                "active_source_odd_counts": active_source_odds,
                "active_source_odd_count_total": len(active_source_odds),
                "rank_upper_bound": upper,
                "dependency_lower_bound": len(block) - upper,
            }
        )
    require(total_upper == 143, "unexpected block rank upper bound")
    require(
        sum(record["dependency_lower_bound"] for record in records) == 18,
        "unexpected dependency count",
    )
    return total_upper, records


def identity_row(sources: Sequence[Composition]) -> list[int]:
    return [int(source == (N, 0, 0)) for source in sources]


def total_size_row(sources: Sequence[Composition]) -> list[int]:
    # Each orbit represents two expanded compositions with equal coefficient;
    # the common factor two is divided out.
    return [1] * len(sources)


def primal_torsion_size_row(
    sources: Sequence[Composition],
) -> list[int]:
    # The b=0 expanded slice has size 2^55; after orbit pairing its sum is 2^54.
    return [int(source[1] == 0) for source in sources]


def dual_torsion_numerator_row(
    sources: Sequence[Composition],
) -> list[int]:
    """Numerator row for the allowed dual odd-symbol-zero orbit sum."""

    allowed_zero_shell = [
        target for target in dual_orbits(allowed=True) if target[1] == 0
    ]
    require(len(allowed_zero_shell) == 43, "dual zero-residue allowed shell")
    return [
        sum(reduced_face_entry(source, target)
            for target in allowed_zero_shell)
        for source in sources
    ]


def shell_fibre_audit(
    sources: Sequence[Composition],
    zero_targets: Sequence[Composition],
    zero_matrix: Sequence[Sequence[int]],
) -> dict[str, object]:
    """Audit exact zero-shell totals and segregate divisibility claims."""

    torsion = primal_torsion_size_row(sources)
    dual_numerator = dual_torsion_numerator_row(sources)
    forbidden_zero_rows = [
        row
        for target, row in zip(zero_targets, zero_matrix, strict=True)
        if target[1] == 0
    ]
    require(len(forbidden_zero_rows) == 7, "forbidden dual zero shell")
    for column in range(len(sources)):
        require(
            dual_numerator[column]
            + sum(row[column] for row in forbidden_zero_rows)
            == 2**98 * torsion[column],
            "primal/dual torsion-shell identity",
        )

    rank_with_primal = modular_rank_and_pivots(
        list(zero_matrix)
        + [identity_row(sources), total_size_row(sources), torsion],
        RANK_CERTIFICATE_PRIME,
    )[0]
    rank_with_both = modular_rank_and_pivots(
        list(zero_matrix)
        + [
            identity_row(sources),
            total_size_row(sources),
            torsion,
            dual_numerator,
        ],
        RANK_CERTIFICATE_PRIME,
    )[0]
    require(rank_with_primal == rank_with_both == 146,
            "dual torsion row should be redundant")
    return {
        "primal_zero_residue_orbit_sum": {
            "equality": "sum_{source_odd=0} A_source=2^54",
            "expanded_interpretation": "|Tor(C)|=2^55",
        },
        "dual_zero_residue_orbit_sum": {
            "equality": "sum_{target_odd=0} B_target=2^44",
            "expanded_interpretation": "|Tor(Cperp)|=2^45",
            "reduced_numerator_rhs": 2**152,
            "independent_after_primal_equality": False,
        },
        "exact_row_identity": (
            "dual_allowed_b0_numerator + sum(dual_forbidden_b0_rows) "
            "= 2^98 * primal_b0_indicator"
        ),
        "rank_with_primal_torsion": rank_with_primal,
        "rank_with_both_torsion_equalities": rank_with_both,
        "constant_fibre_consequences": {
            "primal": (
                "For every residue weight b, the expanded shell total is "
                "2^55 times the number of words of weight b in Res(C). "
                "In orbit coordinates it is 2^54 times that integer."
            ),
            "dual": (
                "For every residue weight b, the expanded shell total is "
                "2^45 times the number of words of weight b in Res(Cperp). "
                "In orbit coordinates it is 2^44 times that integer."
            ),
            "additional_numeric_equalities_over_Q": "NONE",
            "reason": (
                "Only the zero-residue multiplicity is known to be one. "
                "For b>0 the binary residue enumerator coefficients are "
                "unknown; constant fibres give integrality/divisibility, "
                "not fixed rational shell totals."
            ),
            "integer_divisibility_separate_from_rational_face": {
                "primal_orbit_shell_multiple": 2**54,
                "dual_orbit_shell_multiple": 2**44,
            },
        },
    }


def certified_rank(
    matrix: Sequence[Sequence[int]],
    sources: Sequence[Composition],
    upper_bound: int,
) -> dict[str, object]:
    rank, pivot_columns = modular_rank_and_pivots(
        matrix, RANK_CERTIFICATE_PRIME
    )
    require(rank == upper_bound, "modular lower bound misses exact upper bound")
    transpose = [list(column) for column in zip(*matrix, strict=True)]
    transpose_rank, pivot_rows = modular_rank_and_pivots(
        transpose, RANK_CERTIFICATE_PRIME
    )
    require(transpose_rank == rank, "row/column modular ranks disagree")
    minor = [
        [matrix[row][column] for column in pivot_columns]
        for row in pivot_rows
    ]
    determinant_residue = determinant_mod(minor, RANK_CERTIFICATE_PRIME)
    require(determinant_residue != 0, "rank minor is zero modulo prime")
    return {
        "rank_over_Q": rank,
        "nullity": len(sources) - rank,
        "prime": RANK_CERTIFICATE_PRIME,
        "pivot_column_indices": pivot_columns,
        "pivot_row_indices": pivot_rows,
        "pivot_source_compositions": [
            list(sources[index]) for index in pivot_columns
        ],
        "minor_determinant_mod_prime": determinant_residue,
    }


def parse_composition_key(key: str) -> Composition:
    parts = key.split(",")
    require(len(parts) == 3, f"bad composition key: {key}")
    require(all(part.isdigit() for part in parts),
            f"nonintegral composition key: {key}")
    composition = tuple(int(part) for part in parts)
    require(sum(composition) == N, f"bad composition degree: {key}")
    return composition  # type: ignore[return-value]


@lru_cache(maxsize=1)
def frozen_lower_bounds() -> tuple[dict[Composition, int], dict[Composition, int]]:
    require(sha256(WAVE134_RESULTS) == EXPECTED_WAVE134_RESULTS_SHA256,
            "frozen Wave134 result hash drift")
    data = json.loads(WAVE134_RESULTS.read_text(encoding="utf-8"))
    require(data["format"] == "wave134-z4-derived-checkpoint-v1",
            "frozen Wave134 schema")
    require(data["transform"] == {
        "allowed_dual_orbits": 1_114,
        "forbidden_dual_orbits": 161,
        "primal_orbits": 1_119,
        "raw_states": 5_050,
        "zero_monomial_rows_checked": 5_050,
    }, "frozen Wave134 transform counts")
    primal = {
        parse_composition_key(key): int(value)
        for key, value in data["forced_words"]["primal_orbits"].items()
    }
    dual = {
        parse_composition_key(key): int(value)
        for key, value in data["forced_words"]["dual_orbits"].items()
    }
    require(len(primal) == 42, "frozen primal forced orbits")
    require(len(dual) == 22, "frozen dual forced orbits")
    require(set(primal).issubset(primal_orbits()),
            "forced primal orbit outside model")
    require(set(dual).issubset(dual_orbits(allowed=True)),
            "forced dual orbit outside model")
    return primal, dual


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def load_dense_primal(
    candidate: Mapping[str, object],
) -> tuple[str, list[Fraction]]:
    require(candidate.get("format") == "wave135-z4-rational-primal-v1",
            "rational primal schema")
    model = candidate.get("model")
    require(model in (MODEL_BASE, MODEL_TORSION), "unknown primal model")
    encoded = candidate.get("coefficients")
    require(isinstance(encoded, dict), "primal coefficients must be an object")
    sources = primal_orbits()
    expected_keys = [composition_key(source) for source in sources]
    require(
        set(encoded) == set(expected_keys),
        "rational primal must contain every source orbit exactly once",
    )
    coefficients = [parse_rational(encoded[key]) for key in expected_keys]
    return str(model), coefficients


def dot_integer_rational(
    row: Sequence[int], vector: Sequence[Fraction]
) -> Fraction:
    require(len(row) == len(vector), "dot-product length")
    return sum(
        (coefficient * value for coefficient, value in zip(row, vector, strict=True)),
        start=Fraction(0),
    )


def verify_rational_primal(candidate: Mapping[str, object]) -> dict[str, object]:
    """Hostile exact check for a dense rational primal witness."""

    model, coefficients = load_dense_primal(candidate)
    sources, zero_targets, zero_matrix = face_matrix()
    primal_lower, dual_lower = frozen_lower_bounds()

    for source, value in zip(sources, coefficients, strict=True):
        require(
            value >= primal_lower.get(source, 0),
            f"primal lower bound fails at {composition_key(source)}",
        )
    for target, row in zip(zero_targets, zero_matrix, strict=True):
        require(
            dot_integer_rational(row, coefficients) == 0,
            f"forbidden dual row nonzero at {composition_key(target)}",
        )
    require(
        dot_integer_rational(identity_row(sources), coefficients) == 1,
        "identity coefficient is not one",
    )
    require(
        dot_integer_rational(total_size_row(sources), coefficients) == 2**108,
        "primal total size fails",
    )
    torsion_sum = dot_integer_rational(
        primal_torsion_size_row(sources), coefficients
    )
    if model == MODEL_TORSION:
        require(torsion_sum == 2**54, "primal torsion slice size fails")

    minimum_dual_slack: Fraction | None = None
    dual_torsion_sum = Fraction(0)
    for target in dual_orbits(allowed=True):
        row = [reduced_face_entry(source, target) for source in sources]
        numerator = dot_integer_rational(row, coefficients)
        denominator = 2 ** (108 - target[1])
        lower = dual_lower.get(target, 0)
        slack = numerator - lower * denominator
        require(
            slack >= 0,
            f"dual lower bound fails at {composition_key(target)}",
        )
        if minimum_dual_slack is None or slack / denominator < minimum_dual_slack:
            minimum_dual_slack = slack / denominator
        if target[1] == 0:
            dual_torsion_sum += numerator / denominator
    require(minimum_dual_slack is not None, "no allowed dual rows")
    if model == MODEL_TORSION:
        require(dual_torsion_sum == 2**44,
                "dual torsion slice size fails")
    return {
        "format": "wave135-z4-rational-primal-verification-v1",
        "model": model,
        "source_orbits_checked": len(sources),
        "zero_rows_checked": len(zero_targets),
        "allowed_dual_rows_checked": len(dual_orbits(allowed=True)),
        "minimum_dual_slack": fraction_record(minimum_dual_slack),
        "torsion_slice_sum": fraction_record(torsion_sum),
        "dual_torsion_slice_sum": fraction_record(dual_torsion_sum),
        "torsion_size_equality_enforced": model == MODEL_TORSION,
        "classification": (
            "VERIFIED_RATIONAL_TORSION_TIGHTENED"
            if model == MODEL_TORSION
            else "VERIFIED_RATIONAL_BASE_FACE_ONLY"
        ),
        "limitations": (
            "A rational enumerator is not an integral enumerator, Z4 code, "
            "adjacency matrix, graph, or Conway-99 resolution."
        ),
    }


def verify_farkas_arrays(
    equality_rows: Sequence[Sequence[int]],
    equality_rhs: Sequence[int],
    equality_multipliers: Sequence[Fraction],
    inequality_rows: Sequence[Sequence[int]],
    inequality_lower: Sequence[int],
    inequality_multipliers: Sequence[Fraction],
) -> Fraction:
    """Verify the convention Ex=h, Gx>=l, yE+zG=0, yh+zl>0."""

    require(len(equality_rows) == len(equality_rhs)
            == len(equality_multipliers), "Farkas equality lengths")
    require(len(inequality_rows) == len(inequality_lower)
            == len(inequality_multipliers), "Farkas inequality lengths")
    width = len(equality_rows[0]) if equality_rows else len(inequality_rows[0])
    stationarity = [Fraction(0) for _ in range(width)]
    for multiplier, row in zip(
        equality_multipliers, equality_rows, strict=True
    ):
        require(len(row) == width, "Farkas equality width")
        for index, coefficient in enumerate(row):
            stationarity[index] += multiplier * coefficient
    for multiplier, row in zip(
        inequality_multipliers, inequality_rows, strict=True
    ):
        require(multiplier >= 0, "negative Farkas inequality multiplier")
        require(len(row) == width, "Farkas inequality width")
        for index, coefficient in enumerate(row):
            stationarity[index] += multiplier * coefficient
    require(all(value == 0 for value in stationarity),
            "Farkas stationarity fails")
    margin = sum(
        (multiplier * rhs for multiplier, rhs in zip(
            equality_multipliers, equality_rhs, strict=True
        )),
        start=Fraction(0),
    ) + sum(
        (multiplier * lower for multiplier, lower in zip(
            inequality_multipliers, inequality_lower, strict=True
        )),
        start=Fraction(0),
    )
    require(margin > 0, "Farkas contradiction margin is not positive")
    return margin


def verify_farkas_candidate(candidate: Mapping[str, object]) -> dict[str, object]:
    """Hostile exact check for a sparse Farkas certificate."""

    require(candidate.get("format") == "wave135-z4-farkas-v1",
            "Farkas schema")
    model = candidate.get("model")
    require(model in (MODEL_BASE, MODEL_TORSION), "unknown Farkas model")
    encoded_equalities = candidate.get("equality_multipliers")
    encoded_inequalities = candidate.get("inequality_multipliers")
    require(isinstance(encoded_equalities, dict),
            "equality multipliers must be an object")
    require(isinstance(encoded_inequalities, dict),
            "inequality multipliers must be an object")

    sources, zero_targets, zero_matrix = face_matrix()
    primal_lower, dual_lower = frozen_lower_bounds()
    equality_rows: dict[str, tuple[Sequence[int], int]] = {
        f"zero:{composition_key(target)}": (row, 0)
        for target, row in zip(zero_targets, zero_matrix, strict=True)
    }
    equality_rows["identity"] = (identity_row(sources), 1)
    equality_rows["total_size"] = (total_size_row(sources), 2**108)
    if model == MODEL_TORSION:
        equality_rows["primal_torsion_size"] = (
            primal_torsion_size_row(sources),
            2**54,
        )
    require(
        set(encoded_equalities).issubset(equality_rows),
        "unknown equality multiplier key",
    )

    stationarity = [Fraction(0) for _ in sources]
    margin = Fraction(0)
    nonzero_equalities = 0
    for key, encoded in encoded_equalities.items():
        multiplier = parse_rational(encoded)
        row, rhs = equality_rows[key]
        if multiplier:
            nonzero_equalities += 1
        for index, coefficient in enumerate(row):
            stationarity[index] += multiplier * coefficient
        margin += multiplier * rhs

    primal_prefix = "primal:"
    dual_prefix = "dual:"
    source_index = {
        composition_key(source): index for index, source in enumerate(sources)
    }
    allowed_targets = {
        composition_key(target): target for target in dual_orbits(allowed=True)
    }
    nonzero_inequalities = 0
    for key, encoded in encoded_inequalities.items():
        multiplier = parse_rational(encoded)
        require(multiplier >= 0, f"negative multiplier at {key}")
        if multiplier:
            nonzero_inequalities += 1
        if key.startswith(primal_prefix):
            composition = key[len(primal_prefix):]
            require(composition in source_index,
                    f"unknown primal inequality: {composition}")
            index = source_index[composition]
            source = sources[index]
            stationarity[index] += multiplier
            margin += multiplier * primal_lower.get(source, 0)
        elif key.startswith(dual_prefix):
            composition = key[len(dual_prefix):]
            require(composition in allowed_targets,
                    f"unknown dual inequality: {composition}")
            target = allowed_targets[composition]
            for index, source in enumerate(sources):
                stationarity[index] += (
                    multiplier * reduced_face_entry(source, target)
                )
            scaled_lower = (
                dual_lower.get(target, 0) * 2 ** (108 - target[1])
            )
            margin += multiplier * scaled_lower
        else:
            raise AssertionError(f"unknown inequality multiplier key: {key}")

    require(all(value == 0 for value in stationarity),
            "Farkas stationarity fails")
    require(margin > 0, "Farkas contradiction margin is not positive")
    return {
        "format": "wave135-z4-farkas-verification-v1",
        "model": model,
        "nonzero_equality_multipliers": nonzero_equalities,
        "nonzero_inequality_multipliers": nonzero_inequalities,
        "contradiction_margin": fraction_record(margin),
        "classification": "VERIFIED_FARKAS_INFEASIBILITY",
        "scope": (
            "Exact infeasibility of the declared symmetrized-enumerator "
            "relaxation only."
        ),
        "limitations": (
            "The certificate scope does not exceed its declared relaxation; "
            "it is not automatically a direct graph-theoretic proof."
        ),
    }


def verify_discovery_manifest() -> dict[str, object]:
    require(
        sha256(DISCOVERY_MANIFEST) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "Wave135 discovery manifest hash drift",
    )
    entries = 0
    for line in DISCOVERY_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = ROOT / relative
        require(
            target.resolve().is_relative_to(DISCOVERY.resolve()),
            f"Wave135 sealed target escapes package: {relative}",
        )
        require(target.is_file(), f"missing Wave135 sealed target: {relative}")
        require(sha256(target) == expected,
                f"Wave135 sealed target drift: {relative}")
        entries += 1
    require(entries == EXPECTED_DISCOVERY_MANIFEST_ENTRIES,
            "Wave135 manifest entry count")
    return {
        "path": "attempts/wave135-z4-exact-face/package-manifest.sha256",
        "sha256": EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "entries_checked": entries,
    }


def load_json_object(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"JSON root is not an object: {path}")
    return data


def audit_dependency_artifact(
    face: Mapping[str, object],
    targets: Sequence[Composition],
    matrix: Sequence[Sequence[int]],
) -> dict[str, object]:
    target_index = {target: index for index, target in enumerate(targets)}
    require(len(target_index) == len(targets), "duplicate independent targets")
    dependency_data = face["forbidden_row_dependencies"]
    require(dependency_data["dimension"] == 18,
            "sealed dependency dimension")
    basis = dependency_data["basis"]
    require(isinstance(basis, list) and len(basis) == 18,
            "sealed dependency basis size")
    relation_rows: list[list[int]] = []
    maximum_support = 0
    for relation in basis:
        support = relation["support"]
        require(isinstance(support, list) and support,
                "empty sealed dependency")
        relation_vector = [0] * len(targets)
        coefficients = []
        seen_targets: set[Composition] = set()
        for term in support:
            target = tuple(term["target"])
            require(target in target_index,
                    f"dependency target outside zero rows: {target}")
            require(target not in seen_targets,
                    "duplicate target in sealed dependency")
            seen_targets.add(target)
            coefficient = int(term["coefficient"])
            require(coefficient != 0, "zero displayed dependency coefficient")
            coefficients.append(coefficient)
            relation_vector[target_index[target]] = coefficient
        require(math.gcd(*coefficients) == 1,
                "sealed dependency is not primitive")
        for column in range(len(matrix[0])):
            require(
                sum(
                    relation_vector[row] * matrix[row][column]
                    for row in range(len(targets))
                )
                == 0,
                "sealed dependency fails clean-room matrix",
            )
        relation_rows.append(relation_vector)
        maximum_support = max(maximum_support, len(support))
    dependency_rank, _ = modular_rank_and_pivots(
        relation_rows, RANK_CERTIFICATE_PRIME
    )
    require(dependency_rank == 18,
            "sealed dependencies are not independent")

    basis_data = face["forbidden_row_basis"]
    independent_targets = [
        tuple(target) for target in basis_data["independent_targets"]
    ]
    require(len(independent_targets) == 143,
            "sealed independent row count")
    require(len(set(independent_targets)) == 143,
            "duplicate sealed independent row")
    require(set(independent_targets).issubset(target_index),
            "sealed independent row outside target set")
    selected_matrix = [matrix[target_index[target]]
                       for target in independent_targets]
    selected_rank, _ = modular_rank_and_pivots(
        selected_matrix, RANK_CERTIFICATE_PRIME
    )
    require(selected_rank == 143,
            "sealed row basis fails clean-room matrix")
    return {
        "primitive_dependencies_checked": 18,
        "dependency_rank": dependency_rank,
        "maximum_dependency_support": maximum_support,
        "independent_rows_checked": 143,
        "independent_row_rank": selected_rank,
    }


def audit_null_trace(
    path: Path,
    expected_sha256: str,
    expected_iterations: int,
) -> dict[str, object]:
    require(sha256(path) == expected_sha256, f"trace hash drift: {path.name}")
    data = load_json_object(path)
    require(set(data) == {"classification", "trace"},
            f"trace contains promoted fields: {path.name}")
    require(data["classification"] == "UNKNOWN_WALL",
            f"trace classification inflated: {path.name}")
    trace = data["trace"]
    require(isinstance(trace, list) and len(trace) == expected_iterations,
            f"trace iteration count: {path.name}")
    expected_keys = {
        "iteration",
        "most_negative",
        "peak_working_set_bytes",
        "violated_rows",
        "working_rows",
        "working_set_bytes",
    }
    for iteration, record in enumerate(trace):
        require(set(record) == expected_keys,
                f"trace record schema: {path.name}")
        require(record["iteration"] == iteration,
                f"trace iteration ordering: {path.name}")
        require(Fraction(record["most_negative"]) < 0,
                f"trace must remain violated: {path.name}")
        for key in (
            "peak_working_set_bytes",
            "violated_rows",
            "working_rows",
            "working_set_bytes",
        ):
            require(isinstance(record[key], int) and record[key] >= 0,
                    f"trace count field: {path.name}:{key}")
    return {
        "path": f"attempts/wave135-z4-exact-face/{path.name}",
        "sha256": expected_sha256,
        "classification": "UNKNOWN_WALL",
        "iterations_checked": len(trace),
        "terminal_violated_rows": trace[-1]["violated_rows"],
        "inference": "NONE",
    }


def audit_sealed_discovery() -> dict[str, object]:
    require(sha256(DISCOVERY_FACE) == EXPECTED_DISCOVERY_FACE_SHA256,
            "sealed face-rank hash drift")
    require(sha256(DISCOVERY_STATUS) == EXPECTED_DISCOVERY_STATUS_SHA256,
            "sealed search-status hash drift")
    face = load_json_object(DISCOVERY_FACE)
    status = load_json_object(DISCOVERY_STATUS)
    require(face["format"] == "wave135-z4-exact-face-rank-v1",
            "sealed face-rank schema")
    require(face["claim_label"] == "DERIVED",
            "sealed face-rank claim label")
    dimensions = face["dimensions"]
    expected_dimensions = {
        "affine_coefficient_rank_Q": 146,
        "affine_dimension_Q": 973,
        "affine_dimension_before_torsion_shell_Q": 974,
        "affine_rank_before_torsion_shell_Q": 145,
        "affine_rows_with_normalization_and_A0": 163,
        "affine_rows_with_torsion_shell": 164,
        "primal_orbit_variables": 1_119,
        "zero_dual_rows": 161,
        "zero_face_nullity_Q": 976,
        "zero_face_rank_Q": 143,
    }
    require(dimensions == expected_dimensions,
            "sealed exact-face dimensions disagree")

    sources, targets, matrix = face_matrix()
    dependency_audit = audit_dependency_artifact(face, targets, matrix)
    flint = face["flint_rref"]
    require(len(flint["zero_pivot_columns"]) == 143,
            "sealed FLINT zero pivots")
    require(len(flint["combined_pivot_columns"]) == 145,
            "sealed FLINT affine pivots")
    require(len(flint["torsion_extended_pivot_columns"]) == 146,
            "sealed FLINT torsion pivots")
    modular = face["modular_minor_certificate"]
    require(modular["prime"] == 2_147_483_647,
            "sealed modular certificate prime")
    for key, expected in (
        ("zero_rank_mod_prime", 143),
        ("combined_rank_mod_prime", 145),
        ("augmented_rank_mod_prime", 145),
        ("torsion_extended_rank_mod_prime", 146),
        ("torsion_extended_augmented_rank_mod_prime", 146),
    ):
        require(modular[key] == expected,
                f"sealed modular rank mismatch: {key}")
    require(
        face["affine_consistency"]["classification"] == "CONSISTENT",
        "sealed equality consistency",
    )
    require(
        face["torsion_shell_equality"]["rank_increment"] == 1
        and face["torsion_shell_equality"][
            "independent_of_prior_affine_rows"
        ],
        "sealed torsion equality status",
    )

    require(status["format"] == "wave135-z4-exact-face-search-status-v1",
            "sealed search-status schema")
    require(status["claim_label"] == "UNKNOWN",
            "sealed search-status label")
    require(status["rational_feasibility"] == "UNKNOWN_WALL",
            "sealed rational status inflated")
    require(status["corrected_dimensions"] == {
        "affine_dimension_after_torsion_shell": 973,
        "affine_rank_after_torsion_shell": 146,
        "allowed_dual_rows": 1_114,
        "forbidden_dual_rank_Q": 143,
        "forbidden_dual_row_dependencies": 18,
        "forbidden_dual_rows": 161,
        "primal_orbit_variables": 1_119,
    }, "sealed status dimensions")
    for run in status["runs"].values():
        require(run["classification"] == "UNKNOWN_WALL",
                "bounded run status inflated")
    wall = status["status_wall"]
    require(wall["exact_Farkas_certificate"] == "NOT_FOUND",
            "Farkas status inflated")
    require(
        {
            wall["Conway_99"],
            wall["integral_enumerator_feasibility"],
            wall["novelty"],
            wall["quaternary_code_realizability"],
            wall["rational_enumerator_feasibility"],
            wall["strongly_regular_graph_realizability"],
        }
        == {"UNKNOWN"},
        "sealed logical wall inflated",
    )
    shifted = audit_null_trace(
        DISCOVERY_SHIFTED_TRACE,
        EXPECTED_DISCOVERY_SHIFTED_TRACE_SHA256,
        6,
    )
    unshifted = audit_null_trace(
        DISCOVERY_UNSHIFTED_TRACE,
        EXPECTED_DISCOVERY_UNSHIFTED_TRACE_SHA256,
        5,
    )
    return {
        "face_schema": face["format"],
        "face_sha256": EXPECTED_DISCOVERY_FACE_SHA256,
        "status_schema": status["format"],
        "status_sha256": EXPECTED_DISCOVERY_STATUS_SHA256,
        "exact_dimensions_match": True,
        "dependency_artifact": dependency_audit,
        "equality_consistency_match": True,
        "torsion_rank_increment_match": True,
        "shifted_trace": shifted,
        "unshifted_trace": unshifted,
        "rational_primal_present": False,
        "Farkas_certificate_present": False,
        "rational_feasibility": "UNKNOWN_WALL",
        "integral_feasibility": "UNKNOWN",
        "Conway_99": "UNKNOWN",
    }


def rank_certificate() -> dict[str, object]:
    frozen_lower_bounds()
    sources, targets, matrix = face_matrix()
    upper_bound, block_records = block_rank_upper_bound(sources, targets)
    linear = certified_rank(matrix, sources, upper_bound)

    affine_matrix = matrix + [
        identity_row(sources),
        total_size_row(sources),
    ]
    affine = certified_rank(affine_matrix, sources, upper_bound + 2)

    # This equality is a valid additional tightening from the frozen code
    # type, but is deliberately reported separately from the two-row affine
    # normalization used in the Wave135 face claim.
    torsion_matrix = affine_matrix + [primal_torsion_size_row(sources)]
    torsion_tightened = certified_rank(
        torsion_matrix, sources, upper_bound + 3
    )
    shell_fibres = shell_fibre_audit(sources, targets, matrix)
    return {
        "format": "wave135-z4-exact-face-preseal-v1",
        "claim_label": "DERIVED",
        "frozen_input": {
            "path": (
                "attempts/wave134-z4-symmetrized-enumerator/"
                "exact-results.json"
            ),
            "sha256": EXPECTED_WAVE134_RESULTS_SHA256,
            "schema": "wave134-z4-derived-checkpoint-v1",
        },
        "source_orbits": len(sources),
        "zero_rows": len(targets),
        "zero_row_face": {
            "rank_over_Q": linear["rank_over_Q"],
            "linear_nullity": linear["nullity"],
            "row_dependencies": len(targets) - linear["rank_over_Q"],
            "block_upper_bound": upper_bound,
            "block_records": block_records,
        },
        "affine_identity_and_size_slice": {
            "equalities": [
                "A_(99,0,0)=1",
                "sum_over_primal_orbit_coefficients=2^108",
            ],
            "rank_over_Q": affine["rank_over_Q"],
            "affine_dimension": affine["nullity"],
            "right_hand_side": [1, 2**108],
        },
        "torsion_size_tightening": {
            "additional_equality": (
                "sum_{source_odd=0} A_source_orbit=2^54"
            ),
            "rank_over_Q": torsion_tightened["rank_over_Q"],
            "affine_dimension": torsion_tightened["nullity"],
            "right_hand_side": 2**54,
            "note": (
                "This third affine equality follows from |Tor(C)|=2^55 "
                "and is independent of the zero rows, identity, and total size."
            ),
        },
        "shell_fibre_audit": shell_fibres,
        "certificate": {
            "method": (
                "Shell factorization proves rank at most 143. A nonzero "
                "143x143 integer minor modulo a prime proves rank at least "
                "143 over Q. The same argument with two and three appended "
                "affine rows certifies ranks 145 and 146."
            ),
            "prime": RANK_CERTIFICATE_PRIME,
            "matrix_sha256": matrix_sha256(matrix),
            "zero_row_face": linear,
            "affine_identity_and_size": affine,
            "torsion_size_tightened": torsion_tightened,
        },
        "row_scaling": (
            "Each target row has the nonzero rational common factor "
            "2^(target_odd+1) removed."
        ),
        "candidate_contracts": {
            "rational_primal": {
                "format": "wave135-z4-rational-primal-v1",
                "models": [MODEL_BASE, MODEL_TORSION],
                "coefficient_encoding": (
                    "Dense object with all 1,119 composition keys; values "
                    "must be exact integers, strings, or [numerator,denominator]."
                ),
            },
            "Farkas": {
                "format": "wave135-z4-farkas-v1",
                "models": [MODEL_BASE, MODEL_TORSION],
                "convention": (
                    "Ex=h, Gx>=l, z>=0, yE+zG=0, yh+zl>0."
                ),
                "multiplier_encoding": (
                    "Sparse exact objects; omitted multipliers are zero."
                ),
            },
        },
        "status_wall": {
            "rational_primal": "NOT_PRESENT_PRESEAL",
            "Farkas_certificate": "NOT_PRESENT_PRESEAL",
            "rational_feasibility": "UNKNOWN",
            "integral_feasibility": "UNKNOWN",
            "Z4_code_realizability": "UNKNOWN",
            "graph_realizability": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
    }


def build_result(*, preseal: bool = False) -> dict[str, object]:
    result = rank_certificate()
    if preseal:
        return result
    result["format"] = "wave135-z4-exact-face-independent-verification-v1"
    result["claim_label"] = "VERIFIED"
    result["sealed_discovery"] = verify_discovery_manifest()
    result["sealed_discovery_audit"] = audit_sealed_discovery()
    result["status_wall"] = {
        "rational_primal": "NOT_FOUND",
        "Farkas_certificate": "NOT_FOUND",
        "rational_feasibility": "UNKNOWN_WALL",
        "integral_feasibility": "UNKNOWN",
        "Z4_code_realizability": "UNKNOWN",
        "graph_realizability": "UNKNOWN",
        "Conway_99": "UNKNOWN",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--preseal", action="store_true")
    parser.add_argument("--verify-primal", type=Path)
    parser.add_argument("--verify-farkas", type=Path)
    args = parser.parse_args()
    selected = sum(
        option is not None
        for option in (
            args.output,
            args.verify,
            args.verify_primal,
            args.verify_farkas,
        )
    )
    require(selected <= 1, "choose at most one operation")
    if args.verify_primal:
        candidate = json.loads(args.verify_primal.read_text(encoding="utf-8"))
        print(canonical(verify_rational_primal(candidate)), end="")
        return
    if args.verify_farkas:
        candidate = json.loads(args.verify_farkas.read_text(encoding="utf-8"))
        print(canonical(verify_farkas_candidate(candidate)), end="")
        return
    result = build_result(preseal=args.preseal)
    rendered = canonical(result)
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        require(stored == result, "stored exact-face result differs")
        print(f"verified {args.verify}")
    elif args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
