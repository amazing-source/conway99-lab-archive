#!/usr/bin/env python3
"""Independent verifier for the frozen Wave 31 T20 finite package.

This checker does not import or execute the construction-side checker.  It
reads the submitted JSON certificate as data, reconstructs the T20 shell in
two exact coordinate systems, recomputes all pair and moment claims, checks
the rational witness directly, and exhausts the named radius-two domain with
an injective bounded positional encoding.  It separately replays and audits
the submitted modulo-2^64 fingerprint.

The output is deliberately scoped.  Nothing here decides the unrestricted
frame, an oriented frame, Q/B/A4 on T20, the coupled endpoint, n3=708,
Conway-99, or novelty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_OUTPUT = HERE / "independent-results.json"

FROZEN_COMMIT = "67a0e4585c9c378dcd658784a3876564557b70e3"
FROZEN_TREE = "47ef723b915045c0ef83f15b49235b278dbfb6aa"
FROZEN_PARENT = "31bc516a581decb6394bf5e780f07fb05d567274"

SUBMISSION_PATH = "attempts/wave31-t20-frame/exact-results.json"
T20_SOURCE_PATH = "attempts/wave30-h729-construction/exact-results.json"
GENERAL_SOURCE_PATH = "attempts/wave30-general-h729/exact-results.json"
WAVE24_SOURCE_PATH = "verification/wave24-n3-708-index/independent-results.json"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave31-t20-construction.md":
        "d6599fdf81f81410eaccde36a35e6ffee567d90b3b5e7020cb64f7a7c4b1ca49",
    "attempts/wave31-t20-frame/exact_check.py":
        "81acefd270caa81900cb319ca0cb9db68d952f80ce3511edee1f23386c982f8e",
    "attempts/wave31-t20-frame/test_exact_check.py":
        "0c36af2f7cee4797b95c1d82b175274ed02f9674599181220900509777b4a365",
    "attempts/wave31-t20-frame/solver_scout.py":
        "d362197857cbeddc446bedd7cb04945aff598783fbe2421b86a013212e967144",
    "attempts/wave31-t20-frame/exact-results.json":
        "d2592a71e8600a894aa7d87e6ed1c8230010b919488b10f9854710bb77944152",
    "attempts/wave31-t20-frame/input-freeze.sha256":
        "2931d0c8de6e7000112b39aa72232338c5bf14cff54033452bede0842ef92086",
    "attempts/wave31-t20-frame/failure-ledger.md":
        "9c4ad5eb4cc9cd9234c49514a207304e6861799bfd308e2a34e03a629fcf4232",
    "attempts/wave31-t20-frame/run-report.yaml":
        "292403654e0caec8ddbb4a9e286c5f2ab30260d7ff808c758cab6eecd99e1c7c",
    "attempts/wave31-t20-frame/artifact-manifest.sha256":
        "972640b51dd31dc6037ae26b676d1f7c39626f25d038606a71bf18728e9ea3d4",
    "attempts/wave30-h729-construction/exact-results.json":
        "0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11",
    "attempts/wave30-general-h729/exact-results.json":
        "cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c",
    "verification/wave24-n3-708-index/independent-results.json":
        "726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a",
    "verification/wave28-simultaneous-neighbor/independent_check.py":
        "2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db",
}

MASK64 = (1 << 64) - 1
EXACT_POSITIONAL_BASE = 257

# A nontrivial permutation changes the exact LDL recursion tree.  If y is in
# the changed basis, x[PERMUTATION[j]] = y[j] in the submitted basis.
PERMUTATION = (
    7, 1, 14, 0, 19, 3, 11, 6, 17, 8,
    2, 15, 5, 13, 9, 18, 4, 12, 16, 10,
)


class VerificationError(AssertionError):
    """A frozen claim failed an independent exact check."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def git_output(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def validate_frozen_commit_and_inputs() -> dict[str, Any]:
    metadata = git_output(
        "show", "-s", "--format=%H%n%T%n%P", FROZEN_COMMIT
    ).decode("ascii").splitlines()
    if metadata != [FROZEN_COMMIT, FROZEN_TREE, FROZEN_PARENT]:
        raise VerificationError(f"frozen commit metadata drifted: {metadata}")

    commit_hashes: dict[str, str] = {}
    worktree_hashes: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        frozen_bytes = git_output("show", f"{FROZEN_COMMIT}:{relative}")
        frozen_digest = sha256_bytes(frozen_bytes)
        if frozen_digest != expected:
            raise VerificationError(
                f"commit byte hash mismatch for {relative}: "
                f"{frozen_digest} != {expected}"
            )
        worktree_digest = sha256_file(REPO_ROOT / relative)
        if worktree_digest != expected:
            raise VerificationError(
                f"worktree byte hash mismatch for {relative}: "
                f"{worktree_digest} != {expected}"
            )
        commit_hashes[relative] = frozen_digest
        worktree_hashes[relative] = worktree_digest

    def parse_sha256_manifest(path: Path) -> dict[str, str]:
        entries: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            digest, separator, relative = line.partition("  ")
            if (
                separator != "  "
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
                or not relative
                or relative in entries
            ):
                raise VerificationError(f"malformed manifest line: {line!r}")
            entries[relative] = digest
        return entries

    candidate_manifest = parse_sha256_manifest(
        REPO_ROOT / "attempts/wave31-t20-frame/artifact-manifest.sha256"
    )
    expected_candidate_manifest = {
        relative: digest
        for relative, digest in FROZEN_INPUTS.items()
        if (
            relative == "agents/2026-07-24-wave31-t20-construction.md"
            or (
                relative.startswith("attempts/wave31-t20-frame/")
                and not relative.endswith("artifact-manifest.sha256")
            )
        )
    }
    if candidate_manifest != expected_candidate_manifest:
        raise VerificationError("candidate artifact manifest entries failed")
    for relative, digest in candidate_manifest.items():
        if sha256_file(REPO_ROOT / relative) != digest:
            raise VerificationError(
                f"candidate artifact manifest target failed: {relative}"
            )

    candidate_input_freeze = parse_sha256_manifest(
        REPO_ROOT / "attempts/wave31-t20-frame/input-freeze.sha256"
    )
    expected_input_freeze = {
        relative: digest
        for relative, digest in FROZEN_INPUTS.items()
        if relative in {
            T20_SOURCE_PATH,
            GENERAL_SOURCE_PATH,
            WAVE24_SOURCE_PATH,
            "verification/wave28-simultaneous-neighbor/independent_check.py",
        }
    }
    if candidate_input_freeze != expected_input_freeze:
        raise VerificationError("candidate input-freeze entries failed")
    return {
        "commit": FROZEN_COMMIT,
        "tree": FROZEN_TREE,
        "parent": FROZEN_PARENT,
        "commit_blob_sha256": commit_hashes,
        "worktree_sha256": worktree_hashes,
        "candidate_artifact_manifest_entries": len(candidate_manifest),
        "candidate_input_freeze_entries": len(candidate_input_freeze),
        "all_exact": True,
    }


