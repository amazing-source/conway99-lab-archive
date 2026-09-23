#!/usr/bin/env python3
"""Clean-room verifier for the Wave 44 aggregate rooted relaxation.

The protocol in protocol-freeze.md predates discovery inspection.  This file
imports no Wave 44 code.  It rebuilds the complete seven-vertex catalogue,
the public Wave 43 base system, all rooted rows, and checks the sparse witness
with exact integers before running any floating-point solver diagnostic.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PUBLIC_W43 = ROOT / "verification/wave43-seven-deck-endpoint/independent-result.json"
WITNESS = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
DISCOVERY_RESULT = ROOT / "attempts/wave44-rooted-flags/exact-results.json"
DISCOVERY_ROWS = ROOT / "attempts/wave44-rooted-flags/row-system.json"
EXPECTED = {
    PUBLIC_W43: "e38f369d338fada4a561d48019f306511961dd1fd7816e54a12a9ecb09e69f3b",
    WITNESS: "9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9",
    DISCOVERY_RESULT: "c41b194d2d4ae8121883d84ba4f5011f48336a58a0dd4f5cebf9ab560ee3ae19",
    DISCOVERY_ROWS: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
}
N, K, LAMBDA, MU, N3 = 99, 14, 1, 2, 4158
MIN_FREE_PERCENT = 15.0

SOURCE_N_MASKS = (
    7100, 1883, 5941, 1916, 5907, 1749, 926, 1881, 1884, 956, 922, 1880,
    920, 5905, 671, 761, 701, 762, 63, 123, 691, 663, 694, 633, 760, 126,
    693, 246, 700, 31, 61, 121, 659, 122, 692, 0, 1, 3, 36, 7, 44, 37,
    35, 15, 102, 45, 39, 106, 616, 110, 107, 47, 684, 655, 685, 617, 656,
    657, 60, 662, 120, 632,
)
SOURCE_H_CHORDS = (
    (), ((6, 1),), ((5, 2),), ((0, 5), (0, 2)),
    ((0, 5), (0, 3)), ((0, 4), (0, 3)), ((6, 4), (1, 3)),
    ((6, 1), (5, 2)), ((6, 1), (0, 4)), ((6, 3), (1, 4)),
    ((6, 1), (6, 4), (1, 3)), ((0, 2), (0, 5), (1, 4)),
    ((0, 4), (0, 3), (6, 1)), ((0, 4), (0, 3), (5, 2)),
    ((0, 5), (0, 3), (4, 2)), ((6, 4), (1, 3), (5, 2)),
    ((6, 1), (5, 2), (0, 3)),
    ((6, 1), (5, 2), (6, 4), (1, 3)),
    ((6, 1), (5, 2), (0, 4), (0, 3)),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact_hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))


def canonical_family(
    rows: Sequence[Sequence[int]], rhs: Sequence[int]
) -> dict[str, list[object]]:
    """Match the discovery artifact's documented compact-JSON family encoding."""
    return {
        "rows": [list(row) for row in rows],
        "rhs": [int(value) for value in rhs],
    }


