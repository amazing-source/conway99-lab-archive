#!/usr/bin/env python3
"""Independent exact verifier for the Wave 28 simultaneous two-neighbors.

The implementation uses only the Python standard library.  It reconstructs
the Wave 27 block forms from Cartan edge data, constructs each two-neighbor
basis without importing discovery code, transforms all endpoint matrices,
and enumerates both lattice cosets with exact rational LDL bounds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_PATH = REPO_ROOT / "agents" / "2026-07-24-wave28-simultaneous-neighbor-freeze.md"
BRIEF_PATH = REPO_ROOT / "agents" / "2026-07-24-wave28-orchestrator-brief.md"
WAVE27_SOURCE_PATH = (
    REPO_ROOT / "attempts" / "wave27-a2free-construction" / "exact_check.py"
)

EXPECTED_INPUT_HASHES = {
    "agents/2026-07-24-wave28-simultaneous-neighbor-freeze.md":
        "7b8fce3763e2f6d4db2e0f7841e680d01486195d3ea4b6b04c5f59ace768d90a",
    "agents/2026-07-24-wave28-orchestrator-brief.md":
        "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e",
    "attempts/wave27-a2free-construction/exact_check.py":
        "1bd20f820a5d4467f29860a03a93c4ef3192bb9df4b1c87901080ffa8b793f1e",
}

PREFERRED_SUPPORT = (3, 6, 9, 18, 25, 33, 35, 41)
INITIAL_SUPPORT = (0, 3, 11, 14, 22, 28, 30, 42)
PREFERRED_ORTHOGONAL_LINE = (
    (0,) * 32 + (2, 1, 0, -1, -2, 0) + (0,) * 6
)

E8_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7))
E6_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4), (2, 5))

Matrix = list[list[Fraction]]
Vector = tuple[int, ...]


class VerificationError(AssertionError):
    """Raised when an independently reconstructed invariant fails."""


def F(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


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
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def json_scalar(value: Fraction | int) -> int | str:
    value = F(value)
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def json_matrix(matrix: Matrix) -> list[list[int | str]]:
    return [[json_scalar(value) for value in row] for row in matrix]


def eye(n: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]


def transpose(matrix: Matrix) -> Matrix:
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right:
        return []
    if len(left[0]) != len(right):
        raise ValueError("matrix dimension mismatch")
    right_t = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, col)), Fraction()) for col in right_t]
        for row in left
    ]


def matvec(matrix: Matrix, vector: Sequence[int | Fraction]) -> list[Fraction]:
    return [
        sum((entry * F(value) for entry, value in zip(row, vector)), Fraction())
        for row in matrix
    ]


def vecdot(left: Sequence[int | Fraction], right: Sequence[int | Fraction]) -> Fraction:
    return sum((F(a) * F(b) for a, b in zip(left, right)), Fraction())


def bilinear(left: Sequence[int | Fraction], gram: Matrix,
             right: Sequence[int | Fraction]) -> Fraction:
    return vecdot(left, matvec(gram, right))


def quadratic(vector: Sequence[int | Fraction], gram: Matrix) -> Fraction:
    return bilinear(vector, gram, vector)


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(row_l, row_r)]
        for row_l, row_r in zip(left, right)
    ]


def matrix_scale(scale: int | Fraction, matrix: Matrix) -> Matrix:
    scale = F(scale)
    return [[scale * value for value in row] for row in matrix]


def matrix_sub(left: Matrix, right: Matrix) -> Matrix:
    return matrix_add(left, matrix_scale(-1, right))


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction())


def is_symmetric(matrix: Matrix) -> bool:
    return matrix == transpose(matrix)


def is_integral(matrix: Matrix) -> bool:
    return all(value.denominator == 1 for row in matrix for value in row)


def is_even_integral_form(matrix: Matrix) -> bool:
    return (
        is_symmetric(matrix)
        and is_integral(matrix)
        and all(matrix[i][i].numerator % 2 == 0 for i in range(len(matrix)))
    )


def determinant(matrix: Matrix) -> Fraction:
    n = len(matrix)
    work = [row[:] for row in matrix]
    det = Fraction(1)
    sign = 1
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            return Fraction()
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign *= -1
        pivot_value = work[col][col]
        det *= pivot_value
        for row in range(col + 1, n):
            if not work[row][col]:
                continue
            factor = work[row][col] / pivot_value
            for j in range(col + 1, n):
                work[row][j] -= factor * work[col][j]
            work[row][col] = Fraction()
    return sign * det


def inverse(matrix: Matrix) -> Matrix:
    n = len(matrix)
    work = [row[:] + identity_row[:] for row, identity_row in zip(matrix, eye(n))]
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            raise VerificationError("singular matrix")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [value / pivot_value for value in work[col]]
        for row in range(n):
            if row == col or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                a - factor * b for a, b in zip(work[row], work[col])
            ]
    return [row[n:] for row in work]


def matrix_rank(matrix: Matrix) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    rank = 0
    for col in range(cols):
        pivot = next((row for row in range(rank, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(rows):
            if row == rank or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                a - factor * b for a, b in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def ldl(matrix: Matrix) -> tuple[Matrix, list[Fraction]]:
    if not is_symmetric(matrix):
        raise VerificationError("LDL input is not symmetric")
    n = len(matrix)
    lower = eye(n)
    diagonal = [Fraction() for _ in range(n)]
    for i in range(n):
        diagonal[i] = matrix[i][i] - sum(
            lower[i][k] * lower[i][k] * diagonal[k] for k in range(i)
        )
        if diagonal[i] <= 0:
            raise VerificationError(f"nonpositive LDL pivot at {i}")
        for j in range(i + 1, n):
            numerator = matrix[j][i] - sum(
                lower[j][k] * lower[i][k] * diagonal[k] for k in range(i)
            )
            lower[j][i] = numerator / diagonal[i]
    reconstructed = matmul(matmul(lower, [
        [diagonal[i] if i == j else Fraction() for j in range(n)]
        for i in range(n)
    ]), transpose(lower))
    if reconstructed != matrix:
        raise VerificationError("LDL reconstruction mismatch")
    return lower, diagonal


def is_positive_definite(matrix: Matrix) -> bool:
    try:
        _, pivots = ldl(matrix)
    except VerificationError:
        return False
    return all(pivot > 0 for pivot in pivots)


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def enumerate_vectors(
    gram: Matrix,
    cap: int,
    residues: Sequence[int] | None = None,
    modulus: int = 1,
) -> tuple[list[tuple[Vector, int]], dict[str, Any]]:
    """Enumerate every integer vector with q(x)<=cap using exact LDL bounds."""

    n = len(gram)
    lower, diagonal = ldl(gram)
    if residues is None:
        residues = [0] * n
        modulus = 1
    if len(residues) != n or modulus <= 0:
        raise ValueError("invalid residue data")

    x = [0] * n
    output: list[tuple[Vector, int]] = []
    stats = {
        "dimension": n,
        "cap": cap,
        "modulus": modulus,
        "accepted_partial_nodes": 0,
        "leaves": 0,
        "max_abs_coordinate": 0,
        "bound_method": "exact reverse-LDL rational interval with integer isqrt",
    }

    def recurse(index: int, used: Fraction) -> None:
        if index < 0:
            norm = quadratic(x, gram)
            if norm != used or norm > cap or norm.denominator != 1:
                raise VerificationError("enumerator leaf invariant failed")
            vector = tuple(x)
            output.append((vector, norm.numerator))
            stats["leaves"] += 1
            stats["max_abs_coordinate"] = max(
                stats["max_abs_coordinate"], max((abs(value) for value in x), default=0)
            )
            return

        remaining = Fraction(cap) - used
        if remaining < 0:
            return
        center = sum(
            (lower[j][index] * x[j] for j in range(index + 1, n)),
            Fraction(),
        )
        radius_squared = remaining / diagonal[index]
        center_num = center.numerator
        center_den = center.denominator
        scaled_numerator = (
            radius_squared.numerator * center_den * center_den
        )
        scaled_denominator = radius_squared.denominator
        max_scaled = math.isqrt(scaled_numerator // scaled_denominator)
        low = ceil_div(-max_scaled - center_num, center_den)
        high = (max_scaled - center_num) // center_den
        residue = residues[index] % modulus
        first = low + ((residue - low) % modulus)
        for value in range(first, high + 1, modulus):
            term = diagonal[index] * (F(value) + center) ** 2
            if term > remaining:
                continue
            x[index] = value
            stats["accepted_partial_nodes"] += 1
            recurse(index - 1, used + term)
        x[index] = 0

    recurse(n - 1, Fraction())
    output.sort()
    return output, stats


def cartan(rank: int, edges: Iterable[tuple[int, int]]) -> Matrix:
    matrix = [
        [Fraction(2 if i == j else 0) for j in range(rank)]
        for i in range(rank)
    ]
    for i, j in edges:
        matrix[i][j] = matrix[j][i] = Fraction(-1)
    return matrix


def block_diagonal(blocks: Sequence[Matrix]) -> Matrix:
    size = sum(len(block) for block in blocks)
    output = [[Fraction() for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                output[offset + i][offset + j] = value
        offset += len(block)
    return output


def columns_to_matrix(columns: Sequence[Sequence[int | Fraction]]) -> Matrix:
    if not columns:
        return []
    return [
        [F(columns[j][i]) for j in range(len(columns))]
        for i in range(len(columns[0]))
    ]


def matrix_columns(matrix: Matrix) -> list[list[Fraction]]:
    return transpose(matrix)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def reconstruct_wave27() -> dict[str, Any]:
    e8 = cartan(8, E8_EDGES)
    e6 = cartan(6, E6_EDGES)
    require(determinant(e8) == 1, "E8 determinant")
    require(determinant(e6) == 3, "E6 determinant")
    require(is_even_integral_form(e8) and is_positive_definite(e8), "E8 form")
    require(is_even_integral_form(e6) and is_positive_definite(e6), "E6 form")

    e8_inverse = inverse(e8)
    e6_inverse = inverse(e6)
    local_vector = (1, 0, -1, 0, 0, 1)
    dual_vector = matvec(e6_inverse, local_vector)
    dual_norm = vecdot(local_vector, dual_vector)
    require(dual_norm == Fraction(4, 3), "E6 local dual norm")

    row = [
        value / dual_norm for value in matvec(transpose(e6_inverse), local_vector)
    ]
    projector = [
        [F(local_vector[i]) * row[j] for j in range(6)]
        for i in range(6)
    ]
    require(matmul(projector, projector) == projector, "local projector")
    b6 = matrix_add(eye(6), matrix_scale(8, projector))
    q6 = matmul(e6_inverse, b6)
    require(is_even_integral_form(q6), "Q6 even integral")
    require(is_positive_definite(q6), "Q6 positive definite")
    require(determinant(q6) == 3, "Q6 determinant")
    require(trace(b6) == 14 and determinant(b6) == 9, "B6 invariants")

    blocks_s = [e8, e8, e8, e8, e6, e6]
    blocks_q = [e8_inverse, e8_inverse, e8_inverse, e8_inverse, q6, q6]
    starts: list[int] = []
    offset = 0
    for block in blocks_s:
        starts.append(offset)
        offset += len(block)
    s = block_diagonal(blocks_s)
    q = block_diagonal(blocks_q)
    g = matrix_scale(21, inverse(s))
    b = matmul(s, q)
    require(len(s) == 44, "rank-44 reconstruction")
    require(is_even_integral_form(s) and is_positive_definite(s), "S")
    require(is_even_integral_form(q) and is_positive_definite(q), "Q")
    require(is_even_integral_form(g) and is_positive_definite(g), "G")
    require(matmul(s, g) == matrix_scale(21, eye(44)), "SG=21I")
    require(trace(b) == 60 and determinant(b) == 81, "B invariants")
    return {
        "E8": e8,
        "E6": e6,
        "Q6": q6,
        "S": s,
        "Q": q,
        "G": g,
        "B": b,
        "blocks_s": blocks_s,
        "starts": starts,
    }


def construct_neighbor_basis(s: Matrix, support: Sequence[int]) -> dict[str, Any]:
    n = len(s)
    require(len(set(support)) == len(support), "support repeats")
    require(all(0 <= value < n for value in support), "support out of range")
    v = tuple(int(i in set(support)) for i in range(n))
    a_fraction = matvec(s, v)
    require(all(value.denominator == 1 for value in a_fraction), "a integral")
    a = tuple(value.numerator for value in a_fraction)
    require(vecdot(a, v).denominator == 1, "a.v integral")
    require(int(vecdot(a, v)) % 2 == 0, "v not in H")

    pivot = next((i for i, value in enumerate(a) if value % 2), None)
    require(pivot is not None, "parity functional is zero")
    h_columns: list[list[Fraction]] = []
    for col in range(n):
        vector = [Fraction() for _ in range(n)]
        if col == pivot:
            vector[pivot] = Fraction(2)
        else:
            vector[col] = Fraction(1)
            if a[col] % 2:
                vector[pivot] = Fraction(-1)
        require(vecdot(a, vector).denominator == 1, "H basis dot integral")
        require(int(vecdot(a, vector)) % 2 == 0, "H basis parity")
        h_columns.append(vector)
    h_basis = columns_to_matrix(h_columns)
    require(abs(determinant(h_basis)) == 2, "H basis determinant")

    h_inverse = inverse(h_basis)
    coordinates = matvec(h_inverse, v)
    require(all(value.denominator == 1 for value in coordinates), "v not in H basis")
    replacement = next(
        (i for i, value in enumerate(coordinates) if abs(value) == 1),
        None,
    )
    require(replacement is not None, "deterministic primitive replacement unavailable")
    p_columns = [column[:] for column in h_columns]
    p_columns[replacement] = [Fraction(value, 2) for value in v]
    p = columns_to_matrix(p_columns)
    det_p = determinant(p)
    require(abs(det_p) == 1, "neighbor basis determinant")
    p_inverse = inverse(p)
    require(matmul(p, p_inverse) == eye(n), "independent P inverse")
    require(matmul(p_inverse, p) == eye(n), "independent inverse P")
    require(any(F(value).denominator == 2 for value in p_columns[replacement]),
            "neighbor generator accidentally integral")
    return {
        "v": v,
        "a": a,
        "pivot": pivot,
        "replacement": replacement,
        "H_basis": h_basis,
        "H_coordinates_of_v": coordinates,
        "P": p,
        "P_inverse": p_inverse,
        "det_P": det_p,
    }


def transform_forms(base: dict[str, Any], basis: dict[str, Any]) -> dict[str, Matrix]:
    p = basis["P"]
    p_inverse = basis["P_inverse"]
    p_inverse_t = transpose(p_inverse)
    s_prime = matmul(matmul(transpose(p), base["S"]), p)
    q_prime = matmul(matmul(p_inverse, base["Q"]), p_inverse_t)
    g_prime = matmul(matmul(p_inverse, base["G"]), p_inverse_t)
    b_prime = matmul(s_prime, q_prime)
    c_prime = matrix_scale(Fraction(1, 2), matrix_sub(b_prime, eye(44)))
    return {
        "S_prime": s_prime,
        "Q_prime": q_prime,
        "G_prime": g_prime,
        "B_prime": b_prime,
        "C_prime": c_prime,
    }


def transformed_invariants(forms: dict[str, Matrix]) -> dict[str, Any]:
    s = forms["S_prime"]
    q = forms["Q_prime"]
    g = forms["G_prime"]
    b = forms["B_prime"]
    c = forms["C_prime"]
    invariants = {
        "S_even_integral_symmetric_pd": (
            is_even_integral_form(s) and is_positive_definite(s)
        ),
        "Q_even_integral_symmetric_pd": (
            is_even_integral_form(q) and is_positive_definite(q)
        ),
        "G_even_integral_symmetric_pd": (
            is_even_integral_form(g) and is_positive_definite(g)
        ),
        "SG_equals_21I": matmul(s, g) == matrix_scale(21, eye(44)),
        "det_S": json_scalar(determinant(s)),
        "det_Q": json_scalar(determinant(q)),
        "B_integral": is_integral(b),
        "B_identity_mod_2": (
            is_integral(b)
            and all(
                (b[i][j].numerator - int(i == j)) % 2 == 0
                for i in range(44) for j in range(44)
            )
        ),
        "trace_B": json_scalar(trace(b)),
        "det_B": json_scalar(determinant(b)),
        "C_integral": is_integral(c),
        "trace_C": json_scalar(trace(c)),
        "trace_C_squared": json_scalar(trace(matmul(c, c))),
        "C_squared_equals_4C": matmul(c, c) == matrix_scale(4, c),
        "GB_equals_21Q": matmul(g, b) == matrix_scale(21, q),
        "B_G_self_adjoint": matmul(transpose(b), g) == matmul(g, b),
    }
    expected = {
        "S_even_integral_symmetric_pd": True,
        "Q_even_integral_symmetric_pd": True,
        "G_even_integral_symmetric_pd": True,
        "SG_equals_21I": True,
        "det_S": 9,
        "det_Q": 9,
        "B_integral": True,
        "B_identity_mod_2": True,
        "trace_B": 60,
        "det_B": 81,
        "C_integral": True,
        "trace_C": 8,
        "trace_C_squared": 32,
        "C_squared_equals_4C": True,
        "GB_equals_21Q": True,
        "B_G_self_adjoint": True,
    }
    require(invariants == expected, f"transformed invariant mismatch: {invariants}")
    return invariants


def block_root_data(base: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for index, (gram, start) in enumerate(zip(base["blocks_s"], base["starts"])):
        vectors, stats = enumerate_vectors(gram, 2)
        roots = [vector for vector, norm in vectors if norm == 2]
        zero_count = sum(1 for _vector, norm in vectors if norm == 0)
        require(zero_count == 1, "block zero vector")
        expected = 240 if len(gram) == 8 else 72
        require(len(roots) == expected, "block root count")
        output.append({
            "index": index,
            "start": start,
            "rank": len(gram),
            "roots": roots,
            "enumeration": stats,
        })
    return output


def embed_block(vector: Sequence[int], start: int, dimension: int = 44) -> Vector:
    output = [0] * dimension
    output[start:start + len(vector)] = vector
    return tuple(output)


def enumerate_h_roots(
    base: dict[str, Any],
    neighbor: dict[str, Any],
    cached_blocks: list[dict[str, Any]],
) -> tuple[list[Vector], list[dict[str, Any]]]:
    a = neighbor["a"]
    roots: list[Vector] = []
    summaries = []
    for data in cached_blocks:
        kept = []
        rejected = 0
        for block_root in data["roots"]:
            root = embed_block(block_root, data["start"])
            parity = int(vecdot(a, root)) % 2
            if parity == 0:
                roots.append(root)
                kept.append(root)
            else:
                rejected += 1
        summaries.append({
            "block_index": data["index"],
            "rank": data["rank"],
            "all_roots": len(data["roots"]),
            "H_roots": len(kept),
            "rejected_by_H_parity": rejected,
            "root_hash_original_coordinates": canonical_hash([list(x) for x in sorted(kept)]),
            "enumeration": data["enumeration"],
        })
    roots.sort()
    require(len(roots) == len(set(roots)), "duplicate H roots")
    require(all(quadratic(root, base["S"]) == 2 for root in roots), "H root norm")
    require(all(int(vecdot(a, root)) % 2 == 0 for root in roots), "H root parity")
    return roots, summaries


def enumerate_half_coset(
    base: dict[str, Any],
    neighbor: dict[str, Any],
) -> dict[str, Any]:
    """Count every norm-two vector in v/2+H via six exact block cosets."""

    v = neighbor["v"]
    a = neighbor["a"]
    option_summaries = []
    block_options: list[list[tuple[Vector, int, int]]] = []
    for block_index, (gram, start) in enumerate(zip(base["blocks_s"], base["starts"])):
        rank = len(gram)
        residue = v[start:start + rank]
        enumerated, stats = enumerate_vectors(gram, 8, residue, 2)
        options: list[tuple[Vector, int, int]] = []
        histogram: dict[tuple[int, int], int] = {}
        for w, norm in enumerated:
            x = tuple((w[i] - residue[i]) // 2 for i in range(rank))
            require(all(w[i] - residue[i] == 2 * x[i] for i in range(rank)),
                    "half-coset block parity")
            parity = sum(a[start + i] * x[i] for i in range(rank)) % 2
            options.append((w, norm, parity))
            histogram[(norm, parity)] = histogram.get((norm, parity), 0) + 1
        block_options.append(options)
        option_summaries.append({
            "block_index": block_index,
            "rank": rank,
            "residue": list(residue),
            "option_count_q_le_8": len(options),
            "norm_parity_histogram": {
                f"q={norm},h={parity}": count
                for (norm, parity), count in sorted(histogram.items())
            },
            "enumeration": stats,
        })

    # Dynamic programming counts every six-block tuple.  The state is exact
    # total norm and the H parity of x=(w-v)/2.
    dp: dict[tuple[int, int], int] = {(0, 0): 1}
    for options in block_options:
        next_dp: dict[tuple[int, int], int] = {}
        compressed: dict[tuple[int, int], int] = {}
        for _w, norm, parity in options:
            compressed[(norm, parity)] = compressed.get((norm, parity), 0) + 1
        for (total, h_parity), count in dp.items():
            for (norm, parity), multiplicity in compressed.items():
                if total + norm > 8:
                    continue
                key = (total + norm, (h_parity + parity) % 2)
                next_dp[key] = next_dp.get(key, 0) + count * multiplicity
        dp = next_dp

    raw_q8 = sum(dp.get((8, parity), 0) for parity in (0, 1))
    root_count = dp.get((8, 0), 0)
    rejected_by_h = dp.get((8, 1), 0)
    witness: list[list[int]] | None = None
    if root_count:
        chosen: list[Vector] = []

        def find(block_index: int, remaining: int, parity: int) -> bool:
            nonlocal witness
            if block_index == len(block_options):
                if remaining == 0 and parity == 0:
                    witness = [list(item) for item in chosen]
                    return True
                return False
            for w, norm, h_parity in block_options[block_index]:
                if norm > remaining:
                    continue
                chosen.append(w)
                if find(block_index + 1, remaining - norm, (parity + h_parity) % 2):
                    return True
                chosen.pop()
            return False

        find(0, 8, 0)
        require(witness is not None, "positive DP count without witness")

    return {
        "method": (
            "enumerate w blockwise with w=v (mod 2), w^T S w<=8; "
            "combine exact norm/parity states for x=(w-v)/2"
        ),
        "norm_conversion": "q(v/2+x)=2 iff q(v+2x)=8",
        "blocks": option_summaries,
        "final_dp": {
            f"q={norm},h={parity}": count
            for (norm, parity), count in sorted(dp.items())
        },
        "raw_q8_tuples_before_H_filter": raw_q8,
        "q8_tuples_rejected_by_H_parity": rejected_by_h,
        "new_roots_in_v_over_2_plus_H": root_count,
        "first_root_block_witness": witness,
        "complete": True,
        "no_arbitrary_coordinate_box": True,
    }


def connected_components(roots: Sequence[Vector], gram: Matrix) -> list[list[int]]:
    n = len(roots)
    gram_images = [
        tuple(value.numerator for value in matvec(gram, root))
        for root in roots
    ]
    adjacency = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            inner = vecdot(roots[i], gram_images[j])
            require(inner.denominator == 1, "root inner product nonintegral")
            if inner:
                require(abs(inner) <= 2, "unexpected simply-laced root product")
                adjacency[i].add(j)
                adjacency[j].add(i)
    unseen = set(range(n))
    components = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        unseen.remove(seed)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for nxt in sorted(adjacency[current], reverse=True):
                if nxt in unseen:
                    unseen.remove(nxt)
                    stack.append(nxt)
        components.append(sorted(component))
    components.sort(key=lambda comp: (len(comp), [roots[index] for index in comp]))
    return components


def select_simple_roots(component_roots: Sequence[Vector], gram: Matrix) -> list[Vector]:
    dimension = len(component_roots[0])
    functional = None
    selected_base = None
    for base in range(2, 101):
        weights = [base ** i for i in range(dimension)]
        values = [sum(weight * value for weight, value in zip(weights, root))
                  for root in component_roots]
        if all(values):
            functional = values
            selected_base = base
            break
    require(functional is not None and selected_base is not None,
            "failed to choose generic root functional")
    positive = [
        root for root, value in zip(component_roots, functional) if value > 0
    ]
    positive_set = set(positive)
    simple = []
    for root in sorted(positive):
        decomposable = False
        for first in positive:
            second = tuple(a - b for a, b in zip(root, first))
            if second in positive_set:
                decomposable = True
                break
        if not decomposable:
            simple.append(root)
    require(simple, "no simple roots selected")
    simple_gram = [
        [bilinear(left, gram, right) for right in simple]
        for left in simple
    ]
    require(all(simple_gram[i][i] == 2 for i in range(len(simple))), "simple norm")
    require(all(
        simple_gram[i][j] in (0, -1)
        for i in range(len(simple)) for j in range(len(simple)) if i != j
    ), "simple-root off-diagonal Cartan entries")
    return simple


def graph_connected(adjacency: Sequence[set[int]]) -> bool:
    if not adjacency:
        return False
    seen = {0}
    stack = [0]
    while stack:
        current = stack.pop()
        for nxt in adjacency[current]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == len(adjacency)


def classify_cartan(cartan_matrix: Matrix) -> tuple[str, list[int]]:
    rank = len(cartan_matrix)
    adjacency = [set() for _ in range(rank)]
    for i in range(rank):
        require(cartan_matrix[i][i] == 2, "Cartan diagonal")
        for j in range(i + 1, rank):
            value = cartan_matrix[i][j]
            require(value in (0, -1), "Cartan edge value")
            require(cartan_matrix[j][i] == value, "Cartan symmetry")
            if value == -1:
                adjacency[i].add(j)
                adjacency[j].add(i)
    require(graph_connected(adjacency), "Cartan graph disconnected")
    edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    require(edge_count == rank - 1, "Cartan graph is not a tree")
    degrees = [len(neighbors) for neighbors in adjacency]
    if rank == 1 and degrees == [0]:
        return "A1", []
    if max(degrees) <= 2:
        require(sorted(degrees) == [1, 1] + [2] * (rank - 2), "path degrees")
        return f"A{rank}", [rank - 1]
    branch_nodes = [i for i, degree in enumerate(degrees) if degree == 3]
    require(len(branch_nodes) == 1 and max(degrees) == 3, "non-ADE branch graph")
    center = branch_nodes[0]
    arms = []
    for neighbor in sorted(adjacency[center]):
        length = 1
        previous = center
        current = neighbor
        while len(adjacency[current]) == 2:
            nxt = next(vertex for vertex in adjacency[current] if vertex != previous)
            previous, current = current, nxt
            length += 1
        require(len(adjacency[current]) == 1, "arm does not end at leaf")
        arms.append(length)
    arms.sort()
    if arms == [1, 1, rank - 3] and rank >= 4:
        return f"D{rank}", arms
    exceptional = {
        (1, 2, 2): "E6",
        (1, 2, 3): "E7",
        (1, 2, 4): "E8",
    }
    require(tuple(arms) in exceptional, f"unknown ADE arm lengths {arms}")
    return exceptional[tuple(arms)], arms


def independent_row_indices(matrix: Matrix, target_rank: int) -> list[int]:
    chosen: list[int] = []
    current: list[list[Fraction]] = []
    for index, row in enumerate(matrix):
        candidate = current + [row]
        if matrix_rank(candidate) > len(current):
            chosen.append(index)
            current = candidate
            if len(chosen) == target_rank:
                break
    require(len(chosen) == target_rank, "failed to choose independent rows")
    return chosen


def component_analysis(
    roots: Sequence[Vector],
    component_indices: Sequence[int],
    gram: Matrix,
    p_inverse: Matrix,
) -> tuple[dict[str, Any], list[Vector]]:
    component_roots = [roots[index] for index in component_indices]
    simple = select_simple_roots(component_roots, gram)
    simple_matrix = columns_to_matrix(simple)
    rank = matrix_rank(simple_matrix)
    require(rank == len(simple), "dependent simple roots")
    cartan_matrix = matmul(matmul(transpose(simple_matrix), gram), simple_matrix)
    component_type, arm_lengths = classify_cartan(cartan_matrix)

    row_indices = independent_row_indices(simple_matrix, rank)
    square = [[simple_matrix[row][col] for col in range(rank)] for row in row_indices]
    square_inverse = inverse(square)
    max_coefficient = 0
    for root in component_roots:
        rhs = [Fraction(root[row]) for row in row_indices]
        coefficients = matvec(square_inverse, rhs)
        require(all(value.denominator == 1 for value in coefficients),
                "component root not in simple-root lattice")
        require(matvec(simple_matrix, coefficients) == [Fraction(x) for x in root],
                "component span reconstruction")
        max_coefficient = max(
            max_coefficient,
            max((abs(value.numerator) for value in coefficients), default=0),
        )

    simple_p = []
    for root in simple:
        coordinate = matvec(p_inverse, root)
        require(all(value.denominator == 1 for value in coordinate),
                "simple root nonintegral in P basis")
        simple_p.append([value.numerator for value in coordinate])

    result = {
        "type": component_type,
        "root_count": len(component_roots),
        "rank": rank,
        "cartan_determinant": json_scalar(determinant(cartan_matrix)),
        "cartan_hash": canonical_hash(json_matrix(cartan_matrix)),
        "cartan_matrix": json_matrix(cartan_matrix),
        "dynkin_arm_lengths": arm_lengths,
        "simple_roots_P_coordinates": simple_p,
        "all_roots_integrally_generated_by_simple_roots": True,
        "max_abs_simple_coefficient_over_component_roots": max_coefficient,
        "root_hash_original_coordinates": canonical_hash(
            [list(root) for root in sorted(component_roots)]
        ),
    }
    return result, simple


def analyze_roots(
    base: dict[str, Any],
    neighbor: dict[str, Any],
    cached_blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    h_roots, block_summaries = enumerate_h_roots(base, neighbor, cached_blocks)
    half = enumerate_half_coset(base, neighbor)
    require(half["new_roots_in_v_over_2_plus_H"] == 0,
            "unexpected half-coset roots")
    components = connected_components(h_roots, base["S"])
    component_results = []
    all_simple: list[Vector] = []
    for component in components:
        result, simple = component_analysis(
            h_roots, component, base["S"], neighbor["P_inverse"]
        )
        component_results.append(result)
        all_simple.extend(simple)
    component_results.sort(
        key=lambda item: (item["root_count"], item["type"], item["cartan_hash"])
    )
    simple_matrix = columns_to_matrix(all_simple)
    root_span_rank = matrix_rank(simple_matrix)

    roots_p = []
    for root in h_roots:
        coordinate = matvec(neighbor["P_inverse"], root)
        require(all(value.denominator == 1 for value in coordinate),
                "H root not integral in P coordinates")
        roots_p.append([value.numerator for value in coordinate])
    roots_p.sort()

    root_lattice: dict[str, Any] = {
        "rank": root_span_rank,
        "component_cartan_determinant_product": math.prod(
            int(item["cartan_determinant"]) for item in component_results
        ),
        "full_rank": root_span_rank == 44,
        "index_in_neighbor_lattice": None,
        "determinant_if_full_rank": None,
    }
    if root_span_rank == 44:
        require(len(all_simple) == 44, "full rank simple-root count")
        simple_p_matrix = matmul(neighbor["P_inverse"], simple_matrix)
        require(is_integral(simple_p_matrix), "root basis not integral in L'")
        index = abs(determinant(simple_p_matrix))
        root_gram = matmul(matmul(transpose(simple_matrix), base["S"]), simple_matrix)
        root_det = determinant(root_gram)
        require(index.denominator == 1 and root_det.denominator == 1,
                "root lattice determinant data nonintegral")
        require(root_det == Fraction(9) * index * index,
                "root determinant/index relation")
        root_lattice["index_in_neighbor_lattice"] = index.numerator
        root_lattice["determinant_if_full_rank"] = root_det.numerator

    return {
        "H_coset": {
            "root_count": len(h_roots),
            "block_summaries": block_summaries,
        },
        "half_coset": half,
        "total_root_count": len(h_roots),
        "root_hash_P_coordinates": canonical_hash(roots_p),
        "root_span_rank": root_span_rank,
        "component_sizes": sorted(len(component) for component in components),
        "component_types": sorted(item["type"] for item in component_results),
        "components": component_results,
        "root_lattice": root_lattice,
    }


def gcd_entries(values: Sequence[int]) -> int:
    result = 0
    for value in values:
        result = math.gcd(result, abs(value))
    return result


def preferred_glue_dictionary(
    roots: dict[str, Any],
    forms: dict[str, Matrix],
    neighbor: dict[str, Any],
) -> dict[str, Any]:
    """Verify the rank-one complement and H0/H1 indices from first principles."""

    require(roots["root_span_rank"] == 43, "glue dictionary needs root rank 43")
    s_prime = forms["S_prime"]
    z_original = PREFERRED_ORTHOGONAL_LINE
    require(len(z_original) == 44, "orthogonal line dimension")
    z_p_fraction = matvec(neighbor["P_inverse"], z_original)
    require(all(value.denominator == 1 for value in z_p_fraction),
            "orthogonal line not in neighbor lattice")
    z_p = tuple(value.numerator for value in z_p_fraction)
    require(gcd_entries(z_p) == 1, "orthogonal line generator not primitive")
    z_norm = quadratic(z_p, s_prime)
    require(z_norm == 12, "orthogonal line norm")

    root_simple_columns = [
        tuple(vector)
        for component in roots["components"]
        for vector in component["simple_roots_P_coordinates"]
    ]
    require(len(root_simple_columns) == 43, "preferred simple-root count")
    require(all(
        bilinear(z_p, s_prime, root) == 0 for root in root_simple_columns
    ), "proposed line is not root-orthogonal")
    root_simple_matrix = columns_to_matrix(root_simple_columns)
    require(matrix_rank(root_simple_matrix) == 43, "preferred root basis rank")

    pairing_fraction = matvec(s_prime, z_p)
    require(all(value.denominator == 1 for value in pairing_fraction),
            "orthogonal line pairings nonintegral")
    pairing = tuple(value.numerator for value in pairing_fraction)
    divisibility = gcd_entries(pairing)
    require(divisibility == 3, "orthogonal line divisibility")
    primitive_row = tuple(value // divisibility for value in pairing)
    pivot = next((i for i, value in enumerate(primitive_row) if abs(value) == 1), None)
    require(pivot is not None, "primitive pairing row lacks deterministic unit pivot")

    rbar_columns: list[list[Fraction]] = []
    for index in range(44):
        if index == pivot:
            continue
        column = [Fraction() for _ in range(44)]
        column[index] = Fraction(1)
        column[pivot] = Fraction(-primitive_row[index], primitive_row[pivot])
        require(vecdot(primitive_row, column) == 0, "Rbar kernel column")
        rbar_columns.append(column)
    rbar_basis = columns_to_matrix(rbar_columns)
    require(matrix_rank(rbar_basis) == 43, "Rbar basis rank")
    rbar_gram = matmul(matmul(transpose(rbar_basis), s_prime), rbar_basis)
    require(is_even_integral_form(rbar_gram), "Rbar even integral")
    require(is_positive_definite(rbar_gram), "Rbar positive definite")
    rbar_det = determinant(rbar_gram)
    require(rbar_det == 12, "Rbar determinant")

    # Express the complete simple-root basis in the saturated kernel Rbar.
    independent_rows = independent_row_indices(rbar_basis, 43)
    rbar_square = [
        [rbar_basis[row][col] for col in range(43)]
        for row in independent_rows
    ]
    root_square = [
        [root_simple_matrix[row][col] for col in range(43)]
        for row in independent_rows
    ]
    root_in_rbar = matmul(inverse(rbar_square), root_square)
    require(is_integral(root_in_rbar), "root lattice not integral in Rbar")
    require(matmul(rbar_basis, root_in_rbar) == root_simple_matrix,
            "root/Rbar coordinate reconstruction")
    h0_order = abs(determinant(root_in_rbar))
    require(h0_order == 32, "H0 order")

    root_gram = matmul(
        matmul(transpose(root_simple_matrix), s_prime), root_simple_matrix
    )
    root_det = determinant(root_gram)
    require(root_det == 12288, "preferred root lattice determinant")
    require(root_det == rbar_det * h0_order * h0_order,
            "Rbar/R determinant-index relation")

    direct_rbar = columns_to_matrix([list(map(F, z_p))] + rbar_columns)
    h1_order = abs(determinant(direct_rbar))
    require(h1_order == 4, "H1 order")
    require(
        matmul(transpose(columns_to_matrix([z_p])), matmul(s_prime, rbar_basis))
        == [[Fraction() for _ in range(43)]],
        "K and Rbar are not orthogonal",
    )

    direct_root = columns_to_matrix(
        [list(map(F, z_p))]
        + [[F(value) for value in column] for column in root_simple_columns]
    )
    total_glue_index = abs(determinant(direct_root))
    require(total_glue_index == 128, "total glue index")
    require(total_glue_index == h0_order * h1_order, "glue index factorization")
    require(
        (root_det * z_norm) / (h0_order * h0_order * h1_order * h1_order) == 9,
        "H0/H1 determinant dictionary",
    )

    encoded_rbar_basis = json_matrix(rbar_basis)
    encoded_rbar_gram = json_matrix(rbar_gram)
    encoded_root_basis = json_matrix(root_simple_matrix)
    return {
        "notation": {
            "R": "lattice generated by all norm-two vectors",
            "Rbar": "(R tensor Q) intersect L_prime",
            "K": "Rbar_perp intersect L_prime",
            "H0": "Rbar/R",
            "H1": "L_prime/(Rbar orthogonal_sum K)",
        },
        "z_original_coordinates": list(z_original),
        "z_P_coordinates": list(z_p),
        "z_primitive_in_L_prime": True,
        "z_norm": z_norm.numerator,
        "z_pairing_vector_P_coordinates": list(pairing),
        "z_divisibility_in_L_prime": divisibility,
        "K": {
            "rank": 1,
            "gram": [z_norm.numerator],
            "determinant": z_norm.numerator,
            "rootless": True,
            "rootless_reason": "every nonzero vector is m*z and has norm 12*m^2",
        },
        "R": {
            "rank": 43,
            "determinant": root_det.numerator,
            "basis_P_coordinates": encoded_root_basis,
            "basis_hash": canonical_hash(encoded_root_basis),
        },
        "Rbar": {
            "rank": 43,
            "determinant": rbar_det.numerator,
            "kernel_pairing_pivot": pivot,
            "basis_P_coordinates": encoded_rbar_basis,
            "basis_hash": canonical_hash(encoded_rbar_basis),
            "gram": encoded_rbar_gram,
            "gram_hash": canonical_hash(encoded_rbar_gram),
            "saturated_exact_kernel": True,
        },
        "H0_order_Rbar_over_R": h0_order.numerator,
        "H1_order_L_over_Rbar_plus_K": h1_order.numerator,
        "total_index_L_over_K_plus_R": total_glue_index.numerator,
        "determinant_identity": {
            "det_L_prime": 9,
            "formula": "det(R)*det(K)/(|H0|^2*|H1|^2)",
            "evaluated": 9,
        },
        "complete_root_census_excludes_new_norm_two_H0_cosets": True,
    }


def analyze_support(
    name: str,
    support: Sequence[int],
    base: dict[str, Any],
    cached_blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    neighbor = construct_neighbor_basis(base["S"], support)
    forms = transform_forms(base, neighbor)
    invariants = transformed_invariants(forms)

    v = neighbor["v"]
    a = neighbor["a"]
    simultaneous = {
        "v_S_v": json_scalar(quadratic(v, base["S"])),
        "a_Q_a": json_scalar(quadratic(a, base["Q"])),
        "a_G_a": json_scalar(quadratic(a, base["G"])),
    }
    require(simultaneous == {"v_S_v": 16, "a_Q_a": 16, "a_G_a": 336},
            f"{name} simultaneous neighbor norms")

    roots = analyze_roots(base, neighbor, cached_blocks)
    glue_dictionary = None
    component_screen_cross_control = None
    if name == "preferred_all_six_blocks":
        glue_dictionary = preferred_glue_dictionary(roots, forms, neighbor)
        forbidden = {"A2", "A6", "E6", "A20"}
        present = set(roots["component_types"])
        require(present.isdisjoint(forbidden), "preferred forbidden component")
        component_screen_cross_control = {
            "absent_orthogonal_component_types": sorted(forbidden),
            "checked_component_types": roots["component_types"],
            "evades_existing_component_screens": True,
            "scope": (
                "abstract transformed S,Q,G,B,C package only; no projector-frame "
                "or Schur-square compatibility follows"
            ),
        }
    encoded_forms = {
        key: json_matrix(value) for key, value in forms.items()
    }
    matrix_hashes = {
        key: canonical_hash(value) for key, value in encoded_forms.items()
    }
    encoded_p = json_matrix(neighbor["P"])
    encoded_p_inverse = json_matrix(neighbor["P_inverse"])
    return {
        "name": name,
        "support": list(support),
        "simultaneous_neighbor_norms": simultaneous,
        "basis": {
            "parity_pivot": neighbor["pivot"],
            "replacement_column": neighbor["replacement"],
            "det_H_basis": json_scalar(determinant(neighbor["H_basis"])),
            "det_P": json_scalar(neighbor["det_P"]),
            "P": encoded_p,
            "P_hash": canonical_hash(encoded_p),
            "P_inverse": encoded_p_inverse,
            "P_inverse_hash": canonical_hash(encoded_p_inverse),
            "inverse_reconstructed_by_fraction_gauss_jordan": True,
        },
        "invariants": invariants,
        "matrices": encoded_forms,
        "matrix_hashes": matrix_hashes,
        "roots": roots,
        "preferred_glue_dictionary": glue_dictionary,
        "orthogonal_component_screen_cross_control": component_screen_cross_control,
    }


def verify_expected_root_profiles(results: dict[str, Any]) -> None:
    preferred = results["supports"]["preferred_all_six_blocks"]["roots"]
    require(preferred["total_root_count"] == 568, "preferred root count")
    require(preferred["root_span_rank"] == 43, "preferred root rank")
    require(
        preferred["component_sizes"] == [2, 2, 2, 2, 30, 40, 112, 126, 126, 126],
        "preferred component sizes",
    )
    require(
        preferred["component_types"]
        == ["A1", "A1", "A1", "A1", "A5", "D5", "D8", "E7", "E7", "E7"],
        "preferred component types",
    )
    require(not preferred["root_lattice"]["full_rank"], "preferred roots full rank")
    glue = results["supports"]["preferred_all_six_blocks"][
        "preferred_glue_dictionary"
    ]
    require(glue["z_norm"] == 12, "preferred K norm")
    require(glue["z_divisibility_in_L_prime"] == 3, "preferred K divisibility")
    require(glue["R"]["determinant"] == 12288, "preferred R determinant")
    require(glue["Rbar"]["determinant"] == 12, "preferred Rbar determinant")
    require(glue["H0_order_Rbar_over_R"] == 32, "preferred H0")
    require(glue["H1_order_L_over_Rbar_plus_K"] == 4, "preferred H1")
    require(glue["total_index_L_over_K_plus_R"] == 128, "preferred total glue")

    initial = results["supports"]["initial_index_32_cross_control"]["roots"]
    require(initial["total_root_count"] == 568, "initial root count")
    require(initial["root_span_rank"] == 44, "initial root rank")
    require(
        initial["component_sizes"] == [2, 2, 30, 72, 112, 112, 112, 126],
        "initial component sizes",
    )
    require(
        initial["component_types"]
        == ["A1", "A1", "A5", "D8", "D8", "D8", "E6", "E7"],
        "initial component types",
    )
    require(
        initial["root_lattice"]["determinant_if_full_rank"] == 9216,
        "initial root determinant",
    )
    require(
        initial["root_lattice"]["index_in_neighbor_lattice"] == 32,
        "initial root index",
    )


def input_metadata() -> dict[str, Any]:
    paths = [FREEZE_PATH, BRIEF_PATH, WAVE27_SOURCE_PATH]
    actual = {}
    for path in paths:
        relative = path.relative_to(REPO_ROOT).as_posix()
        actual[relative] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        require(
            actual[relative]["sha256"] == EXPECTED_INPUT_HASHES[relative],
            f"input hash drift: {relative}",
        )
    return actual


def build_results() -> dict[str, Any]:
    inputs = input_metadata()
    base = reconstruct_wave27()
    cached_blocks = block_root_data(base)
    supports = {
        "preferred_all_six_blocks": analyze_support(
            "preferred_all_six_blocks", PREFERRED_SUPPORT, base, cached_blocks
        ),
        "initial_index_32_cross_control": analyze_support(
            "initial_index_32_cross_control", INITIAL_SUPPORT, base, cached_blocks
        ),
    }
    results = {
        "schema": "wave28-simultaneous-neighbor-independent-v1",
        "role": "verifier",
        "inputs": inputs,
        "method": {
            "wave27_reconstruction": (
                "Cartan edge lists, exact Fraction inversion, rank-one E6 extension"
            ),
            "neighbor_basis": (
                "deterministic parity-kernel basis; replace a primitive H column "
                "by v/2; compute inverse independently"
            ),
            "root_enumeration": (
                "H roots by complete block norm-two enumeration; half coset by "
                "complete six-block parity-constrained norm-eight LDL enumeration"
            ),
            "component_identification": (
                "generic positive system, indecomposable simple roots, checked "
                "Cartan graph/rank/determinant, integral generation of all roots"
            ),
        },
        "supports": supports,
        "direct_44d_timeout": {
            "reported_elapsed_seconds": 124,
            "source": "frozen orchestrator candidate report",
            "replayed": False,
            "evidentiary": False,
            "reason": "replaced by complete exact six-block coset enumeration",
        },
        "status_wall": {
            "scoped_hostile_controls": "VERIFIED_BY_THIS_INDEPENDENT_CHECK",
            "primitive_Z231_embedding": "NOT_CONSTRUCTED",
            "projector_frame": "NOT_CONSTRUCTED",
            "required_M_entry_alphabet_and_profiles": "NOT_CONSTRUCTED",
            "Schur_square_origin": "NOT_CONSTRUCTED",
            "graph": "NOT_CONSTRUCTED",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }
    verify_expected_root_profiles(results)
    return results


def write_results(path: Path, results: dict[str, Any]) -> None:
    text = json.dumps(results, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = build_results()
    write_results(args.output, results)
    summary = {
        key: {
            "roots": value["roots"]["total_root_count"],
            "rank": value["roots"]["root_span_rank"],
            "components": value["roots"]["component_types"],
            "half_coset_roots": value["roots"]["half_coset"][
                "new_roots_in_v_over_2_plus_H"
            ],
        }
        for key, value in results["supports"].items()
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
