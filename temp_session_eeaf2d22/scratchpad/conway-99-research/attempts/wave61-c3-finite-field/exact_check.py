#!/usr/bin/env python3
"""Wave 61 finite-field and bilinear-form discovery for kappa=3.

This checker imports no Wave 60 code.  It consumes only the frozen component
census, rebuilds every target Gram matrix, and labels all conclusions as
discovery-side necessary conditions or countercontrols.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import itertools
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "attempts" / "wave60-c3-incidence-design" / "component-census.json"
OUTPUT = HERE / "exact-results.json"
MIN_FREE_MEMORY_PERCENT = Fraction(20, 1)
PRIMES = (3, 5, 7, 11)


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_memory_percent() -> Fraction:
    if os.name == "nt":
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return Fraction(100 * status.ullAvailPhys, status.ullTotalPhys)
    pages = os.sysconf("SC_AVPHYS_PAGES")
    total = os.sysconf("SC_PHYS_PAGES")
    return Fraction(100 * pages, total)


def require_memory_headroom() -> Fraction:
    available = free_memory_percent()
    if available < MIN_FREE_MEMORY_PERCENT:
        raise RuntimeError(
            f"free physical memory {float(available):.2f}% is below 20%"
        )
    return available


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    for raw in (HERE / "input-freeze.sha256").read_text(
        encoding="utf-8"
    ).splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split(maxsplit=1)
        actual = sha256(ROOT / relative.strip())
        assert actual == expected, (relative, expected, actual)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def load_types() -> list[dict]:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    assert data["claim_label"] == "UNKNOWN"
    census = data["component_census"]
    assert census["fibre_preserving_type_count"] == 18
    types = census["types"]
    assert [record["type_index"] for record in types] == list(range(18))
    return types


def local_rows(record: dict) -> tuple[int, ...]:
    rows = [0] * 12
    for left, right in record["edges"]:
        assert 0 <= left < right < 12
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    assert {row.bit_count() for row in rows} == {3}
    return tuple(rows)


def local_gram(record: dict) -> tuple[tuple[int, ...], ...]:
    adjacency = local_rows(record)
    matrix = []
    for left in range(12):
        row = []
        for right in range(12):
            common = (adjacency[left] & adjacency[right]).bit_count()
            row.append(
                (12 if left == right else 0)
                - (1 if adjacency[left] & (1 << right) else 0)
                + 2
                - (1 if left // 4 == right // 4 else 0)
                - common
            )
        assert min(row) >= 0
        matrix.append(tuple(row))
    assert [matrix[i][i] for i in range(12)] == [10] * 12
    return tuple(matrix)


def global_vertex(component: int, local_vertex: int) -> int:
    fibre, local_index = divmod(local_vertex, 4)
    return fibre * 12 + component * 4 + local_index


def union_rows(records: Sequence[dict]) -> tuple[int, ...]:
    assert len(records) == 3
    rows = [0] * 36
    for component, record in enumerate(records):
        for left, right in record["edges"]:
            global_left = global_vertex(component, left)
            global_right = global_vertex(component, right)
            rows[global_left] |= 1 << global_right
            rows[global_right] |= 1 << global_left
    assert {row.bit_count() for row in rows} == {3}
    return tuple(rows)


def target_gram(records: Sequence[dict]) -> tuple[tuple[int, ...], ...]:
    adjacency = union_rows(records)
    matrix = []
    for left in range(36):
        row = []
        for right in range(36):
            common = (adjacency[left] & adjacency[right]).bit_count()
            value = (
                (12 if left == right else 0)
                - (1 if adjacency[left] & (1 << right) else 0)
                + 2
                - (1 if left // 12 == right // 12 else 0)
                - common
            )
            assert value >= 0
            row.append(value)
        matrix.append(tuple(row))
    assert all(matrix[i][j] == matrix[j][i] for i in range(36) for j in range(36))
    assert [matrix[i][i] for i in range(36)] == [10] * 36
    return tuple(matrix)


def rank_f2(matrix: Sequence[Sequence[int]]) -> int:
    rows = [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (position for position in range(rank, len(rows))
             if rows[position] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for position in range(len(rows)):
            if position != rank and rows[position] >> column & 1:
                rows[position] ^= rows[rank]
        rank += 1
    return rank


def rref_f2(matrix: Sequence[Sequence[int]]) -> tuple[list[int], list[int]]:
    width = len(matrix[0])
    rows = [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    pivots = []
    rank = 0
    for column in range(width):
        pivot = next(
            (position for position in range(rank, len(rows))
             if rows[position] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for position in range(len(rows)):
            if position != rank and rows[position] >> column & 1:
                rows[position] ^= rows[rank]
        pivots.append(column)
        rank += 1
    return rows[:rank], pivots


def nullspace_f2(matrix: Sequence[Sequence[int]]) -> list[int]:
    rows, pivots = rref_f2(matrix)
    width = len(matrix[0])
    pivot_set = set(pivots)
    basis = []
    for free in range(width):
        if free in pivot_set:
            continue
        vector = 1 << free
        for row, pivot in zip(rows, pivots):
            if row >> free & 1:
                vector |= 1 << pivot
        basis.append(vector)
    return basis


def bit_span_rank(vectors: Sequence[int]) -> int:
    basis: dict[int, int] = {}
    for original in vectors:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def parity_indicators() -> list[int]:
    fibres = [((1 << 12) - 1) << (12 * fibre) for fibre in range(3)]
    components = []
    for component in range(3):
        mask = 0
        for fibre in range(3):
            mask |= ((1 << 4) - 1) << (12 * fibre + 4 * component)
        components.append(mask)
    indicators = fibres + components
    assert bit_span_rank(indicators) == 5
    assert fibres[0] ^ fibres[1] ^ fibres[2] == (
        components[0] ^ components[1] ^ components[2]
    )
    return indicators


def matrix_times_mask_f2(matrix: Sequence[Sequence[int]], mask: int) -> int:
    output = 0
    for row_index, row in enumerate(matrix):
        dot = 0
        selected = mask
        while selected:
            bit = selected & -selected
            selected ^= bit
            dot ^= row[bit.bit_length() - 1] & 1
        output |= dot << row_index
    return output


def half_weight_quadratic(matrix: Sequence[Sequence[int]], mask: int) -> int:
    # Every hypothetical B row has weight 10.  For x selecting rows,
    # wt(B^T x)/2 = |x| + sum_{i<j} G_ij x_i x_j (mod 2).
    value = mask.bit_count() & 1
    selected_vertices = [
        vertex for vertex in range(36) if mask >> vertex & 1
    ]
    for left_index, left in enumerate(selected_vertices):
        for right in selected_vertices[left_index + 1:]:
            value ^= matrix[left][right] & 1
    return value


def f2_form_invariants(matrix: Sequence[Sequence[int]]) -> dict:
    assert all(matrix[index][index] % 2 == 0 for index in range(36))
    rank = rank_f2(matrix)
    assert rank % 2 == 0
    radical = nullspace_f2(matrix)
    assert len(radical) == 36 - rank
    indicators = parity_indicators()
    assert all(matrix_times_mask_f2(matrix, vector) == 0 for vector in indicators)
    assert all(half_weight_quadratic(matrix, vector) == 0 for vector in indicators)
    q_values = [half_weight_quadratic(matrix, vector) for vector in radical]
    q_nonzero = any(q_values)
    q_zero_radical_dimension = len(radical) - (1 if q_nonzero else 0)
    assert q_zero_radical_dimension >= 5
    residual_singular_radical = q_zero_radical_dimension - 5
    quadratic_embedding_dimension_slack = (
        58
        - (
            rank
            + 2 * residual_singular_radical
            + (1 if q_nonzero else 0)
        )
    )
    assert quadratic_embedding_dimension_slack >= 0
    return {
        "rank": rank,
        "radical_dimension": len(radical),
        "quadratic_nonzero_on_radical": q_nonzero,
        "quadratic_zero_radical_dimension": q_zero_radical_dimension,
        "quadratic_embedding_dimension_slack_after_known_kernel":
            quadratic_embedding_dimension_slack,
        "known_parity_kernel_dimension": 5,
        "rank_B_upper_bound_from_known_kernel": 31,
        "alternating": True,
        "alternating_witt_class": f"unique symplectic class of rank {rank}",
    }


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    rank = 0
    width = len(rows[0])
    for column in range(width):
        pivot = next(
            (position for position in range(rank, len(rows))
             if rows[position][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(value * inverse) % prime for value in rows[rank]]
        for position in range(rank + 1, len(rows)):
            coefficient = rows[position][column]
            if coefficient:
                rows[position] = [
                    (left - coefficient * right) % prime
                    for left, right in zip(rows[position], rows[rank])
                ]
        rank += 1
    return rank


def odd_form_invariants(
    matrix: Sequence[Sequence[int]], prime: int
) -> dict:
    work = [[value % prime for value in row] for row in matrix]
    pivots = []
    active = len(work)
    while active:
        diagonal = next(
            (index for index in range(active) if work[index][index]),
            None,
        )
        if diagonal is None:
            off = next(
                (
                    (left, right)
                    for left in range(active)
                    for right in range(left + 1, active)
                    if work[left][right]
                ),
                None,
            )
            if off is None:
                break
            left, right = off
            # Replace e_left by e_left+e_right, a congruence operation.
            # Keep a snapshot: the new diagonal contains both off-diagonal
            # terms, which an in-place row-then-column update can lose.
            previous = [row[:] for row in work]
            for index in range(active):
                if index == left:
                    continue
                value = (
                    previous[left][index] + previous[right][index]
                ) % prime
                work[left][index] = value
                work[index][left] = value
            work[left][left] = (
                previous[left][left]
                + 2 * previous[left][right]
                + previous[right][right]
            ) % prime
            diagonal = left
            assert work[diagonal][diagonal]
        last = active - 1
        if diagonal != last:
            work[diagonal], work[last] = work[last], work[diagonal]
            for row in work:
                row[diagonal], row[last] = row[last], row[diagonal]
        pivot = work[last][last] % prime
        pivots.append(pivot)
        inverse = pow(pivot, -1, prime)
        for left in range(last):
            for right in range(left, last):
                value = (
                    work[left][right]
                    - work[left][last] * work[right][last] * inverse
                ) % prime
                work[left][right] = value
                work[right][left] = value
        active -= 1
    rank = len(pivots)
    assert rank == rank_mod_prime(matrix, prime)
    determinant_class = 1
    for pivot in pivots:
        determinant_class = determinant_class * pivot % prime
    legendre = (
        0 if rank == 0
        else (1 if pow(determinant_class, (prime - 1) // 2, prime) == 1 else -1)
    )
    if rank % 2 == 0:
        hyperbolic_determinant = pow((-1) % prime, rank // 2, prime)
        hyperbolic_legendre = (
            1
            if pow(hyperbolic_determinant, (prime - 1) // 2, prime) == 1
            else -1
        )
        anisotropic_dimension = 0 if legendre == hyperbolic_legendre else 2
    else:
        anisotropic_dimension = 1
    return {
        "rank": rank,
        "discriminant_legendre": legendre,
        "anisotropic_dimension": anisotropic_dimension,
        "embedding_in_I60_blocked": False,
        "reason": (
            "the complementary dimension is at least 28 and either finite-field "
            "discriminant class is available there"
        ),
    }


PAIR_LIST = tuple(itertools.combinations(range(12), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIR_LIST)}
GLOBAL_PAIR_LIST = tuple(itertools.combinations(range(36), 2))
GLOBAL_PAIR_INDEX = {
    pair: index for index, pair in enumerate(GLOBAL_PAIR_LIST)
}


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    profile = [0, 0, 0]
    profile[pair[0] // 4] += 1
    profile[pair[1] // 4] += 1
    return tuple(profile)


PAIR_PROFILES = tuple(pair_profile(pair) for pair in PAIR_LIST)
PROFILE_VALUES = tuple(sorted(set(PAIR_PROFILES)))
PROFILE_INDEX = {profile: index for index, profile in enumerate(PROFILE_VALUES)}


def allowed_local_pairs(record: dict) -> dict:
    gram = local_gram(record)
    allowed = [[] for _ in PROFILE_VALUES]
    rhs = 0
    target_sum = 0
    for index, (left, right) in enumerate(PAIR_LIST):
        value = gram[left][right]
        target_sum += value
        if value & 1:
            rhs |= 1 << index
        if value > 0:
            allowed[PROFILE_INDEX[PAIR_PROFILES[index]]].append(index)
    assert target_sum == 60
    return {
        "allowed_by_profile": tuple(tuple(values) for values in allowed),
        "rhs_parity": rhs,
        "target_sum": target_sum,
        "positive_pair_count": sum(map(len, allowed)),
    }


PROFILE_TRIPLES = tuple(
    (left, middle, right)
    for left in range(len(PROFILE_VALUES))
    for middle in range(len(PROFILE_VALUES))
    for right in range(len(PROFILE_VALUES))
    if tuple(
        PROFILE_VALUES[left][coordinate]
        + PROFILE_VALUES[middle][coordinate]
        + PROFILE_VALUES[right][coordinate]
        for coordinate in range(3)
    ) == (2, 2, 2)
)
assert len(PROFILE_TRIPLES) == 21


def xor_basis_add(basis: dict[int, int], original: int) -> None:
    value = original
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return


def xor_basis_contains(basis: dict[int, int], original: int) -> bool:
    value = original
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            return False
        value ^= basis[pivot]
    return True


def global_pair_bit(component: int, pair_index: int) -> int:
    local_left, local_right = PAIR_LIST[pair_index]
    pair = tuple(sorted((
        global_vertex(component, local_left),
        global_vertex(component, local_right),
    )))
    return 1 << GLOBAL_PAIR_INDEX[pair]


WITHIN_GLOBAL_BITS = tuple(
    tuple(global_pair_bit(component, pair) for pair in range(66))
    for component in range(3)
)


def cross_global_bit(
    left_component: int,
    left_pair_index: int,
    right_component: int,
    right_pair_index: int,
) -> int:
    output = 0
    for left_local in PAIR_LIST[left_pair_index]:
        for right_local in PAIR_LIST[right_pair_index]:
            pair = tuple(sorted((
                global_vertex(left_component, left_local),
                global_vertex(right_component, right_local),
            )))
            output |= 1 << GLOBAL_PAIR_INDEX[pair]
    assert output.bit_count() == 4
    return output


CROSS_GLOBAL_BITS = {
    (left, right): tuple(
        tuple(
            cross_global_bit(left, left_pair, right, right_pair)
            for right_pair in range(66)
        )
        for left_pair in range(66)
    )
    for left, right in ((0, 1), (0, 2), (1, 2))
}


def pair_inventory_parity_filter(
    records: Sequence[dict],
    matrix: Sequence[Sequence[int]],
) -> dict:
    local = [allowed_local_pairs(record) for record in records]
    local_basis: dict[int, int] = {}
    full_basis: dict[int, int] = {}
    candidate_count = 0
    profile_candidate_counts = {}
    for profile_triple in PROFILE_TRIPLES:
        choices = [
            local[component]["allowed_by_profile"][profile_triple[component]]
            for component in range(3)
        ]
        count = len(choices[0]) * len(choices[1]) * len(choices[2])
        profile_candidate_counts[
            ",".join(map(str, profile_triple))
        ] = count
        candidate_count += count
        for first in choices[0]:
            first_bit = 1 << first
            for second in choices[1]:
                first_second = first_bit | (1 << (66 + second))
                full_first_second = (
                    WITHIN_GLOBAL_BITS[0][first]
                    | WITHIN_GLOBAL_BITS[1][second]
                    | CROSS_GLOBAL_BITS[(0, 1)][first][second]
                )
                for third in choices[2]:
                    syndrome = first_second | (1 << (132 + third))
                    xor_basis_add(local_basis, syndrome)
                    full_syndrome = (
                        full_first_second
                        | WITHIN_GLOBAL_BITS[2][third]
                        | CROSS_GLOBAL_BITS[(0, 2)][first][third]
                        | CROSS_GLOBAL_BITS[(1, 2)][second][third]
                    )
                    assert full_syndrome.bit_count() == 15
                    xor_basis_add(full_basis, full_syndrome)
    local_rhs = (
        local[0]["rhs_parity"]
        | (local[1]["rhs_parity"] << 66)
        | (local[2]["rhs_parity"] << 132)
    )
    full_rhs = 0
    for index, (left, right) in enumerate(GLOBAL_PAIR_LIST):
        if matrix[left][right] & 1:
            full_rhs |= 1 << index
    local_consistent = xor_basis_contains(local_basis, local_rhs)
    full_consistent = xor_basis_contains(full_basis, full_rhs)
    return {
        "candidate_count_before_exact_multiplicities": candidate_count,
        "local_198_rank": len(local_basis),
        "local_198_rhs_consistent": local_consistent,
        "full_630_rank": len(full_basis),
        "full_630_rhs_consistent": full_consistent,
        "profile_candidate_counts": profile_candidate_counts,
        "scope": (
            "exact F2 relaxation of first all 198 fixed local-pair inventories, "
            "then all 630 within- and cross-component row-pair inventories, "
            "over distinct fibre-compatible pair triples; integer "
            "multiplicities and simultaneous higher overlaps are not imposed"
        ),
    }


def cubic_moment_boundary(matrix: Sequence[Sequence[int]]) -> dict:
    """Check identities forced on a hypothetical third-order moment tensor.

    If T_ijk counts columns containing three distinct rows, every column
    containing a fixed pair {i,j} supplies four choices of k.  Thus
    sum_{k not in {i,j}} T_ijk = 4 G_ij.  The tensor itself is not fixed by G,
    so these identities expose rather than close the degree-three boundary.
    """
    row_pair_sums = [
        sum(matrix[row][other] for other in range(36) if other != row)
        for row in range(36)
    ]
    total_pair_count = sum(
        matrix[left][right] for left, right in GLOBAL_PAIR_LIST
    )
    assert set(row_pair_sums) == {50}
    assert total_pair_count == 900
    pair_margin_rhs = Counter(
        4 * matrix[left][right] for left, right in GLOBAL_PAIR_LIST
    )
    per_row_triple_count = {
        row_pair_sum * 2 // 1 for row_pair_sum in set(row_pair_sums)
    }
    # The preceding expression is the ordered j,k count.  Divide by two to
    # count unordered pairs {j,k}.
    assert per_row_triple_count == {100}
    total_triple_count = 4 * total_pair_count // 3
    assert total_triple_count == 1200
    return {
        "third_order_variable": (
            "T_ijk = number of columns containing distinct rows i,j,k"
        ),
        "fixed_pair_margin_identity": (
            "sum_{k not in {i,j}} T_ijk = 4 G_ij"
        ),
        "pair_margin_rhs_histogram": {
            str(value): count
            for value, count in sorted(pair_margin_rhs.items())
        },
        "derived_triples_through_each_row": 100,
        "derived_total_triple_incidence": total_triple_count,
        "identity_consistent": True,
        "obstruction_found": False,
        "missing_data": (
            "G fixes only the pair margins of T; nonnegative integral T and "
            "its realization by the same 60 distinct six-subsets remain free"
        ),
    }


def cell_indicator_masks() -> list[int]:
    masks = []
    for component in range(3):
        for fibre in range(3):
            masks.append(((1 << 4) - 1) << (12 * fibre + 4 * component))
    return masks


def cell_target_moment(matrix: Sequence[Sequence[int]]) -> int:
    cells = cell_indicator_masks()
    output = 0
    for left_index, left_mask in enumerate(cells):
        for right_index, right_mask in enumerate(cells):
            value = 0
            left_vertices = [
                vertex for vertex in range(36) if left_mask >> vertex & 1
            ]
            right_vertices = [
                vertex for vertex in range(36) if right_mask >> vertex & 1
            ]
            for left in left_vertices:
                for right in right_vertices:
                    value ^= matrix[left][right] & 1
            output |= value << (9 * left_index + right_index)
    return output


def pattern_parity_moment_filter(matrix: Sequence[Sequence[int]]) -> dict:
    # The 21 integral 3x3 row/column-sum-two patterns are exactly the ordered
    # profile triples above.  Reduce cell counts modulo two.
    basis: dict[int, int] = {}
    pattern_weights = Counter()
    for triple in PROFILE_TRIPLES:
        cell_mask = 0
        for component, profile_index in enumerate(triple):
            profile = PROFILE_VALUES[profile_index]
            for fibre, count in enumerate(profile):
                if count & 1:
                    cell_mask |= 1 << (3 * component + fibre)
        weight = cell_mask.bit_count()
        pattern_weights[weight] += 1
        moment = 1 << 81  # parity of total number of columns
        for left in range(9):
            if not (cell_mask >> left & 1):
                continue
            for right in range(9):
                if cell_mask >> right & 1:
                    moment ^= 1 << (9 * left + right)
        xor_basis_add(basis, moment)
    target = cell_target_moment(matrix)  # 60 is even, so total bit is zero.
    return {
        "integral_pattern_count": 21,
        "binary_pattern_image": {"weight_0": 6, "weight_4": 9, "weight_6": 6},
        "observed_pattern_weights": dict(sorted(pattern_weights.items())),
        "moment_system_rank": len(basis),
        "rhs_consistent": xor_basis_contains(basis, target),
        "scope": (
            "parities of the 21 component/fibre pattern counts only; this is "
            "strictly weaker than the 198 local-pair inventory system"
        ),
    }


def small_countermodels() -> dict:
    # Two independent even rows with disjoint supports have zero Gram matrix,
    # refuting rank(B)=rank(BB^T) in characteristic two.
    rows = (0b0011, 0b1100)
    gram = [
        [(rows[i] & rows[j]).bit_count() & 1 for j in range(2)]
        for i in range(2)
    ]
    assert rank_f2(gram) == 0
    assert bit_span_rank(rows) == 2
    # A hyperbolic alternating block is itself a Gram matrix of even vectors:
    # 1100 and 0110 have dot product one.
    hyperbolic_rows = (0b1100, 0b0110)
    hyperbolic = [
        [
            (hyperbolic_rows[i] & hyperbolic_rows[j]).bit_count() & 1
            for j in range(2)
        ]
        for i in range(2)
    ]
    assert hyperbolic == [[0, 1], [1, 0]]
    return {
        "rank_equality_false": {
            "rank_B": 2,
            "rank_BBt": 0,
            "rows_binary": ["0011", "1100"],
        },
        "alternating_singularity_not_obstruction": {
            "target": [[0, 1], [1, 0]],
            "even_row_factor": ["1100", "0110"],
        },
        "six_indicators_independent_false": {
            "span_dimension": 5,
            "relation": "F0+F1+F2=C0+C1+C2=all-ones",
        },
    }


def histogram_key(values: Sequence[object]) -> str:
    return ",".join(map(str, values))


def build_results() -> dict:
    start_memory = require_memory_headroom()
    check_frozen_inputs()
    types = load_types()
    triples = list(itertools.combinations_with_replacement(range(18), 3))
    assert len(triples) == 1140

    f2_hist: Counter[int] = Counter()
    f2_q_hist: Counter[tuple[int, bool]] = Counter()
    quadratic_slack_hist = Counter()
    odd_rank_hist = {prime: Counter() for prime in PRIMES}
    odd_form_hist = {prime: Counter() for prime in PRIMES}
    local_pair_consistency = Counter()
    local_pair_rank_hist = Counter()
    full_pair_consistency = Counter()
    full_pair_rank_hist = Counter()
    pattern_consistency = Counter()
    pattern_rank_hist = Counter()
    cubic_margin_hist = Counter()
    records = []

    for index, triple in enumerate(triples):
        if index % 64 == 0:
            require_memory_headroom()
        selected = [types[type_index] for type_index in triple]
        gram = target_gram(selected)
        f2 = f2_form_invariants(gram)
        f2_hist[f2["rank"]] += 1
        f2_q_hist[(f2["rank"], f2["quadratic_nonzero_on_radical"])] += 1
        quadratic_slack_hist[
            f2["quadratic_embedding_dimension_slack_after_known_kernel"]
        ] += 1
        odd = {}
        for prime in PRIMES:
            invariant = odd_form_invariants(gram, prime)
            odd[str(prime)] = invariant
            odd_rank_hist[prime][invariant["rank"]] += 1
            odd_form_hist[prime][
                (
                    invariant["rank"],
                    invariant["discriminant_legendre"],
                    invariant["anisotropic_dimension"],
                )
            ] += 1
        pair_filter = pair_inventory_parity_filter(selected, gram)
        local_pair_consistency[
            pair_filter["local_198_rhs_consistent"]
        ] += 1
        local_pair_rank_hist[pair_filter["local_198_rank"]] += 1
        full_pair_consistency[
            pair_filter["full_630_rhs_consistent"]
        ] += 1
        full_pair_rank_hist[pair_filter["full_630_rank"]] += 1
        pattern_filter = pattern_parity_moment_filter(gram)
        pattern_consistency[pattern_filter["rhs_consistent"]] += 1
        pattern_rank_hist[pattern_filter["moment_system_rank"]] += 1
        cubic = cubic_moment_boundary(gram)
        cubic_margin_hist[
            tuple(sorted(cubic["pair_margin_rhs_histogram"].items()))
        ] += 1
        records.append({
            "triple_index": index,
            "type_triple": list(triple),
            "component_C4": [types[value]["C4"] for value in triple],
            "total_C4": sum(types[value]["C4"] for value in triple),
            "rank_F2_G": f2["rank"],
            "F2_quadratic_nonzero_on_radical":
                f2["quadratic_nonzero_on_radical"],
            "F2_quadratic_zero_radical_dimension":
                f2["quadratic_zero_radical_dimension"],
            "F2_quadratic_embedding_dimension_slack":
                f2[
                    "quadratic_embedding_dimension_slack_after_known_kernel"
                ],
            "odd_prime_forms": odd,
            "pair_inventory_F2": {
                key: value for key, value in pair_filter.items()
                if key != "profile_candidate_counts"
            },
            "pattern_parity_F2": pattern_filter,
            "cubic_moment_boundary": cubic,
        })

    assert sum(f2_hist.values()) == 1140
    result = {
        "schema_version": 1,
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "conditional kappa=3 Wave60 component-type triples; finite-field "
            "Gram and parity relaxations only"
        ),
        "input": {
            "component_type_count": 18,
            "unordered_triples_with_repetition": 1140,
            "no_graph_automorphism_assumed": True,
        },
        "universal_F2_derivation": {
            "six_partition_indicators": 6,
            "indicator_span_dimension": 5,
            "indicator_relation": "F0+F1+F2=C0+C1+C2=all-ones",
            "indicator_span_in_kernel_B_transpose": True,
            "rank_B_upper_bound": 31,
            "G_alternating": True,
            "rank_G_even_and_at_most": 30,
            "ambient_even_space": {
                "space": "E60={v:wt(v) even}",
                "radical": "span(all-ones)",
                "quotient_dimension": 58,
                "quotient_quadratic_Arf_invariant": 1,
                "explanation": (
                    "sum_{v in E60}(-1)^(wt(v)/2)=-2^30, hence the "
                    "58-dimensional quotient has minus type"
                ),
            },
        },
        "triple_census": {
            "rank_F2_G_histogram": {
                str(rank): count for rank, count in sorted(f2_hist.items())
            },
            "rank_F2_and_radical_quadratic_histogram": {
                histogram_key((rank, "q_nonzero" if nonzero else "q_zero")): count
                for (rank, nonzero), count in sorted(f2_q_hist.items())
            },
            "quadratic_embedding_dimension_slack_histogram": {
                str(slack): count
                for slack, count in sorted(quadratic_slack_hist.items())
            },
            "odd_prime_rank_histograms": {
                str(prime): {
                    str(rank): count
                    for rank, count in sorted(odd_rank_hist[prime].items())
                }
                for prime in PRIMES
            },
            "odd_prime_form_histograms": {
                str(prime): {
                    histogram_key(key): count
                    for key, count in sorted(odd_form_hist[prime].items())
                }
                for prime in PRIMES
            },
            "local_pair_inventory_F2_consistency": {
                str(key).lower(): count
                for key, count in sorted(local_pair_consistency.items())
            },
            "local_pair_inventory_F2_rank_histogram": {
                str(rank): count
                for rank, count in sorted(local_pair_rank_hist.items())
            },
            "full_pair_inventory_F2_consistency": {
                str(key).lower(): count
                for key, count in sorted(full_pair_consistency.items())
            },
            "full_pair_inventory_F2_rank_histogram": {
                str(rank): count
                for rank, count in sorted(full_pair_rank_hist.items())
            },
            "pattern_parity_F2_consistency": {
                str(key).lower(): count
                for key, count in sorted(pattern_consistency.items())
            },
            "pattern_parity_F2_rank_histogram": {
                str(rank): count
                for rank, count in sorted(pattern_rank_hist.items())
            },
            "cubic_pair_margin_histogram_type_count":
                len(cubic_margin_hist),
            "records": records,
        },
        "component_pattern_parity": {
            "integral_pattern_types": 21,
            "binary_cycle_space_dimension": 4,
            "binary_images": {
                "zero_from_doubled_matchings": 6,
                "weight_four_cycles": 9,
                "weight_six_cycles": 6,
            },
            "interpretation": (
                "the 21 row/column-sum-two contingency patterns reduce onto "
                "all 16 even-row/even-column 3x3 binary matrices"
            ),
        },
        "cubic_moment_boundary": {
            "identity": (
                "for T_ijk counting columns through three distinct rows, "
                "sum_{k not in {i,j}} T_ijk = 4 G_ij"
            ),
            "all_1140_pair_margin_checks_consistent": True,
            "distinct_pair_margin_histogram_types": len(cubic_margin_hist),
            "pair_margin_histogram_type_counts": {
                ";".join(f"{value}:{count}" for value, count in signature):
                    occurrences
                for signature, occurrences
                in sorted(cubic_margin_hist.items())
            },
            "derived_triples_through_each_row": 100,
            "derived_total_triple_incidence": 1200,
            "obstruction_found": False,
            "boundary": (
                "the Gram target fixes only pair margins of the cubic tensor, "
                "not a nonnegative integral tensor realized by the same 60 "
                "distinct columns"
            ),
        },
        "bilinear_form_boundary": {
            "F2_alternating_Witt_obstruction": False,
            "reason_F2": (
                "alternating forms have one Witt class per even rank, and every "
                "observed rank is far below the 58-dimensional symplectic "
                "quotient of the ambient even-weight space"
            ),
            "odd_prime_Witt_obstruction": False,
            "reason_odd": (
                "all observed ranks are at most 32, leaving complementary "
                "dimension at least 28 in the standard 60-space; either "
                "discriminant class is available"
            ),
            "F2_quadratic_dimension_Witt_screen_obstruction": False,
            "reason_F2_quadratic": (
                "after quotienting by the five known q-zero kernel "
                "indicators, the standard 58-dimensional minus-type "
                "quadratic quotient has at least the recorded nonnegative "
                "dimension slack for a singular-radical embedding; the "
                "remaining Witt type can be adjusted in the complement"
            ),
            "finite_field_factor_is_binary_design": False,
        },
        "countermodels": small_countermodels(),
        "disposition": {
            "modular_obstruction_found": full_pair_consistency[False] > 0,
            "triples_eliminated_by_local_pair_inventory_F2":
                local_pair_consistency[False],
            "triples_eliminated_by_full_pair_inventory_F2":
                full_pair_consistency[False],
            "exact_missing_invariant": (
                "integer, distinct-column coupling of all 630 row-pair "
                "inventories with realizable third- and higher-order overlaps; "
                "rank/Witt and parity moments forget these nonnegative "
                "multiplicities"
            ),
            "usable_filter": (
                "for each Wave60 type triple, reduce its 630-bit full pair "
                "parity target against the span of fibre-compatible positive "
                "pair triples before launching any integer search"
            ),
            "simultaneous_B_constructed": False,
            "endpoint_status": "UNKNOWN",
            "conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 20,
            "start_free_physical_memory_percent": round(float(start_memory), 2),
            "finish_free_physical_memory_percent": round(
                float(require_memory_headroom()), 2
            ),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The 18 inputs are fibre-preserving types, not unrestricted graph isomorphism classes.",
            "Finite-field factors do not enforce binary columns or weight profiles.",
            "The F2 pair-inventory filters are necessary only and do not impose exact nonnegative counts.",
            "No solver nonhit is used as evidence.",
            "No endpoint graph, exclusion, or general upper-bound improvement follows.",
        ],
    }
    return result


def write_result(path: Path) -> dict:
    result = build_results()
    path.write_bytes(canonical_bytes(result))
    return result


def verify_saved(path: Path) -> dict:
    expected = json.loads(canonical_bytes(build_results()))
    actual = json.loads(path.read_text(encoding="utf-8"))
    for payload in (expected, actual):
        payload["resource_guard"].pop("start_free_physical_memory_percent")
        payload["resource_guard"].pop("finish_free_physical_memory_percent")
    assert actual == expected
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        result = verify_saved(args.verify)
    else:
        result = write_result(args.output)
    print(json.dumps({
        "claim_label": result["claim_label"],
        "triple_count": result["input"]["unordered_triples_with_repetition"],
        "rank_F2_histogram":
            result["triple_census"]["rank_F2_G_histogram"],
        "full_pair_F2_eliminated":
            result["disposition"][
                "triples_eliminated_by_full_pair_inventory_F2"
            ],
        "endpoint_status": result["disposition"]["endpoint_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
