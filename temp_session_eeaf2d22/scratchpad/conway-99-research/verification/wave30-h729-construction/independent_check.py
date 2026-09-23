#!/usr/bin/env python3
"""Blind exact verifier for the Wave 30 bare h729 lattice construction.

This module deliberately does not import or execute the discovery checker.
All linear algebra, exact LDL decomposition, lattice-index checks, and bounded
enumeration are implemented here with Python integers and fractions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION_PATH = ROOT / "attempts" / "wave30-h729-construction" / "exact-results.json"
REPORT_PATH = ROOT / "agents" / "2026-07-24-wave30-h729-construction.md"

EXPECTED_SUBMISSION_SHA256 = (
    "0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11"
)
EXPECTED_REPORT_SHA256 = (
    "479ed105825ea2b2a0802c34fcc332b8dc1420b27966bec41053702f3212451f"
)


class VerificationError(RuntimeError):
    """A fail-closed verification error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise VerificationError("boolean is not a rational matrix entry")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        pieces = value.split("/")
        if len(pieces) == 1:
            try:
                return Fraction(int(pieces[0]))
            except ValueError as exc:
                raise VerificationError(f"invalid integer entry {value!r}") from exc
        if len(pieces) == 2:
            try:
                numerator = int(pieces[0])
                denominator = int(pieces[1])
            except ValueError as exc:
                raise VerificationError(f"invalid rational entry {value!r}") from exc
            require(denominator != 0, "zero rational denominator")
            return Fraction(numerator, denominator)
    raise VerificationError(f"unsupported rational entry {value!r}")


def qmatrix(raw: Any, name: str) -> list[list[Fraction]]:
    require(isinstance(raw, list) and raw, f"{name}: matrix must be a nonempty list")
    require(all(isinstance(row, list) for row in raw), f"{name}: rows must be lists")
    width = len(raw[0])
    require(width > 0, f"{name}: matrix must have positive width")
    require(all(len(row) == width for row in raw), f"{name}: ragged matrix")
    return [[parse_fraction(value) for value in row] for row in raw]


def nrows(matrix: Sequence[Sequence[Any]]) -> int:
    return len(matrix)


def ncols(matrix: Sequence[Sequence[Any]]) -> int:
    return len(matrix[0]) if matrix else 0


def require_square(matrix: Sequence[Sequence[Any]], name: str) -> int:
    require(matrix and all(len(row) == len(matrix) for row in matrix), f"{name}: not square")
    return len(matrix)


def transpose(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(1 if row == col else 0) for col in range(size)]
        for row in range(size)
    ]


def matmul(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> list[list[Fraction]]:
    require(ncols(left) == nrows(right), "matrix multiplication dimension mismatch")
    right_t = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, col)), Fraction(0)) for col in right_t]
        for row in left
    ]


