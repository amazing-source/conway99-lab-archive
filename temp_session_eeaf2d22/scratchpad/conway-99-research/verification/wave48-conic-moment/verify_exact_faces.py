#!/usr/bin/env python3
"""Independent exact verifier for the Wave48 affine space and moment faces.

The reconstruction phase does not read or import any Wave48 discovery code or
JSON claim.  The comparison phase is intentionally separate and requires a
previously sealed independent reconstruction.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROW_SYSTEM = ROOT / "attempts/wave44-rooted-flags/row-system.json"
W45 = ROOT / "attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json"
W47 = ROOT / "attempts/wave47-three-root-moment/coefficients.json"
DISCOVERY_FACES = ROOT / "attempts/wave48-conic-moment/exact-faces.json"
INDEPENDENT = HERE / "independent-reconstruction.json"
COMPARISON = HERE / "verification-results.json"
EXPECTED = {
    ROW_SYSTEM: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    W45: "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
    W47: "07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3",
    DISCOVERY_FACES: "49d157a2c6025f7a7d1149619959e3f488229d619a5c65a03a79e7a71a93f066",
}
PRIMES = (1000003, 1000033, 1000037)
MIN_FREE_PERCENT = 20.0


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def free_memory_percent() -> float:
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
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
        state = MEMORYSTATUSEX()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    available = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return 100.0 * available / total


def guard(stage: str) -> float:
    free = free_memory_percent()
    if free < MIN_FREE_PERCENT:
        raise MemoryError(f"{stage}: only {free:.2f}% physical memory free")
    print(f"[memory] {stage}: {free:.2f}% free", flush=True)
    return free


def checked_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    if sha256_bytes(payload) != EXPECTED[path]:
        raise ValueError(f"frozen hash mismatch: {path}")
    return payload


def load_exact_input(path: Path) -> dict[str, Any]:
    data = json.loads(checked_bytes(path))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def sparse_rref(
    input_rows: Iterable[dict[int, Fraction]], column_count: int
) -> tuple[list[dict[int, Fraction]], list[int]]:
    rows = [
        {column: Fraction(value) for column, value in row.items() if value}
        for row in input_rows
    ]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(column_count):
        selected = next(
            (index for index in range(pivot_row, len(rows)) if rows[index].get(column)),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = {
            key: value / pivot for key, value in rows[pivot_row].items()
        }
        pivot_data = rows[pivot_row]
        for index, row in enumerate(rows):
            if index == pivot_row:
                continue
            multiplier = row.get(column)
            if not multiplier:
                continue
            updated = dict(row)
            for key, value in pivot_data.items():
                candidate = updated.get(key, Fraction()) - multiplier * value
                if candidate:
                    updated[key] = candidate
                else:
                    updated.pop(key, None)
            rows[index] = updated
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    nonzero = [row for row in rows if row]
    return nonzero, pivots


def integer_vector(vector: list[Fraction]) -> list[int]:
    denominator = math.lcm(*(value.denominator for value in vector))
    values = [int(value * denominator) for value in vector]
    divisor = math.gcd(*(abs(value) for value in values))
    if divisor:
        values = [value // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return values


def nullspace_from_rref(
    rows: list[dict[int, Fraction]], pivots: list[int], column_count: int
) -> list[list[Fraction]]:
    pivot_rows = {
        pivot: row for pivot, row in zip(pivots, rows, strict=True)
    }
    free = [column for column in range(column_count) if column not in pivot_rows]
    basis = []
    for free_column in free:
        vector = [Fraction() for _ in range(column_count)]
        vector[free_column] = Fraction(1)
        for pivot in reversed(pivots):
            row = pivot_rows[pivot]
            vector[pivot] = -sum(
                value * vector[column]
                for column, value in row.items()
                if column != pivot and column < column_count
            )
        basis.append(vector)
    return basis


def affine_space(row_system: dict[str, Any]) -> tuple[
    list[Fraction], list[list[Fraction]], dict[str, Any]
]:
    rows: list[dict[int, Fraction]] = []
    order = ("base", "vertex", "edge", "nonedge")
    row_counts: dict[str, int] = {}
    for family_name in order:
        family = row_system["families"][family_name]
        row_counts[family_name] = len(family["rows"])
        for coefficients, rhs in zip(
            family["rows"], family["rhs"], strict=True
        ):
            row = {
                index: Fraction(value)
                for index, value in enumerate(coefficients)
                if value
            }
            if rhs:
                row[209] = Fraction(rhs)
            rows.append(row)
    if len(rows) != 170:
        raise ValueError("row count changed")
    rref, pivots_augmented = sparse_rref(rows, 210)
    if 209 in pivots_augmented:
        raise ValueError("affine system is inconsistent")
    pivots = pivots_augmented
    rank = len(pivots)
    if rank != 93 or 209 - rank != 116:
        raise ValueError(f"unexpected affine rank/nullity: {rank}/{209-rank}")
    pivot_rows = {
        pivot: row for pivot, row in zip(pivots, rref, strict=True)
    }
    particular = [Fraction() for _ in range(209)]
    for pivot in pivots:
        particular[pivot] = pivot_rows[pivot].get(209, Fraction())
    homogeneous_rows = [
        {key: value for key, value in row.items() if key < 209}
        for row in rref
    ]
    nullspace = nullspace_from_rref(homogeneous_rows, pivots, 209)
    # Exact certificate checks against the original integer system.
    particular_checks = 0
    null_checks = 0
    for family_name in order:
        family = row_system["families"][family_name]
        for coefficients, rhs in zip(
            family["rows"], family["rhs"], strict=True
        ):
            if sum(Fraction(c) * x for c, x in zip(coefficients, particular)) != rhs:
                raise ValueError("particular solution certificate failed")
            particular_checks += 1
            for vector in nullspace:
                if sum(Fraction(c) * x for c, x in zip(coefficients, vector)):
                    raise ValueError("nullspace certificate failed")
                null_checks += 1
    basis_catalog = [
        [[index, fstr(value)] for index, value in enumerate(vector) if value]
        for vector in nullspace
    ]
    record = {
        "row_count": 170,
        "column_count": 209,
        "row_family_counts": row_counts,
        "rational_rank": rank,
        "affine_nullity": len(nullspace),
        "consistent": True,
        "pivot_columns": pivots,
        "free_columns": [
            column for column in range(209) if column not in pivots
        ],
        "particular_solution_sha256": sha256_bytes(
            canonical_payload([fstr(value) for value in particular])
        ),
        "nullspace_basis_sha256": sha256_bytes(canonical_payload(basis_catalog)),
        "exact_particular_row_checks": particular_checks,
        "exact_nullspace_row_checks": null_checks,
    }
    return particular, nullspace, record


def edge_pairs(order: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(order) for j in range(i + 1, order)]


def relabel_mask(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    pair_to_bit = {pair: bit for bit, pair in enumerate(edge_pairs(order))}
    result = 0
    for bit, (left, right) in enumerate(edge_pairs(order)):
        if (mask >> bit) & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            result |= 1 << pair_to_bit[image]
    return result


_CANONICAL: dict[tuple[int, int], int] = {}


def canonical_mask(mask: int, order: int) -> int:
    key = (order, mask)
    if key not in _CANONICAL:
        _CANONICAL[key] = min(
            relabel_mask(mask, order, permutation)
            for permutation in itertools.permutations(range(order))
        )
    return _CANONICAL[key]


def induced_mask(mask: int, order: int, subset: tuple[int, ...]) -> int:
    pair_to_bit = {pair: bit for bit, pair in enumerate(edge_pairs(order))}
    result = 0
    for new_bit, (left, right) in enumerate(edge_pairs(len(subset))):
        old_pair = tuple(sorted((subset[left], subset[right])))
        if (mask >> pair_to_bit[old_pair]) & 1:
            result |= 1 << new_bit
    return result


def lower_counts(
    classes7: list[int],
    particular: list[Fraction],
    masks_by_order: dict[int, list[int]],
    nullspace: list[list[Fraction]],
) -> tuple[dict[int, dict[int, int]], dict[str, Any]]:
    output: dict[int, dict[int, int]] = {}
    fixed_direction_checks = 0
    catalog: dict[str, list[list[int]]] = {}
    for order in sorted(masks_by_order):
        if order == 7:
            continue
        subset_count = math.comb(99 - order, 7 - order)
        counts: dict[int, int] = {}
        order_catalog: list[list[int]] = []
        for target in masks_by_order[order]:
            containment = []
            for host in classes7:
                count = sum(
                    canonical_mask(induced_mask(host, 7, subset), order) == target
                    for subset in itertools.combinations(range(7), order)
                )
                containment.append(count)
            value = sum(
                Fraction(coefficient) * particular[index]
                for index, coefficient in enumerate(containment)
            ) / subset_count
            if value.denominator != 1:
                raise ValueError(f"nonintegral lower count order {order} mask {target}")
            for direction in nullspace:
                if sum(
                    Fraction(coefficient) * direction[index]
                    for index, coefficient in enumerate(containment)
                ):
                    raise ValueError("lower count is not fixed on affine space")
                fixed_direction_checks += 1
            counts[target] = value.numerator
            order_catalog.append([target, value.numerator])
        output[order] = counts
        catalog[str(order)] = order_catalog
    return output, {
        "counts": catalog,
        "sha256": sha256_bytes(canonical_payload(catalog)),
        "fixed_affine_direction_checks": fixed_direction_checks,
    }


def zero_matrix(size: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def add_upper(
    matrix: list[list[Fraction]], row: int, column: int, value: Fraction
) -> None:
    matrix[row][column] += value
    if row != column:
        matrix[column][row] += value


class ExactRowSpan:
    def __init__(self, width: int) -> None:
        self.width = width
        self.rows: dict[int, dict[int, Fraction]] = {}
        self.rows_seen = 0
        self.dependent_rows = 0

    def add(self, dense: list[Fraction]) -> None:
        self.rows_seen += 1
        row = {index: value for index, value in enumerate(dense) if value}
        for pivot in sorted(self.rows):
            multiplier = row.get(pivot)
            if not multiplier:
                continue
            for column, value in self.rows[pivot].items():
                candidate = row.get(column, Fraction()) - multiplier * value
                if candidate:
                    row[column] = candidate
                else:
                    row.pop(column, None)
        if not row:
            self.dependent_rows += 1
            return
        pivot = min(row)
        scale = row[pivot]
        self.rows[pivot] = {
            column: value / scale for column, value in row.items()
        }

    def rref(self) -> tuple[list[dict[int, Fraction]], list[int]]:
        return sparse_rref(self.rows.values(), self.width)


def moment_matrices(
    family: dict[str, Any],
    lower: dict[int, dict[int, int]],
    particular: list[Fraction],
    nullspace: list[list[Fraction]],
    class_index: dict[int, int],
) -> Iterator[list[list[Fraction]]]:
    size = int(family["matrix_size"])
    constant = zero_matrix(size)
    order7: list[tuple[int, list[list[int]]]] = []
    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        if order < 7:
            multiplier = lower[order][mask]
            for row, column, coefficient in record["upper_entries"]:
                add_upper(
                    constant,
                    int(row),
                    int(column),
                    Fraction(int(coefficient) * multiplier),
                )
        else:
            order7.append((class_index[mask], record["upper_entries"]))
    # Process homogeneous directions first. After primitive integer rescaling
    # by the caller these matrices are integral, which keeps row-span
    # elimination small before the single affine-point matrix is introduced.
    for direction in nullspace:
        matrix = zero_matrix(size)
        for variable, entries in order7:
            multiplier = direction[variable]
            if multiplier:
                for row, column, coefficient in entries:
                    add_upper(
                        matrix,
                        int(row),
                        int(column),
                        multiplier * int(coefficient),
                    )
        yield matrix
    point = [row[:] for row in constant]
    for variable, entries in order7:
        multiplier = particular[variable]
        if multiplier:
            for row, column, coefficient in entries:
                add_upper(
                    point, int(row), int(column), multiplier * int(coefficient)
                )
    flat_integer = integer_vector([value for row in point for value in row])
    yield [
        [Fraction(flat_integer[row * size + column]) for column in range(size)]
        for row in range(size)
    ]


def rank_mod_prime(
    rows: list[dict[int, Fraction]], width: int, prime: int
) -> int:
    modular = []
    for row in rows:
        converted = {}
        for column, value in row.items():
            denominator = value.denominator % prime
            if denominator == 0:
                raise ValueError("modular prime divides a denominator")
            converted[column] = (
                value.numerator % prime
            ) * pow(denominator, -1, prime) % prime
        modular.append(converted)
    rank = 0
    for column in range(width):
        selected = next(
            (index for index in range(rank, len(modular)) if modular[index].get(column, 0)),
            None,
        )
        if selected is None:
            continue
        modular[rank], modular[selected] = modular[selected], modular[rank]
        inverse = pow(modular[rank][column], -1, prime)
        modular[rank] = {
            key: value * inverse % prime
            for key, value in modular[rank].items()
            if value % prime
        }
        for index in range(rank + 1, len(modular)):
            multiplier = modular[index].get(column, 0)
            if not multiplier:
                continue
            for key, value in modular[rank].items():
                candidate = (
                    modular[index].get(key, 0) - multiplier * value
                ) % prime
                if candidate:
                    modular[index][key] = candidate
                else:
                    modular[index].pop(key, None)
        rank += 1
    return rank


def reconstruct_family(
    source: str,
    name: str,
    family: dict[str, Any],
    lower: dict[int, dict[int, int]],
    particular: list[Fraction],
    nullspace: list[list[Fraction]],
    class_index: dict[int, int],
) -> dict[str, Any]:
    size = int(family["matrix_size"])
    span = ExactRowSpan(size)
    digest = hashlib.sha256()
    forced_zero = [True] * size
    matrix_count = 0
    for matrix in moment_matrices(
        family, lower, particular, nullspace, class_index
    ):
        matrix_count += 1
        for index in range(size):
            if matrix[index][index]:
                forced_zero[index] = False
        for row in matrix:
            digest.update(
                (",".join(fstr(value) for value in row) + "\n").encode()
            )
            span.add(row)
    rref, pivots = span.rref()
    kernel_fraction = nullspace_from_rref(rref, pivots, size)
    kernel = [integer_vector(vector) for vector in kernel_fraction]
    exact_identity_checks = 0
    for row in rref:
        for vector in kernel:
            if sum(value * vector[column] for column, value in row.items()):
                raise ValueError(f"kernel identity failed for {source}/{name}")
            exact_identity_checks += 1
    modular = {
        str(prime): rank_mod_prime(rref, size, prime) for prime in PRIMES
    }
    if any(rank != len(pivots) for rank in modular.values()):
        raise ValueError(f"modular rank disagreement for {source}/{name}")
    if len(pivots) + len(kernel) != size:
        raise ValueError("rank-nullity completeness failed")
    return {
        "source": source,
        "name": name,
        "matrix_size": size,
        "affine_matrices_stacked": matrix_count,
        "stack_rows_seen": span.rows_seen,
        "exact_active_rank": len(pivots),
        "exact_nullity": len(kernel),
        "rank_plus_nullity": len(pivots) + len(kernel),
        "complete_common_kernel": True,
        "kernel_vectors": kernel,
        "kernel_basis_sha256": sha256_bytes(canonical_payload(kernel)),
        "stack_rows_sha256": digest.hexdigest(),
        "forced_zero_diagonals": [
            index for index, is_zero in enumerate(forced_zero) if is_zero
        ],
        "exact_basis_identity_checks": exact_identity_checks,
        "exact_dependent_row_reductions": span.dependent_rows,
        "modular_active_ranks": modular,
    }


def reconstruct() -> dict[str, Any]:
    memory_start = guard("reconstruction start")
    row_system = load_exact_input(ROW_SYSTEM)
    w45 = load_exact_input(W45)
    w47 = load_exact_input(W47)
    # DISCOVERY_FACES is intentionally not read in this phase.
    particular, nullspace, affine = affine_space(row_system)
    print(
        f"[affine] rank={affine['rational_rank']} nullity={affine['affine_nullity']}",
        flush=True,
    )
    classes7 = [int(mask) for mask in row_system["classes"]]
    class_index = {mask: index for index, mask in enumerate(classes7)}
    masks_by_order: dict[int, list[int]] = {}
    for coefficients in (w45, w47):
        for family in coefficients["families"].values():
            for record in family["class_coefficients"]:
                masks_by_order.setdefault(int(record["order"]), []).append(
                    int(record["canonical_mask"])
                )
    masks_by_order = {
        order: sorted(set(masks)) for order, masks in masks_by_order.items()
    }
    lower, lower_record = lower_counts(
        classes7, particular, masks_by_order, nullspace
    )
    # Independently rescale each rational null direction to a primitive
    # integer direction. This preserves its one-dimensional span and makes
    # the exact stacked-matrix elimination substantially smaller.
    moment_nullspace = [
        [Fraction(value) for value in integer_vector(vector)]
        for vector in nullspace
    ]
    families = []
    for source, coefficients in (("wave45", w45), ("wave47", w47)):
        for name, family in coefficients["families"].items():
            record = reconstruct_family(
                source,
                name,
                family,
                lower,
                particular,
                moment_nullspace,
                class_index,
            )
            print(
                f"[face] {source}/{name}: rank={record['exact_active_rank']} "
                f"nullity={record['exact_nullity']}",
                flush=True,
            )
            families.append(record)
            guard(f"after {source}/{name}")
    result = {
        "format": "wave48-independent-exact-face-reconstruction-v1",
        "role": "verifier",
        "claim_label": "CANDIDATE_INDEPENDENT_PENDING_COMPARISON",
        "scope": "exact rational affine space and complete universal kernels only",
        "discovery_wave48_code_imported_or_executed": False,
        "discovery_exact_faces_opened": False,
        "floating_solver_artifacts_opened": False,
        "inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": EXPECTED[path],
            }
            for path in (ROW_SYSTEM, W45, W47)
        ],
        "affine": affine,
        "lower_counts": lower_record,
        "families": families,
        "resource_guard": {
            "minimum_free_percent": MIN_FREE_PERCENT,
            "free_percent_at_start": round(memory_start, 2),
            "free_percent_at_finish": round(guard("reconstruction finish"), 2),
        },
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "aggregate_feasibility": "UNKNOWN",
        },
    }
    payload = canonical_payload(result)
    INDEPENDENT.write_bytes(payload)
    print(f"independent_sha256={sha256_bytes(payload)}")
    return result


def rational_rank(vectors: list[list[int]]) -> int:
    if not vectors:
        return 0
    rows = [
        {index: Fraction(value) for index, value in enumerate(vector) if value}
        for vector in vectors
    ]
    _, pivots = sparse_rref(rows, len(vectors[0]))
    return len(pivots)


def compare() -> dict[str, Any]:
    independent_payload = INDEPENDENT.read_bytes()
    independent = json.loads(independent_payload)
    independent_hash = sha256_bytes(independent_payload)
    if independent["discovery_exact_faces_opened"]:
        raise ValueError("independent phase was not sealed cleanly")
    discovery = json.loads(checked_bytes(DISCOVERY_FACES))
    comparisons = []
    discovery_lookup = {
        (record["source"], record["name"]): record
        for record in discovery["families"]
    }
    all_pass = True
    for actual in independent["families"]:
        key = (actual["source"], actual["name"])
        expected = discovery_lookup[key]
        expected_vectors = [
            [int(value) for value in item["vector"]]
            for item in expected["kernel_vectors"]
        ]
        actual_vectors = actual["kernel_vectors"]
        dimension = actual["exact_nullity"]
        subspace_equal = (
            rational_rank(actual_vectors) == dimension
            and rational_rank(expected_vectors) == dimension
            and rational_rank(actual_vectors + expected_vectors) == dimension
        )
        checks = {
            "matrix_size_equal": actual["matrix_size"] == expected["ambient_size"],
            "active_rank_equal": actual["exact_active_rank"]
            == expected["exact_rational_active_rank_certified"],
            "nullity_equal": actual["exact_nullity"]
            == expected["exact_rational_nullity_certified"],
            "kernel_subspace_equal": subspace_equal,
            "forced_zero_diagonals_equal": actual["forced_zero_diagonals"]
            == expected["forced_zero_diagonals"],
            "discovery_claimed_exact_affine_identities": expected[
                "all_kernel_vectors_exact_affine_identities"
            ],
            "modular_ranks_equal": actual["modular_active_ranks"]
            == {
                str(key): int(value)
                for key, value in expected["modular_active_ranks"].items()
            },
        }
        passed = all(checks.values())
        all_pass &= passed
        comparisons.append(
            {
                "source": key[0],
                "name": key[1],
                "status": "PASS" if passed else "FAIL",
                "checks": checks,
            }
        )
    affine_checks = {
        "rank_93": independent["affine"]["rational_rank"] == 93,
        "nullity_116": independent["affine"]["affine_nullity"] == 116,
        "discovery_rank_equal": independent["affine"]["rational_rank"]
        == discovery["wave44_exact_affine_rank"],
        "discovery_nullity_equal": independent["affine"]["affine_nullity"]
        == discovery["wave44_exact_affine_nullity"],
    }
    all_pass &= all(affine_checks.values())
    result = {
        "format": "wave48-exact-face-clean-verification-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED" if all_pass else "REFUTED",
        "scope": "exact Wave44 affine rank/nullity and 11 complete universal moment kernels",
        "independent_reconstruction": {
            "path": INDEPENDENT.relative_to(ROOT).as_posix(),
            "sha256": independent_hash,
            "sealed_before_discovery_comparison": True,
        },
        "discovery_comparison_input": {
            "path": DISCOVERY_FACES.relative_to(ROOT).as_posix(),
            "sha256": EXPECTED[DISCOVERY_FACES],
        },
        "affine_checks": affine_checks,
        "family_comparisons": comparisons,
        "families_passed": sum(item["status"] == "PASS" for item in comparisons),
        "families_total": len(comparisons),
        "discovery_wave48_code_imported_or_executed": False,
        "floating_solver_artifacts_opened": False,
        "conclusion": {
            "exact_facial_reduction_claims": (
                "VERIFIED_SCOPED" if all_pass else "REFUTED"
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "aggregate_feasibility": "UNKNOWN",
        },
        "limitations": [
            "This verification covers exact affine rank and universal kernels only.",
            "No floating solver artifact was opened or used.",
            "Exact facial reduction does not decide feasibility or construct a graph.",
        ],
    }
    payload = canonical_payload(result)
    COMPARISON.write_bytes(payload)
    print(
        f"status={result['claim_label']} families="
        f"{result['families_passed']}/{result['families_total']}"
    )
    print(f"verification_sha256={sha256_bytes(payload)}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("reconstruct", "compare"))
    args = parser.parse_args()
    if args.phase == "reconstruct":
        reconstruct()
    else:
        compare()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
