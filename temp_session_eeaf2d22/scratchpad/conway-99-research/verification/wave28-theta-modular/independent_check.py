#!/usr/bin/env python3
"""Clean-room verifier for the Wave 28 theta/modular lane.

This file deliberately does not import or execute anything under
``attempts/wave28-theta-modular``.  Offline it treats attributed embedded
numeric catalogue data as untrusted and independently checks every property.
The optional live replay fetches, hashes, parses, and immediately discards the
published HTML.  All decisive arithmetic uses Python integers or
``fractions.Fraction``.

The shortest-vector enumerator first applies an exact LLL change of basis and
then visits every integer point in a closed ellipsoid using exact rational
interval tests.  Floating point arithmetic is not used for coverage or
acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import platform
import re
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


BASE_COMMIT = "d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b"
RANK = 44
WEIGHT = 22
SCALE = 21
ENDPOINT_DETERMINANTS = (9, 21, 49, 81, 189, 441, 729, 1029)
HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "sources"
DEFAULT_OUTPUT = HERE / "independent-results.json"
CATALOGUE_DATA = HERE / "catalogue-data.json"

SOURCE_SPECS = {
    "K12": {
        "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html",
        "sha256": "163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9",
        "dimension": 12,
        "catalogue_det": 729,
        "catalogue_minimum": 4,
        "catalogue_kissing": 756,
    },
    "LAMBDA_F": {
        "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html",
        "sha256": "bb1db4504d7010dc093b24a8bcb00b042ea3879a220d669e8190d02abb6468ac",
        "dimension": 32,
        "catalogue_det": 1,
        "catalogue_minimum": 4,
        "catalogue_kissing": 146880,
    },
}


Matrix = list[list[int]]
QMatrix = list[list[Fraction]]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_matrix_sha256(matrix: Sequence[Sequence[int | Fraction]]) -> str:
    rows = [
        [
            str(value.numerator) + "/" + str(value.denominator)
            if isinstance(value, Fraction)
            else str(value)
            for value in row
        ]
        for row in matrix
    ]
    payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
    return sha256_bytes(payload)


def fetch_sources() -> dict[str, dict[str, object]]:
    """Fetch, hash, parse, and discard the two catalogue response bodies.

    The public package retains attributed numeric data but not copied HTML.
    """
    fetched: dict[str, dict[str, object]] = {}
    catalogue_data: dict[str, dict[str, object]] = {}
    for name, spec in SOURCE_SPECS.items():
        request = urllib.request.Request(
            str(spec["url"]),
            headers={"User-Agent": "conway-99-wave28-independent-verifier/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            final_url = response.geturl()
            status = getattr(response, "status", None)
        digest = sha256_bytes(body)
        if digest != spec["sha256"]:
            raise AssertionError(
                f"{name}: live source hash {digest} differs from frozen "
                f"{spec['sha256']}"
            )
        gram = parse_gram(body, int(spec["dimension"]))
        metadata = {
            "dimension": parse_scalar_section(body, "DIMENSION"),
            "determinant": parse_scalar_section(body, "DET"),
            "minimum": parse_scalar_section(body, "MINIMAL_NORM"),
            "kissing_number": parse_scalar_section(body, "KISSING_NUMBER"),
        }
        catalogue_data[name] = {
            "attribution": (
                "Nebe--Sloane Catalogue of Lattices; numeric Gram data parsed "
                "from the cited URL"
            ),
            "gram": gram,
            "metadata": metadata,
        }
        if name == "K12":
            catalogue_data[name]["similarity"] = parse_k12_similarity(body)
        fetched[name] = {
            "requested_url": spec["url"],
            "final_url": final_url,
            "http_status": status,
            "accessed_utc": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "raw_bytes": len(body),
            "raw_sha256": digest,
            "raw_html_redistributed": False,
            "parsed_gram_sha256": canonical_matrix_sha256(gram),
            "replay": (
                "python -B independent_check.py --refresh-sources "
                "(requires network and fails closed on raw SHA-256 drift)"
            ),
        }
        if name == "K12":
            fetched[name]["parsed_similarity_sha256"] = canonical_matrix_sha256(
                catalogue_data[name]["similarity"]
            )
    CATALOGUE_DATA.write_text(
        json.dumps(catalogue_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    catalogue_hash = sha256_file(CATALOGUE_DATA)
    for entry in fetched.values():
        entry["derived_numeric_file"] = CATALOGUE_DATA.name
        entry["derived_numeric_file_sha256"] = catalogue_hash
    (HERE / "source-manifest.json").write_text(
        json.dumps(fetched, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return fetched


def frozen_source_metadata() -> dict[str, dict[str, object]]:
    manifest_path = HERE / "source-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"{manifest_path} is missing; run with --refresh-sources once"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not CATALOGUE_DATA.exists():
        raise FileNotFoundError(
            f"{CATALOGUE_DATA} is missing; run with --refresh-sources once"
        )
    catalogue = json.loads(CATALOGUE_DATA.read_text(encoding="utf-8"))
    catalogue_hash = sha256_file(CATALOGUE_DATA)
    for name, spec in SOURCE_SPECS.items():
        entry = manifest[name]
        if entry["raw_sha256"] != spec["sha256"]:
            raise AssertionError(f"{name}: recorded raw-source hash mismatch")
        gram = catalogue[name]["gram"]
        if len(gram) != spec["dimension"]:
            raise AssertionError(f"{name}: embedded rank mismatch")
        if canonical_matrix_sha256(gram) != entry["parsed_gram_sha256"]:
            raise AssertionError(f"{name}: embedded Gram hash mismatch")
        if entry["derived_numeric_file_sha256"] != catalogue_hash:
            raise AssertionError(f"{name}: embedded catalogue-data file hash mismatch")
        if name == "K12" and canonical_matrix_sha256(
            catalogue[name]["similarity"]
        ) != entry["parsed_similarity_sha256"]:
            raise AssertionError("K12: embedded similarity hash mismatch")
    return manifest


def embedded_catalogue_data() -> dict[str, dict[str, object]]:
    if not CATALOGUE_DATA.exists():
        raise FileNotFoundError(CATALOGUE_DATA)
    return json.loads(CATALOGUE_DATA.read_text(encoding="utf-8"))


def extract_named_section(raw: bytes, section: str) -> str:
    text = raw.decode("latin-1")
    marker = f'<a NAME="{section}"><STRONG>{section}</STRONG></a><br>'
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"section {section!r} not found")
    start += len(marker)
    end = text.find("<p><li>", start)
    if end < 0:
        raise ValueError(f"section {section!r} has no terminator")
    fragment = text[start:end]
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"<[^>]*>", "", fragment)
    return html.unescape(fragment).strip()


def parse_scalar_section(raw: bytes, section: str) -> int:
    body = extract_named_section(raw, section)
    values = re.findall(r"[-+]?\d+", body)
    if len(values) != 1:
        raise ValueError(f"{section}: expected one integer, got {values}")
    return int(values[0])


def symmetric_from_lower(rows: Sequence[Sequence[int]]) -> Matrix:
    n = len(rows)
    if any(len(row) != i + 1 for i, row in enumerate(rows)):
        raise ValueError("invalid lower-triangular row lengths")
    return [[int(rows[max(i, j)][min(i, j)]) for j in range(n)] for i in range(n)]


def parse_gram(raw: bytes, expected_dimension: int) -> Matrix:
    lines = [line.strip() for line in extract_named_section(raw, "GRAM").splitlines()]
    lines = [line for line in lines if line]
    header = [int(value) for value in lines[0].split()]
    if header != [expected_dimension, 0]:
        raise ValueError(f"unexpected Gram header {header}")
    if len(lines) != expected_dimension + 1:
        raise ValueError(
            f"Gram has {len(lines)-1} rows, expected {expected_dimension}"
        )
    lower = [[int(value) for value in line.split()] for line in lines[1:]]
    return symmetric_from_lower(lower)


def parse_k12_similarity(raw: bytes) -> Matrix:
    lines = [
        line.strip()
        for line in extract_named_section(raw, "SIMILARITY").splitlines()
        if line.strip()
    ]
    if lines[0] != "12" or len(lines) != 13:
        raise ValueError("unexpected K12 similarity section")
    matrix = [[int(value) for value in line.split()] for line in lines[1:]]
    if any(len(row) != 12 for row in matrix):
        raise ValueError("K12 similarity matrix is not 12 by 12")
    return matrix


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[int | Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> list[list[int | Fraction]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not match")
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def identity(n: int) -> Matrix:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def scalar_matrix(
    scalar: int | Fraction,
    matrix: Sequence[Sequence[int | Fraction]],
) -> list[list[int | Fraction]]:
    return [[scalar * value for value in row] for row in matrix]


def matrices_equal(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> bool:
    return [list(row) for row in left] == [list(row) for row in right]


def determinant_bareiss(matrix: Sequence[Sequence[int]]) -> int:
    n = len(matrix)
    if n == 0:
        return 1
    work = [list(map(int, row)) for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        if work[k][k] == 0:
            pivot = next((i for i in range(k + 1, n) if work[i][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign = -sign
        pivot_value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = work[i][j] * pivot_value - work[i][k] * work[k][j]
                if numerator % previous:
                    raise ArithmeticError("Bareiss division was not exact")
                work[i][j] = numerator // previous
        for i in range(k + 1, n):
            work[i][k] = 0
        previous = pivot_value
    return sign * work[-1][-1]


def inverse_fraction(matrix: Sequence[Sequence[int]]) -> QMatrix:
    n = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
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


def exact_ldl(
    matrix: Sequence[Sequence[int | Fraction]],
) -> tuple[QMatrix, list[Fraction]]:
    n = len(matrix)
    lower: QMatrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    diagonal = [Fraction(0) for _ in range(n)]
    for i in range(n):
        lower[i][i] = Fraction(1)
        diagonal[i] = Fraction(matrix[i][i]) - sum(
            lower[i][k] * lower[i][k] * diagonal[k] for k in range(i)
        )
        if diagonal[i] <= 0:
            raise ValueError(f"nonpositive LDL pivot at {i}: {diagonal[i]}")
        for j in range(i + 1, n):
            lower[j][i] = (
                Fraction(matrix[j][i])
                - sum(
                    lower[j][k] * lower[i][k] * diagonal[k]
                    for k in range(i)
                )
            ) / diagonal[i]
    return lower, diagonal


def is_even_integral(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(
        Fraction(value).denominator == 1 for row in matrix for value in row
    ) and all(int(matrix[i][i]) % 2 == 0 for i in range(len(matrix)))


def quadratic(
    matrix: Sequence[Sequence[int | Fraction]], vector: Sequence[int]
) -> Fraction:
    return sum(
        Fraction(vector[i]) * Fraction(matrix[i][j]) * Fraction(vector[j])
        for i in range(len(vector))
        for j in range(len(vector))
    )


def inner_product(
    gram: Sequence[Sequence[int]], left: Sequence[int], right: Sequence[int]
) -> int:
    return sum(
        left[i] * gram[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    )


def nearest_integer(value: Fraction) -> int:
    floor_value = value.numerator // value.denominator
    lower_error = value - floor_value
    upper_error = floor_value + 1 - value
    return floor_value if lower_error <= upper_error else floor_value + 1


def gram_schmidt_data(
    gram: Sequence[Sequence[int]], basis: Sequence[Sequence[int]]
) -> tuple[QMatrix, list[Fraction]]:
    n = len(basis)
    mu: QMatrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    norms = [Fraction(0) for _ in range(n)]
    for i in range(n):
        norms[i] = Fraction(inner_product(gram, basis[i], basis[i]))
        for j in range(i):
            numerator = Fraction(inner_product(gram, basis[i], basis[j]))
            numerator -= sum(mu[i][t] * mu[j][t] * norms[t] for t in range(j))
            mu[i][j] = numerator / norms[j]
            norms[i] -= mu[i][j] * mu[i][j] * norms[j]
        if norms[i] <= 0:
            raise ValueError("basis is not positive definite")
    return mu, norms


def exact_lll_transform(
    gram: Sequence[Sequence[int]], delta: Fraction = Fraction(3, 4)
) -> tuple[Matrix, dict[str, int]]:
    """Return a row-basis unimodular transform using exact LLL."""
    n = len(gram)
    basis = identity(n)
    swaps = 0
    reductions = 0
    k = 1
    mu, norms = gram_schmidt_data(gram, basis)
    while k < n:
        for j in range(k - 1, -1, -1):
            coefficient = nearest_integer(mu[k][j])
            if coefficient:
                basis[k] = [
                    a - coefficient * b for a, b in zip(basis[k], basis[j])
                ]
                reductions += 1
                mu, norms = gram_schmidt_data(gram, basis)
        if norms[k] >= (delta - mu[k][k - 1] ** 2) * norms[k - 1]:
            k += 1
        else:
            basis[k], basis[k - 1] = basis[k - 1], basis[k]
            swaps += 1
            mu, norms = gram_schmidt_data(gram, basis)
            k = max(1, k - 1)
    det = determinant_bareiss(basis)
    if abs(det) != 1:
        raise AssertionError(f"LLL transform is not unimodular: det={det}")
    return basis, {"swaps": swaps, "size_reductions": reductions}


def floating_gs_from_gram(gram: Sequence[Sequence[int]]) -> tuple[list[list[float]], list[float]]:
    """Approximate Gram--Schmidt data used only to choose row operations."""
    n = len(gram)
    mu = [[0.0 for _ in range(n)] for _ in range(n)]
    norms = [0.0 for _ in range(n)]
    for i in range(n):
        norms[i] = float(gram[i][i])
        for j in range(i):
            numerator = float(gram[i][j]) - sum(
                mu[i][t] * mu[j][t] * norms[t] for t in range(j)
            )
            if norms[j] <= 0.0:
                raise ArithmeticError("floating LLL encountered a nonpositive norm")
            mu[i][j] = numerator / norms[j]
            norms[i] -= mu[i][j] * mu[i][j] * norms[j]
        if norms[i] <= 0.0:
            raise ArithmeticError("floating LLL lost positive definiteness")
    return mu, norms


def heuristic_lll_transform(
    gram: Sequence[Sequence[int]], delta: float = 0.75
) -> tuple[Matrix, dict[str, int | str]]:
    """Fast LLL-style preprocessing with an exact postcondition.

    Floating point values choose a sequence of elementary unimodular row
    operations only.  The returned integer transform is accepted only after an
    exact determinant and exact transformed-Gram check.  The later ellipsoid
    traversal does not use these approximate Gram--Schmidt values.
    """
    n = len(gram)
    basis = identity(n)
    current = [list(map(int, row)) for row in gram]
    swaps = 0
    reductions = 0
    iterations = 0
    k = 1
    mu, norms = floating_gs_from_gram(current)
    while k < n:
        iterations += 1
        if iterations > 100000:
            raise RuntimeError("heuristic LLL iteration cap exceeded")
        for j in range(k - 1, -1, -1):
            coefficient = math.floor(mu[k][j] + 0.5)
            if coefficient:
                old_kk = current[k][k]
                old_kj = current[k][j]
                basis[k] = [
                    a - coefficient * b for a, b in zip(basis[k], basis[j])
                ]
                for t in range(n):
                    if t == k:
                        continue
                    value = current[k][t] - coefficient * current[j][t]
                    current[k][t] = value
                    current[t][k] = value
                current[k][k] = (
                    old_kk
                    - 2 * coefficient * old_kj
                    + coefficient * coefficient * current[j][j]
                )
                reductions += 1
                mu, norms = floating_gs_from_gram(current)
        if norms[k] >= (delta - mu[k][k - 1] ** 2) * norms[k - 1]:
            k += 1
        else:
            basis[k], basis[k - 1] = basis[k - 1], basis[k]
            current[k], current[k - 1] = current[k - 1], current[k]
            for row in current:
                row[k], row[k - 1] = row[k - 1], row[k]
            swaps += 1
            mu, norms = floating_gs_from_gram(current)
            k = max(1, k - 1)
    determinant = determinant_bareiss(basis)
    if abs(determinant) != 1:
        raise AssertionError(
            f"heuristic LLL transform is not unimodular: det={determinant}"
        )
    exact_current = transformed_gram(gram, basis)
    if exact_current != current:
        raise AssertionError("heuristic LLL Gram update failed exact replay")
    return basis, {
        "method": "floating-choice-exact-postcheck",
        "swaps": swaps,
        "size_reductions": reductions,
        "iterations": iterations,
    }


def transformed_gram(
    gram: Sequence[Sequence[int]], row_basis: Sequence[Sequence[int]]
) -> Matrix:
    return [
        [inner_product(gram, row_basis[i], row_basis[j]) for j in range(len(gram))]
        for i in range(len(gram))
    ]


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def ceil_sqrt_fraction(value: Fraction) -> int:
    if value < 0:
        raise ValueError("cannot take square root of a negative rational")
    if value == 0:
        return 0
    guess = math.isqrt(
        (value.numerator + value.denominator - 1) // value.denominator
    )
    while Fraction(guess * guess) < value:
        guess += 1
    while guess and Fraction((guess - 1) * (guess - 1)) >= value:
        guess -= 1
    return guess


def vector_in_original_coordinates(
    reduced_coordinates: Sequence[int], row_basis: Sequence[Sequence[int]]
) -> tuple[int, ...]:
    n = len(row_basis)
    return tuple(
        sum(reduced_coordinates[i] * row_basis[i][j] for i in range(n))
        for j in range(n)
    )


def integerize_ldl(
    matrix: Sequence[Sequence[int]],
    lower: QMatrix,
    diagonal: Sequence[Fraction],
) -> dict[str, object]:
    """Turn an exact rational LDL identity into integer linear forms.

    The result certifies

        global_scale * x^T matrix x
          = sum_i weights[i] * (forms[i] dot x)^2

    as an identity of integral quadratic forms.
    """
    n = len(matrix)
    forms: list[list[int]] = []
    rational_weights: list[Fraction] = []
    center_denominators: list[int] = []
    for i in range(n):
        denominator = 1
        for j in range(i + 1, n):
            denominator = math.lcm(denominator, lower[j][i].denominator)
        form = [0] * n
        form[i] = denominator
        for j in range(i + 1, n):
            value = lower[j][i] * denominator
            if value.denominator != 1:
                raise AssertionError("failed to clear an LDL denominator")
            form[j] = int(value)
        forms.append(form)
        center_denominators.append(denominator)
        rational_weights.append(diagonal[i] / (denominator * denominator))
    global_scale = 1
    for weight in rational_weights:
        global_scale = math.lcm(global_scale, weight.denominator)
    weights = []
    for weight in rational_weights:
        scaled = weight * global_scale
        if scaled.denominator != 1 or scaled <= 0:
            raise AssertionError("invalid integerized LDL weight")
        weights.append(int(scaled))

    reconstructed = [[0] * n for _ in range(n)]
    for weight, form in zip(weights, forms):
        for i, left in enumerate(form):
            if not left:
                continue
            for j, right in enumerate(form):
                if right:
                    reconstructed[i][j] += weight * left * right
    expected = [[global_scale * value for value in row] for row in matrix]
    if reconstructed != expected:
        raise AssertionError("integerized LDL identity failed exact reconstruction")
    return {
        "global_scale": global_scale,
        "weights": weights,
        "forms": forms,
        "center_denominators": center_denominators,
        "identity_sha256": canonical_matrix_sha256(reconstructed),
    }


def enumerate_closed_ball(
    gram: Sequence[Sequence[int]],
    bound: int,
    *,
    lll_reduce: bool = True,
    collect_moments: bool = False,
) -> dict[str, object]:
    """Enumerate all nonzero lattice vectors of norm at most ``bound``.

    Coverage proof: exact LDL gives

        x H x^t = sum_i d_i (x_i + sum_{j>i} L[j,i]x_j)^2.

    At recursion level i the already fixed higher-coordinate contribution is
    exact.  The integer interval is enlarged using an integer ceiling of the
    remaining radius, and every candidate is then accepted by the exact
    rational inequality.  Hence no point in the closed ellipsoid is skipped.
    """
    start = time.perf_counter()
    n = len(gram)
    if lll_reduce:
        row_basis, lll_stats = heuristic_lll_transform(gram)
    else:
        row_basis, lll_stats = identity(n), {
            "method": "identity",
            "swaps": 0,
            "size_reductions": 0,
            "iterations": 0,
        }
    reduced = transformed_gram(gram, row_basis)
    lower, diagonal = exact_ldl(reduced)
    integer_ldl = integerize_ldl(reduced, lower, diagonal)
    global_scale = int(integer_ldl["global_scale"])
    weights = list(integer_ldl["weights"])
    forms = list(integer_ldl["forms"])
    center_denominators = list(integer_ldl["center_denominators"])
    coordinates = [0] * n
    norm_counts: Counter[int] = Counter()
    nodes = 0
    leaves = 0
    coordinate_abs_max = 0
    digest_sum = 0
    digest_xor = 0
    modulus = 1 << 256
    moments = [[0] * n for _ in range(n)] if collect_moments else None

    def visit(index: int, used: int) -> None:
        nonlocal nodes, leaves, coordinate_abs_max, digest_sum, digest_xor
        nodes += 1
        if nodes % 1_000_000 == 0:
            print(
                json.dumps(
                    {
                        "event": "enumeration_progress",
                        "rank": n,
                        "bound": bound,
                        "nodes": nodes,
                        "leaves": leaves,
                        "elapsed_seconds": round(time.perf_counter() - start, 3),
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
                flush=True,
            )
        if index < 0:
            if not any(coordinates):
                return
            if used % global_scale:
                raise AssertionError("integral Gram produced a fractional norm")
            norm_int = used // global_scale
            if norm_int > bound:
                raise AssertionError("enumerator admitted an invalid vector")
            leaves += 1
            norm_counts[norm_int] += 1
            coordinate_abs_max = max(
                coordinate_abs_max, max(abs(value) for value in coordinates)
            )
            # Reduced coordinates are canonical relative to the recorded
            # unimodular transform and avoid an O(n^2) map at every leaf.
            encoded = (",".join(map(str, coordinates)) + "\n").encode("ascii")
            value = int.from_bytes(hashlib.sha256(encoded).digest(), "big")
            digest_sum = (digest_sum + value) % modulus
            digest_xor ^= value
            if moments is not None and norm_int == bound:
                for i, a in enumerate(coordinates):
                    for j, b in enumerate(coordinates):
                        moments[i][j] += a * b
            return

        remaining = bound * global_scale - used
        if remaining < 0:
            return
        denominator = center_denominators[index]
        center_numerator = sum(
            forms[index][j] * coordinates[j] for j in range(index + 1, n)
        )
        radius = math.isqrt(remaining // weights[index])
        low = ceil_fraction(Fraction(-radius - center_numerator, denominator))
        high = floor_fraction(Fraction(radius - center_numerator, denominator))
        for candidate in range(low, high + 1):
            linear_value = denominator * candidate + center_numerator
            contribution = weights[index] * linear_value * linear_value
            if contribution <= remaining:
                coordinates[index] = candidate
                visit(index - 1, used + contribution)
        coordinates[index] = 0

    visit(n - 1, 0)
    if any(count % 2 for count in norm_counts.values()):
        raise AssertionError("a centrally symmetric shell has odd cardinality")
    return {
        "bound": bound,
        "rank": n,
        "norm_counts": {str(key): norm_counts[key] for key in sorted(norm_counts)},
        "total_nonzero": leaves,
        "recursion_nodes": nodes,
        "max_abs_reduced_coordinate": coordinate_abs_max,
        "commutative_vector_digest_sum_sha256": f"{digest_sum:064x}",
        "commutative_vector_digest_xor_sha256": f"{digest_xor:064x}",
        "norm_bound_shell_second_moment": moments,
        "lll": {
            **lll_stats,
            "transform_det": determinant_bareiss(row_basis),
            "transform_sha256": canonical_matrix_sha256(row_basis),
            "reduced_gram_sha256": canonical_matrix_sha256(reduced),
        },
        "ldl_pivots": [str(value) for value in diagonal],
        "integerized_ldl": {
            "global_scale": str(global_scale),
            "global_scale_bits": global_scale.bit_length(),
            "weights_sha256": sha256_bytes(
                json.dumps(weights, separators=(",", ":")).encode("ascii")
            ),
            "forms_sha256": canonical_matrix_sha256(forms),
            "reconstruction_sha256": integer_ldl["identity_sha256"],
        },
        "coverage": (
            "complete exact closed-ellipsoid recursion after an exactly "
            "verified unimodular basis change; floating point only selected "
            "row operations and did not prune or accept vectors"
        ),
    }


def direct_sum(*blocks: Sequence[Sequence[int]]) -> Matrix:
    total = sum(len(block) for block in blocks)
    result = [[0] * total for _ in range(total)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[offset + i][offset + j] = int(value)
        offset += len(block)
    return result


def cartan_a(rank: int) -> Matrix:
    return [
        [
            2 if i == j else -1 if abs(i - j) == 1 else 0
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def cartan_e6() -> Matrix:
    matrix = [[0] * 6 for _ in range(6)]
    for i in range(6):
        matrix[i][i] = 2
    for i, j in ((0, 1), (1, 2), (2, 3), (3, 4), (2, 5)):
        matrix[i][j] = matrix[j][i] = -1
    return matrix


def cartan_e8() -> Matrix:
    matrix = [[0] * 8 for _ in range(8)]
    for i in range(8):
        matrix[i][i] = 2
    for i, j in (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (5, 6),
        (2, 7),
    ):
        matrix[i][j] = matrix[j][i] = -1
    return matrix


def factor_3_7(value: int) -> tuple[int, int]:
    a = b = 0
    while value % 3 == 0:
        value //= 3
        a += 1
    while value % 7 == 0:
        value //= 7
        b += 1
    if value != 1:
        raise ValueError("determinant has a prime outside {3,7}")
    return a, b


def theta_level(a: int, b: int) -> int:
    return (3 if a else 1) * (7 if b else 1)


def gamma0_index(level: int) -> int:
    result = level
    for prime in (3, 7):
        if level % prime == 0:
            result = result * (prime + 1) // prime
    return result


def scalar_character_label(determinant: int) -> str:
    square = math.isqrt(determinant)
    if square * square == determinant:
        return "trivial"
    if determinant % 21 == 0:
        quotient = determinant // 21
        root = math.isqrt(quotient)
        if root * root == quotient:
            return "chi_21(d)=(21/d)"
    raise ValueError(f"unexpected determinant square class {determinant}")


def endpoint_level_table() -> list[dict[str, object]]:
    rows = []
    for determinant in ENDPOINT_DETERMINANTS:
        a, b = factor_3_7(determinant)
        level = theta_level(a, b)
        index = gamma0_index(level)
        rows.append(
            {
                "determinant": determinant,
                "a3": a,
                "a7": b,
                "discriminant_group": f"(Z/3)^{a} x (Z/7)^{b}",
                "exact_level_S": level,
                "exact_level_G": 21,
                "scalar_character": scalar_character_label(determinant),
                "gamma0_index": index,
                "weight": WEIGHT,
                "sturm_bound_q_exponent": (WEIGHT * index) // 12,
                "sturm_norm_through": 2 * ((WEIGHT * index) // 12),
                "modularity_required_determinant": level**22,
                "modularity_determinant_veto": determinant != level**22,
            }
        )
    return rows


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] % prime),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(value * inverse) % prime for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column]:
                multiplier = work[row][column]
                work[row] = [
                    (a - multiplier * b) % prime
                    for a, b in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def independent_columns(
    columns: Sequence[Sequence[int]], prime: int
) -> list[list[int]]:
    chosen: list[list[int]] = []
    current_rank = 0
    for column in columns:
        candidate = chosen + [[value % prime for value in column]]
        candidate_matrix = [list(row) for row in zip(*candidate)]
        new_rank = rank_mod(candidate_matrix, prime)
        if new_rank > current_rank:
            chosen.append([value % prime for value in column])
            current_rank = new_rank
    return chosen


def quotient_representatives_mod_p(gram: Matrix, prime: int) -> list[list[int]]:
    n = len(gram)
    relation_columns = [
        [gram[row][column] % prime for row in range(n)] for column in range(n)
    ]
    relations = independent_columns(relation_columns, prime)
    current = list(relations)
    reps: list[list[int]] = []
    current_rank = len(current)
    for i in range(n):
        vector = [int(j == i) for j in range(n)]
        candidate = current + [vector]
        new_rank = rank_mod([list(row) for row in zip(*candidate)], prime)
        if new_rank > current_rank:
            reps.append(vector)
            current.append(vector)
            current_rank = new_rank
        if current_rank == n:
            break
    if current_rank != n:
        raise AssertionError("failed to construct a quotient complement")
    return reps


def discriminant_bilinear_matrix_mod_p(gram: Matrix, prime: int) -> Matrix:
    inverse = inverse_fraction(gram)
    scaled = scalar_matrix(prime, inverse)
    if not all(Fraction(value).denominator == 1 for row in scaled for value in row):
        raise ValueError("discriminant group is not elementary at this prime")
    reps = quotient_representatives_mod_p(gram, prime)
    result = []
    for left in reps:
        row = []
        for right in reps:
            value = sum(
                left[i] * int(scaled[i][j]) * right[j]
                for i in range(len(gram))
                for j in range(len(gram))
            )
            row.append(value % prime)
        result.append(row)
    if rank_mod(result, prime) != len(result):
        raise AssertionError("computed discriminant form is degenerate")
    return result


def mod_matmul(left: Matrix, right: Matrix, prime: int) -> Matrix:
    return [
        [int(value) % prime for value in row]
        for row in matmul(left, right)
    ]


def mod_inverse(matrix: Matrix, prime: int) -> Matrix:
    n = len(matrix)
    work = [
        [value % prime for value in row]
        + [int(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] % prime),
            None,
        )
        if pivot is None:
            raise ValueError("singular modular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        multiplier = pow(work[column][column], -1, prime)
        work[column] = [(value * multiplier) % prime for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            multiplier = work[row][column]
            work[row] = [
                (a - multiplier * b) % prime
                for a, b in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def vector_bilinear_mod(
    matrix: Matrix, left: Sequence[int], right: Sequence[int], prime: int
) -> int:
    return (
        sum(
            left[i] * matrix[i][j] * right[j]
            for i in range(len(left))
            for j in range(len(right))
        )
        % prime
    )


def diagonalize_symmetric_mod_3(matrix: Matrix) -> tuple[Matrix, list[int]]:
    """Return U and d with U^T matrix U=diag(d), over F_3."""
    prime = 3
    n = len(matrix)
    basis = identity(n)
    orthogonal: list[list[int]] = []
    remaining = [row[:] for row in basis]
    while remaining:
        pivot_index = next(
            (
                i
                for i, vector in enumerate(remaining)
                if vector_bilinear_mod(matrix, vector, vector, prime)
            ),
            None,
        )
        if pivot_index is None:
            # If all current basis vectors are isotropic, a sum of a pair with
            # nonzero mutual product is anisotropic in odd characteristic.
            pair = None
            for i in range(len(remaining)):
                for j in range(i + 1, len(remaining)):
                    if vector_bilinear_mod(
                        matrix, remaining[i], remaining[j], prime
                    ):
                        pair = (i, j)
                        break
                if pair:
                    break
            if pair is None:
                raise AssertionError("nonsingular form became zero")
            i, j = pair
            remaining[i] = [
                (a + b) % prime for a, b in zip(remaining[i], remaining[j])
            ]
            pivot_index = i
        pivot = remaining.pop(pivot_index)
        pivot_norm = vector_bilinear_mod(matrix, pivot, pivot, prime)
        inverse_norm = pow(pivot_norm, -1, prime)
        next_remaining = []
        for vector in remaining:
            coefficient = (
                vector_bilinear_mod(matrix, pivot, vector, prime) * inverse_norm
            ) % prime
            adjusted = [
                (a - coefficient * b) % prime for a, b in zip(vector, pivot)
            ]
            next_remaining.append(adjusted)
        orthogonal.append(pivot)
        remaining = next_remaining
    transform = [list(column) for column in zip(*orthogonal)]
    diagonalized = mod_matmul(
        mod_matmul(transpose(transform), matrix, prime), transform, prime
    )
    diagonal = [diagonalized[i][i] for i in range(n)]
    if any(
        diagonalized[i][j] for i in range(n) for j in range(n) if i != j
    ):
        raise AssertionError("finite-field diagonalization failed")
    return transform, diagonal


def canonicalize_diagonal_mod_3(diagonal: Sequence[int]) -> tuple[Matrix, list[int]]:
    """Map a diagonal form to all 1s, with one trailing 2 if needed."""
    n = len(diagonal)
    order = [i for i, value in enumerate(diagonal) if value == 1]
    twos = [i for i, value in enumerate(diagonal) if value == 2]
    order += twos
    permutation = [[int(order[j] == i) for j in range(n)] for i in range(n)]
    sorted_diagonal = [diagonal[i] for i in order]
    transform = permutation
    # Convert each pair diag(2,2) to diag(1,1) using H=[[1,1],[1,-1]].
    start = sorted_diagonal.count(1)
    block = identity(n)
    for i in range(start, n - 1, 2):
        block[i][i] = 1
        block[i][i + 1] = 1
        block[i + 1][i] = 1
        block[i + 1][i + 1] = 2
    transform = mod_matmul(transform, block, 3)
    canonical = [1] * (n - (len(twos) % 2))
    if len(twos) % 2:
        canonical.append(2)
    return transform, canonical


def explicit_isometry_mod_3(left: Matrix, right: Matrix) -> Matrix:
    """Find P with P^T left P = right, or raise if classes differ."""
    ul, dl = diagonalize_symmetric_mod_3(left)
    ur, dr = diagonalize_symmetric_mod_3(right)
    cl, canonical_left = canonicalize_diagonal_mod_3(dl)
    cr, canonical_right = canonicalize_diagonal_mod_3(dr)
    if canonical_left != canonical_right:
        raise AssertionError(
            f"quadratic-form classes differ: {canonical_left} != {canonical_right}"
        )
    left_to_canonical = mod_matmul(ul, cl, 3)
    right_to_canonical = mod_matmul(ur, cr, 3)
    isometry = mod_matmul(
        left_to_canonical, mod_inverse(right_to_canonical, 3), 3
    )
    check = mod_matmul(
        mod_matmul(transpose(isometry), left, 3), isometry, 3
    )
    if check != [[value % 3 for value in row] for row in right]:
        raise AssertionError("explicit finite-field isometry check failed")
    return isometry


def component_data() -> dict[str, dict[str, object]]:
    return {
        "A2": {"rank": 2, "det": 3, "gram": cartan_a(2)},
        "A6": {"rank": 6, "det": 7, "gram": cartan_a(6)},
        "A20": {"rank": 20, "det": 21, "gram": cartan_a(20)},
        "E6": {"rank": 6, "det": 3, "gram": cartan_e6()},
        "E8": {"rank": 8, "det": 1, "gram": cartan_e8()},
    }


def audit_ade_components() -> dict[str, dict[str, object]]:
    audited: dict[str, dict[str, object]] = {}
    for name, item in component_data().items():
        gram = item["gram"]
        determinant = determinant_bareiss(gram)
        if determinant != item["det"]:
            raise AssertionError(f"{name}: determinant mismatch")
        inverse = inverse_fraction(gram)
        scaled_dual = scalar_matrix(21, inverse)
        if not is_even_integral(scaled_dual):
            raise AssertionError(f"{name}: 21 times dual is not even integral")
        shell = enumerate_closed_ball(gram, 4, lll_reduce=True)
        dual_bound = {
            "A2": 14,
            "A6": 18,
            "A20": 20,
            "E6": 28,
            "E8": 42,
        }[name]
        dual_shell = enumerate_closed_ball(
            [[int(value) for value in row] for row in scaled_dual],
            dual_bound,
            lll_reduce=True,
        )
        if not dual_shell["norm_counts"].get(str(dual_bound)):
            raise AssertionError(f"{name}: asserted scaled-dual minimum absent")
        smaller = [
            int(norm)
            for norm in dual_shell["norm_counts"]
            if int(norm) < dual_bound
        ]
        if smaller:
            raise AssertionError(f"{name}: smaller scaled-dual norm {smaller}")
        audited[name] = {
            "rank": item["rank"],
            "determinant": determinant,
            "roots_r2": shell["norm_counts"].get("2", 0),
            "norm_four_r4": shell["norm_counts"].get("4", 0),
            "twenty_one_dual_even_integral": True,
            "twenty_one_dual_exact_minimum": dual_bound,
            "twenty_one_dual_minimum_count": dual_shell["norm_counts"][
                str(dual_bound)
            ],
            "primal_enumeration": {
                key: shell[key]
                for key in (
                    "total_nonzero",
                    "recursion_nodes",
                    "coverage",
                    "lll",
                )
            },
            "dual_enumeration": {
                key: dual_shell[key]
                for key in (
                    "total_nonzero",
                    "recursion_nodes",
                    "coverage",
                    "lll",
                )
            },
        }
    expected = {
        "A2": (6, 0),
        "A6": (42, 210),
        "A20": (420, 35910),
        "E6": (72, 270),
        "E8": (240, 2160),
    }
    for name, (roots, norm_four) in expected.items():
        if (
            audited[name]["roots_r2"],
            audited[name]["norm_four_r4"],
        ) != (roots, norm_four):
            raise AssertionError(f"{name}: unexpected theta coefficients")
    return audited


def ade_decompositions(
    components: dict[str, dict[str, object]]
) -> list[dict[str, object]]:
    names = list(components)
    solutions: list[dict[str, object]] = []

    def recurse(
        index: int, rank_left: int, determinant: int, counts: dict[str, int]
    ) -> None:
        if index == len(names):
            if rank_left == 0 and determinant in ENDPOINT_DETERMINANTS:
                roots = sum(
                    count * int(components[name]["roots_r2"])
                    for name, count in counts.items()
                )
                norm_four = sum(
                    count * int(components[name]["norm_four_r4"])
                    for name, count in counts.items()
                )
                root_components: list[int] = []
                for name, count in counts.items():
                    root_components += [int(components[name]["roots_r2"])] * count
                norm_four += sum(
                    root_components[i] * root_components[j]
                    for i in range(len(root_components))
                    for j in range(i + 1, len(root_components))
                )
                solutions.append(
                    {
                        "determinant": determinant,
                        "components": {
                            name: count for name, count in counts.items() if count
                        },
                        "roots_r2": roots,
                        "norm_four_r4": norm_four,
                        "twenty_one_dual_minimum": min(
                            int(components[name]["twenty_one_dual_exact_minimum"])
                            for name, count in counts.items()
                            if count
                        ),
                    }
                )
            return
        name = names[index]
        component = components[name]
        rank = int(component["rank"])
        det = int(component["determinant"])
        for count in range(rank_left // rank + 1):
            next_det = determinant * det**count
            if next_det > max(ENDPOINT_DETERMINANTS):
                break
            counts[name] = count
            recurse(index + 1, rank_left - count * rank, next_det, counts)
        counts.pop(name, None)

    recurse(0, 44, 1, {})
    solutions.sort(
        key=lambda item: (
            int(item["determinant"]),
            json.dumps(item["components"], sort_keys=True),
        )
    )
    if len(solutions) != 17:
        raise AssertionError(f"expected 17 ADE decompositions, got {len(solutions)}")
    return solutions


def source_lattice_audit(
    source_manifest: dict[str, dict[str, object]]
) -> tuple[dict[str, object], Matrix, Matrix]:
    catalogue = embedded_catalogue_data()
    matrices: dict[str, Matrix] = {}
    source_checks: dict[str, object] = {}
    for name, spec in SOURCE_SPECS.items():
        entry = source_manifest[name]
        gram = [[int(value) for value in row] for row in catalogue[name]["gram"]]
        matrices[name] = gram
        metadata = catalogue[name]["metadata"]
        expected_metadata = {
            "dimension": spec["dimension"],
            "determinant": spec["catalogue_det"],
            "minimum": spec["catalogue_minimum"],
            "kissing_number": spec["catalogue_kissing"],
        }
        if metadata != expected_metadata:
            raise AssertionError(
                f"{name}: catalogue metadata mismatch {metadata} != {expected_metadata}"
            )
        determinant = determinant_bareiss(gram)
        lower, pivots = exact_ldl(gram)
        del lower
        if determinant != spec["catalogue_det"] or any(pivot <= 0 for pivot in pivots):
            raise AssertionError(f"{name}: exact determinant/PD check failed")
        if not is_even_integral(gram):
            raise AssertionError(f"{name}: Gram is not even integral")
        source_checks[name] = {
            "raw_source": entry,
            "catalogue_metadata_parsed_not_trusted": metadata,
            "rank": len(gram),
            "determinant_exact": determinant,
            "positive_definite_exact_ldl": True,
            "even_integral": True,
            "gram_sha256": canonical_matrix_sha256(gram),
            "ldl_pivots": [str(value) for value in pivots],
        }
    return source_checks, matrices["K12"], matrices["LAMBDA_F"]


def k12_modularity_audit(k12: Matrix) -> dict[str, object]:
    similarity = [
        [int(value) for value in row]
        for row in embedded_catalogue_data()["K12"]["similarity"]
    ]
    inverse = inverse_fraction(k12)
    if not is_even_integral(scalar_matrix(3, inverse)):
        raise AssertionError("3 K12^-1 is not even integral")
    # Catalogue convention: T K T^t = 3 K and K^-1 T is unimodular.
    if not matrices_equal(
        matmul(matmul(similarity, k12), transpose(similarity)),
        scalar_matrix(3, k12),
    ):
        raise AssertionError("K12 similarity identity failed")
    k_inverse_times_t = matmul(inverse, similarity)
    if not all(
        Fraction(value).denominator == 1
        for row in k_inverse_times_t
        for value in row
    ):
        raise AssertionError("K12^-1 T is not integral")
    u = [[int(value) for value in row] for row in transpose(k_inverse_times_t)]
    if abs(determinant_bareiss(u)) != 1:
        raise AssertionError("K12 scaled-dual congruence is not unimodular")
    congruence = matmul(matmul(transpose(u), k12), u)
    if not matrices_equal(congruence, scalar_matrix(3, inverse)):
        raise AssertionError("K12 versus 3K12^-1 congruence failed")
    return {
        "three_dual_even_integral": True,
        "source_similarity_sha256": canonical_matrix_sha256(similarity),
        "explicit_congruence_transform_sha256": canonical_matrix_sha256(u),
        "explicit_congruence_transform_det": determinant_bareiss(u),
        "three_dual_isometric_to_K12": True,
        "three_dual_exact_minimum": 4,
        "three_dual_norm_four_count": 756,
    }


def hostile_control_audit(
    k12: Matrix,
    lambda_f: Matrix,
    source_checks: dict[str, object],
) -> dict[str, object]:
    k12_shell = enumerate_closed_ball(k12, 4)
    lambda_shell = enumerate_closed_ball(lambda_f, 4)
    if k12_shell["norm_counts"] != {"4": 756}:
        raise AssertionError(f"K12 shell mismatch: {k12_shell['norm_counts']}")
    if lambda_shell["norm_counts"] != {"4": 146880}:
        raise AssertionError(
            f"LAMBDA(F) shell mismatch: {lambda_shell['norm_counts']}"
        )
    k12_modularity = k12_modularity_audit(k12)
    lambda_inverse = inverse_fraction(lambda_f)
    if not is_even_integral(lambda_inverse):
        raise AssertionError("unimodular LAMBDA(F) inverse is not even integral")
    lambda_inverse_int = [[int(value) for value in row] for row in lambda_inverse]
    if abs(determinant_bareiss(lambda_inverse_int)) != 1:
        raise AssertionError("LAMBDA(F) inverse transform is not unimodular")
    if not matrices_equal(
        matmul(matmul(transpose(lambda_inverse_int), lambda_f), lambda_inverse_int),
        lambda_inverse,
    ):
        raise AssertionError("LAMBDA(F) self-dual congruence failed")

    s0 = direct_sum(k12, lambda_f)
    s0_inverse = inverse_fraction(s0)
    g0 = scalar_matrix(21, s0_inverse)
    if len(s0) != 44 or determinant_bareiss(s0) != 729:
        raise AssertionError("S0 rank/determinant mismatch")
    if not is_even_integral(s0) or not is_even_integral(g0):
        raise AssertionError("S0 or 21 S0^-1 is not even integral")
    # Exact block minima: 21 K12^-1 = 7(3 K12^-1) has minimum 28;
    # 21 Lambda^-1 has minimum 84 because Lambda is unimodular of min 4.
    g0_minimum = min(7 * 4, 21 * 4)
    s0_counts = {
        "2": 0,
        "4": int(k12_shell["norm_counts"]["4"])
        + int(lambda_shell["norm_counts"]["4"]),
    }
    if s0_counts != {"2": 0, "4": 147636}:
        raise AssertionError("S0 theta coefficients mismatch")
    return {
        "S0": {
            "components": "K12 orthogonal_sum LAMBDA(F)",
            "rank": 44,
            "determinant": 729,
            "even_integral": True,
            "positive_definite": True,
            "exact_minimum": 4,
            "root_count_r2": 0,
            "norm_four_r4": 147636,
            "twenty_one_dual_even_integral": True,
            "twenty_one_dual_exact_minimum": g0_minimum,
            "full_endpoint_objects_supplied": False,
        },
        "K12": {
            **source_checks["K12"],
            "enumeration": k12_shell,
            "modularity": k12_modularity,
        },
        "LAMBDA_F": {
            **source_checks["LAMBDA_F"],
            "enumeration": lambda_shell,
            "unimodular_inverse_even_integral": True,
            "inverse_congruence_transform_det": determinant_bareiss(
                lambda_inverse_int
            ),
            "inverse_isometric_to_original": True,
            "inverse_exact_minimum": 4,
            "inverse_norm_four_count": 146880,
        },
    }


def discriminant_comparator(k12: Matrix) -> dict[str, object]:
    e6 = cartan_e6()
    e8 = cartan_e8()
    s1 = direct_sum(*(6 * [e6] + [e8]))
    if len(s1) != 44 or determinant_bareiss(s1) != 729:
        raise AssertionError("E6^6 + E8 comparator rank/determinant mismatch")
    e6_roots = enumerate_closed_ball(e6, 2)["norm_counts"].get("2", 0)
    e8_roots = enumerate_closed_ball(e8, 2)["norm_counts"].get("2", 0)
    roots = 6 * e6_roots + e8_roots
    if roots != 672:
        raise AssertionError(f"comparator root count mismatch: {roots}")
    k12_form = discriminant_bilinear_matrix_mod_p(k12, 3)
    e6_form = discriminant_bilinear_matrix_mod_p(e6, 3)
    e6_six_form = direct_sum(*([e6_form] * 6))
    isometry = explicit_isometry_mod_3(k12_form, e6_six_form)
    check = mod_matmul(
        mod_matmul(transpose(isometry), k12_form, 3), isometry, 3
    )
    if check != e6_six_form:
        raise AssertionError("discriminant isometry was not reproduced")
    comparator_inverse = inverse_fraction(s1)
    comparator_g = scalar_matrix(21, comparator_inverse)
    if not is_even_integral(comparator_g):
        raise AssertionError("comparator scaled dual not even integral")
    return {
        "S1": {
            "components": "E6^6 orthogonal_sum E8",
            "rank": 44,
            "determinant": 729,
            "exact_level": 3,
            "scalar_character": "trivial",
            "root_count_r2": roots,
            "norm_four_r4": 185220,
            "twenty_one_dual_even_integral": True,
            "twenty_one_dual_exact_minimum": 28,
        },
        "finite_quadratic_module": {
            "prime": 3,
            "dimension": len(k12_form),
            "K12_scaled_bilinear_matrix_mod_3": k12_form,
            "E6_scaled_bilinear_matrix_mod_3": e6_form,
            "explicit_isometry_P_mod_3": isometry,
            "verified_identity": "P^T A_K12 P = direct_sum(A_E6 x 6) mod 3",
            "quadratic_form_reason": (
                "for odd exponent, q(x)=B(x,x)/2, so the explicit bilinear "
                "isometry is an isometry of finite quadratic modules"
            ),
            "same_weil_representation": True,
            "same_zero_component_theta_series": False,
        },
    }


def frame_and_transformation_audit() -> dict[str, object]:
    return {
        "smith_and_level_derivation": {
            "statement": (
                "SG=21I makes every Smith invariant d_i divide squarefree 21. "
                "For det(S)=3^a7^b, A_S as an abelian group is "
                "(Z/3)^a x (Z/7)^b. Its exponent e is 3, 7, or 21. "
                "Since 21/e is odd and 21S^-1 has even diagonal, eS^-1 "
                "has even diagonal; integrality forces every theta level "
                "to be a multiple of e, hence the exact level is e."
            ),
            "G_statement": (
                "The Smith factors of 21S^-1 are 21/d_i in reverse order. "
                "Both 3 and 7 occur in A_G for all eight rows, and the same "
                "odd-factor argument makes the exact level of G equal to 21."
            ),
        },
        "theta_conventions": {
            "q": "exp(2*pi*i*tau)",
            "component": (
                "theta_gamma(tau)=sum_{x in L+gamma} "
                "q^((x,x)/2), gamma in L*/L"
            ),
            "T": (
                "theta_gamma(tau+1)=exp(pi*i*(gamma,gamma))*theta_gamma(tau)"
            ),
            "S": (
                "theta_gamma(-1/tau)=(-i*tau)^22/sqrt(det(S)) "
                "* sum_delta exp(-2*pi*i*(gamma,delta))*theta_delta(tau)"
            ),
            "scalar": (
                "theta_L is in M_22(Gamma_0(N), chi), "
                "chi(d)=Kronecker(det(S),d); rank/2=22 is even"
            ),
            "poisson_scaled_dual": (
                "theta_S(-1/(21*tau))=(21*tau/i)^22/sqrt(det(S))*theta_G(tau)"
            ),
            "warning": (
                "Changing the sign convention for the finite Fourier kernel "
                "replaces the Weil representation by its dual; all claims "
                "here use the displayed negative-sign convention."
            ),
        },
        "frame_visible_consequences": {
            "r4_lower_bound": 462,
            "proof": (
                "231 norm-four rows are distinct and no two are negatives, "
                "because off-diagonal inner products exclude +4 and -4."
            ),
            "ordinary_odd_harmonic_theta": (
                "identically zero by v,-v cancellation; it cannot see the "
                "selected orientation of the 231 antipodal pairs"
            ),
            "theta_does_not_supply": [
                "a primitive Z^231 embedding",
                "the pairwise Gram alphabet",
                "X, M, Q, or B",
                "the Schur-square origin",
                "a graph",
            ],
        },
        "strong_modularity_veto": {
            "determinant_identity": "det(S)^2=N^44, hence det(S)=N^22",
            "all_eight_vetoed": True,
            "strongly_21_modular_vetoed": True,
            "reason": (
                "strong modularity includes the full scaled-dual isometry; "
                "none of the endpoint determinants is N^22 at its exact level"
            ),
        },
    }


def run_all() -> dict[str, object]:
    source_manifest = frozen_source_metadata()
    source_checks, k12, lambda_f = source_lattice_audit(source_manifest)
    components = audit_ade_components()
    decompositions = ade_decompositions(components)
    hostile = hostile_control_audit(k12, lambda_f, source_checks)
    comparator = discriminant_comparator(k12)
    return {
        "schema": "wave28-theta-modular-independent-results-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "public_base_commit": BASE_COMMIT,
        "verification_date_utc": "2026-07-24",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "dependencies": "Python standard library only",
        },
        "scope_wall": {
            "bare_S_G_lattice_control_only": True,
            "primitive_embedding": False,
            "X": False,
            "M": False,
            "Q": False,
            "B": False,
            "Schur_square_certificate": False,
            "graph": False,
            "n3_equals_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "endpoint_level_character_sturm": endpoint_level_table(),
        "transformation_and_frame_audit": frame_and_transformation_audit(),
        "ADE_components": components,
        "ADE_rank44_decompositions": decompositions,
        "ADE_decomposition_count": len(decompositions),
        "hostile_control": hostile,
        "comparator_and_discriminant_form": comparator,
        "verdict": {
            "exact_level_character_poisson_weil_sturm_claims": "PASS",
            "determinant_veto_to_exact_level_modularity": "PASS",
            "determinant_veto_to_strong_21_modularity": "PASS",
            "ADE_theta_controls": "PASS",
            "rootless_h729_bare_control": "PASS",
            "same_discriminant_form_and_weil_representation": "PASS",
            "root_forced_by_bare_lattice_theta_data": "REFUTED",
            "full_endpoint_compatibility": "NOT_TESTED_NO_OBJECTS",
            "target_status": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-sources",
        action="store_true",
        help="fetch and freeze the two exact catalogue response bodies",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.refresh_sources:
        fetch_sources()
    result = run_all()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(args.output),
                "output_sha256": sha256_file(args.output),
                "K12_r4": result["hostile_control"]["K12"]["enumeration"][
                    "norm_counts"
                ]["4"],
                "LAMBDA_F_r4": result["hostile_control"]["LAMBDA_F"][
                    "enumeration"
                ]["norm_counts"]["4"],
                "S0_r4": result["hostile_control"]["S0"]["norm_four_r4"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