def matvec(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> list[Fraction]:
    require(ncols(matrix) == len(vector), "matrix-vector dimension mismatch")
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def scale_matrix(
    scalar: Fraction, matrix: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    return [[scalar * entry for entry in row] for row in matrix]


def block_diagonal(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    rows_left, rows_right = nrows(left), nrows(right)
    cols_left, cols_right = ncols(left), ncols(right)
    require(rows_left == cols_left and rows_right == cols_right, "blocks must be square")
    zero_left = [Fraction(0)] * cols_right
    zero_right = [Fraction(0)] * cols_left
    return (
        [list(row) + zero_left for row in left]
        + [zero_right + list(row) for row in right]
    )


def qform(matrix: Sequence[Sequence[Fraction]], vector: Sequence[int]) -> Fraction:
    qvector = [Fraction(value) for value in vector]
    image = matvec(matrix, qvector)
    return sum((value * mapped for value, mapped in zip(qvector, image)), Fraction(0))


def integer_matrix(
    matrix: Sequence[Sequence[Fraction]], name: str
) -> list[list[int]]:
    require(
        all(entry.denominator == 1 for row in matrix for entry in row),
        f"{name}: matrix is not integral",
    )
    return [[entry.numerator for entry in row] for row in matrix]


def det_bareiss(integer: Sequence[Sequence[int]]) -> int:
    size = require_square(integer, "Bareiss input")
    if size == 1:
        return int(integer[0][0])
    work = [[int(entry) for entry in row] for row in integer]
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        pivot_row = next(
            (row for row in range(pivot_index, size) if work[row][pivot_index] != 0),
            None,
        )
        if pivot_row is None:
            return 0
        if pivot_row != pivot_index:
            work[pivot_index], work[pivot_row] = work[pivot_row], work[pivot_index]
            sign = -sign
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for col in range(pivot_index + 1, size):
                numerator = (
                    work[row][col] * pivot
                    - work[row][pivot_index] * work[pivot_index][col]
                )
                require(
                    numerator % previous == 0,
                    "Bareiss exact-division invariant failed",
                )
                work[row][col] = numerator // previous
            work[row][pivot_index] = 0
        previous = pivot
    return sign * work[size - 1][size - 1]


def det_fraction(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    size = require_square(matrix, "determinant input")
    work = [list(row) for row in matrix]
    determinant = Fraction(1)
    sign = 1
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        pivot_value = work[col][col]
        determinant *= pivot_value
        for row in range(col + 1, size):
            factor = work[row][col] / pivot_value
            if not factor:
                continue
            for index in range(col + 1, size):
                work[row][index] -= factor * work[col][index]
            work[row][col] = Fraction(0)
    return determinant * sign


def inverse(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    size = require_square(matrix, "inverse input")
    work = [list(row) + identity(size)[index] for index, row in enumerate(matrix)]
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col]), None)
        require(pivot is not None, "singular matrix")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [entry / pivot_value for entry in work[col]]
        for row in range(size):
            if row == col:
                continue
            factor = work[row][col]
            if not factor:
                continue
            work[row] = [
                entry - factor * source
                for entry, source in zip(work[row], work[col])
            ]
    result = [row[size:] for row in work]
    require(matmul(matrix, result) == identity(size), "left inverse check failed")
    require(matmul(result, matrix) == identity(size), "right inverse check failed")
    return result


def ldlt(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[list[list[Fraction]], list[Fraction]]:
    size = require_square(matrix, "LDL input")
    require(matrix == transpose(matrix), "LDL input is not symmetric")
    lower = identity(size)
    diagonal = [Fraction(0)] * size
    for col in range(size):
        diagonal[col] = matrix[col][col] - sum(
            (
                lower[col][prior] * lower[col][prior] * diagonal[prior]
                for prior in range(col)
            ),
            Fraction(0),
        )
        require(diagonal[col] != 0, f"zero LDL pivot at {col}")
        for row in range(col + 1, size):
            numerator = matrix[row][col] - sum(
                (
                    lower[row][prior]
                    * lower[col][prior]
                    * diagonal[prior]
                    for prior in range(col)
                ),
                Fraction(0),
            )
            lower[row][col] = numerator / diagonal[col]
    reconstructed = matmul(matmul(lower, [
        [
            diagonal[row] if row == col else Fraction(0)
            for col in range(size)
        ]
        for row in range(size)
    ]), transpose(lower))
    require(reconstructed == [list(row) for row in matrix], "LDL reconstruction failed")
    return lower, diagonal


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def canonical_entry(value: Fraction) -> int | str:
    if value.denominator == 1:
        return value.numerator
    return fraction_text(value)


def canonical_matrix(matrix: Sequence[Sequence[Fraction]]) -> list[list[int | str]]:
    return [[canonical_entry(entry) for entry in row] for row in matrix]


def matrix_sha256(matrix: Sequence[Sequence[Fraction]]) -> str:
    payload = json.dumps(
        canonical_matrix(matrix),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_bytes(payload)


def leading_principal_determinants(matrix: Sequence[Sequence[Fraction]]) -> list[int]:
    integer = integer_matrix(matrix, "Sylvester matrix")
    determinants = [
        det_bareiss([row[:size] for row in integer[:size]])
        for size in range(1, len(integer) + 1)
    ]
    return determinants


def check_gram(
    matrix: Sequence[Sequence[Fraction]],
    name: str,
    expected_rank: int | None = None,
    expected_determinant: int | None = None,
) -> dict[str, Any]:
    size = require_square(matrix, name)
    if expected_rank is not None:
        require(size == expected_rank, f"{name}: rank mismatch")
    require(matrix == transpose(matrix), f"{name}: nonsymmetric")
    integer = integer_matrix(matrix, name)
    require(all(integer[index][index] % 2 == 0 for index in range(size)), f"{name}: odd")
    lower, pivots = ldlt(matrix)
    require(all(pivot > 0 for pivot in pivots), f"{name}: not positive definite")
    sylvester = leading_principal_determinants(matrix)
    require(all(value > 0 for value in sylvester), f"{name}: Sylvester failure")
    pivot_products: list[Fraction] = []
    product = Fraction(1)
    for pivot in pivots:
        product *= pivot
        pivot_products.append(product)
    require(
        all(value.denominator == 1 for value in pivot_products),
        f"{name}: nonintegral leading determinant from LDL",
    )
    require(
        [value.numerator for value in pivot_products] == sylvester,
        f"{name}: LDL/Sylvester disagreement",
    )
    determinant = det_bareiss(integer)
    require(determinant == sylvester[-1], f"{name}: determinant disagreement")
    if expected_determinant is not None:
        require(determinant == expected_determinant, f"{name}: determinant mismatch")
    del lower
    return {
        "rank": size,
        "symmetric": True,
        "integral": True,
        "even_diagonal": True,
        "positive_definite_exact_ldlt": True,
        "positive_definite_exact_sylvester": True,
        "determinant": determinant,
        "ldl_pivots": [fraction_text(value) for value in pivots],
        "leading_principal_determinants": [str(value) for value in sylvester],
        "matrix_sha256": matrix_sha256(matrix),
    }


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_div(numerator: int, denominator: int) -> int:
    require(denominator > 0, "ceil_div requires positive denominator")
    return -((-numerator) // denominator)


def vector_set_sha256(vectors: Iterable[Sequence[int]]) -> str:
    ordered = [list(vector) for vector in sorted(tuple(vector) for vector in vectors)]
    payload = json.dumps(
        ordered,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_bytes(payload)


def enumerate_short_vectors(
    matrix: Sequence[Sequence[Fraction]],
    cap: int,
) -> dict[str, Any]:
    """Enumerate every integral coordinate vector with x^T G x <= cap.

    Exact LDL bounds are used.  At level i, after fixing x_j for j>i, the
    inequality is reduced to

        (b*x_i-a)^2 <= floor(b^2 * remaining / d_i),

    so both endpoints are computed with integer square roots.  There are no
    floating-point bounds or heuristic coordinate boxes.
    """

    require(cap >= 0, "negative enumeration cap")
    size = require_square(matrix, "enumeration matrix")
    lower, diagonal = ldlt(matrix)
    require(all(value > 0 for value in diagonal), "enumeration requires positive definite")
    vector = [0] * size
    by_norm: dict[int, list[tuple[int, ...]]] = {}
    nodes_by_level = [0] * size
    accepted_partial_nodes = 0

    def recurse(index: int, partial: Fraction) -> None:
        nonlocal accepted_partial_nodes
        if index < 0:
            require(partial.denominator == 1, "integral Gram produced fractional norm")
            norm = partial.numerator
            require(norm <= cap, "enumeration admitted vector above cap")
            by_norm.setdefault(norm, []).append(tuple(vector))
            return
        nodes_by_level[index] += 1
        remaining = Fraction(cap) - partial
        if remaining < 0:
            return
        shift = sum(
            (lower[row][index] * vector[row] for row in range(index + 1, size)),
            Fraction(0),
        )
        center = -shift
        denominator = center.denominator
        numerator = center.numerator
        squared_limit = (remaining / diagonal[index]) * denominator * denominator
        max_integer_offset = math.isqrt(floor_fraction(squared_limit))
        low = ceil_div(numerator - max_integer_offset, denominator)
        high = (numerator + max_integer_offset) // denominator
        for coordinate in range(low, high + 1):
            term = diagonal[index] * (Fraction(coordinate) + shift) ** 2
            next_partial = partial + term
            if next_partial <= cap:
                accepted_partial_nodes += 1
                vector[index] = coordinate
                recurse(index - 1, next_partial)
        vector[index] = 0

    recurse(size - 1, Fraction(0))
    counts = {str(norm): len(vectors) for norm, vectors in sorted(by_norm.items())}
    vector_hashes = {
        str(norm): vector_set_sha256(vectors)
        for norm, vectors in sorted(by_norm.items())
        if norm != 0
    }
    for norm, vectors in by_norm.items():
        vector_set = set(vectors)
        require(
            all(tuple(-entry for entry in vector) in vector_set for vector in vectors),
            f"shell {norm}: negation closure failed",
        )
        require(
            all(qform(matrix, vector) == norm for vector in vectors),
            f"shell {norm}: direct quadratic recheck failed",
        )
    maximum_coordinate = max(
        (
            abs(entry)
            for vectors in by_norm.values()
            for vector_value in vectors
            for entry in vector_value
        ),
        default=0,
    )
    return {
        "cap": cap,
        "dimension": size,
        "bound_method": "exact rational LDL with integer-square-root endpoints",
        "floating_point_used": False,
        "counts": counts,
        "vector_hashes": vector_hashes,
        "complete_vector_count": sum(counts.values()),
        "accepted_partial_nodes": accepted_partial_nodes,
        "nodes_by_level": nodes_by_level,
        "max_abs_coordinate": maximum_coordinate,
        "_vectors": by_norm,
    }


def public_enumeration(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "_vectors"}


def is_integral(matrix: Sequence[Sequence[Fraction]]) -> bool:
    return all(entry.denominator == 1 for row in matrix for entry in row)


def is_even_integral(matrix: Sequence[Sequence[Fraction]]) -> bool:
    return is_integral(matrix) and all(
        matrix[index][index].numerator % 2 == 0 for index in range(len(matrix))
    )


def determinant_is_unit(matrix: Sequence[Sequence[Fraction]]) -> bool:
    return abs(det_fraction(matrix)) == 1


def standard_neighbor_kernel_basis(
    pairing: Sequence[int], pivot: int
) -> list[list[Fraction]]:
    size = len(pairing)
    require(0 <= pivot < size, "parity pivot outside range")
    require(pairing[pivot] % 2 != 0, "parity pivot does not have odd pairing")
    basis = identity(size)
    for row in range(size):
        basis[row][pivot] = Fraction(0)
    basis[pivot][pivot] = Fraction(2)
    for col in range(size):
        if col == pivot:
            continue
        basis[pivot][col] = Fraction(-(pairing[col] & 1))
    return basis


def verify_neighbor_step(
    previous: Sequence[Sequence[Fraction]],
    following: Sequence[Sequence[Fraction]],
    raw_entry: dict[str, Any],
) -> dict[str, Any]:
    size = require_square(previous, "previous neighbor Gram")
    require_square(following, "following neighbor Gram")
    support_raw = raw_entry.get("support_in_previous_reduced_basis")
    require(isinstance(support_raw, list) and support_raw, "missing/empty support")
    support = [int(value) for value in support_raw]
    require(support == sorted(set(support)), "support is not strictly unique/sorted")
    require(all(0 <= index < size for index in support), "support outside range")
    vector = [1 if index in support else 0 for index in range(size)]
    require(math.gcd(*vector) == 1, "neighbor vector is not primitive")
    norm = qform(previous, vector)
    require(norm.denominator == 1, "neighbor norm is nonintegral")
    require(norm.numerator == int(raw_entry["neighbor_vector_norm"]), "neighbor norm mismatch")
    require(norm.numerator % 8 == 0, "neighbor norm is not divisible by eight")

    pairing_q = matvec(previous, [Fraction(value) for value in vector])
    require(all(value.denominator == 1 for value in pairing_q), "nonintegral pairing")
    pairing = [value.numerator for value in pairing_q]
    require(any(value % 2 for value in pairing), "neighbor parity functional is zero")
    pivot = int(raw_entry["parity_pivot"])
    require(0 <= pivot < size and pairing[pivot] % 2, "invalid parity pivot")

    basis_p = qmatrix(raw_entry["neighbor_basis_P"], "neighbor P")
    submitted_p_inverse = qmatrix(raw_entry["neighbor_basis_P_inverse"], "neighbor P inverse")
    require(nrows(basis_p) == size and ncols(basis_p) == size, "P dimension mismatch")
    computed_p_inverse = inverse(basis_p)
    require(submitted_p_inverse == computed_p_inverse, "submitted P inverse mismatch")
    require(abs(det_fraction(basis_p)) == 1, "neighbor P does not have covolume one")
    require(int(raw_entry["det_P"]) == det_fraction(basis_p), "submitted det(P) mismatch")
    require(
        all(entry.denominator in (1, 2) for row in basis_p for entry in row),
        "P has denominator other than two",
    )
    half_col = int(raw_entry["half_vector_replacement_column"])
    require(0 <= half_col < size, "half-vector column outside range")
    require(
        [basis_p[row][half_col] for row in range(size)]
        == [Fraction(value, 2) for value in vector],
        "P half-vector column is not v/2",
    )

    kernel_basis = standard_neighbor_kernel_basis(pairing, pivot)
    kernel_det = abs(det_fraction(kernel_basis))
    require(kernel_det == 2, "parity-kernel basis does not have index two")
    kernel_inverse = inverse(kernel_basis)
    for col in range(size):
        column = [kernel_basis[row][col] for row in range(size)]
        paired = sum(
            (Fraction(value) * entry for value, entry in zip(pairing, column)),
            Fraction(0),
        )
        require(paired.denominator == 1 and paired.numerator % 2 == 0, "kernel basis parity")
    coordinates_in_p = matmul(computed_p_inverse, kernel_basis)
    require(is_integral(coordinates_in_p), "parity kernel is not contained in P lattice")
    vector_coordinates_in_kernel = matvec(
        kernel_inverse, [Fraction(value) for value in vector]
    )
    require(
        all(value.denominator == 1 for value in vector_coordinates_in_kernel),
        "v is not in parity kernel",
    )
    half_coordinates_in_kernel = [
        value / 2 for value in vector_coordinates_in_kernel
    ]
    require(
        any(value.denominator != 1 for value in half_coordinates_in_kernel),
        "v/2 unexpectedly lies in parity kernel",
    )

    raw_neighbor = matmul(matmul(transpose(basis_p), previous), basis_p)
    raw_check = check_gram(raw_neighbor, "raw neighbor", size, None)
    transform_u = qmatrix(raw_entry["exact_lll_row_transform_U"], "submitted U")
    require(nrows(transform_u) == size and ncols(transform_u) == size, "U dimension mismatch")
    require(is_integral(transform_u), "U is not integral")
    require(determinant_is_unit(transform_u), "U is not unimodular")
    reduced_neighbor = matmul(matmul(transform_u, raw_neighbor), transpose(transform_u))
    require(reduced_neighbor == [list(row) for row in following], "neighbor transition mismatch")
    require(
        raw_check["determinant"]
        == det_bareiss(integer_matrix(previous, "previous Gram")),
        "neighbor determinant changed",
    )
    require(matrix_sha256(raw_neighbor) == raw_entry["raw_neighbor_gram_sha256"], "raw hash mismatch")
    require(
        matrix_sha256(reduced_neighbor) == raw_entry["reduced_gram_sha256"],
        "reduced hash mismatch",
    )
    return {
        "step": int(raw_entry["step"]),
        "support": support,
        "primitive_neighbor_vector": True,
        "neighbor_vector_norm": norm.numerator,
        "norm_divisible_by_8": True,
        "parity_pivot": pivot,
        "parity_functional_nonzero": True,
        "common_kernel_full_rank": True,
        "index_previous_over_common": 2,
        "index_neighbor_over_common": 2,
        "p_determinant": fraction_text(det_fraction(basis_p)),
        "u_determinant": fraction_text(det_fraction(transform_u)),
        "p_inverse_reproduced": True,
        "raw_neighbor_even_integral_positive_definite": True,
        "raw_neighbor_sha256": matrix_sha256(raw_neighbor),
        "reduced_neighbor_sha256": matrix_sha256(reduced_neighbor),
        "_raw_neighbor": raw_neighbor,
    }


def reconstruct_chain(
    final_gram: Sequence[Sequence[Fraction]],
    raw_entries: list[dict[str, Any]],
) -> list[list[list[Fraction]]]:
    require(len(raw_entries) == 5, "expected exactly five neighbor steps")
    chain: list[list[list[Fraction]] | None] = [None] * 6
    chain[5] = [list(row) for row in final_gram]
    current = chain[5]
    for position in range(4, -1, -1):
        entry = raw_entries[position]
        basis_p = qmatrix(entry["neighbor_basis_P"], f"P step {position + 1}")
        transform_u = qmatrix(entry["exact_lll_row_transform_U"], f"U step {position + 1}")
        p_inverse = inverse(basis_p)
        u_inverse = inverse(transform_u)
        raw_neighbor = matmul(matmul(u_inverse, current), transpose(u_inverse))
        previous = matmul(matmul(transpose(p_inverse), raw_neighbor), p_inverse)
        require(is_integral(previous), f"step {position + 1}: reconstructed prior not integral")
        chain[position] = previous
        current = previous
    return [value for value in chain if value is not None]


def unimodular_attack_matrix(size: int) -> list[list[Fraction]]:
    transform = identity(size)
    transform[0][1] = Fraction(1)
    transform[2][0] = Fraction(-1)
    for index in range(size):
        if index % 3 == 1:
            transform[index][index] = Fraction(-1)
    require(determinant_is_unit(transform), "internal attack matrix is not unimodular")
    return transform


def changed_basis_gram(
    gram: Sequence[Sequence[Fraction]], transform: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    return matmul(matmul(transpose(transform), gram), transform)


def verify_scope(submission: dict[str, Any]) -> dict[str, Any]:
    candidate = submission["rank44_candidate"]
    not_constructed = " ".join(str(value) for value in candidate["not_constructed"])
    required_disclaimers = (
        "determinant-five Q",
        "B=S*Q",
        "tight frame",
        "complete 231-row X",
        "M=X*S*X^T",
        "Q=X^T*(M o M)*X",
        "graph",
    )
    require(
        all(term.lower() in not_constructed.lower() for term in required_disclaimers),
        "scope omissions",
    )
    require(
        not any(key in candidate for key in ("Q", "B", "X", "M", "W", "Schur")),
        "candidate unexpectedly embeds a downstream certificate",
    )
    global_status = str(submission["restrictions"]["global_status"])
    require(
        "neither realizes nor excludes n3=708" in global_status
        and "does not resolve Conway-99" in global_status,
        "global nonresolution disclaimer is missing",
    )
    require(
        "No subset" in str(submission["restrictions"]["frame_status"])
        and "is supplied" in str(submission["restrictions"]["frame_status"]),
        "frame nonconstruction disclaimer is missing",
    )
    return {
        "bare_S_G_only": True,
        "no_Q_B_X_M_W_frame_Schur_graph_certificate": True,
        "n3_708_status": "UNKNOWN",
        "conway_99_graph_status": "UNKNOWN",
    }


def verify_dual(
    gram: Sequence[Sequence[Fraction]],
    scale: int,
    submitted: Sequence[Sequence[Fraction]] | None = None,
) -> tuple[list[list[Fraction]], dict[str, Any]]:
    gram_inverse = inverse(gram)
    scaled = scale_matrix(Fraction(scale), gram_inverse)
    require(is_even_integral(scaled), f"{scale}*inverse is not even integral")
    if submitted is not None:
        require(scaled == [list(row) for row in submitted], f"submitted {scale}*inverse mismatch")
    return scaled, {
        "scale": scale,
        "integral": True,
        "even_diagonal": True,
        "matrix_sha256": matrix_sha256(scaled),
    }


def extract_direct_sum_leech(
    submitted_s: Sequence[Sequence[Fraction]],
    final_gram: Sequence[Sequence[Fraction]],
) -> list[list[Fraction]]:
    require(nrows(submitted_s) == 44 and ncols(submitted_s) == 44, "S dimension mismatch")
    require(
        [list(row[:20]) for row in submitted_s[:20]]
        == [list(row) for row in final_gram],
        "S top-left block differs from T20",
    )
    require(
        all(submitted_s[row][col] == 0 for row in range(20) for col in range(20, 44)),
        "S top-right block is nonzero",
    )
    require(
        all(submitted_s[row][col] == 0 for row in range(20, 44) for col in range(20)),
        "S bottom-left block is nonzero",
    )
    return [list(row[20:]) for row in submitted_s[20:]]


def strip_private_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_private_fields(item)
            for key, item in value.items()
            if not key.startswith("_")
        }
    if isinstance(value, list):
        return [strip_private_fields(item) for item in value]
    return value


def run_verification(submission: dict[str, Any] | None = None) -> dict[str, Any]:
    if submission is None:
        require(
            sha256_file(SUBMISSION_PATH) == EXPECTED_SUBMISSION_SHA256,
            "submitted JSON changed after preinspection freeze",
        )
        require(
            sha256_file(REPORT_PATH) == EXPECTED_REPORT_SHA256,
            "submitted report changed after preinspection freeze",
        )
        submission = json.loads(SUBMISSION_PATH.read_text(encoding="utf-8"))
    else:
        submission = copy.deepcopy(submission)

    scope = verify_scope(submission)
    rank20 = submission["rank20_construction"]
    candidate = submission["rank44_candidate"]
    final_gram = qmatrix(rank20["T20"]["gram"], "T20")
    raw_steps = rank20["neighbor_chain"]
    chain = reconstruct_chain(final_gram, raw_steps)
    require(len(chain) == 6, "reconstructed chain length mismatch")

    gram_reports = [
        check_gram(gram, f"T20 chain form {index}", 20, 729)
        for index, gram in enumerate(chain)
    ]
    require(chain[-1] == final_gram, "final Gram reconstruction mismatch")
    require(
        matrix_sha256(final_gram) == rank20["T20"]["gram_sha256"],
        "T20 submitted hash mismatch",
    )

    neighbor_reports = []
    for index, entry in enumerate(raw_steps):
        require(int(entry["step"]) == index + 1, "neighbor step numbering mismatch")
        report = verify_neighbor_step(chain[index], chain[index + 1], entry)
        neighbor_reports.append(report)

    starting = chain[0]
    require(
        all(starting[row][col] == 0 for row in range(12) for col in range(12, 20)),
        "starting Gram upper cross-block is nonzero",
    )
    require(
        all(starting[row][col] == 0 for row in range(12, 20) for col in range(12)),
        "starting Gram lower cross-block is nonzero",
    )
    k12 = [row[:12] for row in starting[:12]]
    e8 = [row[12:] for row in starting[12:]]
    k12_report = check_gram(k12, "reconstructed K12", 12, 729)
    e8_report = check_gram(e8, "reconstructed E8", 8, 1)
    require(
        matrix_sha256(k12) == rank20["starting_form"]["K12_gram_sha256"],
        "reconstructed K12 hash mismatch",
    )
    require(
        matrix_sha256(e8) == rank20["starting_form"]["E8_gram_sha256"],
        "reconstructed E8 hash mismatch",
    )

    root_enumerations = [enumerate_short_vectors(gram, 2) for gram in chain]
    root_counts = [result["counts"].get("2", 0) for result in root_enumerations]
    require(root_counts == [240, 112, 48, 20, 6, 0], "root-count chain mismatch")
    require(root_counts == rank20["root_count_chain"], "submitted root-count chain mismatch")
    for index, entry in enumerate(raw_steps):
        expected_hash = entry["root_shell_through_norm_2"]["vector_hashes"].get("2")
        actual_hash = root_enumerations[index + 1]["vector_hashes"].get("2")
        require(
            actual_hash == expected_hash,
            f"step {index + 1}: complete root-coordinate set hash mismatch",
        )

    final_shell = enumerate_short_vectors(final_gram, 4)
    require(final_shell["counts"].get("2", 0) == 0, "T20 has roots")
    require(final_shell["counts"].get("4", 0) == 5076, "T20 norm-four count mismatch")
    require(final_shell["counts"].get("0", 0) == 1, "T20 zero-vector count mismatch")
    require(
        final_shell["vector_hashes"].get("4")
        == rank20["T20"]["shell_through_norm_4"]["vector_hashes"]["4"],
        "T20 complete norm-four coordinate set hash mismatch",
    )

    scaled_t20_3, scaled_t20_3_report = verify_dual(final_gram, 3)
    submitted_t20_21 = qmatrix(
        rank20["T20"]["scaled_dual_21_T20_inverse"],
        "submitted 21*T20 inverse",
    )
    scaled_t20_21, scaled_t20_21_report = verify_dual(
        final_gram, 21, submitted_t20_21
    )
    require(
        matrix_sha256(scaled_t20_3)
        == rank20["T20"]["three_scaled_dual_gram_sha256"],
        "3*T20 inverse hash mismatch",
    )
    require(
        matrix_sha256(scaled_t20_21)
        == rank20["T20"]["scaled_dual_gram_sha256"],
        "21*T20 inverse hash mismatch",
    )

    submitted_s = qmatrix(candidate["S"], "submitted S")
    leech = extract_direct_sum_leech(submitted_s, final_gram)
    leech_report = check_gram(leech, "embedded Leech Gram", 24, 1)
    require(
        matrix_sha256(leech) == candidate["Leech"]["gram_sha256"],
        "Leech Gram hash mismatch",
    )
    leech_inverse = inverse(leech)
    require(is_even_integral(leech_inverse), "Leech inverse is not even integral")
    require(
        matrix_sha256(leech_inverse) == candidate["Leech"]["inverse_gram_sha256"],
        "Leech inverse hash mismatch",
    )
    leech_roots = enumerate_short_vectors(leech, 2)
    require(leech_roots["counts"].get("2", 0) == 0, "Leech block has roots")
    require(any(leech[index][index] == 4 for index in range(24)), "no norm-four basis vector")
    leech_minimum = 4

    expected_s = block_diagonal(final_gram, leech)
    require(submitted_s == expected_s, "S is not the claimed direct sum")
    s_report = check_gram(submitted_s, "rank-44 S", 44, 729)
    require(matrix_sha256(submitted_s) == candidate["S_sha256"], "S hash mismatch")
    s_roots = enumerate_short_vectors(submitted_s, 2)
    require(s_roots["counts"].get("2", 0) == 0, "S has roots")
    require(final_shell["counts"].get("4", 0) > 0, "T20 lacks norm-four vector")
    s_minimum = min(4, leech_minimum)

    scaled_s_3, scaled_s_3_report = verify_dual(submitted_s, 3)
    require(
        matrix_sha256(scaled_s_3) == candidate["three_scaled_dual_sha256"],
        "3*S inverse hash mismatch",
    )
    submitted_g = qmatrix(candidate["G_equals_21_S_inverse"], "submitted G")
    scaled_s_21, g_report = verify_dual(submitted_s, 21, submitted_g)
    require(matrix_sha256(scaled_s_21) == candidate["G_sha256"], "G hash mismatch")
    require(matmul(submitted_s, submitted_g) == scale_matrix(Fraction(21), identity(44)), "SG")
    g_gram_report = check_gram(submitted_g, "rank-44 G", 44, None)

    attack_t20_transform = unimodular_attack_matrix(20)
    attack_t20 = changed_basis_gram(final_gram, attack_t20_transform)
    attack_t20_report = check_gram(attack_t20, "T20 changed basis", 20, 729)
    attack_t20_shell = enumerate_short_vectors(attack_t20, 4)
    require(
        attack_t20_shell["counts"] == final_shell["counts"],
        "T20 shell count depends on submitted reduced basis",
    )
    attack_leech_transform = unimodular_attack_matrix(24)
    attack_leech = changed_basis_gram(leech, attack_leech_transform)
    attack_leech_report = check_gram(attack_leech, "Leech changed basis", 24, 1)
    attack_leech_roots = enumerate_short_vectors(attack_leech, 2)
    require(
        attack_leech_roots["counts"] == leech_roots["counts"],
        "Leech root count depends on submitted basis",
    )

    result = {
        "claim_label": "VERIFIED",
        "scope": scope,
        "inputs": {
            "submission_path": "attempts/wave30-h729-construction/exact-results.json",
            "submission_sha256": EXPECTED_SUBMISSION_SHA256,
            "report_path": "agents/2026-07-24-wave30-h729-construction.md",
            "report_sha256": EXPECTED_REPORT_SHA256,
        },
        "implementation": {
            "discovery_code_imported_or_executed": False,
            "arithmetic": "Python integers and fractions.Fraction only",
            "determinant": "fraction-free Bareiss elimination",
            "positive_definiteness": "exact LDL plus independently recomputed Sylvester minors",
            "enumeration": "complete exact rational-LDL recursion with integer-square-root bounds",
            "floating_point_used": False,
        },
        "rank20_chain": {
            "forms": gram_reports,
            "starting_form": {
                "orthogonal_decomposition_verified": True,
                "K12": k12_report,
                "E8": e8_report,
            },
            "neighbor_steps": neighbor_reports,
            "root_count_chain": root_counts,
            "root_enumerations": [public_enumeration(value) for value in root_enumerations],
            "T20_shell_through_norm_4": public_enumeration(final_shell),
            "T20_minimum": 4,
            "T20_norm_four_count": 5076,
            "T20_three_scaled_inverse": scaled_t20_3_report,
            "T20_twenty_one_scaled_inverse": scaled_t20_21_report,
        },
        "leech": {
            "gram": leech_report,
            "inverse_even_integral": True,
            "inverse_sha256": matrix_sha256(leech_inverse),
            "root_enumeration": public_enumeration(leech_roots),
            "rootless": True,
            "minimum": leech_minimum,
        },
        "rank44": {
            "S": s_report,
            "direct_sum_verified": True,
            "root_enumeration": public_enumeration(s_roots),
            "rootless": True,
            "minimum": s_minimum,
            "three_scaled_inverse": scaled_s_3_report,
            "G_equals_21_S_inverse": g_report,
            "G_gram": g_gram_report,
            "SG_equals_21I": True,
        },
        "basis_and_canonicalization_attacks": {
            "submitted_LLL_claim_trusted": False,
            "all_submitted_U_matrices_rechecked_unimodular": True,
            "all_transition_equalities_reconstructed": True,
            "T20_changed_basis_gram": attack_t20_report,
            "T20_changed_basis_shell": public_enumeration(attack_t20_shell),
            "Leech_changed_basis_gram": attack_leech_report,
            "Leech_changed_basis_roots": public_enumeration(attack_leech_roots),
            "basis_invariance_passed": True,
        },
        "limitations": [
            "This verifies only the submitted bare S/G lattice construction.",
            "No Q, B, X, M, W, frame, Schur-complement, or graph certificate was supplied or verified.",
            "The n3=708 endpoint remains UNKNOWN.",
            "Conway's 99-graph problem remains UNKNOWN.",
        ],
        "passes": [
            "all exact dimensions, symmetry, integrality, evenness, LDL/Sylvester, and determinants",
            "all five primitive 2-neighbor index-two transitions",
            "complete root counts 240 -> 112 -> 48 -> 20 -> 6 -> 0",
            "T20 minimum 4 and exact norm-four count 5076",
            "3*T20^-1 and 21*T20^-1 even integral",
            "Leech determinant 1, minimum 4, and rootlessness",
            "rank-44 S determinant 729, minimum 4, and rootlessness",
            "G=21*S^-1 even integral and S*G=21I",
            "basis-change and canonicalization attacks",
        ],
    }
    return strip_private_fields(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_verification()
    encoded = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if arguments.output is None:
        print(encoded, end="")
    else:
        arguments.output.write_text(encoded, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