def strict_json(path: Path, expected: str | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    if expected is not None and sha256(raw) != expected:
        raise ValueError(f"hash mismatch: {path}")

    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON must be an object")
    return value


def memory_sample(label: str) -> dict[str, object]:
    if sys.platform == "win32":
        class Status(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
                ("total_page", ctypes.c_ulonglong), ("available_page", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                ("extended", ctypes.c_ulonglong),
            ]
        status = Status()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("memory query failed")
        total, available = int(status.total), int(status.available)
    else:
        page = os.sysconf("SC_PAGE_SIZE")
        total = int(os.sysconf("SC_PHYS_PAGES") * page)
        available = int(os.sysconf("SC_AVPHYS_PAGES") * page)
    percent = 100.0 * available / total
    if percent < MIN_FREE_PERCENT:
        raise MemoryError(f"{label}: only {percent:.2f}% memory free")
    return {
        "label": label, "total_bytes": total, "available_bytes": available,
        "free_percent_floor": math.floor(percent * 100) / 100,
    }


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(order) for v in range(u + 1, order))


def bit_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def permutation_maps(order: int) -> tuple[tuple[int, ...], ...]:
    positions = bit_positions(order)
    return tuple(
        tuple(positions[tuple(sorted((permutation[u], permutation[v])))] for u, v in edges(order))
        for permutation in itertools.permutations(range(order))
    )


def relabel(mask: int, mapping: Sequence[int]) -> int:
    result = 0
    while mask:
        low = mask & -mask
        source = low.bit_length() - 1
        result |= 1 << mapping[source]
        mask ^= low
    return result


@dataclass(frozen=True)
class Catalogue:
    order: int
    classes: tuple[int, ...]
    canonical: tuple[int, ...]
    orbit_sizes: tuple[int, ...]


def complete_catalogue(order: int) -> Catalogue:
    universe = 1 << math.comb(order, 2)
    remaining = set(range(universe))
    canonical = [-1] * universe
    orbit_size: dict[int, int] = {}
    maps = permutation_maps(order)
    while remaining:
        representative = next(iter(remaining))
        orbit = {relabel(representative, mapping) for mapping in maps}
        key = min(orbit)
        if key in orbit_size:
            raise AssertionError("repeated canonical orbit")
        orbit_size[key] = len(orbit)
        for labelled in orbit:
            if canonical[labelled] != -1:
                raise AssertionError("overlapping permutation orbits")
            canonical[labelled] = key
        remaining.difference_update(orbit)
    classes = tuple(sorted(orbit_size))
    sizes = tuple(orbit_size[key] for key in classes)
    expected = {6: 156, 7: 1044}[order]
    if len(classes) != expected or sum(sizes) != universe or min(canonical) < 0:
        raise AssertionError("unlabeled catalogue completeness failed")
    return Catalogue(order, classes, tuple(canonical), sizes)


def adjacency(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for bit, (u, v) in enumerate(edges(order)):
        if mask >> bit & 1:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    return tuple(rows)


def admissible(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    for u, v in itertools.combinations(range(order), 2):
        common = (rows[u] & rows[v]).bit_count()
        if rows[u] >> v & 1:
            if common > LAMBDA:
                return False
        elif common > MU:
            return False
    return True


def mask_from_edges(order: int, chosen: Iterable[tuple[int, int]]) -> int:
    positions = bit_positions(order)
    result = 0
    for u, v in chosen:
        result |= 1 << positions[tuple(sorted((u, v)))]
    return result


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    remaining = [v for v in range(order) if v != deleted]
    new_index = {v: i for i, v in enumerate(remaining)}
    positions = bit_positions(order - 1)
    result = 0
    for bit, (u, v) in enumerate(edges(order)):
        if u == deleted or v == deleted or not (mask >> bit & 1):
            continue
        result |= 1 << positions[tuple(sorted((new_index[u], new_index[v])))]
    return result


def deletion_rows(classes7: Sequence[int], catalogue6: Catalogue) -> tuple[tuple[int, ...], ...]:
    row_index = {mask: index for index, mask in enumerate(SOURCE_N_MASKS)}
    rows = [[0] * len(classes7) for _ in SOURCE_N_MASKS]
    for column, mask in enumerate(classes7):
        for deleted in range(7):
            card = delete_vertex(mask, 7, deleted)
            canonical_card = catalogue6.canonical[card]
            if canonical_card not in row_index:
                raise AssertionError("seven-class has inadmissible card")
            rows[row_index[canonical_card]][column] += 1
    if any(sum(row[column] for row in rows) != 7 for column in range(len(classes7))):
        raise AssertionError("deletion column does not total seven")
    return tuple(tuple(row) for row in rows)


def hamiltonian_masks(catalogue7: Catalogue) -> tuple[int, ...]:
    cycle = tuple((v, (v + 1) % 7) for v in range(7))
    result = tuple(
        catalogue7.canonical[mask_from_edges(7, cycle + chords)]
        for chords in SOURCE_H_CHORDS
    )
    if len(set(result)) != 19:
        raise AssertionError("Hamiltonian representatives collide")
    return result


def hamiltonian_affine_rows() -> tuple[tuple[int, int], ...]:
    """Return (constant at n3=4158, coefficient of y=h11/4)."""
    common = N * K * (K - 2)
    b = common * (K - 4)
    values = (
        (Fraction(b * (2 * K**2 - 30 * K + 133), 14) - 10 * N3, -4),
        (Fraction(common * (2 * K**2 - 25 * K + 68), 2) + 16 * N3, 6),
        (Fraction(b * (K - 8)) + 12 * N3, 10),
        (Fraction(b) - 2 * N3, -2),
        (Fraction(b) - 4 * N3, 0),
        (Fraction(b, 2), -2),
        (Fraction(b) - 8 * N3, 0),
        (Fraction(b, 2), -6),
        (Fraction(2 * b) - 8 * N3, -8),
        (Fraction(b) - 2 * N3, -6),
        (Fraction(2 * N3), 0),
        (Fraction(0), 4),
        (Fraction(common, 4) - N3, 1),
        (Fraction(0), 2),
        (Fraction(4 * N3), 0),
        (Fraction(2 * N3), 0),
        (Fraction(-2 * N3), 4),
        (Fraction(common, 4) - N3, 0),
        (Fraction(N3), -1),
    )
    result = []
    for constant, coefficient in values:
        if constant.denominator != 1:
            raise AssertionError("nonintegral Hamiltonian constant")
        result.append((constant.numerator, coefficient))
    return tuple(result)


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first, *tail)


def signatures(common_cap: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(value for value in compositions(5, 4) if value[0] <= common_cap)


def pair_signature(rows: Sequence[int], first: int, second: int) -> tuple[int, int, int, int]:
    counts = [0, 0, 0, 0]
    for vertex in range(7):
        if vertex in (first, second):
            continue
        a = bool(rows[first] >> vertex & 1)
        b = bool(rows[second] >> vertex & 1)
        counts[0 if a and b else 1 if a else 2 if b else 3] += 1
    return tuple(counts)


def vertex_family(classes: Sequence[int]) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    rows = [[0] * len(classes) for _ in range(7)]
    for column, mask in enumerate(classes):
        graph = adjacency(mask, 7)
        for root in range(7):
            rows[graph[root].bit_count()][column] += 1
    rhs = tuple(N * math.comb(K, d) * math.comb(N - 1 - K, 6 - d) for d in range(7))
    return tuple(tuple(row) for row in rows), rhs


def pair_family(
    classes: Sequence[int], adjacent_roots: bool
) -> tuple[tuple[tuple[int, int, int, int], ...], tuple[tuple[int, ...], ...], tuple[int, ...]]:
    cap = LAMBDA if adjacent_roots else MU
    universe = signatures(cap)
    index = {signature: row for row, signature in enumerate(universe)}
    rows = [[0] * len(classes) for _ in universe]
    for column, mask in enumerate(classes):
        graph = adjacency(mask, 7)
        for first in range(7):
            for second in range(7):
                if first == second or bool(graph[first] >> second & 1) != adjacent_roots:
                    continue
                signature = pair_signature(graph, first, second)
                rows[index[signature]][column] += 1
    if adjacent_roots:
        sizes, root_count = (1, 12, 12, 72), N * K
    else:
        sizes, root_count = (2, 12, 12, 71), N * (N - 1 - K)
    rhs = tuple(
        root_count * math.prod(math.comb(size, selected) for size, selected in zip(sizes, signature))
        for signature in universe
    )
    return universe, tuple(tuple(row) for row in rows), rhs


def assemble_system() -> dict[str, object]:
    public = strict_json(PUBLIC_W43, EXPECTED[PUBLIC_W43])
    samples = [memory_sample("before-catalogues")]
    cat6 = complete_catalogue(6)
    classes6 = tuple(mask for mask in cat6.classes if admissible(mask, 6))
    if len(classes6) != 62 or set(classes6) != set(SOURCE_N_MASKS):
        raise AssertionError("public six-class interface mismatch")
    cat7 = complete_catalogue(7)
    classes7 = tuple(mask for mask in cat7.classes if admissible(mask, 7))
    if len(classes7) != 208:
        raise AssertionError("seven-class count mismatch")
    class_stream = sha256(b"".join(mask.to_bytes(3, "big") for mask in classes7))
    public_hash = public["catalogues"]["order_7"]["class_stream_sha256"]
    if class_stream != public_hash:
        raise AssertionError("seven-class stream differs from verified Wave43")
    samples.append(memory_sample("after-catalogues"))

    deck = deletion_rows(classes7, cat6)
    public_six = tuple(int(x) for x in public["model"]["six_counts"])
    if len(public_six) != 62:
        raise AssertionError("public six-count vector length mismatch")
    deck_rhs = tuple((N - 6) * value for value in public_six)

    h_masks = hamiltonian_masks(cat7)
    if list(h_masks) != public["model"]["hamiltonian_masks"]:
        raise AssertionError("independent Hamiltonian masks differ from Wave43")
    affines = hamiltonian_affine_rows()
    base_rows = [tuple(row) + (0,) for row in deck]
    base_rhs = list(deck_rhs)
    class_index = {mask: index for index, mask in enumerate(classes7)}
    for mask, (constant, y_coefficient) in zip(h_masks, affines):
        row = [0] * 209
        row[class_index[mask]] = 1
        row[-1] = -y_coefficient
        base_rows.append(tuple(row))
        base_rhs.append(constant)

    vertex_rows, vertex_rhs = vertex_family(classes7)
    edge_universe, edge_rows, edge_rhs = pair_family(classes7, True)
    nonedge_universe, nonedge_rows, nonedge_rhs = pair_family(classes7, False)
    extend = lambda family: tuple(tuple(row) + (0,) for row in family)
    rows = tuple(base_rows) + extend(vertex_rows) + extend(edge_rows) + extend(nonedge_rows)
    rhs = tuple(base_rhs) + vertex_rhs + edge_rhs + nonedge_rhs
    if len(rows) != 170 or len(rows[0]) != 209:
        raise AssertionError("170x209 system shape failed")
    for column in range(208):
        if sum(row[column] for row in vertex_rows) != 7:
            raise AssertionError("vertex-root column partition failed")
        if sum(row[column] for row in edge_rows) + sum(row[column] for row in nonedge_rows) != 42:
            raise AssertionError("ordered-pair column partition failed")
    if sum(vertex_rhs) != 7 * math.comb(N, 7):
        raise AssertionError("vertex-root RHS total failed")
    if sum(edge_rhs) != N * K * math.comb(N - 2, 5):
        raise AssertionError("edge-root RHS total failed")
    if sum(nonedge_rhs) != N * (N - 1 - K) * math.comb(N - 2, 5):
        raise AssertionError("nonedge-root RHS total failed")
    samples.append(memory_sample("system-complete"))
    return {
        "classes": classes7, "rows": rows, "rhs": rhs,
        "base_rows": tuple(base_rows), "base_rhs": tuple(base_rhs),
        "vertex_rows": extend(vertex_rows), "vertex_rhs": vertex_rhs,
        "edge_universe": edge_universe, "edge_rows": extend(edge_rows), "edge_rhs": edge_rhs,
        "nonedge_universe": nonedge_universe, "nonedge_rows": extend(nonedge_rows), "nonedge_rhs": nonedge_rhs,
        "class_stream_sha256": class_stream, "memory_samples": samples,
    }


def residuals(
    rows: Sequence[Sequence[int]], rhs: Sequence[int], vector: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector)) - target
        for row, target in zip(rows, rhs)
    )


def load_witness(system: dict[str, object]) -> tuple[tuple[int, ...], list[dict[str, int]], dict[str, object]]:
    payload = strict_json(WITNESS, EXPECTED[WITNESS])
    if payload.get("format") != "wave44-rooted-flags-witness-v1":
        raise AssertionError("witness format mismatch")
    support = payload.get("support")
    if not isinstance(support, list) or len(support) != 91:
        raise AssertionError("witness support is not a 91-record list")
    classes = system["classes"]
    index = {mask: position for position, mask in enumerate(classes)}
    counts = [0] * len(classes)
    normalized: list[dict[str, int]] = []
    seen: set[int] = set()
    for record in support:
        if not isinstance(record, dict) or set(record) != {"canonical_mask", "count"}:
            raise AssertionError("malformed witness record")
        mask, count = record["canonical_mask"], record["count"]
        if type(mask) is not int or type(count) is not int or count <= 0:
            raise AssertionError("witness record is not positive integral")
        if mask not in index or mask in seen:
            raise AssertionError("unknown or duplicate witness class")
        seen.add(mask)
        counts[index[mask]] = count
        normalized.append({"canonical_mask": mask, "count": count})
    if normalized != sorted(normalized, key=lambda record: record["canonical_mask"]):
        raise AssertionError("witness support not canonical-mask ordered")
    if compact_hash(normalized) != payload.get("support_sha256"):
        raise AssertionError("witness support digest mismatch")
    h11 = payload.get("h11")
    if type(h11) is not int or h11 % 4 or h11 // 4 != 4158:
        raise AssertionError("witness y is not 4158")
    vector = tuple(counts) + (h11 // 4,)
    exact = residuals(system["rows"], system["rhs"], vector)
    if any(exact):
        raise AssertionError("witness fails an exact rooted row")
    if sum(counts) != math.comb(N, 7):
        raise AssertionError("seven-subset total mismatch")
    return vector, normalized, payload


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[int(x) % prime for x in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((r for r in range(rank, len(work)) if work[r][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(x * inverse) % prime for x in work[rank]]
        for row in range(len(work)):
            if row == rank:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == len(work):
            break
    return rank


def hostile_controls(system: dict[str, object], vector: tuple[int, ...]) -> list[dict[str, object]]:
    controls: list[dict[str, object]] = []

    def reject(label: str, operation: Callable[[], bool]) -> None:
        if not operation():
            raise AssertionError(f"hostile control accepted: {label}")
        controls.append({"label": label, "outcome": "REJECTED"})

    positive = next(index for index, value in enumerate(vector[:-1]) if value)
    changed = list(vector)
    changed[positive] += 1
    reject("increment positive support coefficient", lambda: any(residuals(system["rows"], system["rhs"], changed)))
    changed_y = list(vector)
    changed_y[-1] += 1
    reject("increment y", lambda: any(residuals(system["rows"], system["rhs"], changed_y)))

    families = (
        ("vertex coefficient", system["vertex_rows"], system["vertex_rhs"]),
        ("edge coefficient", system["edge_rows"], system["edge_rhs"]),
        ("nonedge coefficient", system["nonedge_rows"], system["nonedge_rhs"]),
    )
    for label, rows, rhs in families:
        hostile = [list(row) for row in rows]
        location = next(
            (r, c) for r, row in enumerate(hostile)
            for c, coefficient in enumerate(row)
            if coefficient and vector[c]
        )
        hostile[location[0]][location[1]] += 1
        reject(label, lambda hostile=hostile, rhs=rhs: any(residuals(hostile, rhs, vector)))
    hostile_rhs = list(system["rhs"])
    hostile_rhs[0] += 1
    reject("increment exact RHS", lambda: any(residuals(system["rows"], hostile_rhs, vector)))
    return controls


def scipy_diagnostic(
    rows: Sequence[Sequence[int]], rhs: Sequence[int], vector: Sequence[int]
) -> dict[str, object]:
    row_index: list[int] = []
    col_index: list[int] = []
    values: list[float] = []
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            if value:
                row_index.append(r)
                col_index.append(c)
                values.append(float(value))
    matrix = coo_array(
        (np.asarray(values), (np.asarray(row_index), np.asarray(col_index))),
        shape=(len(rows), len(rows[0])),
    ).tocsr()
    lower = np.zeros(len(vector))
    upper = np.full(len(vector), np.inf)
    lower[-1], upper[-1] = 2079, 4158
    raw = milp(
        c=np.zeros(len(vector)), integrality=np.ones(len(vector), dtype=np.uint8),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(matrix, np.asarray(rhs, dtype=float), np.asarray(rhs, dtype=float)),
        options={"presolve": True, "time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    exact_residual = residuals(rows, rhs, vector)
    float_residual = matrix @ np.asarray(vector, dtype=float) - np.asarray(rhs, dtype=float)
    scales = np.maximum(np.max(np.abs(matrix.toarray()), axis=1), np.abs(np.asarray(rhs, dtype=float)))
    scales[scales == 0] = 1
    scaled_matrix = matrix.multiply((1.0 / scales)[:, None]).tocsr()
    scaled_rhs = np.asarray(rhs, dtype=float) / scales
    scaled = milp(
        c=np.zeros(len(vector)), integrality=np.ones(len(vector), dtype=np.uint8),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(scaled_matrix, scaled_rhs, scaled_rhs),
        options={"presolve": True, "time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    fixed_values = np.asarray(vector, dtype=float)
    fixed_presolve = milp(
        c=np.zeros(len(vector)), integrality=np.ones(len(vector), dtype=np.uint8),
        bounds=Bounds(fixed_values, fixed_values),
        constraints=LinearConstraint(matrix, np.asarray(rhs, dtype=float), np.asarray(rhs, dtype=float)),
        options={"presolve": True, "time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    fixed_no_presolve = milp(
        c=np.zeros(len(vector)), integrality=np.ones(len(vector), dtype=np.uint8),
        bounds=Bounds(fixed_values, fixed_values),
        constraints=LinearConstraint(matrix, np.asarray(rhs, dtype=float), np.asarray(rhs, dtype=float)),
        options={"presolve": False, "time_limit": 30.0, "mip_rel_gap": 0.0},
    )
    nonzero_rhs = [abs(value) for value in rhs if value]
    return {
        "unscaled": {
            "status": int(raw.status), "success": bool(raw.success),
            "message": str(raw.message),
        },
        "row_scaled": {
            "status": int(scaled.status), "success": bool(scaled.success),
            "message": str(scaled.message),
        },
        "exact_witness_fixed_bounds_presolve": {
            "status": int(fixed_presolve.status),
            "success": bool(fixed_presolve.success),
            "message": str(fixed_presolve.message),
        },
        "exact_witness_fixed_bounds_no_presolve": {
            "status": int(fixed_no_presolve.status),
            "success": bool(fixed_no_presolve.success),
            "message": str(fixed_no_presolve.message),
        },
        "absolute_nonzero_rhs_range": [min(nonzero_rhs), max(nonzero_rhs)],
        "exact_witness_max_abs_integer_residual": max(map(abs, exact_residual)),
        "exact_witness_max_abs_float_residual": float(np.max(np.abs(float_residual))),
        "unscaled_infeasible_status_is_false": int(raw.status) == 2 and not any(exact_residual),
        "solver_exit_code_used_as_certificate": False,
        "assessment": "Any infeasible status is refuted by the exact nonnegative integer witness; scaling sensitivity is numerical, not mathematical evidence.",
    }


def compare_discovery_rows(
    system: dict[str, object], discovery: dict[str, object]
) -> tuple[dict[str, object], dict[str, str]]:
    """Strictly compare the post-freeze discovery artifact to independent rows."""
    payload = strict_json(DISCOVERY_ROWS, EXPECTED[DISCOVERY_ROWS])
    if payload.get("format") != "wave44-rooted-row-system-v1":
        raise AssertionError("discovery row-system format mismatch")
    if payload.get("canonical_hash_encoding") != (
        "UTF-8 compact JSON with sort_keys=True and separators=(',',':')"
    ):
        raise AssertionError("discovery row-system hash encoding mismatch")

    classes = payload.get("classes")
    if not isinstance(classes, list) or any(type(mask) is not int for mask in classes):
        raise AssertionError("discovery class stream is not a strict integer list")
    if classes != list(system["classes"]):
        raise AssertionError("discovery and independent class streams differ")

    independent_families = {
        "base": canonical_family(system["base_rows"], system["base_rhs"]),
        "vertex": canonical_family(system["vertex_rows"], system["vertex_rhs"]),
        "edge": canonical_family(system["edge_rows"], system["edge_rhs"]),
        "nonedge": canonical_family(system["nonedge_rows"], system["nonedge_rhs"]),
    }
    published_families = payload.get("families")
    if not isinstance(published_families, dict) or set(published_families) != set(independent_families):
        raise AssertionError("discovery row-system family set mismatch")
    expected_counts = {"base": 81, "vertex": 7, "edge": 36, "nonedge": 46}
    for name, expected_family in independent_families.items():
        family = published_families[name]
        if not isinstance(family, dict) or set(family) != {"rows", "rhs"}:
            raise AssertionError(f"malformed discovery {name} family")
        rows, rhs = family["rows"], family["rhs"]
        if not isinstance(rows, list) or not isinstance(rhs, list):
            raise AssertionError(f"discovery {name} rows/RHS are not lists")
        if len(rows) != expected_counts[name] or len(rhs) != expected_counts[name]:
            raise AssertionError(f"discovery {name} row count mismatch")
        if any(
            not isinstance(row, list)
            or len(row) != 209
            or any(type(value) is not int for value in row)
            for row in rows
        ):
            raise AssertionError(f"discovery {name} coefficients are not strict 209-integer rows")
        if any(type(value) is not int for value in rhs):
            raise AssertionError(f"discovery {name} RHS is not strictly integral")
        if family != expected_family:
            raise AssertionError(f"discovery {name} differs from independent ordered rows/RHS")

    published_hashes = payload.get("row_rhs_sha256")
    if not isinstance(published_hashes, dict) or set(published_hashes) != {
        "base", "vertex", "edge", "nonedge", "combined"
    }:
        raise AssertionError("discovery row-system hash table mismatch")
    independent_hashes = {
        name: compact_hash(family) for name, family in independent_families.items()
    }
    independent_hashes["combined"] = compact_hash(independent_families)
    if published_hashes != independent_hashes:
        raise AssertionError("published row-system hashes do not bind the independent rows")
    discovery_hashes = discovery.get("rooted_system", {}).get("row_rhs_sha256")
    if discovery_hashes != independent_hashes:
        raise AssertionError("discovery result and row-system hash tables differ")

    comparison = {
        "discovery_row_system_format": payload["format"],
        "discovery_row_system_sha256": EXPECTED[DISCOVERY_ROWS],
        "class_stream_exact_ordered_match": True,
        "family_set_exact_match": True,
        "all_170_rows_exact_ordered_match": True,
        "all_170_rhs_exact_ordered_match": True,
        "coefficients_compared": 170 * 209,
        "rhs_values_compared": 170,
        "canonical_discovery_hashes_exact_match": True,
        "hash_encoding": payload["canonical_hash_encoding"],
        "prior_provisional_hash_note": (
            "The provisional verifier digest hashed [numeric_rows,rhs]; the "
            "published commitment hashes {'rows':numeric_rows,'rhs':rhs}. "
            "Both encode the same exact streams, and the verifier now records "
            "the published canonical object encoding."
        ),
    }
    return comparison, independent_hashes


def compute() -> dict[str, object]:
    for path, expected in EXPECTED.items():
        if sha256(path.read_bytes()) != expected:
            raise ValueError(f"frozen input changed: {path}")
    system = assemble_system()
    vector, support, witness = load_witness(system)
    controls = hostile_controls(system, vector)
    rank_table = {}
    base = system["base_rows"]
    vertex = system["vertex_rows"]
    edge = system["edge_rows"]
    nonedge = system["nonedge_rows"]
    for prime in (101, 103, 107):
        rank_table[str(prime)] = {
            "base": rank_mod(base, prime),
            "base_plus_vertex": rank_mod(base + vertex, prime),
            "base_plus_vertex_edge": rank_mod(base + vertex + edge, prime),
            "all_rooted": rank_mod(base + vertex + edge + nonedge, prime),
        }
    diagnostic = scipy_diagnostic(system["rows"], system["rhs"], vector)
    discovery = strict_json(DISCOVERY_RESULT, EXPECTED[DISCOVERY_RESULT])
    row_comparison, discovery_row_hashes = compare_discovery_rows(system, discovery)
    row_hashes = {
        "base_rows_rhs_sha256": discovery_row_hashes["base"],
        "vertex_rows_rhs_sha256": discovery_row_hashes["vertex"],
        "edge_rows_rhs_sha256": discovery_row_hashes["edge"],
        "nonedge_rows_rhs_sha256": discovery_row_hashes["nonedge"],
        "all_170_rows_rhs_sha256": discovery_row_hashes["combined"],
        "internal_numeric_pair_encoding_sha256": compact_hash([system["rows"], system["rhs"]]),
        "zero_residual_stream_sha256": compact_hash(residuals(system["rows"], system["rhs"], vector)),
    }
    result = {
        "format": "wave44-rooted-flags-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_FEASIBILITY",
        "scope": "exact feasibility of the frozen 170-row, 209-variable aggregate rooted seven-class relaxation at n3=y=4158",
        "inputs": {
            path.relative_to(ROOT).as_posix(): expected for path, expected in EXPECTED.items()
        },
        "catalogue": {
            "classes": len(system["classes"]),
            "class_stream_sha256": system["class_stream_sha256"],
        },
        "system": {
            "variables": 209, "rows": 170, "unrooted_rows": 81,
            "vertex_rows": 7, "edge_rows": 36, "nonedge_rows": 46,
            "edge_signatures": [list(x) for x in system["edge_universe"]],
            "nonedge_signatures": [list(x) for x in system["nonedge_universe"]],
            "edge_category_sizes": [1, 12, 12, 72],
            "nonedge_category_sizes": [2, 12, 12, 71],
            "rank_table": rank_table,
            **row_hashes,
        },
        "certificate": {
            "y": vector[-1], "h11": 4 * vector[-1],
            "support_size": len(support), "zero_classes": 208 - len(support),
            "maximum_count": max(vector[:-1]), "seven_subset_total": sum(vector[:-1]),
            "support_sha256": compact_hash(support),
            "witness_file_sha256": EXPECTED[WITNESS],
            "all_170_exact_integer_rows": "PASS",
        },
        "comparison": {
            "discovery_claim_label": discovery.get("claim_label"),
            "discovery_summary_exact_match": (
                discovery.get("rooted_system", {}).get("total_rows") == 170
                and discovery.get("rooted_system", {}).get("variables_including_h11_over_4") == 209
                and discovery.get("exact_positive_control", {}).get("support_sha256") == compact_hash(support)
                and discovery.get("exact_positive_control", {}).get("all_170_exact_integer_rows") == "PASS"
            ),
            "discovery_row_system_exact_match": True,
            **row_comparison,
        },
        "controls": controls,
        "solver_diagnostic": diagnostic,
        "resource_guard": {
            "minimum_free_memory_percent": MIN_FREE_PERCENT,
            "checkpoints": [
                sample["label"]
                for sample in system["memory_samples"] + [memory_sample("verifier-finish")]
            ],
            "all_runtime_samples_met_minimum": True,
            "runtime_values_archived": False,
        },
        "conclusion": {
            "aggregate_rooted_system": "EXACT_FEASIBLE",
            "graph_constructed": False, "endpoint_evidence": False,
            "endpoint_n3_4158": "UNKNOWN", "upper_bound_below_4158": "NOT_PROVED",
            "conway_99": "UNKNOWN", "automorphism_assumed": False,
            "solver_exit_code_authority": "REJECTED",
        },
        "limitations": [
            "Aggregate rooted rows do not enforce compatibility between overlapping seven-subsets.",
            "The exact count vector is not a graph and is not evidence that a graph exists.",
            "No positive-semidefinite flag moment matrix is imposed.",
            "No endpoint exclusion, upper-bound improvement, novelty, or priority claim follows.",
        ],
    }
    validate(result)
    return result


def validate(value: dict[str, object]) -> None:
    if value.get("claim_label") != "VERIFIED_SCOPED_FEASIBILITY":
        raise ValueError("wrong scoped label")
    system = value["system"]
    if (system["variables"], system["rows"], system["unrooted_rows"],
        system["vertex_rows"], system["edge_rows"], system["nonedge_rows"]) != (209, 170, 81, 7, 36, 46):
        raise ValueError("system shape mismatch")
    if any(record != {"base": 81, "base_plus_vertex": 82, "base_plus_vertex_edge": 87, "all_rooted": 93}
           for record in system["rank_table"].values()):
        raise ValueError("rank table mismatch")
    certificate = value["certificate"]
    if certificate["y"] != 4158 or certificate["support_size"] != 91 or certificate["all_170_exact_integer_rows"] != "PASS":
        raise ValueError("certificate mismatch")
    if not value["comparison"]["discovery_summary_exact_match"]:
        raise ValueError("discovery summary mismatch")
    if not value["comparison"]["discovery_row_system_exact_match"]:
        raise ValueError("discovery row-system mismatch")
    if not value["comparison"]["all_170_rows_exact_ordered_match"]:
        raise ValueError("discovery coefficient mismatch")
    if not value["comparison"]["all_170_rhs_exact_ordered_match"]:
        raise ValueError("discovery RHS mismatch")
    if any(control["outcome"] != "REJECTED" for control in value["controls"]):
        raise ValueError("hostile mutation accepted")
    diagnostic = value["solver_diagnostic"]
    if diagnostic["exact_witness_max_abs_integer_residual"] != 0 or diagnostic["solver_exit_code_used_as_certificate"]:
        raise ValueError("solver status improperly promoted")
    conclusion = value["conclusion"]
    if conclusion["endpoint_evidence"] or conclusion["graph_constructed"] or conclusion["endpoint_n3_4158"] != "UNKNOWN" or conclusion["conway_99"] != "UNKNOWN":
        raise ValueError("status inflation")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    observed = compute()
    payload = canonical(observed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        expected = strict_json(args.verify)
        validate(expected)
        if payload != canonical(expected):
            raise ValueError("live rooted replay differs from archived result")
    print("PASS: exact 170-row rooted aggregate witness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
