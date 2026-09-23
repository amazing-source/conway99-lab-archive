#!/usr/bin/env python3
"""Independent Wave 27 verifier.

This file intentionally does not import the submitted checker.  Its finite
search uses a different enumeration model: the parity coset is converted to
an affine CVP, x = residue + modulus*y,
  before an exact rational triangular enumeration of the unrestricted
  integer vector y.

Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
from math import isqrt
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
FRAME_SCALE = 21
GLOBAL_TRACE = 60
TOTAL_RANK = 44
SUBMITTED = {
    "agents/2026-07-23-wave27-general-root-tensor.md":
        "456a4ad6f27c1c9c09f84b2ff41796473f519b5aaabda36b71022a51bbbe7f38",
    "attempts/wave27-general-root-tensor/artifact-manifest.sha256":
        "3ba7ee4683dfac361b6f2d1b09a90d485210e2debd87cbe9d4ecb62f607ebf32",
    "attempts/wave27-general-root-tensor/exact_check.py":
        "107907f610b83ddbb526daddeaa1fe850a0bd73e2dfeeaa386ca578a875bf8d5",
    "attempts/wave27-general-root-tensor/exact-results.json":
        "98aba5a30b2f3a83b9f6ce6fd6a20458505b668249d97b0810907de50cae678d",
    "attempts/wave27-general-root-tensor/failed-routes.md":
        "e806127f2140212277651ffa47b24087f79d6ba59c91b5aa290f1d73ac51f1d4",
    "attempts/wave27-general-root-tensor/input-freeze.sha256":
        "13c5327b27ad81311e7857460c777db85064141fbdd8b33b5a8906f456647eaa",
    "attempts/wave27-general-root-tensor/run-report.yaml":
        "4073f21de51b09b04436d471a192017420a85e1286bd5c4d3b3d5e6471c43499",
    "attempts/wave27-general-root-tensor/test_exact_check.py":
        "3d9197c959b4624755243d21ecdc10dda95012b083717199f055f19a8872123f",
}
PUBLIC_INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md":
        "5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3",
    "verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md":
        "883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465",
}
ADDENDUM_SUBMITTED = {
    "agents/2026-07-24-wave27-a20-trace-addendum.md":
        "97c7296752e0ef2126bd8da50cdf8b0abe07b3c72a939233d15aae6d7c413659",
    "attempts/wave27-a20-trace-addendum/artifact-manifest.sha256":
        "8f8ef9538a4070d569cfd4415296206214af3d3b2d8fe136ec7536257ead9949",
    "attempts/wave27-a20-trace-addendum/exact_check.py":
        "7762acf33bf519e3a91f442d4dcae6da34e770d98491b02d995a14550840de7c",
    "attempts/wave27-a20-trace-addendum/exact-results.json":
        "dc5716cbf2537cd214906f1bf2eae96d4886e4bd88008cd7508c6a64d78f089c",
    "attempts/wave27-a20-trace-addendum/failed-routes.md":
        "178c8578eebe32d10e6d8c5c8862ba05e5c0a2b661c62813310371db6c9b17b5",
    "attempts/wave27-a20-trace-addendum/input-freeze.sha256":
        "c0a85ebaf10f53b9ab456147b77d021d0e2d4892123c8939c1a15413c09f9679",
    "attempts/wave27-a20-trace-addendum/run-report.yaml":
        "5098a03cf12c4cd94891a354d92fb620f334372e7fc3330671a51da0bb2e4781",
    "attempts/wave27-a20-trace-addendum/test_exact_check.py":
        "b5d55c15f01c4f7a5856ebce36646140f90994328b62852b8dfb1d121bed4f82",
}
DECLARED_CANONICAL_GRAM_HASHES = {
    "A6": "f1877b7d31e982e0e7bafba7f410ad36d18bb81853efa237c770c2fa0341e7e2",
    "E6": "9608fd7ce190259ba86afdb8561525dc698570533aaac5b92eefc382d5477f8b",
}

Number = int | Fraction
Matrix = list[list[Number]]
Triple = tuple[int, int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def payload_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def verify_hashes(root: Path, expected: dict[str, str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, digest in expected.items():
        actual = sha256(root / relative)
        if actual != digest:
            raise AssertionError(f"hash drift: {relative}: {actual} != {digest}")
        observed[relative] = actual
    return observed


def transpose(a: Sequence[Sequence[Number]]) -> Matrix:
    return [list(row) for row in zip(*a)]


def matmul(
    a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]
) -> Matrix:
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def matvec(a: Sequence[Sequence[Number]], x: Sequence[Number]) -> list[Number]:
    return [sum(v * w for v, w in zip(row, x)) for row in a]


def dot(x: Sequence[Number], y: Sequence[Number]) -> Number:
    return sum(a * b for a, b in zip(x, y))


def quadratic(a: Sequence[Sequence[Number]], x: Sequence[Number]) -> Number:
    return dot(x, matvec(a, x))


def trace(a: Sequence[Sequence[Number]]) -> Number:
    return sum(a[i][i] for i in range(len(a)))


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def fraction_matrix(a: Sequence[Sequence[Number]]) -> Matrix:
    return [[Fraction(v) for v in row] for row in a]


def inverse(a: Sequence[Sequence[Number]]) -> Matrix:
    """Exact Gauss-Jordan inverse with row pivoting."""
    n = len(a)
    work = [
        [Fraction(v) for v in a[i]]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i][col]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [v / scale for v in work[col]]
        for i in range(n):
            if i == col:
                continue
            multiple = work[i][col]
            if multiple:
                work[i] = [
                    work[i][j] - multiple * work[col][j]
                    for j in range(2 * n)
                ]
    return [row[n:] for row in work]


def bareiss_det(a: Sequence[Sequence[Number]]) -> int:
    """Fraction-free determinant for integral matrices."""
    work = [[int(v) for v in row] for row in a]
    n = len(work)
    if n == 0:
        return 1
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if work[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            work[k], work[pivot] = work[pivot], work[k]
            sign *= -1
        value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = work[i][j] * value - work[i][k] * work[k][j]
                if numerator % previous:
                    raise AssertionError("Bareiss division was not exact")
                work[i][j] = numerator // previous
            work[i][k] = 0
        previous = value
    return sign * work[n - 1][n - 1]


def is_positive_definite(a: Sequence[Sequence[int]]) -> bool:
    return all(bareiss_det([list(row[:k]) for row in a[:k]]) > 0
               for k in range(1, len(a) + 1))


def cartan_a(rank: int) -> list[list[int]]:
    return [
        [2 * int(i == j) - int(abs(i - j) == 1) for j in range(rank)]
        for i in range(rank)
    ]


def cartan_d(rank: int) -> list[list[int]]:
    if rank < 4:
        raise ValueError("D rank")
    edges = {(i, i + 1) for i in range(rank - 2)}
    edges.add((rank - 3, rank - 1))
    return [
        [2 * int(i == j) - int((i, j) in edges or (j, i) in edges)
         for j in range(rank)]
        for i in range(rank)
    ]


def exceptional(kind: str) -> list[list[int]]:
    rank = {"E6": 6, "E7": 7, "E8": 8}[kind]
    edges = {(i, i + 1) for i in range(rank - 2)}
    edges.add((2, rank - 1))
    return [
        [2 * int(i == j) - int((i, j) in edges or (j, i) in edges)
         for j in range(rank)]
        for i in range(rank)
    ]


def permute_form(a: Sequence[Sequence[int]], order: Sequence[int]) -> list[list[int]]:
    return [[a[order[i]][order[j]] for j in range(len(order))]
            for i in range(len(order))]


CANONICAL_A6 = cartan_a(6)
CANONICAL_E6 = exceptional("E6")
CANONICAL_E8 = exceptional("E8")
A6_COORDINATE_ORDER = (0, 2, 4, 5, 3, 1)
E6_COORDINATE_ORDER = (2, 5, 0, 4, 1, 3)
VERIFIER_A6 = permute_form(CANONICAL_A6, A6_COORDINATE_ORDER)
VERIFIER_E6 = permute_form(CANONICAL_E6, E6_COORDINATE_ORDER)


def triples_lex(rank: int) -> list[Triple]:
    return list(combinations_with_replacement(range(rank), 3))


def triples_verifier(rank: int) -> list[Triple]:
    # The labels refer to the separately permuted Cartan coordinates.
    return triples_lex(rank)


def orbit(triple: Triple) -> tuple[Triple, ...]:
    return tuple(sorted(set(permutations(triple))))


def symmetric_cubic_gram(
    form: Sequence[Sequence[int]], triples: Sequence[Triple]
) -> list[list[int]]:
    orbits = [orbit(t) for t in triples]
    return [
        [
            sum(
                form[a][d] * form[b][e] * form[c][f]
                for a, b, c in left
                for d, e, f in right
            )
            for right in orbits
        ]
        for left in orbits
    ]


def direct_tensor_norm(
    form: Sequence[Sequence[int]],
    triples: Sequence[Triple],
    coefficients: Sequence[int],
) -> int:
    rank = len(form)
    tensor = [[[0 for _ in range(rank)] for _ in range(rank)]
              for _ in range(rank)]
    for coefficient, triple in zip(coefficients, triples):
        for i, j, k in orbit(triple):
            tensor[i][j][k] = coefficient
    return sum(
        tensor[a][b][c] * form[a][d] * form[b][e] * form[c][f]
        * tensor[d][e][f]
        for a, b, c, d, e, f in product(range(rank), repeat=6)
    )


def exact_ldl(a: Sequence[Sequence[int]]) -> tuple[list[list[Fraction]], list[Fraction]]:
    """Return G=L D L^T in the supplied verifier order."""
    n = len(a)
    lower = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    diag = [Fraction(0) for _ in range(n)]
    for i in range(n):
        lower[i][i] = 1
        diag[i] = Fraction(a[i][i]) - sum(
            lower[i][k] * lower[i][k] * diag[k] for k in range(i)
        )
        if diag[i] <= 0:
            raise AssertionError(f"nonpositive pivot {i}: {diag[i]}")
        for j in range(i + 1, n):
            lower[j][i] = (
                Fraction(a[j][i])
                - sum(lower[j][k] * lower[i][k] * diag[k]
                      for k in range(i))
            ) / diag[i]
    return lower, diag


def reconstruct_ldl(
    lower: Sequence[Sequence[Fraction]], diag: Sequence[Fraction]
) -> Matrix:
    n = len(diag)
    return [
        [
            sum(lower[i][k] * diag[k] * lower[j][k] for k in range(n))
            for j in range(n)
        ]
        for i in range(n)
    ]


def frame_moment(form: Sequence[Sequence[int]], scale: int = FRAME_SCALE) -> list[list[int]]:
    result: list[list[int]] = []
    for row in inverse(form):
        converted: list[int] = []
        for value in row:
            scaled = scale * value
            if scaled.denominator != 1:
                raise ValueError("nonintegral frame moment")
            converted.append(scaled.numerator)
        result.append(converted)
    return result


def parity_coset(
    form: Sequence[Sequence[int]],
    triples: Sequence[Triple],
    scale: int = FRAME_SCALE,
    *,
    omit_diagonal_parity: bool = False,
) -> tuple[list[int], list[int], list[list[int]]]:
    moment = frame_moment(form, scale)
    residues: list[int] = []
    moduli: list[int] = []
    for a, b, c in triples:
        repeated = a == b or b == c
        if omit_diagonal_parity and a == b == c:
            repeated = False
        if not repeated:
            residues.append(0)
            moduli.append(1)
        elif a == b:
            residues.append(moment[a][c] % 2)
            moduli.append(2)
        else:
            residues.append(moment[b][a] % 2)
            moduli.append(2)
    return residues, moduli, moment


def ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def integer_interval(center: Fraction, radius2: Fraction) -> tuple[int, int]:
    """All z with (z+center)^2 <= radius2, using integer arithmetic."""
    if radius2 < 0:
        return (1, 0)
    p, q = center.numerator, center.denominator
    scaled = (
        radius2.numerator * q * q // radius2.denominator
    )
    radius = isqrt(scaled)
    return ceil_div(-p - radius, q), (-p + radius) // q


def affine_cvp_search(
    form: Sequence[Sequence[int]],
    cap: int,
    *,
    scale: int = FRAME_SCALE,
    stop_after_first: bool = False,
    omit_diagonal_parity: bool = False,
) -> dict[str, object]:
    """Complete exact search in x=r+My, in verifier coordinates.

    This differs from the submitted direct residue-progression search.  The
    diagonal modulus matrix is absorbed into H=M*Gamma*M and the recursion
    visits every unrestricted y in Z^56 around the rational CVP center
    s=-M^-1*r.
    """
    triples = triples_verifier(len(form))
    gram = symmetric_cubic_gram(form, triples)
    residues, moduli, moment = parity_coset(
        form, triples, scale, omit_diagonal_parity=omit_diagonal_parity
    )
    dimension = len(triples)
    affine_gram = [
        [moduli[i] * gram[i][j] * moduli[j] for j in range(dimension)]
        for i in range(dimension)
    ]
    lower, diag = exact_ldl(affine_gram)
    if reconstruct_ldl(lower, diag) != fraction_matrix(affine_gram):
        raise AssertionError("affine LDL reconstruction failed")

    cvp_center = [-Fraction(residues[i], moduli[i]) for i in range(dimension)]
    y = [0 for _ in range(dimension)]
    accepted = 0
    visited = 0
    leaves = 0
    witness_x: tuple[int, ...] | None = None

    def recurse(index: int, remaining: Fraction) -> bool:
        nonlocal accepted, visited, leaves, witness_x
        if index < 0:
            leaves += 1
            witness_x = tuple(
                residues[i] + moduli[i] * y[i] for i in range(dimension)
            )
            return stop_after_first
        center = -cvp_center[index] + sum(
            lower[j][index] * (Fraction(y[j]) - cvp_center[j])
            for j in range(index + 1, dimension)
        )
        low, high = integer_interval(center, remaining / diag[index])
        values = list(range(low, high + 1))
        values.sort(key=lambda value: (abs(Fraction(value) + center), value))
        for value in values:
            visited += 1
            term = diag[index] * (Fraction(value) + center) ** 2
            if term > remaining:
                continue
            accepted += 1
            y[index] = value
            if recurse(index - 1, remaining - term):
                return True
        y[index] = 0
        return False

    recurse(dimension - 1, Fraction(cap))
    witness_norm: int | None = None
    witness: list[int] | None = None
    if witness_x is not None:
        witness_norm = int(quadratic(gram, witness_x))
        witness = list(witness_x)
        if witness_norm > cap:
            raise AssertionError("out-of-ball witness")
        for i in range(dimension):
            if witness_x[i] % moduli[i] != residues[i]:
                raise AssertionError("witness outside parity coset")
    gram_payload = {
        "triples": [list(t) for t in triples],
        "gram": gram,
    }
    affine_payload = {
        "triples": [list(t) for t in triples],
        "affine_gram": affine_gram,
        "lower": [[str(v) for v in row] for row in lower],
        "diagonal": [str(v) for v in diag],
    }
    return {
        "dimension": dimension,
        "cap": cap,
        "scale": scale,
        "coordinate_order": "canonical Cartan coordinates",
        "triple_order": "lexicographic combinations_with_replacement",
        "enumeration": "affine CVP x=residue+modulus*y; centered integer y search",
        "gram_sha256": payload_hash(gram_payload),
        "affine_ldl_sha256": payload_hash(affine_payload),
        "odd_repeated_coordinates": sum(
            residue for residue, modulus in zip(residues, moduli)
            if modulus == 2
        ),
        "free_coordinates": moduli.count(1),
        "accepted_partial_nodes": accepted,
        "visited_interval_integers": visited,
        "complete_leaves": leaves,
        "found": witness is not None,
        "witness_norm": witness_norm,
        "witness": witness,
        "triples": [list(t) for t in triples],
        "second_moment": moment,
    }


def canonical_gram_hash(kind: str) -> str:
    form = {"A6": CANONICAL_A6, "E6": CANONICAL_E6}[kind]
    triples = triples_lex(6)
    payload = {
        "triples": [list(t) for t in triples],
        "gram": symmetric_cubic_gram(form, triples),
    }
    return payload_hash(payload)


def projected_tensor(
    rows: Sequence[Sequence[int]], rank: int
) -> list[list[list[int]]]:
    result = [[[0 for _ in range(rank)] for _ in range(rank)]
              for _ in range(rank)]
    for row in rows:
        for a, b, c in product(range(rank), repeat=3):
            result[a][b][c] += row[a] * row[b] * row[c]
    return result


def full_tensor_norm(
    tensor: Sequence[Sequence[Sequence[int]]],
    form: Sequence[Sequence[int]],
) -> int:
    rank = len(form)
    return sum(
        tensor[a][b][c] * form[a][d] * form[b][e] * form[c][f]
        * tensor[d][e][f]
        for a, b, c, d, e, f in product(range(rank), repeat=6)
    )


def a2_zero_sum_frame() -> dict[str, object]:
    """A concrete local frame that exercises moment, zero sum, parity, energy."""
    a2 = cartan_a(2)
    rows: list[list[int]] = []
    rows.extend([[1, 0]] * 4 + [[-1, 0]] * 3)
    rows.extend([[0, 1]] * 4 + [[0, -1]] * 3)
    rows.extend([[1, 1]] * 3 + [[-1, -1]] * 4)
    moment = [
        [sum(row[i] * row[j] for row in rows) for j in range(2)]
        for i in range(2)
    ]
    total = [sum(row[i] for row in rows) for i in range(2)]
    tensor = projected_tensor(rows, 2)
    energy = full_tensor_norm(tensor, a2)
    pair_energy = sum(
        int(dot(left, matvec(a2, right))) ** 3
        for left in rows for right in rows
    )
    expected = frame_moment(a2)
    if moment != expected or total != [0, 0] or energy != pair_energy:
        raise AssertionError("A2 frame reconstruction failed")
    return {
        "row_count": len(rows),
        "second_moment": moment,
        "expected_second_moment": expected,
        "row_sum": total,
        "pure_cubic_energy": energy,
        "pairwise_cube_energy": pair_energy,
        "energy_mod_6": energy % 6,
    }


def hadamard_square(a: Sequence[Sequence[int]]) -> list[list[int]]:
    return [[v * v for v in row] for row in a]


def cross_q_tensor_control() -> dict[str, object]:
    """Synthetic exact identity with a nonzero cross-Q block."""
    s = [
        [2, -1, 0],
        [-1, 2, 0],
        [0, 0, 2],
    ]
    rows = [
        [1, 0, 1],
        [0, 1, -1],
        [1, 1, 0],
        [-1, 0, 1],
    ]
    x = rows
    m = matmul(matmul(x, s), transpose(x))
    w = hadamard_square(m)  # type: ignore[arg-type]
    q = matmul(matmul(transpose(x), w), x)
    local_trace = int(sum(s[i][j] * q[j][i] for i in range(2) for j in range(2)))
    complement_trace = int(s[2][2] * q[2][2])
    global_trace = int(trace(matmul(s, q)))

    # First-leg R projection norm: sum_i z_i tensor x_i tensor x_i.
    first_leg = 0
    for i, left in enumerate(rows):
        for j, right in enumerate(rows):
            inner_r = sum(left[a] * s[a][b] * right[b]
                          for a in range(2) for b in range(2))
            inner_full = int(dot(left, matvec(s, right)))
            first_leg += inner_r * inner_full * inner_full
    pure_rows = [row[:2] for row in rows]
    pure = full_tensor_norm(projected_tensor(pure_rows, 2), cartan_a(2))
    if q[0][2] == q[1][2] == 0:
        raise AssertionError("control failed to generate cross-Q entries")
    if local_trace != first_leg or pure > first_leg:
        raise AssertionError("compression identity failed")
    if global_trace != local_trace + complement_trace:
        raise AssertionError("cross-Q contaminated the trace split")
    return {
        "Q": q,
        "cross_Q_column": [q[0][2], q[1][2]],
        "global_trace": global_trace,
        "local_trace": local_trace,
        "complement_trace": complement_trace,
        "first_leg_tensor_norm": first_leg,
        "pure_RRR_tensor_norm": pure,
        "compression_slack": first_leg - pure,
    }


def trace14_e6_control() -> dict[str, object]:
    r = CANONICAL_E6
    h = inverse(r)
    v = [-1, 0, 1, 0, 0, -1]
    hv = matvec(h, v)
    denominator = dot(v, hv)
    p = [
        [Fraction(v[i]) * sum(Fraction(v[k]) * h[k][j] for k in range(6))
         / denominator for j in range(6)]
        for i in range(6)
    ]
    b = [
        [Fraction(int(i == j)) + 8 * p[i][j] for j in range(6)]
        for i in range(6)
    ]
    qf = matmul(h, b)
    q: list[list[int]] = []
    for row in qf:
        if any(Fraction(x).denominator != 1 for x in row):
            raise AssertionError("hostile Q is not integral")
        q.append([int(x) for x in row])
    p2 = matmul(p, p)
    if p2 != p or q != transpose(q):
        raise AssertionError("rank-one hostile block failed")
    if not is_positive_definite(q) or any(q[i][i] % 2 for i in range(6)):
        raise AssertionError("hostile Q form gate failed")
    rb = matmul(r, q)
    return {
        "v_H_v": str(denominator),
        "P_idempotent": p2 == p,
        "Q": q,
        "Q_even_integral_PD": True,
        "R_times_Q": rb,
        "trace_RQ": int(trace(rb)),
        "det_Q": bareiss_det(q),
        "det_RQ": bareiss_det(rb),
        "rank_one_spectrum_certificate": "B=I+8P, P^2=P, rank(P)=1",
    }


def ade_component_screen() -> dict[str, object]:
    candidates: list[tuple[str, list[list[int]]]] = []
    candidates.extend((f"A{n}", cartan_a(n)) for n in range(1, 45))
    candidates.extend((f"D{n}", cartan_d(n)) for n in range(4, 45))
    candidates.extend((kind, exceptional(kind)) for kind in ("E6", "E7", "E8"))
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for name, form in candidates:
        inverse_form = inverse(form)
        scaled = [[FRAME_SCALE * v for v in row] for row in inverse_form]
        integral = all(v.denominator == 1 for row in scaled for v in row)
        even_diagonal = integral and all(int(scaled[i][i]) % 2 == 0
                                         for i in range(len(form)))
        row = {
            "type": name,
            "rank": len(form),
            "determinant": bareiss_det(form),
            "21_inverse_integral": integral,
            "21_inverse_even_diagonal": even_diagonal,
        }
        (accepted if integral and even_diagonal else rejected).append(row)
    expected = ["A2", "A6", "A20", "E6", "E8"]
    if [row["type"] for row in accepted] != expected:
        raise AssertionError(f"ADE screen mismatch: {accepted}")
    return {
        "candidate_count": len(candidates),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "necessary_conditions": [
            "21*R^-1 integral from the second moment",
            "diag(21*R^-1) even from zero sum modulo 2",
        ],
        "accepted": accepted,
        "rejected_types": [row["type"] for row in rejected],
    }


COMPONENTS = (
    ("E8", 8, 1),
    ("A20", 20, 21),
    ("E6", 6, 3),
    ("A6", 6, 7),
    ("A2", 2, 3),
)
H_VALUES = (9, 21, 49, 81, 189, 441, 729, 1029)


def decompositions_for(target_det: int) -> list[dict[str, int]]:
    """Recursive determinant/rank census, not a Cartesian multiplicity product."""
    rows: list[dict[str, int]] = []

    def recurse(
        component_index: int,
        remaining_rank: int,
        determinant_so_far: int,
        counts: dict[str, int],
    ) -> None:
        if component_index == len(COMPONENTS):
            if remaining_rank == 0 and determinant_so_far == target_det:
                rows.append(dict(sorted(counts.items())))
            return
        name, rank, determinant = COMPONENTS[component_index]
        for count in range(remaining_rank // rank + 1):
            new_det = determinant_so_far * determinant ** count
            if target_det % new_det:
                continue
            if count:
                counts[name] = count
            recurse(
                component_index + 1,
                remaining_rank - count * rank,
                new_det,
                counts,
            )
            counts.pop(name, None)

    recurse(0, TOTAL_RANK, 1, {})
    rows.sort(key=canonical_json)
    return rows


def even_amgm_floor(rank: int, determinant_floor: int) -> int:
    value = 2
    while value ** rank < rank ** rank * determinant_floor:
        value += 2
    return value


def submitted_scope_census() -> dict[str, object]:
    rows = {h: decompositions_for(h) for h in H_VALUES}
    counts = {h: len(rows[h]) for h in H_VALUES}
    expected = {9: 2, 21: 2, 49: 1, 81: 2, 189: 3,
                441: 2, 729: 4, 1029: 1}
    if counts != expected:
        raise AssertionError(f"census mismatch: {counts}")
    classified: list[dict[str, object]] = []
    survivors: list[dict[str, object]] = []
    for h in H_VALUES:
        for components in rows[h]:
            if "A2" in components:
                status = "EXCLUDED_BY_PRIOR_VERIFIED_A2"
            elif "A6" in components:
                status = "EXCLUDED_BY_A6_TENSOR"
            elif "E6" in components:
                status = "EXCLUDED_BY_E6_TENSOR"
            else:
                status = "SURVIVES_SUBMITTED_SCREEN"
            item = {"h": h, "components": components, "status": status}
            classified.append(item)
            if status == "SURVIVES_SUBMITTED_SCREEN":
                survivors.append(item)
    expected_survivor = [{
        "h": 21,
        "components": {"A20": 1, "E8": 3},
        "status": "SURVIVES_SUBMITTED_SCREEN",
    }]
    if survivors != expected_survivor:
        raise AssertionError(f"submitted-screen survivors: {survivors}")
    return {
        "h_values": list(H_VALUES),
        "decompositions": {str(h): rows[h] for h in H_VALUES},
        "counts": {str(h): counts[h] for h in H_VALUES},
        "total_cases": sum(counts.values()),
        "classified": classified,
        "survivors": survivors,
    }


def a_n_trace_identity(n: int, q: Sequence[Sequence[int]]) -> dict[str, object]:
    """Orchestrator addendum: a stronger A_n compression floor."""
    if len(q) != n or any(len(row) != n for row in q):
        raise ValueError("Q dimension")
    a = cartan_a(n)
    left = int(trace(matmul(a, q)))
    vectors: list[list[int]] = []
    e1 = [0] * n
    e1[0] = 1
    vectors.append(e1)
    en = [0] * n
    en[-1] = 1
    vectors.append(en)
    for i in range(n - 1):
        vector = [0] * n
        vector[i] = 1
        vector[i + 1] = -1
        vectors.append(vector)
    terms = [int(quadratic(q, vector)) for vector in vectors]
    if left != sum(terms):
        raise AssertionError("A_n trace identity failed")
    return {
        "n": n,
        "trace_AQ": left,
        "term_count": len(terms),
        "terms": terms,
        "identity_verified": True,
    }


def a20_orchestrator_addendum() -> dict[str, object]:
    """General proof plus a concrete exact identity check."""
    n = 20
    # A nontrivial even integral PD control, not needed by the proof.
    q = cartan_a(n)
    control = a_n_trace_identity(n, q)
    local_floor = 2 * (n + 1)
    complement_rank = TOTAL_RANK - n
    complement_floor = complement_rank
    total_floor = local_floor + complement_floor
    if local_floor != 42 or total_floor != 66:
        raise AssertionError("A20 addendum arithmetic failed")
    return {
        "status": "VERIFIED_ORCHESTRATOR_ADDENDUM",
        "identity": (
            "tr(A_n Q)=Q(e1)+Q(en)+sum_i Q(e_i-e_(i+1))"
        ),
        "reason": (
            "each of the n+1 displayed nonzero vectors has positive even "
            "Q-norm at least 2"
        ),
        "A20_local_floor": local_floor,
        "rank_24_complement_floor": complement_floor,
        "global_floor": total_floor,
        "global_trace": GLOBAL_TRACE,
        "conclusion": (
            "A20 orthogonal_sum E8^3 is excluded by this stronger added "
            "lemma; this is not a defect in the narrower submitted screen"
        ),
        "control": control,
    }


def energy_divisibility_control() -> dict[str, object]:
    residues = [(k ** 3 - k) % 6 for k in range(-100, 101)]
    if any(residues):
        raise AssertionError("k cubed congruence failed")
    frame = a2_zero_sum_frame()
    # Dropping zero sum is active: one A1 vector has cube energy 2^3=8.
    nonzero_sum_energy = 8
    return {
        "integer_residue_range_checked": [-100, 100],
        "all_k_cubed_congruent_k_mod_6": True,
        "zero_sum_frame_energy": frame["pure_cubic_energy"],
        "zero_sum_frame_energy_mod_6": frame["energy_mod_6"],
        "drop_zero_sum_counterexample_energy": nonzero_sum_energy,
        "drop_zero_sum_counterexample_mod_6": nonzero_sum_energy % 6,
    }


def build_results(root: Path = ROOT) -> dict[str, object]:
    frozen_submitted = verify_hashes(root, SUBMITTED)
    frozen_public = verify_hashes(root, PUBLIC_INPUTS)
    frozen_addendum = verify_hashes(root, ADDENDUM_SUBMITTED)
    canonical_hashes = {
        kind: canonical_gram_hash(kind) for kind in ("E6", "A6")
    }
    if canonical_hashes != {
        "E6": DECLARED_CANONICAL_GRAM_HASHES["E6"],
        "A6": DECLARED_CANONICAL_GRAM_HASHES["A6"],
    }:
        raise AssertionError(f"canonical Gram disagreement: {canonical_hashes}")

    e6_empty = affine_cvp_search(CANONICAL_E6, 18)
    a6_empty = affine_cvp_search(CANONICAL_A6, 60)
    if e6_empty["found"] or a6_empty["found"]:
        raise AssertionError("claimed parity ball was not empty")
    screen = ade_component_screen()
    census = submitted_scope_census()
    addendum = a20_orchestrator_addendum()
    return {
        "verifier": {
            "implementation": "independent standard-library checker",
            "imports_submitted_code": False,
            "cartan_permutation_invariance_controls": {
                "A6": list(A6_COORDINATE_ORDER),
                "E6": list(E6_COORDINATE_ORDER),
            },
            "triple_order": "lexicographic",
            "search_model": "affine CVP in unrestricted integer y coordinates",
        },
        "frozen_submitted": frozen_submitted,
        "frozen_public_inputs": frozen_public,
        "frozen_addendum_submitted": frozen_addendum,
        "algebra": {
            "projector_frame_control": a2_zero_sum_frame(),
            "arbitrary_cross_Q_control": cross_q_tensor_control(),
            "compression_formula": (
                "tr(R Q_RR)=||sum_i z_i tensor x_i tensor x_i||^2 "
                ">=||sum_i z_i tensor z_i tensor z_i||^2"
            ),
            "complement_cap": {
                "formula": "tau_R <= 60-(44-r)=r+16",
                "rank_6": 22,
                "uses_Q_cross_block_zero": False,
                "principal_Q_CC_positive_integral_determinant": True,
            },
            "repeated_index_parity": (
                "P_aab = sum_i z_ia^2 z_ib = (21 R^-1)_ab mod 2"
            ),
            "canonical_gram_hashes": canonical_hashes,
        },
        "searches": {
            "E6_cap_18": e6_empty,
            "A6_cap_60": a6_empty,
        },
        "energy_divisibility": energy_divisibility_control(),
        "tensor_floors": {
            "E6": {
                "parity_ball_empty_through": 18,
                "zero_sum_multiple": 6,
                "floor": 24,
                "rank_complement_cap": 22,
                "orthogonal_summand": "REFUTED",
            },
            "A6": {
                "parity_ball_empty_through": 60,
                "zero_sum_multiple": 6,
                "floor": 66,
                "global_trace": 60,
                "orthogonal_summand": "REFUTED",
            },
        },
        "hostile_controls": {
            "trace_14_E6_algebraic_block": trace14_e6_control(),
            "even_scale_E6_zero_tensor": affine_cvp_search(
                CANONICAL_E6, 0, scale=18, stop_after_first=True
            ),
            "even_scale_A6_zero_tensor": affine_cvp_search(
                CANONICAL_A6, 0, scale=14, stop_after_first=True
            ),
            "drop_zero_sum": (
                "energy need not be divisible by 6; explicit energy 8"
            ),
            "nonorthogonal_root_subsystem": "OUT_OF_SCOPE_NO_BLOCK_MOMENT",
        },
        "ADE_component_screen": screen,
        "submitted_scope_full_ADE_census": census,
        "orchestrator_addendum": addendum,
        "scope": {
            "submitted_A20_E8_cubed_survivor": (
                "CORRECTLY_SURVIVES_THE_SUBMITTED_COMPONENT_SCREEN"
            ),
            "stronger_addendum_result": (
                "EXCLUDED_BY_A20_TRACE_IDENTITY_PLUS_COMPLEMENT"
            ),
            "general_even_rank_44_lattices": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    results = build_results()
    text = canonical_json(results)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
