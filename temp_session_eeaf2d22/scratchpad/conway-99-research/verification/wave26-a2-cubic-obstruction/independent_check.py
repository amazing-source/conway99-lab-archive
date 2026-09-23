#!/usr/bin/env python3
"""Independent exact checker for the Wave 26 A2 cubic obstruction.

This standard-library-only checker intentionally reads only the hash-frozen
public premise files and the Wave 24 survivor certificate.  It does not read
or import the Wave 26 discovery report or discovery attempt directory.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[2]

PUBLIC_INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
}

A2: Tuple[Tuple[int, int], Tuple[int, int]] = ((2, -1), (-1, 2))
ROOT_REPRESENTATIVES: Tuple[Tuple[int, int], ...] = (
    (1, 0),
    (0, 1),
    (1, 1),
)

Number = int | Fraction
Matrix = List[List[Fraction]]
Vector = List[Fraction]
Tensor = Dict[Tuple[int, ...], Fraction]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def as_fraction_matrix(matrix: Sequence[Sequence[Number]]) -> Matrix:
    require(bool(matrix), "matrix must be nonempty")
    width = len(matrix[0])
    require(width > 0 and all(len(row) == width for row in matrix),
            "matrix must be rectangular")
    return [[Fraction(value) for value in row] for row in matrix]


def transpose(matrix: Sequence[Sequence[Number]]) -> Matrix:
    matrix_f = as_fraction_matrix(matrix)
    return [list(column) for column in zip(*matrix_f)]


def matmul(
    left: Sequence[Sequence[Number]],
    right: Sequence[Sequence[Number]],
) -> Matrix:
    left_f = as_fraction_matrix(left)
    right_f = as_fraction_matrix(right)
    require(len(left_f[0]) == len(right_f), "matrix product shape mismatch")
    right_t = transpose(right_f)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0))
         for column in right_t]
        for row in left_f
    ]


def matvec(
    matrix: Sequence[Sequence[Number]],
    vector: Sequence[Number],
) -> Vector:
    matrix_f = as_fraction_matrix(matrix)
    vector_f = [Fraction(value) for value in vector]
    require(len(matrix_f[0]) == len(vector_f), "matrix-vector shape mismatch")
    return [
        sum((a * b for a, b in zip(row, vector_f)), Fraction(0))
        for row in matrix_f
    ]


def hadamard(
    left: Sequence[Sequence[Number]],
    right: Sequence[Sequence[Number]],
) -> Matrix:
    left_f = as_fraction_matrix(left)
    right_f = as_fraction_matrix(right)
    require(len(left_f) == len(right_f), "Hadamard row mismatch")
    require(all(len(a) == len(b) for a, b in zip(left_f, right_f)),
            "Hadamard column mismatch")
    return [
        [a * b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left_f, right_f)
    ]


def identity(size: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(size)]
        for i in range(size)
    ]


def inverse(matrix: Sequence[Sequence[Number]]) -> Matrix:
    matrix_f = as_fraction_matrix(matrix)
    size = len(matrix_f)
    require(all(len(row) == size for row in matrix_f), "inverse needs square matrix")
    augmented = [
        row[:] + identity(size)[i]
        for i, row in enumerate(matrix_f)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column]),
            None,
        )
        require(pivot is not None, f"singular matrix at column {column}")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def determinant(matrix: Sequence[Sequence[Number]]) -> Fraction:
    matrix_f = as_fraction_matrix(matrix)
    size = len(matrix_f)
    require(all(len(row) == size for row in matrix_f), "determinant needs square matrix")
    work = [row[:] for row in matrix_f]
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for j in range(column + 1, size):
                work[row][j] -= factor * work[column][j]
    return result


def rank(matrix: Sequence[Sequence[Number]]) -> int:
    work = as_fraction_matrix(matrix)
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((r for r in range(pivot_row, rows) if work[r][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def block_diagonal(*blocks: Sequence[Sequence[Number]]) -> Matrix:
    converted = [as_fraction_matrix(block) for block in blocks]
    total_rows = sum(len(block) for block in converted)
    total_columns = sum(len(block[0]) for block in converted)
    result = [[Fraction(0) for _ in range(total_columns)] for _ in range(total_rows)]
    row_offset = 0
    column_offset = 0
    for block in converted:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[row_offset + i][column_offset + j] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def kronecker(
    left: Sequence[Sequence[Number]],
    right: Sequence[Sequence[Number]],
) -> Matrix:
    left_f = as_fraction_matrix(left)
    right_f = as_fraction_matrix(right)
    return [
        [
            left_f[i][j] * right_f[k][ell]
            for j in range(len(left_f[0]))
            for ell in range(len(right_f[0]))
        ]
        for i in range(len(left_f))
        for k in range(len(right_f))
    ]


def quadratic(
    left: Sequence[Number],
    metric: Sequence[Sequence[Number]],
    right: Sequence[Number] | None = None,
) -> Fraction:
    left_f = [Fraction(value) for value in left]
    right_f = left_f if right is None else [Fraction(value) for value in right]
    return sum(
        (
            left_f[i] * Fraction(metric[i][j]) * right_f[j]
            for i in range(len(left_f))
            for j in range(len(right_f))
        ),
        Fraction(0),
    )


def trace_product(
    left: Sequence[Sequence[Number]],
    right: Sequence[Sequence[Number]],
) -> Fraction:
    left_f = as_fraction_matrix(left)
    right_f = as_fraction_matrix(right)
    require(len(left_f) == len(left_f[0]), "left trace factor must be square")
    require(len(right_f) == len(right_f[0]), "right trace factor must be square")
    require(len(left_f) == len(right_f), "trace factor shape mismatch")
    return sum(
        (
            left_f[i][j] * right_f[j][i]
            for i in range(len(left_f))
            for j in range(len(left_f))
        ),
        Fraction(0),
    )


def submatrix(
    matrix: Sequence[Sequence[Number]],
    rows: Sequence[int],
    columns: Sequence[int],
) -> Matrix:
    matrix_f = as_fraction_matrix(matrix)
    return [[matrix_f[i][j] for j in columns] for i in rows]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_public_hashes() -> Dict[str, Dict[str, object]]:
    results: Dict[str, Dict[str, object]] = {}
    for relative, expected in PUBLIC_INPUTS.items():
        path = ROOT / relative
        require(path.is_file(), f"missing public input: {relative}")
        actual = sha256_file(path)
        require(actual == expected, f"public input hash mismatch: {relative}")
        results[relative] = {
            "actual": actual,
            "expected": expected,
            "match": True,
        }
    return results


def a2_norm(vector: Sequence[int]) -> int:
    value = quadratic(vector, A2)
    require(value.denominator == 1, "A2 norm unexpectedly nonintegral")
    return value.numerator


def outer(vector: Sequence[int]) -> List[List[int]]:
    return [[a * b for b in vector] for a in vector]


def add_integer_matrices(
    matrices: Iterable[Sequence[Sequence[int]]],
    size: int,
) -> List[List[int]]:
    result = [[0 for _ in range(size)] for _ in range(size)]
    for matrix in matrices:
        for i in range(size):
            for j in range(size):
                result[i][j] += int(matrix[i][j])
    return result


def root_enumeration() -> Dict[str, object]:
    vectors = [
        (a, b)
        for a in range(-2, 3)
        for b in range(-2, 3)
        if a2_norm((a, b)) <= 4
    ]
    roots = sorted(vector for vector in vectors if a2_norm(vector) == 2)
    norm_four = sorted(vector for vector in vectors if a2_norm(vector) == 4)
    expected_roots = sorted(
        representative
        for root in ROOT_REPRESENTATIVES
        for representative in (root, (-root[0], -root[1]))
    )
    require(roots == expected_roots, "A2 root enumeration changed")
    require(not norm_four, "A2 unexpectedly has an integral norm-four vector")
    require(vectors == sorted([(0, 0), *expected_roots]),
            "A2 norm-at-most-four enumeration changed")
    return {
        "coordinate_bound": 2,
        "norm_at_most_four_vectors": [list(vector) for vector in vectors],
        "norm_two_roots": [list(vector) for vector in roots],
        "norm_four_vectors": [],
        "mod_three_obstruction": "a^2-a*b+b^2=(a+b)^2 mod 3 cannot equal 2 mod 3",
    }


def frame_line_counts() -> Dict[str, object]:
    inverse_a2 = inverse(A2)
    target_fractional = [
        [Fraction(21) * entry for entry in row]
        for row in inverse_a2
    ]
    require(all(entry.denominator == 1 for row in target_fractional for entry in row),
            "21*A2^-1 is unexpectedly nonintegral")
    target = [
        [entry.numerator for entry in row]
        for row in target_fractional
    ]
    solutions: List[Tuple[int, int, int]] = []
    line_outer = [outer(root) for root in ROOT_REPRESENTATIVES]
    for counts in itertools.product(range(22), repeat=3):
        moment = add_integer_matrices(
            (
                [[counts[k] * entry for entry in row] for row in line_outer[k]]
                for k in range(3)
            ),
            2,
        )
        if moment == target:
            solutions.append(counts)
    require(solutions == [(7, 7, 7)], "A2 root-line count is not uniquely 7,7,7")
    return {
        "frame_block": target,
        "root_line_representatives": [list(root) for root in ROOT_REPRESENTATIVES],
        "unique_unoriented_line_counts": list(solutions[0]),
        "total_nonzero_a2_rows": sum(solutions[0]),
    }


def cubic_gram() -> List[List[int]]:
    return [
        [
            a2_norm_pair(left, right) ** 3
            for right in ROOT_REPRESENTATIVES
        ]
        for left in ROOT_REPRESENTATIVES
    ]


def a2_norm_pair(left: Sequence[int], right: Sequence[int]) -> int:
    value = quadratic(left, A2, right)
    require(value.denominator == 1, "A2 pairing unexpectedly nonintegral")
    return value.numerator


def cubic_value(imbalance: Sequence[int], gram: Sequence[Sequence[int]]) -> int:
    value = quadratic(imbalance, gram)
    require(value.denominator == 1, "cubic norm unexpectedly nonintegral")
    return value.numerator


def imbalance_floor() -> Dict[str, object]:
    gram = cubic_gram()
    expected = [[8, -1, 1], [-1, 8, 1], [1, 1, 8]]
    require(gram == expected, "A2 cubic Gram matrix changed")

    eigenpairs = [
        ((1, 1, -1), 6),
        ((1, -1, 0), 9),
        ((1, 1, 2), 9),
    ]
    for vector, eigenvalue in eigenpairs:
        require(
            matvec(gram, vector)
            == [Fraction(eigenvalue * coordinate) for coordinate in vector],
            f"wrong cubic Gram eigenpair: {vector}",
        )
    eigenvector_matrix = [
        [eigenpairs[column][0][row] for column in range(3)]
        for row in range(3)
    ]
    require(determinant(eigenvector_matrix) != 0, "cubic Gram eigenvectors dependent")

    domain = tuple(range(-7, 8, 2))
    scored = [
        (cubic_value(imbalance, gram), imbalance)
        for imbalance in itertools.product(domain, repeat=3)
    ]
    minimum = min(value for value, _ in scored)
    minimizers = sorted(list(imbalance) for value, imbalance in scored if value == minimum)
    require(minimum == 18, "odd-imbalance cubic floor changed")
    require(minimizers == [[-1, -1, 1], [1, 1, -1]],
            "odd-imbalance minimizers changed")

    zero_sum = [
        (value, imbalance)
        for value, imbalance in scored
        if (
            imbalance[0] + imbalance[2] == 0
            and imbalance[1] + imbalance[2] == 0
        )
    ]
    require(zero_sum, "M1=0 imbalance domain unexpectedly empty")
    zero_sum_minimum = min(value for value, _ in zero_sum)
    require(zero_sum_minimum == minimum,
            "M1=0 changed the numeric cubic floor")
    require(
        all(
            imbalance[0] == imbalance[1] == -imbalance[2]
            for _, imbalance in zero_sum
        ),
        "M1=0 imbalance parameterization failed",
    )

    no_m1_example = (1, 1, 1)
    require(cubic_value(no_m1_example, gram) == 26,
            "dropped-M1 positive control changed")

    return {
        "cubic_root_line_gram": gram,
        "exact_eigenvalues": [6, 9, 9],
        "imbalance_domain_per_line": list(domain),
        "all_imbalances_are_odd": True,
        "minimum_without_M1_zero": minimum,
        "minimizers_without_M1_zero": minimizers,
        "minimum_with_M1_zero": zero_sum_minimum,
        "M1_zero_parameterization": "d=(t,t,-t), t odd",
        "M1_zero_required_for_bound": False,
        "dropped_M1_example": {
            "imbalance": list(no_m1_example),
            "first_moment": [2, 2],
            "pure_cubic_norm": cubic_value(no_m1_example, gram),
        },
    }


def row_tensor_matrix(rows: Sequence[Sequence[Number]]) -> Matrix:
    rows_f = as_fraction_matrix(rows)
    return [
        [a * b for a in row for b in row]
        for row in rows_f
    ]


def projector_data(
    rows: Sequence[Sequence[Number]],
    scaled_dual: Sequence[Sequence[Number]],
) -> Dict[str, Matrix]:
    x = as_fraction_matrix(rows)
    s = as_fraction_matrix(scaled_dual)
    require(len(x[0]) == len(s) == len(s[0]), "row/scaled-dual shape mismatch")
    m = matmul(matmul(x, s), transpose(x))
    w = hadamard(m, m)
    q = matmul(matmul(transpose(x), w), x)
    z = row_tensor_matrix(x)
    c = matmul(transpose(z), x)
    q_tensor = matmul(matmul(transpose(c), kronecker(s, s)), c)
    require(q == q_tensor, "ordered tensor factorization Q=C^T(S tensor S)C failed")
    return {"X": x, "M": m, "W": w, "Q": q, "Z": z, "C": c}


def cubic_tensor(rows: Sequence[Sequence[Number]], a_dimension: int = 2) -> Tensor:
    rows_f = as_fraction_matrix(rows)
    dimension = len(rows_f[0])
    require(0 < a_dimension <= dimension, "bad A-block dimension")
    tensor: Tensor = {}
    for row in rows_f:
        for first in range(a_dimension):
            for second in range(dimension):
                for third in range(dimension):
                    index = (first, second, third)
                    tensor[index] = (
                        tensor.get(index, Fraction(0))
                        + row[first] * row[second] * row[third]
                    )
    return {index: value for index, value in tensor.items() if value}


def tensor_norm(
    tensor: Mapping[Tuple[int, ...], Number],
    metrics: Sequence[Sequence[Sequence[Number]]],
) -> Fraction:
    require(tensor, "tensor must be nonzero for this check")
    converted = {index: Fraction(value) for index, value in tensor.items()}
    result = Fraction(0)
    for left_index, left_value in converted.items():
        for right_index, right_value in converted.items():
            require(len(left_index) == len(metrics) == len(right_index),
                    "tensor metric arity mismatch")
            metric_factor = Fraction(1)
            for axis, metric in enumerate(metrics):
                metric_factor *= Fraction(metric[left_index[axis]][right_index[axis]])
            result += left_value * right_value * metric_factor
    return result


def tensor_block(
    tensor: Mapping[Tuple[int, int, int], Number],
    second_indices: Sequence[int],
    third_indices: Sequence[int],
) -> Tensor:
    second_set = set(second_indices)
    third_set = set(third_indices)
    return {
        index: Fraction(value)
        for index, value in tensor.items()
        if index[1] in second_set and index[2] in third_set
    }


def tensor_and_basis_checks() -> Dict[str, object]:
    scaled_dual = block_diagonal(A2, ((3,),))
    rows = [
        [1, 0, 1],
        [0, 1, -1],
        [1, 1, 0],
        [-1, 0, 1],
    ]
    data = projector_data(rows, scaled_dual)
    a2_block_q = submatrix(data["Q"], [0, 1], [0, 1])
    direct_trace = trace_product(A2, a2_block_q)

    tensor = cubic_tensor(rows)
    full_norm = tensor_norm(tensor, (A2, scaled_dual, scaled_dual))
    require(full_norm == direct_trace,
            "trace(A2 Q_AA) does not match ordered cubic tensor norm")

    a_indices = [0, 1]
    r_indices = [2]
    aaa = tensor_block(tensor, a_indices, a_indices)
    aar = tensor_block(tensor, a_indices, r_indices)
    ara = tensor_block(tensor, r_indices, a_indices)
    arr = tensor_block(tensor, r_indices, r_indices)
    aaa_norm = tensor_norm(aaa, (A2, scaled_dual, scaled_dual))
    aar_norm = tensor_norm(aar, (A2, scaled_dual, scaled_dual))
    ara_norm = tensor_norm(ara, (A2, scaled_dual, scaled_dual))
    arr_norm = tensor_norm(arr, (A2, scaled_dual, scaled_dual))
    require(aar_norm == ara_norm, "ordered mixed tensor blocks have unequal norms")
    require(full_norm == aaa_norm + aar_norm + ara_norm + arr_norm,
            "orthogonal tensor block norms do not sum to full norm")
    require(full_norm >= aaa_norm, "cross blocks lowered the compression norm")

    p = as_fraction_matrix(((1, 1, 0), (0, 1, 0), (0, 0, 1)))
    p_inverse = inverse(p)
    contragredient = transpose(p_inverse)
    rows_changed = matmul(rows, contragredient)
    scaled_dual_changed = matmul(matmul(transpose(p), scaled_dual), p)
    changed = projector_data(rows_changed, scaled_dual_changed)
    require(changed["M"] == data["M"], "contragredient basis change altered M")
    expected_q_changed = matmul(matmul(p_inverse, data["Q"]), transpose(p_inverse))
    require(changed["Q"] == expected_q_changed, "basis covariance of Q failed")
    old_trace = trace_product(A2, a2_block_q)
    new_a = submatrix(scaled_dual_changed, [0, 1], [0, 1])
    new_q = submatrix(changed["Q"], [0, 1], [0, 1])
    new_trace = trace_product(new_a, new_q)
    require(new_trace == old_trace, "block trace changed under internal basis change")

    return {
        "row_orientation": "X is 231-by-44; x_i is the transpose of row i",
        "ordered_tensor_factorization": "Q=C^T(S tensor S)C",
        "synthetic_trace": direct_trace,
        "orthogonal_compression": {
            "full_norm": full_norm,
            "AAA_norm": aaa_norm,
            "AAR_norm": aar_norm,
            "ARA_norm": ara_norm,
            "ARR_norm": arr_norm,
            "identity": "full=AAA+AAR+ARA+ARR=AAA+2*AAR+ARR",
        },
        "symmetric_square_normalization":
            "normalized mixed basis has coefficient sqrt(2); ordered tensors need no factor",
        "basis_covariance": {
            "M_unchanged": True,
            "Q_rule": "Q'=P^-1 Q P^-T",
            "S_rule": "S'=P^T S P",
            "trace_unchanged": True,
        },
    }


def dropped_frame_control() -> Dict[str, object]:
    scaled_dual = block_diagonal(A2, A2)
    positive_rows = [
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [1, 1, 1, 0],
    ]
    rows = [
        row
        for positive in positive_rows
        for row in (positive, [-value for value in positive])
    ]
    data = projector_data(rows, scaled_dual)
    norms = [quadratic(row, scaled_dual) for row in rows]
    require(all(norm == 4 for norm in norms), "dropped-frame control row norm changed")
    require(rank(rows) == 4, "dropped-frame control lost full column rank")
    row_sums = [sum(row) for row in data["M"]]
    require(all(value == 0 for value in row_sums),
            "dropped-frame control no longer has M1=0")
    q_block = submatrix(data["Q"], [0, 1], [0, 1])
    trace_value = trace_product(A2, q_block)
    require(trace_value == 0, "dropped-frame control no longer kills the cubic block")
    frame = matmul(transpose(rows), rows)
    required_frame = [
        [Fraction(21) * value for value in row]
        for row in inverse(scaled_dual)
    ]
    require(frame != required_frame, "dropped-frame control accidentally became tight")
    off_diagonal = sorted(
        {
            data["M"][i][j]
            for i in range(len(rows))
            for j in range(len(rows))
            if i != j
        }
    )
    return {
        "description":
            "antipodal norm-four full-rank rows retain M1=0 but omit the tight frame",
        "row_count": len(rows),
        "column_rank": rank(rows),
        "all_row_norms": 4,
        "M1_zero": True,
        "trace_A2_Q_AA": trace_value,
        "tight_frame_holds": False,
        "off_diagonal_M_values": off_diagonal,
        "also_violates_public_off_diagonal_alphabet": any(
            value not in {Fraction(-2), Fraction(-1), Fraction(0), Fraction(1)}
            for value in off_diagonal
        ),
    }


def block_is_orthogonal_copy(
    matrix: Sequence[Sequence[Number]],
    block: Sequence[Sequence[Number]],
    start: int,
) -> bool:
    matrix_f = as_fraction_matrix(matrix)
    block_f = as_fraction_matrix(block)
    indices = list(range(start, start + len(block_f)))
    if indices[-1] >= len(matrix_f):
        return False
    if submatrix(matrix_f, indices, indices) != block_f:
        return False
    outside = [index for index in range(len(matrix_f)) if index not in indices]
    return all(
        matrix_f[i][j] == 0 and matrix_f[j][i] == 0
        for i in indices
        for j in outside
    )


def survivor_check() -> Dict[str, object]:
    relative = "verification/wave24-n3-708-index/survivor-certificate.json"
    path = ROOT / relative
    certificate = json.loads(path.read_text(encoding="utf-8"))
    require(certificate["format"] == "row-major exact integer matrices",
            "survivor matrix format changed")
    require("Abstract coordinate-lattice survivor only" in certificate["scope"],
            "survivor scope wall changed")
    matrices = certificate["matrices"]
    require(matrices["A2"] == [list(row) for row in A2], "certificate A2 changed")
    s = matrices["S"]
    q = matrices["Q"]
    require(len(s) == len(q) == 44, "survivor rank changed")
    require(all(len(row) == 44 for row in s + q), "survivor matrix shape changed")
    require(s == [list(row) for row in transpose(s)], "survivor S is not symmetric")
    require(q == [list(row) for row in transpose(q)], "survivor Q is not symmetric")
    starts = [
        start
        for start in range(43)
        if block_is_orthogonal_copy(s, A2, start)
    ]
    require(starts == [40, 42], "orthogonal A2 block locations changed")
    traces = []
    q_blocks = []
    for start in starts:
        indices = [start, start + 1]
        q_block = submatrix(q, indices, indices)
        require(q_block == as_fraction_matrix(A2),
                f"Q block at {start} is not A2")
        require(block_is_orthogonal_copy(q, A2, start),
                f"Q block at {start} is not orthogonal")
        trace_value = trace_product(A2, q_block)
        require(trace_value == 10, f"survivor block trace at {start} changed")
        q_blocks.append(q_block)
        traces.append(trace_value)
    require(all(trace < 18 for trace in traces),
            "survivor no longer violates the cubic floor")
    return {
        "certificate_sha256": sha256_file(path),
        "rank": 44,
        "orthogonal_A2_block_starts_zero_based": starts,
        "S_AA": A2,
        "Q_AA_blocks": q_blocks,
        "trace_A2_Q_AA": traces,
        "required_minimum": 18,
        "deficit_per_block": [18 - trace for trace in traces],
        "full_projector_Schur_origin_for_this_survivor": False,
        "abstract_coordinate_lattice_certificate": "unchanged and still exact",
    }


def jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def build_result() -> Dict[str, object]:
    hashes = verify_public_hashes()
    roots = root_enumeration()
    frame = frame_line_counts()
    imbalance = imbalance_floor()
    tensor_checks = tensor_and_basis_checks()
    dropped_frame = dropped_frame_control()
    survivor = survivor_check()

    require(frame["total_nonzero_a2_rows"] == 21, "A2 incidence total changed")
    require(imbalance["minimum_without_M1_zero"] == 18, "cubic floor changed")
    require(survivor["trace_A2_Q_AA"] == [10, 10],
            "survivor trace comparison changed")

    return {
        "claim_label": "VERIFIED",
        "verdict": "PASS_SCOPED_A2_CUBIC_OBSTRUCTION",
        "scope":
            "conditional full 231-row projector/Schur origin with an orthogonal A2 summand",
        "public_input_hashes": hashes,
        "projector_identities_used": [
            "X has shape 231 x 44 and full column rank",
            "G=X^T X",
            "S=21 G^-1",
            "M=X S X^T",
            "M_ii=4",
            "W=M o M",
            "Q=X^T W X",
        ],
        "projector_identities_not_needed_for_numeric_floor": [
            "M 1=0",
            "the off-diagonal alphabet after the row norm and frame consequences are fixed",
            "n3=708 except as context selecting the frozen survivor",
        ],
        "a2_integral_arithmetic": roots,
        "a2_frame_block": frame,
        "cubic_imbalance_floor": imbalance,
        "tensor_normalization_and_covariance": tensor_checks,
        "hostile_controls": {
            "drop_M1_zero":
                "the minimum stays 18; M1=0 is redundant for the numeric floor",
            "drop_tight_frame": dropped_frame,
        },
        "wave24_survivor": survivor,
        "conclusions": {
            "trace_A2_Q_AA_minimum": 18,
            "wave24_survivor_trace": 10,
            "wave24_survivor_has_full_projector_Schur_origin": False,
            "all_h9_forms_excluded": False,
            "n3_708_excluded": False,
            "Conway_99_resolved": False,
            "novelty_status": "UNKNOWN",
        },
    }


def write_json(path: Path, value: object) -> None:
    rendered = json.dumps(jsonable(value), indent=2, sort_keys=True) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
        help="deterministic JSON output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_result()
    write_json(args.output, result)
    print(json.dumps(jsonable(result["conclusions"]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