def transpose(matrix: Sequence[Sequence[Any]]) -> list[list[Any]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[Any]],
    right: Sequence[Sequence[Any]],
) -> list[list[Any]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def matvec(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
) -> tuple[int, ...]:
    return tuple(
        sum(int(a) * int(b) for a, b in zip(row, vector))
        for row in matrix
    )


def quadratic(vector: Sequence[int], gram: Sequence[Sequence[int]]) -> int:
    transformed = matvec(gram, vector)
    return sum(int(a) * int(b) for a, b in zip(vector, transformed))


def bareiss_determinant(matrix: Sequence[Sequence[int]]) -> int:
    n = len(matrix)
    work = [[int(value) for value in row] for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        if work[k][k] == 0:
            replacement = next(
                (row for row in range(k + 1, n) if work[row][k] != 0),
                None,
            )
            if replacement is None:
                return 0
            work[k], work[replacement] = work[replacement], work[k]
            sign *= -1
        pivot = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = work[i][j] * pivot - work[i][k] * work[k][j]
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise VerificationError("Bareiss division was not exact")
                work[i][j] = quotient
            work[i][k] = 0
        previous = pivot
    return sign * work[-1][-1]


def rational_inverse(
    matrix: Sequence[Sequence[int]],
) -> list[list[Fraction]]:
    n = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            raise VerificationError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    a - multiplier * b
                    for a, b in zip(work[row], work[column])
                ]
    return [row[n:] for row in work]


def exact_ldlt(
    matrix: Sequence[Sequence[int]],
) -> tuple[list[list[Fraction]], list[Fraction]]:
    n = len(matrix)
    lower = [
        [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    diagonal = [Fraction() for _ in range(n)]
    for column in range(n):
        diagonal[column] = (
            Fraction(matrix[column][column])
            - sum(
                lower[column][k] ** 2 * diagonal[k]
                for k in range(column)
            )
        )
        if diagonal[column] <= 0:
            raise VerificationError(
                f"nonpositive exact LDL pivot {column}: {diagonal[column]}"
            )
        for row in range(column + 1, n):
            numerator = (
                Fraction(matrix[row][column])
                - sum(
                    lower[row][k] * lower[column][k] * diagonal[k]
                    for k in range(column)
                )
            )
            lower[row][column] = numerator / diagonal[column]

    diagonal_matrix = [
        [
            diagonal[i] if i == j else Fraction()
            for j in range(n)
        ]
        for i in range(n)
    ]
    reconstructed = matmul(matmul(lower, diagonal_matrix), transpose(lower))
    expected = [[Fraction(value) for value in row] for row in matrix]
    if reconstructed != expected:
        raise VerificationError("exact LDL reconstruction failed")
    return lower, diagonal


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def enumerate_short_vectors(
    gram: Sequence[Sequence[int]],
    cap: int,
) -> tuple[list[tuple[tuple[int, ...], int]], dict[str, Any]]:
    """Complete exact enumeration from the identity q=x^T L D L^T x."""

    n = len(gram)
    lower, diagonal = exact_ldlt(gram)
    vector = [0] * n
    output: list[tuple[tuple[int, ...], int]] = []
    accepted_nodes = 0

    def visit(index: int, consumed: Fraction) -> None:
        nonlocal accepted_nodes
        if index < 0:
            norm = quadratic(vector, gram)
            if Fraction(norm) != consumed or norm > cap:
                raise VerificationError("enumeration leaf invariant failed")
            output.append((tuple(vector), norm))
            return

        remaining = Fraction(cap) - consumed
        if remaining < 0:
            return
        center = sum(
            lower[j][index] * vector[j]
            for j in range(index + 1, n)
        )
        radius_squared = remaining / diagonal[index]
        # For center=p/q, solve exactly
        #     (q*x+p)^2 * radius_den <= radius_num*q^2.
        p = center.numerator
        q = center.denominator
        integer_limit = math.isqrt(
            (radius_squared.numerator * q * q)
            // radius_squared.denominator
        )
        low = ceil_div(-integer_limit - p, q)
        high = (integer_limit - p) // q
        for value in range(low, high + 1):
            shifted = Fraction(value) + center
            contribution = diagonal[index] * shifted * shifted
            if contribution > remaining:
                continue
            vector[index] = value
            accepted_nodes += 1
            visit(index - 1, consumed + contribution)
        vector[index] = 0

    visit(n - 1, Fraction())
    output.sort()
    return output, {
        "dimension": n,
        "cap": cap,
        "accepted_partial_nodes": accepted_nodes,
        "leaves": len(output),
        "method": (
            "independent exact Fraction LDL recursion with integer-square-root "
            "bounds"
        ),
    }


def permute_gram(
    gram: Sequence[Sequence[int]],
    permutation: Sequence[int],
) -> list[list[int]]:
    return [
        [int(gram[permutation[i]][permutation[j]]) for j in range(len(gram))]
        for i in range(len(gram))
    ]


def unpermute_vector(
    vector: Sequence[int],
    permutation: Sequence[int],
) -> tuple[int, ...]:
    output = [0] * len(vector)
    for changed_index, original_index in enumerate(permutation):
        output[original_index] = int(vector[changed_index])
    return tuple(output)


def canonical_line(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((int(value) for value in vector if value), None)
    if first is None:
        raise VerificationError("zero vector has no antipodal line")
    if first > 0:
        return tuple(int(value) for value in vector)
    return tuple(-int(value) for value in vector)


def upper_pairs(dimension: int) -> list[tuple[int, int]]:
    return [
        (i, j)
        for i in range(dimension)
        for j in range(i, dimension)
    ]


def outer_feature(
    vector: Sequence[int],
    pairs: Sequence[tuple[int, int]],
) -> tuple[int, ...]:
    return tuple(int(vector[i]) * int(vector[j]) for i, j in pairs)


def sum_features(
    features: Sequence[Sequence[int]],
    indices: Iterable[int],
) -> tuple[int, ...]:
    result = [0] * len(features[0])
    for index in indices:
        feature = features[int(index)]
        for coordinate, value in enumerate(feature):
            result[coordinate] += int(value)
    return tuple(result)


def gf2_rank(rows: Sequence[int]) -> int:
    pivots: dict[int, int] = {}
    for source in rows:
        row = int(source)
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def verify_gf2_system(
    features: Sequence[Sequence[int]],
    target: Sequence[int],
) -> dict[str, Any]:
    variable_count = len(features)
    coefficient_rows: list[int] = []
    rhs: list[int] = []
    for equation in range(len(target)):
        row = 0
        for variable, feature in enumerate(features):
            if int(feature[equation]) & 1:
                row |= 1 << variable
        coefficient_rows.append(row)
        rhs.append(int(target[equation]) & 1)
    coefficient_rows.append((1 << variable_count) - 1)
    rhs.append(1)
    augmented_rows = [
        row | (right << variable_count)
        for row, right in zip(coefficient_rows, rhs)
    ]
    coefficient_rank = gf2_rank(coefficient_rows)
    augmented_rank = gf2_rank(augmented_rows)
    return {
        "variables": variable_count,
        "equations_including_cardinality": len(coefficient_rows),
        "coefficient_rank": coefficient_rank,
        "augmented_rank": augmented_rank,
        "dependencies": len(coefficient_rows) - coefficient_rank,
        "consistent": coefficient_rank == augmented_rank,
    }


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def verify_rational_witness(
    submitted: dict[str, Any],
    features: Sequence[Sequence[int]],
    target: Sequence[int],
) -> dict[str, Any]:
    unit = [int(value) for value in submitted["unit_indices"]]
    fractional = [
        int(value) for value in submitted["fractional_indices"]
    ]
    weights = [
        parse_fraction(value) for value in submitted["fractional_weights"]
    ]
    if len(unit) != 33 or len(fractional) != 210 or len(weights) != 210:
        raise VerificationError("rational support cardinalities failed")
    if len(set(unit)) != len(unit) or len(set(fractional)) != len(fractional):
        raise VerificationError("rational support repeats an index")
    if set(unit) & set(fractional):
        raise VerificationError("unit and fractional supports overlap")
    if min(unit + fractional) < 0 or max(unit + fractional) >= len(features):
        raise VerificationError("rational support index out of range")
    if not all(Fraction(0) < weight < Fraction(1) for weight in weights):
        raise VerificationError("fractional weight is outside (0,1)")

    all_weights = [Fraction(0) for _ in features]
    for index in unit:
        all_weights[index] = Fraction(1)
    for index, weight in zip(fractional, weights):
        all_weights[index] = weight
    if not all(Fraction(0) <= weight <= Fraction(1) for weight in all_weights):
        raise VerificationError("a full line weight is outside [0,1]")
    total_weight = sum(all_weights, Fraction())
    if total_weight != 105:
        raise VerificationError(f"weight sum is {total_weight}, not 105")

    reconstructed = [Fraction() for _ in target]
    for index, weight in enumerate(all_weights):
        if not weight:
            continue
        for equation, value in enumerate(features[index]):
            reconstructed[equation] += weight * int(value)
    expected = [Fraction(value) for value in target]
    if reconstructed != expected:
        failures = [
            index
            for index, (actual, wanted) in enumerate(
                zip(reconstructed, expected)
            )
            if actual != wanted
        ]
        raise VerificationError(
            f"rational moment witness failed equations {failures[:10]}"
        )

    certificate = {
        "unit_indices": unit,
        "fractional_indices": fractional,
        "fractional_weights": [
            (
                str(weight.numerator)
                if weight.denominator == 1
                else f"{weight.numerator}/{weight.denominator}"
            )
            for weight in weights
        ],
    }
    certificate_hash = canonical_hash(certificate)
    if certificate_hash != submitted["weight_certificate_sha256"]:
        raise VerificationError("rational weight-certificate hash failed")
    return {
        "all_2538_weights_in_closed_unit_interval": True,
        "unit_weights": len(unit),
        "strictly_fractional_weights": len(fractional),
        "zero_weights": len(features) - len(unit) - len(fractional),
        "support_size": len(unit) + len(fractional),
        "weight_sum": str(total_weight),
        "verified_moment_entries": len(target),
        "minimum_fractional_weight": str(min(weights)),
        "maximum_fractional_weight": str(max(weights)),
        "weight_certificate_sha256": certificate_hash,
        "verdict": "EXACT_RATIONAL_BOX_RELAXATION_WITNESS_VERIFIED",
        "not_boolean": True,
    }


def splitmix64_coefficients(count: int) -> list[int]:
    state = 0x9E3779B97F4A7C15
    output = []
    for _ in range(count):
        state = (state + 0x9E3779B97F4A7C15) & MASK64
        value = state
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
        value ^= value >> 31
        output.append(value & MASK64)
    return output


def modular_fingerprint(
    feature: Sequence[int],
    coefficients: Sequence[int],
) -> int:
    return sum(
        (int(value) % (1 << 64)) * int(coefficient)
        for value, coefficient in zip(feature, coefficients)
    ) & MASK64


def positional_coefficients(count: int) -> list[int]:
    coefficients = [1]
    for _ in range(1, count):
        coefficients.append(coefficients[-1] * EXACT_POSITIONAL_BASE)
    return coefficients


def linear_code(
    feature: Sequence[int],
    coefficients: Sequence[int],
) -> int:
    return sum(
        int(value) * int(coefficient)
        for value, coefficient in zip(feature, coefficients)
    )


def add_vectors(
    left: Sequence[int],
    right: Sequence[int],
) -> tuple[int, ...]:
    return tuple(int(a) + int(b) for a, b in zip(left, right))


def subtract_vectors(
    left: Sequence[int],
    right: Sequence[int],
) -> tuple[int, ...]:
    return tuple(int(a) - int(b) for a, b in zip(left, right))


def verify_near_frame(
    submitted: dict[str, Any],
    features: Sequence[Sequence[int]],
    target: Sequence[int],
) -> dict[str, Any]:
    selected = tuple(int(value) for value in submitted["canonical_line_indices"])
    if len(selected) != 105 or len(set(selected)) != 105:
        raise VerificationError("near-frame support is not 105 distinct lines")
    if min(selected) < 0 or max(selected) >= len(features):
        raise VerificationError("near-frame support index out of range")
    if canonical_hash(list(selected)) != submitted[
        "canonical_line_indices_sha256"
    ]:
        raise VerificationError("near-frame support hash failed")

    selected_set = set(selected)
    unselected = tuple(
        index for index in range(len(features)) if index not in selected_set
    )
    current = sum_features(features, selected)
    residual = subtract_vectors(current, target)
    if list(residual) != submitted["moment_residual_upper_triangle"]:
        raise VerificationError("submitted near-frame residual is wrong")
    if canonical_hash(list(residual)) != submitted["moment_residual_sha256"]:
        raise VerificationError("submitted near-frame residual hash failed")
    pairs = upper_pairs(20)
    score = sum(
        (1 if i == j else 2) * residual[position] ** 2
        for position, (i, j) in enumerate(pairs)
    )
    nonzero = sum(value != 0 for value in residual)
    max_residual = max(abs(value) for value in residual)
    if (score, nonzero, max_residual) != (121, 63, 2):
        raise VerificationError(
            f"near-frame residual metrics drifted: "
            f"{score}, {nonzero}, {max_residual}"
        )

    max_feature = max(abs(value) for feature in features for value in feature)
    difference_bound_radius_two = 4 * max_feature + max_residual
    if difference_bound_radius_two >= EXACT_POSITIONAL_BASE:
        raise VerificationError(
            "positional base is too small for collision-free comparison"
        )
    exact_coefficients = positional_coefficients(len(target))
    exact_codes = [
        linear_code(feature, exact_coefficients) for feature in features
    ]
    residual_exact_code = linear_code(residual, exact_coefficients)

    modular_coefficients = splitmix64_coefficients(len(target))
    coefficient_hash = canonical_hash(modular_coefficients)
    if coefficient_hash != submitted["fingerprint"]["coefficient_sha256"]:
        raise VerificationError("submitted modulo-2^64 coefficients drifted")
    modular_codes = [
        modular_fingerprint(feature, modular_coefficients)
        for feature in features
    ]
    residual_modular_code = modular_fingerprint(
        residual, modular_coefficients
    )

    exact_required_one: dict[int, list[int]] = defaultdict(list)
    modular_required_one: dict[int, list[int]] = defaultdict(list)
    for removed in selected:
        exact_required_one[
            exact_codes[removed] - residual_exact_code
        ].append(removed)
        modular_required_one[
            (modular_codes[removed] - residual_modular_code) & MASK64
        ].append(removed)

    exact_one_code_candidates = 0
    modular_one_candidates = 0
    exact_one_matches: list[list[int]] = []
    modular_one_matches: list[list[int]] = []
    for added in unselected:
        exact_removals = exact_required_one.get(exact_codes[added], ())
        exact_one_code_candidates += len(exact_removals)
        for removed in exact_removals:
            required = subtract_vectors(features[removed], residual)
            if tuple(features[added]) == required:
                exact_one_matches.append([removed, added])
            else:
                raise VerificationError(
                    "collision in claimed injective positional radius-one code"
                )
        modular_removals = modular_required_one.get(modular_codes[added], ())
        modular_one_candidates += len(modular_removals)
        for removed in modular_removals:
            required = subtract_vectors(features[removed], residual)
            if tuple(features[added]) == required:
                modular_one_matches.append([removed, added])

    exact_required_two: dict[int, list[tuple[int, int]]] = defaultdict(list)
    modular_required_two: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for left_position, left in enumerate(selected):
        for right in selected[left_position + 1:]:
            exact_required_two[
                exact_codes[left] + exact_codes[right] - residual_exact_code
            ].append((left, right))
            modular_required_two[
                (
                    modular_codes[left]
                    + modular_codes[right]
                    - residual_modular_code
                ) & MASK64
            ].append((left, right))

    exact_two_code_candidates = 0
    modular_two_candidates = 0
    exact_two_matches: list[list[int]] = []
    modular_two_matches: list[list[int]] = []
    for left_position, left in enumerate(unselected):
        for right in unselected[left_position + 1:]:
            exact_removals = exact_required_two.get(
                exact_codes[left] + exact_codes[right], ()
            )
            exact_two_code_candidates += len(exact_removals)
            if exact_removals:
                added_sum = add_vectors(features[left], features[right])
                for removed_left, removed_right in exact_removals:
                    required_sum = subtract_vectors(
                        add_vectors(
                            features[removed_left], features[removed_right]
                        ),
                        residual,
                    )
                    if added_sum == required_sum:
                        exact_two_matches.append([
                            removed_left, removed_right, left, right
                        ])
                    else:
                        raise VerificationError(
                            "collision in claimed injective positional "
                            "radius-two code"
                        )

            modular_removals = modular_required_two.get(
                (modular_codes[left] + modular_codes[right]) & MASK64, ()
            )
            modular_two_candidates += len(modular_removals)
            if modular_removals:
                added_sum = add_vectors(features[left], features[right])
                for removed_left, removed_right in modular_removals:
                    required_sum = subtract_vectors(
                        add_vectors(
                            features[removed_left], features[removed_right]
                        ),
                        residual,
                    )
                    if added_sum == required_sum:
                        modular_two_matches.append([
                            removed_left, removed_right, left, right
                        ])

    if exact_one_matches or exact_two_matches:
        raise VerificationError("the named neighbourhood contains a repair")
    if modular_one_matches or modular_two_matches:
        raise VerificationError("modular replay found an exact repair")
    if modular_one_candidates != submitted["radius_one"][
        "fingerprint_collision_candidates"
    ]:
        raise VerificationError("radius-one modular candidate count drifted")
    if modular_two_candidates != submitted["radius_two"][
        "fingerprint_collision_candidates"
    ]:
        raise VerificationError("radius-two modular candidate count drifted")

    removal_pairs = len(selected) * (len(selected) - 1) // 2
    addition_pairs = len(unselected) * (len(unselected) - 1) // 2
    if removal_pairs != 5460 or addition_pairs != 2958528:
        raise VerificationError("exchange pair counts failed")
    if submitted["radius_two"]["removal_pair_count"] != removal_pairs:
        raise VerificationError("submitted removal-pair count failed")
    if submitted["radius_two"]["addition_pair_count"] != addition_pairs:
        raise VerificationError("submitted addition-pair count failed")

    return {
        "near_frame_id": submitted["near_frame_id"],
        "selected_lines": len(selected),
        "unselected_lines": len(unselected),
        "support_sha256": canonical_hash(list(selected)),
        "residual_sha256": canonical_hash(list(residual)),
        "frobenius_residual_score": score,
        "nonzero_upper_triangle_entries": nonzero,
        "maximum_absolute_residual_entry": max_residual,
        "radius_one": {
            "removal_choices": len(selected),
            "addition_choices": len(unselected),
            "all_exchange_choices": len(selected) * len(unselected),
            "injective_code_candidates": exact_one_code_candidates,
            "exact_repairs": exact_one_matches,
            "modulo_2_64_candidates": modular_one_candidates,
            "modulo_2_64_exact_repairs_after_entrywise_checks":
                modular_one_matches,
        },
        "radius_two": {
            "removal_pair_count": removal_pairs,
            "addition_pair_count": addition_pairs,
            "all_pair_of_pair_choices": removal_pairs * addition_pairs,
            "injective_code_candidates": exact_two_code_candidates,
            "exact_repairs": exact_two_matches,
            "modulo_2_64_candidates": modular_two_candidates,
            "modulo_2_64_exact_repairs_after_entrywise_checks":
                modular_two_matches,
        },
        "injective_code": {
            "base": EXACT_POSITIONAL_BASE,
            "maximum_absolute_outer_feature_entry": max_feature,
            "maximum_absolute_comparison_difference":
                difference_bound_radius_two,
            "proof": (
                "For any compared radius-two vectors, each coordinate of "
                "their difference has absolute value at most 4F+R=102<257. "
                "Equality of sum_e d_e*257^e then forces d_0=0 modulo 257 "
                "and inductively every d_e=0. The code is collision-free on "
                "this bounded domain."
            ),
        },
        "submitted_modulo_2_64_fingerprint": {
            "coefficient_sha256": coefficient_hash,
            "linearity_checked_by_independent_replay": True,
            "soundness": (
                "Reduction modulo 2^64 is a homomorphism. Exact feature "
                "equality must produce equal fingerprints. The submitted "
                "algorithm enumerates every matching key and checks the full "
                "210-entry vectors, so collisions can add candidates but "
                "cannot remove a repair."
            ),
        },
        "verdict": (
            "VERIFIED_NO_SECOND_MOMENT_SELECTION_WITHIN_TWO_EXCHANGES_OF_"
            "W31_T20_NEAR_105_001"
        ),
        "global_second_moment_frame": "UNKNOWN",
    }


def verify_status_walls(submission: dict[str, Any]) -> dict[str, Any]:
    expected_unknown = {
        "global_105_row_second_moment_frame",
        "oriented_zero_sum_alphabet_frame",
        "Q_A_B_A_A4_A_package",
        "coupled_T20_U24_projector_Schur_package",
        "n3_equals_708",
        "Conway_99",
        "novelty",
    }
    status = submission["status"]
    failures = {
        key: status.get(key)
        for key in expected_unknown
        if status.get(key) != "UNKNOWN"
    }
    if failures:
        raise VerificationError(f"global status inflation: {failures}")
    scout = submission["solver_scout_summary"]
    expected_scout = {
        "status": "ALL_NONCERTIFYING",
        "unrestricted_second_moment_witness": "NOT_FOUND",
        "unrestricted_second_moment_nonexistence": "NOT_PROVED",
        "unrestricted_oriented_frame": "NOT_FOUND_OR_EXCLUDED",
    }
    for key, value in expected_scout.items():
        if scout.get(key) != value:
            raise VerificationError(
                f"solver telemetry status drifted at {key}: {scout.get(key)}"
            )
    restrictions = submission["restrictions"]
    required_restrictions = {
        "no_target_automorphism_assumed": True,
        "full_shell_enumerated": True,
        "integer_solver_search_complete": False,
        "radius_two_exchange_search_complete": True,
        "U24_matrix_chosen_in_this_lane": False,
        "graph_gap_imposed_on_matrix_search": False,
    }
    for key, value in required_restrictions.items():
        if restrictions.get(key) != value:
            raise VerificationError(
                f"restriction drifted at {key}: {restrictions.get(key)}"
            )
    return {
        "unknown_statuses_verified": sorted(expected_unknown),
        "solver_telemetry_noncertifying": True,
        "unrestricted_solver_search_complete": False,
        "no_automorphism_restriction": True,
        "rooted_and_integrally_indecomposable_forms": "OUT_OF_SCOPE",
        "verdict": "NO_STATUS_INFLATION_DETECTED",
    }


def build_result() -> dict[str, Any]:
    frozen = validate_frozen_commit_and_inputs()
    submission = json.loads(
        (REPO_ROOT / SUBMISSION_PATH).read_text(encoding="utf-8")
    )
    source = json.loads(
        (REPO_ROOT / T20_SOURCE_PATH).read_text(encoding="utf-8")
    )
    general = json.loads(
        (REPO_ROOT / GENERAL_SOURCE_PATH).read_text(encoding="utf-8")
    )
    wave24 = json.loads(
        (REPO_ROOT / WAVE24_SOURCE_PATH).read_text(encoding="utf-8")
    )

    source_t20 = source["rank20_construction"]["T20"]
    gram = [[int(value) for value in row] for row in source_t20["gram"]]
    if len(gram) != 20 or any(len(row) != 20 for row in gram):
        raise VerificationError("T20 is not 20 by 20")
    if gram != transpose(gram):
        raise VerificationError("T20 is not symmetric")
    if any(gram[i][i] % 2 for i in range(20)):
        raise VerificationError("T20 diagonal is not even")
    gram_hash = canonical_hash(gram)
    if gram_hash != "1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6":
        raise VerificationError("displayed T20 canonical hash failed")
    if source_t20["gram_sha256"] != gram_hash:
        raise VerificationError("source T20 hash label failed")
    determinant = bareiss_determinant(gram)
    if determinant != 729:
        raise VerificationError(f"T20 determinant is {determinant}")
    inverse = rational_inverse(gram)
    scaled_inverse = [[21 * value for value in row] for row in inverse]
    if any(value.denominator != 1 for row in scaled_inverse for value in row):
        raise VerificationError("21*T20^-1 is not integral")
    target_matrix = [
        [int(value) for value in row] for row in scaled_inverse
    ]
    if target_matrix != source_t20["scaled_dual_21_T20_inverse"]:
        raise VerificationError("fresh 21*T20^-1 disagrees with source")
    if matmul(gram, target_matrix) != [
        [21 if i == j else 0 for j in range(20)]
        for i in range(20)
    ]:
        raise VerificationError("T20*(21*T20^-1) != 21I")
    target_hash = canonical_hash(target_matrix)
    if target_hash != "006011e5ea2fa29cc942bcaa3e72e6d300a549fbad6b6991f3edffb20371a024":
        raise VerificationError("scaled dual canonical hash failed")

    shell_original, original_stats = enumerate_short_vectors(gram, 4)
    changed_gram = permute_gram(gram, PERMUTATION)
    shell_changed, changed_stats = enumerate_short_vectors(changed_gram, 4)
    mapped_changed = sorted(
        (unpermute_vector(vector, PERMUTATION), norm)
        for vector, norm in shell_changed
    )
    if shell_original != mapped_changed:
        raise VerificationError("changed-basis shell differs from original shell")
    norm_counts = Counter(norm for _vector, norm in shell_original)
    if norm_counts != Counter({0: 1, 4: 5076}):
        raise VerificationError(f"complete norm<=4 counts failed: {norm_counts}")
    canonical_lines = sorted({
        canonical_line(vector)
        for vector, norm in shell_original
        if norm == 4
    })
    if len(canonical_lines) != 2538:
        raise VerificationError("canonical antipodal line count failed")
    submitted_lines = [
        tuple(int(value) for value in line)
        for line in submission["T20"]["canonical_lines"]
    ]
    if canonical_lines != submitted_lines:
        raise VerificationError(
            "independently enumerated ordered lines differ from submission"
        )
    line_hash = canonical_hash([list(line) for line in canonical_lines])
    if line_hash != "25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e":
        raise VerificationError("canonical-line hash failed")

    height_distribution = Counter(
        max(abs(value) for value in line) for line in canonical_lines
    )
    mod2_count = len({
        tuple(value % 2 for value in line) for line in canonical_lines
    })
    mod3_count = len({
        tuple(value % 3 for value in line) for line in canonical_lines
    })
    if mod2_count != 2538 or mod3_count != 2538:
        raise VerificationError("mod-2 or mod-3 residue injectivity failed")
    if height_distribution != Counter({
        1: 1196, 2: 1019, 3: 278, 4: 36, 5: 9,
    }):
        raise VerificationError("coordinate-height distribution failed")

    transformed = [matvec(gram, line) for line in canonical_lines]
    signed_pairs: Counter[int] = Counter()
    degrees = [0] * len(canonical_lines)
    for left, transformed_left in enumerate(transformed):
        for right in range(left + 1, len(canonical_lines)):
            inner = sum(
                int(a) * int(b)
                for a, b in zip(transformed_left, canonical_lines[right])
            )
            signed_pairs[inner] += 1
            if abs(inner) == 2:
                degrees[left] += 1
                degrees[right] += 1
    expected_pairs = Counter({
        -2: 80883,
        -1: 671126,
        0: 1382670,
        1: 923008,
        2: 161766,
    })
    if signed_pairs != expected_pairs:
        raise VerificationError(f"pair geometry failed: {signed_pairs}")
    degree_distribution = Counter(degrees)
    expected_degrees = Counter({
        160: 108,
        178: 840,
        196: 1242,
        214: 330,
        232: 15,
        322: 3,
    })
    if degree_distribution != expected_degrees:
        raise VerificationError(
            f"absolute-two degree distribution failed: {degree_distribution}"
        )

    pairs = upper_pairs(20)
    features = [outer_feature(line, pairs) for line in canonical_lines]
    target_upper = tuple(target_matrix[i][j] for i, j in pairs)
    parity = verify_gf2_system(features, target_upper)
    expected_parity = {
        "variables": 2538,
        "equations_including_cardinality": 211,
        "coefficient_rank": 210,
        "augmented_rank": 210,
        "dependencies": 1,
        "consistent": True,
    }
    if parity != expected_parity:
        raise VerificationError(f"GF(2) result failed: {parity}")
    # Every frame row has norm four. Taking trace after multiplication by
    # T20 makes the cardinality equation sum z=105; it is therefore a
    # necessary part of the displayed 105-line formulation. Repeated lines
    # are impossible in an alphabet frame because they give inner product
    # +/-4, outside {0,+/-1,-2}.
    trace_t_target = sum(
        gram[i][j] * target_matrix[j][i]
        for i in range(20)
        for j in range(20)
    )
    if trace_t_target != 420 or trace_t_target // 4 != 105:
        raise VerificationError("105-row trace formulation failed")

    rational = verify_rational_witness(
        submission["exact_105_row_problem"]["rational_relaxation"],
        features,
        target_upper,
    )
    near_frame = verify_near_frame(
        submission["exact_105_row_problem"][
            "bounded_integer_neighbourhood"
        ],
        features,
        target_upper,
    )

    cap_one_available = sum(
        max(abs(value) for value in line) <= 1
        for line in canonical_lines
    )
    if cap_one_available != 1196:
        raise VerificationError("cap-one line count failed")
    cap_coordinate = 1
    cap_target = target_matrix[cap_coordinate][cap_coordinate]
    if cap_target != 266 or 105 >= cap_target:
        raise VerificationError("cap-one diagonal obstruction failed")

    survivor = general["surviving_boundary"]
    if survivor["frame"] != {
        "A_rows": 105, "U_rows": 126, "total_rows": 231,
    }:
        raise VerificationError("frozen Wave 30 row split failed")
    if survivor["schur_blocks"]["U"]["B_equals_identity"] is not True:
        raise VerificationError("frozen Wave 30 B_U=I premise failed")
    endpoint = wave24["endpoint_reconstruction"]
    if endpoint["diagonal_excess_units"] != 84:
        raise VerificationError("frozen global excess-unit premise failed")
    if endpoint["trace_A4"] != 1260:
        raise VerificationError("frozen global A4 trace premise failed")
    u_rows = survivor["frame"]["U_rows"]
    a_rows = survivor["frame"]["A_rows"]
    u_trace = 4 * u_rows
    a_trace = endpoint["trace_A4"] - u_trace
    if (u_trace, a_trace) != (504, 756):
        raise VerificationError("A4 trace transfer arithmetic failed")
    if a_trace != 4 * (a_rows + endpoint["diagonal_excess_units"]):
        raise VerificationError("all 84 excess units did not transfer to A")

    row_profiles = []
    for c_value in range(13):
        profile = {
            "c_minus_two": c_value,
            "a_plus_one": 32 - c_value,
            "b_minus_one": 36 - 3 * c_value,
            "zero_within_A_block": 36 + 3 * c_value,
            "zero_in_full_231_row": 162 + 3 * c_value,
            "q_actual_graph_notation": 12 - c_value,
            "cubic_row_sum": 60 - 6 * c_value,
        }
        if (
            profile["a_plus_one"]
            + profile["b_minus_one"]
            + profile["c_minus_two"]
            + profile["zero_within_A_block"]
        ) != 104:
            raise VerificationError("row-profile count does not total 104")
        row_profiles.append(profile)
    submitted_block = submission["full_T20_block_constraints_after_a_frame"]
    if row_profiles != submitted_block["row_alphabet_table"]:
        raise VerificationError("submitted row-profile table failed")
    trace_b_a = int(survivor["schur_blocks"]["A"]["traceB"])
    # Each T20 row contributes 4^3=64 on the diagonal and
    # a-b-8c=-4-6c off the diagonal. Hence
    # trace(B_A)=sum_ij M_ij^3=105*60-6*sum_i c_i.
    sum_c_numerator = a_rows * 60 - trace_b_a
    sum_c, sum_c_remainder = divmod(sum_c_numerator, 6)
    if sum_c_remainder or sum_c != 1044:
        raise VerificationError("T20 trace(B_A) did not force sum c=1044")
    aggregates = {
        "plus_one": 105 * 32 - sum_c,
        "minus_one": 105 * 36 - 3 * sum_c,
        "minus_two": sum_c,
        "zero": 105 * 36 + 3 * sum_c,
        "sum_c_minus_two": sum_c,
        "sum_q_actual_graph_notation": 105 * 12 - sum_c,
    }
    if aggregates != submitted_block["aggregate_directed_internal_counts"]:
        raise VerificationError("aggregate T20 row counts failed")

    status_audit = verify_status_walls(submission)
    return {
        "schema": "wave31-t20-frame-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "verdict": "PASS_SCOPED_FINITE_EVIDENCE",
        "frozen_submission": frozen,
        "T20_input": {
            "rank": 20,
            "symmetric_even_integral": True,
            "positive_definite_from_exact_LDL": True,
            "determinant": determinant,
            "gram_sha256": gram_hash,
            "scaled_dual_21_inverse_integral": True,
            "scaled_dual_sha256": target_hash,
            "matrix_identity": "T20*(21*T20^-1)=21I_20",
        },
        "complete_shell": {
            "cap": 4,
            "norm_counts_including_zero": {
                str(key): norm_counts[key] for key in sorted(norm_counts)
            },
            "norm_four_vectors": 5076,
            "antipodal_lines": len(canonical_lines),
            "canonical_lines_sha256": line_hash,
            "full_ordered_line_list_equals_submission": True,
            "no_automorphism_quotient": True,
            "coordinate_height_distribution": {
                str(key): height_distribution[key]
                for key in sorted(height_distribution)
            },
            "distinct_residue_classes_mod_2": mod2_count,
            "distinct_residue_classes_mod_3": mod3_count,
            "original_basis_enumeration": original_stats,
            "changed_basis_enumeration": {
                **changed_stats,
                "permutation": list(PERMUTATION),
                "mapped_shell_equals_original": True,
            },
        },
        "line_pair_geometry": {
            "unordered_pairs": len(canonical_lines)
                * (len(canonical_lines) - 1) // 2,
            "signed_inner_product_counts": {
                str(key): signed_pairs[key] for key in sorted(signed_pairs)
            },
            "absolute_inner_product_counts": {
                "0": signed_pairs[0],
                "1": signed_pairs[-1] + signed_pairs[1],
                "2": signed_pairs[-2] + signed_pairs[2],
            },
            "absolute_two_edges": signed_pairs[-2] + signed_pairs[2],
            "absolute_two_degree_distribution": {
                str(key): degree_distribution[key]
                for key in sorted(degree_distribution)
            },
            "degree_sum_equals_twice_edges": (
                sum(degree * count for degree, count in degree_distribution.items())
                == 2 * (signed_pairs[-2] + signed_pairs[2])
            ),
        },
        "second_moment_formulation": {
            "Boolean_line_variables": len(canonical_lines),
            "selected_lines": 105,
            "upper_triangle_moment_equations": len(pairs),
            "target": "21*T20^-1",
            "cardinality_from_T20_trace": trace_t_target // 4,
            "line_repetition_excluded_by_endpoint_alphabet": True,
            "GF2": parity,
        },
        "rational_relaxation": rational,
        "named_radius_two_neighbourhood": near_frame,
        "cap_one_coordinate_restriction": {
            "available_lines": cap_one_available,
            "coordinate_zero_based": cap_coordinate,
            "target_diagonal": cap_target,
            "maximum_from_105_cap_one_rows": 105,
            "verdict": "EXCLUDED_ONLY_IN_THIS_RESTRICTED_DOMAIN",
            "remaining_lines_not_excluded": len(canonical_lines) - cap_one_available,
        },
        "A4_U_transfer": {
            "premises": [
                "B_U=U*Q_U=I_24, so Q_U=U^-1",
                "M_U=X_U*U*X_U^T",
                "Q_U=X_U^T*(M_U o M_U)*X_U",
                "A4_U=M_U*(M_U o M_U)*M_U",
            ],
            "algebra": (
                "A4_U=X_U*U*Q_U*U*X_U^T="
                "X_U*U*X_U^T=M_U"
            ),
            "U_rows": u_rows,
            "diag_M_U": 4,
            "U_trace_A4": u_trace,
            "U_excess_units": 0,
            "global_excess_units_at_n3_708": 84,
            "A_rows": a_rows,
            "A_trace_A4": a_trace,
            "A_excess_units": 84,
            "transfer_verified": True,
        },
        "conditional_row_data": {
            "status": "NECESSARY_IF_A_FRAME_EXISTS",
            "row_profile_count": len(row_profiles),
            "trace_B_A": trace_b_a,
            "sum_c_derivation": "trace(B_A)=105*60-6*sum_i(c_i)",
            "sum_c_minus_two": sum_c,
            "aggregate_directed_counts": aggregates,
        },
        "status_audit": status_audit,
        "limitations": [
            "The exact nonhit covers only the named radius-two support neighbourhood.",
            "No unrestricted Boolean second-moment frame is found or excluded.",
            "No orientation, zero-sum row set, Q_A, B_A, or A4_A is supplied.",
            "No coupled T20 plus U24 endpoint is found or excluded by this package.",
            "Rooted and integrally indecomposable forms are outside this lane.",
            "n3=708, Conway-99, and novelty remain UNKNOWN.",
            "Solver timeouts and no-incumbent telemetry were not used as evidence.",
        ],
        "runtime": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": "Python standard library only",
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        json.dumps(
            value, indent=2, sort_keys=True, ensure_ascii=True
        ).encode("utf-8") + b"\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    result = build_result()
    write_json(arguments.output, result)
    print(json.dumps({
        "verdict": result["verdict"],
        "canonical_lines_sha256":
            result["complete_shell"]["canonical_lines_sha256"],
        "rational_weight_certificate_sha256":
            result["rational_relaxation"]["weight_certificate_sha256"],
        "radius_two_verdict":
            result["named_radius_two_neighbourhood"]["verdict"],
        "global_second_moment_frame":
            result["named_radius_two_neighbourhood"][
                "global_second_moment_frame"
            ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
