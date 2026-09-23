#!/usr/bin/env python3
"""Independent verifier for the frozen Wave 61 finite-field package.

This implementation consumes the Wave 60 component census but imports no
discovery code.  It reconstructs all targets directly from edge lists and
uses its own least-pivot binary elimination and forward symmetric
congruence elimination.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CENSUS = ROOT / "attempts/wave60-c3-incidence-design/component-census.json"
DISCOVERY = ROOT / "attempts/wave61-c3-finite-field/exact-results.json"
FREEZE = HERE / "preinspection-freeze.sha256"
DEFAULT_OUTPUT = HERE / "independent-results.json"
ODD_PRIMES = (3, 5, 7, 11)
MIN_FREE_PERCENT = 20.0


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


def free_memory_percent() -> float:
    if os.name != "nt":
        available = os.sysconf("SC_AVPHYS_PAGES")
        total = os.sysconf("SC_PHYS_PAGES")
        return 100.0 * available / total
    state = MemoryStatusEx()
    state.dwLength = ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * state.ullAvailPhys / state.ullTotalPhys


def require_headroom() -> None:
    available = free_memory_percent()
    if available < MIN_FREE_PERCENT:
        raise RuntimeError(
            f"free physical memory {available:.2f}% is below "
            f"{MIN_FREE_PERCENT:.0f}%"
        )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def frozen_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in FREEZE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        expected, relative = line.split(maxsplit=1)
        entries[relative.replace("\\", "/")] = expected
    return entries


def verify_frozen_inputs() -> dict[str, str]:
    entries = frozen_entries()
    required = {
        "attempts/wave60-c3-incidence-design/component-census.json",
        "attempts/wave58-cross-incidence-rank/exact-results.json",
        "attempts/wave61-c3-finite-field/exact_check.py",
        "attempts/wave61-c3-finite-field/exact-results.json",
        "attempts/wave61-c3-finite-field/protocol.md",
        "attempts/wave61-c3-finite-field/report.md",
        "attempts/wave61-c3-finite-field/test_exact_check.py",
    }
    assert required <= entries.keys()
    for relative, expected in entries.items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert file_sha256(path) == expected, relative
    return entries


def edge_mask(edges: Iterable[Sequence[int]], order: int = 12) -> int:
    pairs = list(itertools.combinations(range(order), 2))
    index = {pair: position for position, pair in enumerate(pairs)}
    mask = 0
    for raw_left, raw_right in edges:
        left, right = sorted((int(raw_left), int(raw_right)))
        assert left != right
        bit = 1 << index[(left, right)]
        assert not mask & bit
        mask |= bit
    return mask


def component_adjacency(record: dict) -> tuple[int, ...]:
    rows = [0] * 12
    for raw_left, raw_right in record["edges"]:
        left, right = sorted((int(raw_left), int(raw_right)))
        assert 0 <= left < right < 12
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return tuple(rows)


def connected(rows: Sequence[int]) -> bool:
    reached = 1
    frontier = 1
    while frontier:
        union = 0
        scan = frontier
        while scan:
            bit = scan & -scan
            scan ^= bit
            union |= rows[bit.bit_length() - 1]
        frontier = union & ~reached
        reached |= frontier
    return reached == (1 << len(rows)) - 1


def fibre_preserving_signature(record: dict) -> int:
    """Canonical edge mask under S4 x S4 x S4, with fibres fixed."""
    original = {
        tuple(sorted((int(left), int(right))))
        for left, right in record["edges"]
    }
    permutations = tuple(itertools.permutations(range(4)))
    best: int | None = None
    for p0 in permutations:
        for p1 in permutations:
            for p2 in permutations:
                parts = (p0, p1, p2)
                relabelled = []
                for left, right in original:
                    lf, li = divmod(left, 4)
                    rf, ri = divmod(right, 4)
                    new_left = 4 * lf + parts[lf][li]
                    new_right = 4 * rf + parts[rf][ri]
                    relabelled.append(tuple(sorted((new_left, new_right))))
                code = edge_mask(relabelled)
                if best is None or code < best:
                    best = code
    assert best is not None
    return best


def validate_component(record: dict) -> dict:
    rows = component_adjacency(record)
    assert [row.bit_count() for row in rows] == [3] * 12
    assert connected(rows)
    triangles = sum(
        1
        for a, b, c in itertools.combinations(range(12), 3)
        if (rows[a] >> b & 1)
        and (rows[a] >> c & 1)
        and (rows[b] >> c & 1)
    )
    assert triangles == 0
    for fibre in range(3):
        vertices = range(4 * fibre, 4 * fibre + 4)
        internal_edges = sum(
            rows[left] >> right & 1
            for left, right in itertools.combinations(vertices, 2)
        )
        assert internal_edges == 2
        assert all(
            sum(rows[v] >> w & 1 for w in vertices) == 1
            for v in vertices
        )
    for left_fibre, right_fibre in itertools.combinations(range(3), 2):
        left_vertices = range(4 * left_fibre, 4 * left_fibre + 4)
        right_vertices = range(4 * right_fibre, 4 * right_fibre + 4)
        assert all(
            sum(rows[v] >> w & 1 for w in right_vertices) == 1
            for v in left_vertices
        )
        assert all(
            sum(rows[v] >> w & 1 for w in left_vertices) == 1
            for v in right_vertices
        )
    c4 = 0
    for left, right in itertools.combinations(range(12), 2):
        common = (rows[left] & rows[right]).bit_count()
        adjacent = rows[left] >> right & 1
        if adjacent:
            assert common == 0
        else:
            cap = 1 if left // 4 == right // 4 else 2
            assert common <= cap
            c4 += common * (common - 1) // 2
    c4 //= 2
    assert c4 == record["C4"]
    return {"rows": rows, "C4": c4}


def load_and_validate_types() -> list[dict]:
    payload = json.loads(CENSUS.read_text(encoding="utf-8"))
    assert payload["claim_label"] == "UNKNOWN"
    census = payload["component_census"]
    assert census["fibre_preserving_type_count"] == 18
    records = census["types"]
    assert [entry["type_index"] for entry in records] == list(range(18))
    signatures = []
    for record in records:
        validate_component(record)
        signatures.append(fibre_preserving_signature(record))
    assert len(set(signatures)) == 18
    return records


def global_index(component: int, local: int) -> int:
    fibre, within = divmod(local, 4)
    return 12 * fibre + 4 * component + within


def target_gram(records: Sequence[dict]) -> tuple[tuple[int, ...], ...]:
    adjacency = [0] * 36
    for component, record in enumerate(records):
        for raw_left, raw_right in record["edges"]:
            left = global_index(component, int(raw_left))
            right = global_index(component, int(raw_right))
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    assert [row.bit_count() for row in adjacency] == [3] * 36
    matrix = [[0] * 36 for _ in range(36)]
    for left in range(36):
        for right in range(36):
            value = (
                (12 if left == right else 0)
                - ((adjacency[left] >> right) & 1)
                + 2
                - (left // 12 == right // 12)
                - (adjacency[left] & adjacency[right]).bit_count()
            )
            assert value >= 0
            matrix[left][right] = int(value)
    assert all(
        matrix[left][right] == matrix[right][left]
        for left in range(36)
        for right in range(36)
    )
    assert [matrix[index][index] for index in range(36)] == [10] * 36
    return tuple(tuple(row) for row in matrix)


def binary_basis(vectors: Iterable[int]) -> dict[int, int]:
    """Least-significant-pivot echelon basis."""
    basis: dict[int, int] = {}
    for original in vectors:
        value = original
        while value:
            bit = value & -value
            pivot = bit.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return basis


def extend_binary_basis(basis: dict[int, int], original: int) -> bool:
    value = original
    while value:
        bit = value & -value
        pivot = bit.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    return False


def in_binary_span(basis: dict[int, int], original: int) -> bool:
    value = original
    while value:
        bit = value & -value
        pivot = bit.bit_length() - 1
        if pivot not in basis:
            return False
        value ^= basis[pivot]
    return True


def matrix_row_bits_mod2(matrix: Sequence[Sequence[int]]) -> list[int]:
    return [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]


def nullspace_mod2(matrix: Sequence[Sequence[int]]) -> list[int]:
    width = len(matrix[0])
    rows = matrix_row_bits_mod2(matrix)
    pivots: list[int] = []
    rank = 0
    for column in range(width):
        pivot = next(
            (
                position
                for position in range(rank, len(rows))
                if rows[position] >> column & 1
            ),
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
    pivot_set = set(pivots)
    output = []
    for free in range(width):
        if free in pivot_set:
            continue
        vector = 1 << free
        for row, pivot in zip(rows[:rank], pivots):
            if row >> free & 1:
                vector |= 1 << pivot
        output.append(vector)
    return output


def multiply_mod2(matrix: Sequence[Sequence[int]], vector: int) -> int:
    result = 0
    for row_number, row in enumerate(matrix_row_bits_mod2(matrix)):
        result |= ((row & vector).bit_count() & 1) << row_number
    return result


def q_pullback(matrix: Sequence[Sequence[int]], vector: int) -> int:
    """q(B^T x), derived from row weights ten and pairwise Gram entries."""
    value = vector.bit_count() & 1
    selected = [index for index in range(36) if vector >> index & 1]
    for position, left in enumerate(selected):
        for right in selected[position + 1 :]:
            value ^= matrix[left][right] & 1
    return value


def partition_indicators() -> tuple[int, ...]:
    fibres = tuple(((1 << 12) - 1) << (12 * fibre) for fibre in range(3))
    components = []
    for component in range(3):
        mask = 0
        for fibre in range(3):
            mask |= 0b1111 << (12 * fibre + 4 * component)
        components.append(mask)
    output = fibres + tuple(components)
    assert len(binary_basis(output)) == 5
    assert fibres[0] ^ fibres[1] ^ fibres[2] == (
        components[0] ^ components[1] ^ components[2]
    )
    return output


def binary_form_data(matrix: Sequence[Sequence[int]]) -> dict:
    assert all(matrix[index][index] % 2 == 0 for index in range(36))
    radical = nullspace_mod2(matrix)
    rank = 36 - len(radical)
    assert rank % 2 == 0
    indicators = partition_indicators()
    assert all(multiply_mod2(matrix, vector) == 0 for vector in indicators)
    assert all(q_pullback(matrix, vector) == 0 for vector in indicators)
    q_nonzero = any(q_pullback(matrix, vector) for vector in radical)
    q_zero_radical_dimension = len(radical) - int(q_nonzero)
    assert q_zero_radical_dimension >= 5
    singular_after_kernel = q_zero_radical_dimension - 5
    occupied_dimension_bound = (
        rank + 2 * singular_after_kernel + int(q_nonzero)
    )
    slack = 58 - occupied_dimension_bound
    assert slack >= 0
    # The quotient ambient dimension is even.  If q is nonzero on the
    # radical, the next even dimension is automatically used; all observed
    # adjusted slack values below remain nonnegative.
    parity_adjusted_slack = slack - int(q_nonzero)
    assert parity_adjusted_slack >= 0
    return {
        "rank": rank,
        "radical_dimension": len(radical),
        "q_nonzero_on_radical": q_nonzero,
        "q_zero_radical_dimension": q_zero_radical_dimension,
        "reported_slack": slack,
        "even_ambient_adjusted_slack": parity_adjusted_slack,
    }


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (
                position
                for position in range(rank, len(rows))
                if rows[position][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        for position in range(rank + 1, len(rows)):
            factor = rows[position][column] * inverse % prime
            if factor:
                rows[position] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[position], rows[rank])
                ]
        rank += 1
    return rank


def congruence_invariants(
    matrix: Sequence[Sequence[int]], prime: int
) -> tuple[int, int, int]:
    """Diagonalize a symmetric form from the leading corner by congruence."""
    work = [[value % prime for value in row] for row in matrix]
    diagonals: list[int] = []
    start = 0
    order = len(work)
    while start < order:
        pivot = next(
            (index for index in range(start, order) if work[index][index]),
            None,
        )
        if pivot is None:
            off = next(
                (
                    (left, right)
                    for left in range(start, order)
                    for right in range(left + 1, order)
                    if work[left][right]
                ),
                None,
            )
            if off is None:
                break
            left, right = off
            old = [row[:] for row in work]
            # Simultaneously replace basis vector left by left+right.
            for index in range(order):
                if index != left:
                    work[left][index] = (
                        old[left][index] + old[right][index]
                    ) % prime
                    work[index][left] = work[left][index]
            work[left][left] = (
                old[left][left]
                + 2 * old[left][right]
                + old[right][right]
            ) % prime
            pivot = left
        if pivot != start:
            work[start], work[pivot] = work[pivot], work[start]
            for row in work:
                row[start], row[pivot] = row[pivot], row[start]
        diagonal = work[start][start] % prime
        assert diagonal
        diagonals.append(diagonal)
        inverse = pow(diagonal, -1, prime)
        tail = [work[index][start] for index in range(start + 1, order)]
        for left_offset, left in enumerate(range(start + 1, order)):
            for right in range(left, order):
                right_offset = right - start - 1
                value = (
                    work[left][right]
                    - tail[left_offset] * tail[right_offset] * inverse
                ) % prime
                work[left][right] = value
                work[right][left] = value
        start += 1
    rank = len(diagonals)
    assert rank == rank_mod_prime(matrix, prime)
    determinant = 1
    for value in diagonals:
        determinant = determinant * value % prime
    legendre = 1 if pow(determinant, (prime - 1) // 2, prime) == 1 else -1
    if rank % 2:
        anisotropic = 1
    else:
        hyperbolic_det = pow((-1) % prime, rank // 2, prime)
        hyperbolic_legendre = (
            1
            if pow(hyperbolic_det, (prime - 1) // 2, prime) == 1
            else -1
        )
        anisotropic = 0 if legendre == hyperbolic_legendre else 2
    return rank, legendre, anisotropic


LOCAL_PAIRS = tuple(itertools.combinations(range(12), 2))
GLOBAL_PAIRS = tuple(itertools.combinations(range(36), 2))
GLOBAL_PAIR_INDEX = {pair: index for index, pair in enumerate(GLOBAL_PAIRS)}


def local_gram(record: dict) -> tuple[tuple[int, ...], ...]:
    rows = component_adjacency(record)
    matrix = []
    for left in range(12):
        output_row = []
        for right in range(12):
            output_row.append(
                (12 if left == right else 0)
                - ((rows[left] >> right) & 1)
                + 2
                - (left // 4 == right // 4)
                - (rows[left] & rows[right]).bit_count()
            )
        matrix.append(tuple(int(value) for value in output_row))
    return tuple(matrix)


def local_pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    counts = [0, 0, 0]
    for vertex in pair:
        counts[vertex // 4] += 1
    return tuple(counts)


PAIR_PROFILES = tuple(sorted({local_pair_profile(pair) for pair in LOCAL_PAIRS}))
PROFILE_INDEX = {profile: index for index, profile in enumerate(PAIR_PROFILES)}
PATTERNS = tuple(
    triple
    for triple in itertools.product(range(len(PAIR_PROFILES)), repeat=3)
    if all(
        sum(PAIR_PROFILES[triple[component]][fibre] for component in range(3))
        == 2
        for fibre in range(3)
    )
)
assert len(PATTERNS) == 21


def local_inventory(record: dict) -> dict:
    gram = local_gram(record)
    by_profile = [[] for _ in PAIR_PROFILES]
    rhs = 0
    target_sum = 0
    for index, pair in enumerate(LOCAL_PAIRS):
        value = gram[pair[0]][pair[1]]
        target_sum += value
        if value > 0:
            by_profile[PROFILE_INDEX[local_pair_profile(pair)]].append(index)
        if value % 2:
            rhs |= 1 << index
    assert target_sum == 60
    return {
        "by_profile": tuple(tuple(values) for values in by_profile),
        "rhs": rhs,
    }


def embedded_pair_bit(component: int, local_pair_index: int) -> int:
    left, right = LOCAL_PAIRS[local_pair_index]
    pair = tuple(
        sorted((global_index(component, left), global_index(component, right)))
    )
    return 1 << GLOBAL_PAIR_INDEX[pair]


WITHIN_BITS = tuple(
    tuple(embedded_pair_bit(component, index) for index in range(66))
    for component in range(3)
)


def cross_bits(
    left_component: int,
    left_pair_index: int,
    right_component: int,
    right_pair_index: int,
) -> int:
    result = 0
    for local_left in LOCAL_PAIRS[left_pair_index]:
        for local_right in LOCAL_PAIRS[right_pair_index]:
            pair = tuple(
                sorted(
                    (
                        global_index(left_component, local_left),
                        global_index(right_component, local_right),
                    )
                )
            )
            result |= 1 << GLOBAL_PAIR_INDEX[pair]
    assert result.bit_count() == 4
    return result


CROSS_BITS = {
    components: tuple(
        tuple(
            cross_bits(components[0], left, components[1], right)
            for right in range(66)
        )
        for left in range(66)
    )
    for components in ((0, 1), (0, 2), (1, 2))
}


def pair_inventory_data(
    records: Sequence[dict], matrix: Sequence[Sequence[int]]
) -> dict:
    local = [local_inventory(record) for record in records]
    local_basis: dict[int, int] = {}
    full_basis: dict[int, int] = {}
    candidate_count = 0
    for pattern in PATTERNS:
        choices = [
            local[component]["by_profile"][pattern[component]]
            for component in range(3)
        ]
        candidate_count += len(choices[0]) * len(choices[1]) * len(choices[2])
        for first in choices[0]:
            for second in choices[1]:
                local_prefix = (1 << first) | (1 << (66 + second))
                full_prefix = (
                    WITHIN_BITS[0][first]
                    | WITHIN_BITS[1][second]
                    | CROSS_BITS[(0, 1)][first][second]
                )
                for third in choices[2]:
                    extend_binary_basis(
                        local_basis, local_prefix | (1 << (132 + third))
                    )
                    syndrome = (
                        full_prefix
                        | WITHIN_BITS[2][third]
                        | CROSS_BITS[(0, 2)][first][third]
                        | CROSS_BITS[(1, 2)][second][third]
                    )
                    assert syndrome.bit_count() == 15
                    extend_binary_basis(full_basis, syndrome)
    local_rhs = (
        local[0]["rhs"]
        | (local[1]["rhs"] << 66)
        | (local[2]["rhs"] << 132)
    )
    full_rhs = 0
    for index, (left, right) in enumerate(GLOBAL_PAIRS):
        full_rhs |= (matrix[left][right] & 1) << index
    return {
        "candidate_count": candidate_count,
        "local_rank": len(local_basis),
        "local_consistent": in_binary_span(local_basis, local_rhs),
        "full_rank": len(full_basis),
        "full_consistent": in_binary_span(full_basis, full_rhs),
        "_local_basis": local_basis,
        "_full_basis": full_basis,
        "_local_rhs": local_rhs,
        "_full_rhs": full_rhs,
    }


def pattern_vectors() -> tuple[list[int], Counter[int]]:
    vectors = []
    weights: Counter[int] = Counter()
    for pattern in PATTERNS:
        cells = 0
        for component, profile_index in enumerate(pattern):
            for fibre, count in enumerate(PAIR_PROFILES[profile_index]):
                cells |= (count & 1) << (3 * component + fibre)
        weights[cells.bit_count()] += 1
        vector = 1 << 81
        selected = [cell for cell in range(9) if cells >> cell & 1]
        for left in selected:
            for right in selected:
                vector ^= 1 << (9 * left + right)
        vectors.append(vector)
    return vectors, weights


PATTERN_VECTORS, PATTERN_WEIGHTS = pattern_vectors()
PATTERN_BASIS = binary_basis(PATTERN_VECTORS)


def pattern_target(matrix: Sequence[Sequence[int]]) -> int:
    target = 0
    for left_cell in range(9):
        lc, lf = divmod(left_cell, 3)
        left_vertices = [
            12 * lf + 4 * lc + index for index in range(4)
        ]
        for right_cell in range(9):
            rc, rf = divmod(right_cell, 3)
            right_vertices = [
                12 * rf + 4 * rc + index for index in range(4)
            ]
            parity = sum(
                matrix[left][right]
                for left in left_vertices
                for right in right_vertices
            ) & 1
            target |= parity << (9 * left_cell + right_cell)
    return target


def cubic_data(matrix: Sequence[Sequence[int]]) -> dict:
    row_pair_totals = [
        sum(matrix[row][other] for other in range(36) if other != row)
        for row in range(36)
    ]
    pair_total = sum(matrix[left][right] for left, right in GLOBAL_PAIRS)
    assert row_pair_totals == [50] * 36
    assert pair_total == 900
    margins = Counter(
        4 * matrix[left][right] for left, right in GLOBAL_PAIRS
    )
    return {
        "pair_margin_histogram": {
            str(value): count for value, count in sorted(margins.items())
        },
        "triples_through_each_row": 100,
        "total_triple_incidence": 1200,
        "identity": "sum_{k not in {i,j}} T_ijk = 4 G_ij",
        "tensor_feasibility_tested": False,
    }


def histogram(counter: Counter) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}


def build_result() -> dict:
    require_headroom()
    frozen = verify_frozen_inputs()
    records = load_and_validate_types()
    triples = tuple(itertools.combinations_with_replacement(range(18), 3))
    assert len(triples) == 1140
    assert len(PATTERNS) == 21
    assert len({vector ^ (1 << 81) for vector in PATTERN_VECTORS}) == 16
    assert PATTERN_WEIGHTS == Counter({4: 9, 0: 6, 6: 6})
    assert len(PATTERN_BASIS) == 11

    f2_ranks: Counter[int] = Counter()
    q_classes: Counter[str] = Counter()
    reported_slacks: Counter[int] = Counter()
    adjusted_slacks: Counter[int] = Counter()
    odd_ranks = {prime: Counter() for prime in ODD_PRIMES}
    odd_forms = {prime: Counter() for prime in ODD_PRIMES}
    local_ranks: Counter[int] = Counter()
    full_ranks: Counter[int] = Counter()
    local_consistency: Counter[bool] = Counter()
    full_consistency: Counter[bool] = Counter()
    pattern_consistency: Counter[bool] = Counter()
    cubic_signatures: Counter[str] = Counter()
    compact_records = []
    hostile_reference: dict | None = None

    for triple_index, triple in enumerate(triples):
        if triple_index % 32 == 0:
            require_headroom()
        chosen = [records[index] for index in triple]
        gram = target_gram(chosen)
        f2 = binary_form_data(gram)
        f2_ranks[f2["rank"]] += 1
        q_key = (
            f'{f2["rank"]},'
            f'{"q_nonzero" if f2["q_nonzero_on_radical"] else "q_zero"}'
        )
        q_classes[q_key] += 1
        reported_slacks[f2["reported_slack"]] += 1
        adjusted_slacks[f2["even_ambient_adjusted_slack"]] += 1
        odd = {}
        for prime in ODD_PRIMES:
            rank, legendre, anisotropic = congruence_invariants(gram, prime)
            odd[str(prime)] = [rank, legendre, anisotropic]
            odd_ranks[prime][rank] += 1
            odd_forms[prime][f"{rank},{legendre},{anisotropic}"] += 1
        pair_data = pair_inventory_data(chosen, gram)
        local_ranks[pair_data["local_rank"]] += 1
        full_ranks[pair_data["full_rank"]] += 1
        local_consistency[pair_data["local_consistent"]] += 1
        full_consistency[pair_data["full_consistent"]] += 1
        ptarget = pattern_target(gram)
        pconsistent = in_binary_span(PATTERN_BASIS, ptarget)
        pattern_consistency[pconsistent] += 1
        cubic = cubic_data(gram)
        cubic_signature = ";".join(
            f"{key}:{value}"
            for key, value in cubic["pair_margin_histogram"].items()
        )
        cubic_signatures[cubic_signature] += 1
        compact_records.append(
            {
                "index": triple_index,
                "triple": list(triple),
                "rank_F2_G": f2["rank"],
                "q_nonzero_on_radical": f2["q_nonzero_on_radical"],
                "reported_quadratic_slack": f2["reported_slack"],
                "even_ambient_adjusted_slack":
                    f2["even_ambient_adjusted_slack"],
                "odd_forms": odd,
                "candidate_count": pair_data["candidate_count"],
                "local_198_rank": pair_data["local_rank"],
                "local_198_consistent": pair_data["local_consistent"],
                "full_630_rank": pair_data["full_rank"],
                "full_630_consistent": pair_data["full_consistent"],
                "pattern_rank": len(PATTERN_BASIS),
                "pattern_consistent": pconsistent,
                "cubic_pair_margin_signature": cubic_signature,
            }
        )
        if triple_index == 0:
            hostile_reference = {
                "gram": gram,
                "pair": pair_data,
                "pattern_target": ptarget,
            }

    assert hostile_reference is not None
    # Hostile mutation: find unit-coordinate changes outside each span.
    pair_data = hostile_reference["pair"]
    local_bad = next(
        bit
        for bit in range(198)
        if not in_binary_span(pair_data["_local_basis"], 1 << bit)
    )
    full_bad = next(
        bit
        for bit in range(630)
        if not in_binary_span(pair_data["_full_basis"], 1 << bit)
    )
    pattern_bad = next(
        bit
        for bit in range(82)
        if not in_binary_span(PATTERN_BASIS, 1 << bit)
    )
    assert not in_binary_span(
        pair_data["_local_basis"], pair_data["_local_rhs"] ^ (1 << local_bad)
    )
    assert not in_binary_span(
        pair_data["_full_basis"], pair_data["_full_rhs"] ^ (1 << full_bad)
    )
    assert not in_binary_span(
        PATTERN_BASIS, hostile_reference["pattern_target"] ^ (1 << pattern_bad)
    )

    # Discovery comparison occurs only after all independent reconstruction.
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    dcensus = discovery["triple_census"]
    comparisons = {
        "rank_F2_G_histogram": (
            histogram(f2_ranks) == dcensus["rank_F2_G_histogram"]
        ),
        "rank_F2_and_radical_quadratic_histogram": (
            histogram(q_classes)
            == dcensus["rank_F2_and_radical_quadratic_histogram"]
        ),
        "quadratic_embedding_dimension_slack_histogram": (
            histogram(reported_slacks)
            == dcensus["quadratic_embedding_dimension_slack_histogram"]
        ),
        "odd_prime_rank_histograms": all(
            histogram(odd_ranks[prime])
            == dcensus["odd_prime_rank_histograms"][str(prime)]
            for prime in ODD_PRIMES
        ),
        "odd_prime_form_histograms": all(
            histogram(odd_forms[prime])
            == dcensus["odd_prime_form_histograms"][str(prime)]
            for prime in ODD_PRIMES
        ),
        "local_pair_inventory_F2_rank_histogram": (
            histogram(local_ranks)
            == dcensus["local_pair_inventory_F2_rank_histogram"]
        ),
        "full_pair_inventory_F2_rank_histogram": (
            histogram(full_ranks)
            == dcensus["full_pair_inventory_F2_rank_histogram"]
        ),
        "all_local_consistency": local_consistency == Counter({True: 1140}),
        "all_full_consistency": full_consistency == Counter({True: 1140}),
        "all_pattern_consistency": pattern_consistency == Counter({True: 1140}),
    }
    assert all(comparisons.values()), comparisons

    record_digest = hashlib.sha256(canonical_bytes(compact_records)).hexdigest()
    result = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_WITH_CORRECTION",
        "scope": (
            "conditional kappa=3 finite-field and parity relaxations for all "
            "1,140 unordered triples with repetition of the 18 frozen "
            "fibre-preserving Wave 60 component types"
        ),
        "frozen_inputs": {
            "wave60_component_census_sha256": frozen[
                "attempts/wave60-c3-incidence-design/component-census.json"
            ],
            "wave61_discovery_results_sha256": frozen[
                "attempts/wave61-c3-finite-field/exact-results.json"
            ],
            "preinspection_freeze_sha256": file_sha256(FREEZE),
        },
        "component_and_triple_reconstruction": {
            "validated_component_types": 18,
            "pairwise_distinct_fibre_preserving_signatures": 18,
            "unordered_triples_with_repetition": len(triples),
            "complete_index_range": [0, len(triples) - 1],
            "no_graph_automorphism_assumed": True,
            "normalization_used_only_to_validate_input_type_distinctness": True,
        },
        "universal_F2": {
            "partition_indicator_count": 6,
            "indicator_span_dimension": 5,
            "single_relation": "F0+F1+F2=C0+C1+C2=all-ones",
            "rank_B_upper_bound": 31,
            "G_alternating": True,
            "rank_G_even_upper_bound": 30,
            "rank_F2_G_histogram": histogram(f2_ranks),
        },
        "quadratic_embedding": {
            "E60_radical": "span(all-ones)",
            "E60_quotient_dimension": 58,
            "E60_quotient_Arf_invariant": 1,
            "gauss_sum_E60": "-2^30",
            "reported_slack_histogram": histogram(reported_slacks),
            "even_ambient_adjusted_slack_histogram":
                histogram(adjusted_slacks),
            "obstruction_found": False,
            "audit_note": (
                "the discovery's reported slack counts the q-nonzero radical "
                "line as one occupied dimension; because the ambient quotient "
                "is even-dimensional, subtracting one more dimension gives "
                "the parity-adjusted slack. It remains nonnegative in every "
                "case, so the no-obstruction conclusion is unchanged."
            ),
        },
        "odd_prime_forms": {
            "rank_histograms": {
                str(prime): histogram(odd_ranks[prime])
                for prime in ODD_PRIMES
            },
            "rank_discriminant_anisotropic_histograms": {
                str(prime): histogram(odd_forms[prime])
                for prime in ODD_PRIMES
            },
            "maximum_rank": max(
                max(counter.keys()) for counter in odd_ranks.values()
            ),
            "ambient_complement_minimum_dimension": 28,
            "unrestricted_Gram_factor_obstruction_found": False,
            "binary_weight_profile_design_constructed": False,
        },
        "component_patterns": {
            "integral_patterns": len(PATTERNS),
            "binary_images": len(
                {vector ^ (1 << 81) for vector in PATTERN_VECTORS}
            ),
            "weight_histogram": histogram(PATTERN_WEIGHTS),
            "moment_rank": len(PATTERN_BASIS),
            "consistent_targets": pattern_consistency[True],
            "eliminated_targets": pattern_consistency[False],
        },
        "pair_inventory_F2": {
            "local_198_rank_histogram": histogram(local_ranks),
            "local_consistent_targets": local_consistency[True],
            "local_eliminated_targets": local_consistency[False],
            "full_630_rank_histogram": histogram(full_ranks),
            "full_consistent_targets": full_consistency[True],
            "full_eliminated_targets": full_consistency[False],
            "candidate_count_range": [
                min(record["candidate_count"] for record in compact_records),
                max(record["candidate_count"] for record in compact_records),
            ],
        },
        "cubic_margin": {
            "identity": "sum_{k not in {i,j}} T_ijk = 4 G_ij",
            "triples_through_each_row": 100,
            "total_triple_incidence": 1200,
            "pair_margin_histogram_type_count": len(cubic_signatures),
            "pair_margin_histogram_type_counts": histogram(cubic_signatures),
            "correction": (
                "these are necessary scalar margin identities only; neither "
                "the discovery nor this verifier tests existence of a "
                "nonnegative integral symmetric tensor T satisfying all 630 "
                "pair margins. Therefore 'all consequences determined by G' "
                "must not be read as a complete cubic-feasibility claim."
            ),
        },
        "hostile_mutations": {
            "local_rhs_flipped_coordinate_rejected": local_bad,
            "full_rhs_flipped_coordinate_rejected": full_bad,
            "pattern_rhs_flipped_coordinate_rejected": pattern_bad,
            "component_edge_mutation_covered_by_tests": True,
            "freeze_byte_mutation_covered_by_tests": True,
        },
        "discovery_comparison": comparisons,
        "compact_records_sha256": record_digest,
        "compact_records": compact_records,
        "status_boundary": {
            "endpoint_status": "UNKNOWN",
            "conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
            "simultaneous_integer_B_constructed": False,
            "compatible_A_Y_constructed": False,
            "endpoint_excluded": False,
            "improved_general_n3_upper_bound": False,
        },
        "limitations": [
            "The verification is conditional on the Wave 60 kappa=3 component census.",
            "The 18 types are fibre-preserving classes, not unrestricted graph isomorphism classes.",
            "Finite-field and parity feasibility does not imply a 60-column binary incidence design.",
            "Integer multiplicity, distinct-column, cubic-tensor, A_Y, and full-SRG compatibility remain unproved.",
            "No solver nonhit is used as evidence.",
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_PERCENT,
            "checked_before_start_and_every_32_triples": True,
        },
    }
    return result


def verify_saved(path: Path) -> None:
    expected = build_result()
    actual = json.loads(path.read_text(encoding="utf-8"))
    assert actual == expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify is not None:
        verify_saved(args.verify)
        print(json.dumps({"verified": str(args.verify)}, sort_keys=True))
        return
    result = build_result()
    args.output.write_bytes(canonical_bytes(result))
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "triple_count": result[
                    "component_and_triple_reconstruction"
                ]["unordered_triples_with_repetition"],
                "full_pair_eliminations": result["pair_inventory_F2"][
                    "full_eliminated_targets"
                ],
                "endpoint_status": result["status_boundary"][
                    "endpoint_status"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
