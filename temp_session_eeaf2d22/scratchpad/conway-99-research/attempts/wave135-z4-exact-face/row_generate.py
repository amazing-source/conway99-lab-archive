"""Bounded exact row generation on the shifted Wave135 affine face.

The forced primal lower bounds are translated out first: ``x = lower + z``.
Consequently every primal inequality is simply ``z_i >= 0``.  Only an exact
independent basis of the forbidden equalities is sent to RREF, while terminal
replay checks every omitted equality and all allowed dual inequalities.
"""

from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import math
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

import cdd.gmp as cdd
from flint import fmpq, fmpq_mat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE134 = ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
SPEC = importlib.util.spec_from_file_location(
    "wave134_exact_check", WAVE134 / "exact_check.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)
DEFAULT_OUTPUT = HERE / "row-generation.json"
ORBIT_TOTAL = 1 << 108
TORSION_SHELL_TOTAL = 1 << 54
PRIME = 2_147_483_647


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page", ctypes.c_ulonglong),
        ("avail_page", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


class ProcessMemory(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("page_fault_count", ctypes.c_ulong),
        ("peak_working_set_size", ctypes.c_size_t),
        ("working_set_size", ctypes.c_size_t),
        ("quota_peak_paged_pool_usage", ctypes.c_size_t),
        ("quota_paged_pool_usage", ctypes.c_size_t),
        ("quota_peak_nonpaged_pool_usage", ctypes.c_size_t),
        ("quota_nonpaged_pool_usage", ctypes.c_size_t),
        ("pagefile_usage", ctypes.c_size_t),
        ("peak_pagefile_usage", ctypes.c_size_t),
    ]


def memory_snapshot() -> tuple[float, int, int]:
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return (
        100.0 * status.avail_phys / status.total_phys,
        0,
        0,
    )


def fq(value: Q | int) -> fmpq:
    value = Q(value)
    return fmpq(value.numerator, value.denominator)


def to_q(value) -> Q:
    return Q(int(value.numerator), int(value.denominator))


def primitive(values: list[Q]) -> list[int]:
    denominator = 1
    for value in values:
        denominator = math.lcm(denominator, value.denominator)
    integers = [
        value.numerator * (denominator // value.denominator)
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if divisor:
        integers = [value // divisor for value in integers]
    return integers


def independent_row_indices(
    rows: list[list[int]], prime: int = PRIME
) -> list[int]:
    basis: dict[int, list[int]] = {}
    selected = []
    for index, original in enumerate(rows):
        row = [value % prime for value in original]
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                row = [
                    (left - factor * right) % prime
                    for left, right in zip(row, basis[pivot])
                ]
        pivot = next((column for column, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        inverse = pow(row[pivot], prime - 2, prime)
        basis[pivot] = [value * inverse % prime for value in row]
        selected.append(index)
    return selected


def affine_face():
    sources = MODEL.primal_states()
    primal_lower = MODEL.forced_primal()
    shift = [primal_lower.get(state, 0) for state in sources]
    zero_rows = [
        [
            MODEL.transform_coefficient(source, target)
            for source in sources
        ]
        for target in MODEL.forbidden_dual_states()
    ]
    independent = independent_row_indices(zero_rows)
    if len(independent) != 143:
        raise AssertionError("unexpected forbidden-row basis size")
    rows = [zero_rows[index] for index in independent]
    right = [
        -sum(value * lower for value, lower in zip(row, shift))
        for row in rows
    ]
    rows.append([1] * len(sources))
    right.append(ORBIT_TOTAL - sum(shift))
    unit = [0] * len(sources)
    zero_index = sources.index((99, 0, 0))
    unit[zero_index] = 1
    rows.append(unit)
    right.append(1 - shift[zero_index])
    torsion_shell = [
        1 if state[1] == 0 else 0 for state in sources
    ]
    rows.append(torsion_shell)
    right.append(
        TORSION_SHELL_TOTAL
        - sum(
            lower
            for state, lower in zip(sources, shift)
            if state[1] == 0
        )
    )
    augmented = fmpq_mat(
        len(rows),
        len(sources) + 1,
        [
            value
            for row, rhs in zip(rows, right)
            for value in row + [rhs]
        ],
    )
    echelon, rank = augmented.rref()
    if rank != 146:
        raise AssertionError("unexpected affine rank")
    pivots = []
    for row in range(rank):
        pivot = next(
            column
            for column in range(len(sources) + 1)
            if echelon[row, column]
        )
        if pivot == len(sources):
            raise AssertionError("inconsistent affine face")
        pivots.append(pivot)
    pivot_set = set(pivots)
    free = [
        column for column in range(len(sources)) if column not in pivot_set
    ]
    block = fmpq_mat(
        rank,
        len(free),
        [echelon[row, column] for row in range(rank) for column in free],
    )
    rhs = [echelon[row, len(sources)] for row in range(rank)]
    return (
        sources,
        shift,
        zero_rows,
        independent,
        pivots,
        free,
        block,
        rhs,
    )


def constraint_catalog(sources):
    primal_lower = MODEL.forced_primal()
    dual_lower = MODEL.forced_dual()
    catalog = []
    for index, state in enumerate(sources):
        catalog.append(
            {
                "label": "P:" + ",".join(map(str, state)),
                "kind": "primal",
                "index": index,
                "state": state,
                "lower": primal_lower.get(state, 0),
            }
        )
    for state in MODEL.dual_states():
        catalog.append(
            {
                "label": "D:" + ",".join(map(str, state)),
                "kind": "dual",
                "state": state,
                "lower": dual_lower.get(state, 0) * ORBIT_TOTAL,
            }
        )
    return catalog


def raw_constraint(constraint, sources, shift):
    if constraint["kind"] == "primal":
        row = [0] * len(sources)
        row[constraint["index"]] = 1
        return row, Q(constraint["lower"]) - shift[constraint["index"]]
    row = [
        MODEL.transform_coefficient(source, constraint["state"])
        for source in sources
    ]
    shifted_lower = Q(constraint["lower"]) - sum(
        Q(value) * lower for value, lower in zip(row, shift)
    )
    return row, shifted_lower


def reduce_constraint(
    constraint,
    sources,
    shift,
    pivots,
    free,
    block,
    rhs,
):
    raw, lower = raw_constraint(constraint, sources, shift)
    pivot_values = [raw[column] for column in pivots]
    pivot_row = fmpq_mat(1, len(pivots), pivot_values)
    correction = pivot_row * block
    coefficients = [
        Q(raw[column]) - to_q(correction[0, index])
        for index, column in enumerate(free)
    ]
    constant = -Q(lower) + sum(
        Q(value) * to_q(rhs[index])
        for index, value in enumerate(pivot_values)
    )
    return primitive([constant] + coefficients)


def reconstruct(parameters, sources, shift, pivots, free, block, rhs):
    parameter_column = fmpq_mat(
        len(parameters), 1, [fq(value) for value in parameters]
    )
    correction = block * parameter_column
    translated = [Q(0)] * len(sources)
    for index, column in enumerate(free):
        translated[column] = parameters[index]
    for index, column in enumerate(pivots):
        translated[column] = to_q(rhs[index] - correction[index, 0])
    return [
        lower + value for lower, value in zip(shift, translated)
    ]


def replay(candidate, catalog, sources):
    nonzero = [
        (index, value)
        for index, value in enumerate(candidate)
        if value
    ]
    violations = []
    for index, constraint in enumerate(catalog):
        if constraint["kind"] == "primal":
            slack = (
                candidate[constraint["index"]] - constraint["lower"]
            )
        else:
            value = sum(
                MODEL.transform_coefficient(
                    sources[source_index], constraint["state"]
                )
                * coefficient
                for source_index, coefficient in nonzero
            )
            slack = value - constraint["lower"]
        if slack < 0:
            violations.append((slack, index))
    violations.sort(key=lambda item: (item[0], item[1]))
    return violations


def replay_equalities(candidate, sources, zero_rows):
    failures = []
    for index, row in enumerate(zero_rows):
        value = sum(
            Q(coefficient) * candidate[column]
            for column, coefficient in enumerate(row)
            if coefficient
        )
        if value:
            failures.append((index, value))
    normalization = sum(candidate)
    if normalization != ORBIT_TOTAL:
        failures.append(("normalization", normalization - ORBIT_TOTAL))
    zero_value = candidate[sources.index((99, 0, 0))]
    if zero_value != 1:
        failures.append(("A0", zero_value - 1))
    torsion_shell_total = sum(
        value
        for state, value in zip(sources, candidate)
        if state[1] == 0
    )
    if torsion_shell_total != TORSION_SHELL_TOTAL:
        failures.append(
            (
                "torsion_shell",
                torsion_shell_total - TORSION_SHELL_TOTAL,
            )
        )
    return failures


def encode(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def solve(wall_seconds: float, batch_size: int):
    started = time.monotonic()
    free_percent, _, _ = memory_snapshot()
    if free_percent < 15:
        raise RuntimeError("free physical memory below 15%")
    (
        sources,
        shift,
        zero_rows,
        independent,
        pivots,
        free,
        block,
        rhs,
    ) = affine_face()
    catalog = constraint_catalog(sources)
    working = {
        index
        for index, constraint in enumerate(catalog)
        if (
            constraint["kind"] == "dual"
            and constraint["state"] in MODEL.forced_dual()
        )
    }
    reduced = {}
    trace = []
    parameters = [Q(0)] * len(free)
    for iteration in range(20):
        remaining = wall_seconds - (time.monotonic() - started)
        free_percent, current, peak = memory_snapshot()
        if remaining <= 1:
            return {
                "classification": "UNKNOWN_WALL",
                "trace": trace,
            }
        if free_percent < 15:
            return {
                "classification": "UNKNOWN_MEMORY_GUARD",
                "trace": trace,
            }
        if iteration:
            ordered = sorted(working)
            for index in ordered:
                if index not in reduced:
                    reduced[index] = reduce_constraint(
                        catalog[index],
                        sources,
                        shift,
                        pivots,
                        free,
                        block,
                        rhs,
                    )
            array = [reduced[index] for index in ordered]
            array.append([0] + [0] * len(free))
            print(
                f"phase=cdd iteration={iteration} working={len(ordered)} "
                f"remaining={remaining:.1f}",
                flush=True,
            )
            lp = cdd.linprog_from_array(
                array, obj_type=cdd.LPObjType.MIN
            )
            cdd.linprog_solve(lp, cdd.LPSolverType.DUAL_SIMPLEX)
            if lp.status != cdd.LPStatusType.OPTIMAL:
                return {
                    "classification": "UNKNOWN_CDD_" + lp.status.name,
                    "trace": trace,
                }
            parameters = [Q(value) for value in lp.primal_solution]
            if len(parameters) != len(free):
                return {
                    "classification": "UNKNOWN_BAD_PRIMAL",
                    "trace": trace,
                }
        candidate = reconstruct(
            parameters, sources, shift, pivots, free, block, rhs
        )
        violations = replay(candidate, catalog, sources)
        trace.append(
            {
                "iteration": iteration,
                "working_rows": len(working),
                "violated_rows": len(violations),
                "most_negative": (
                    encode(violations[0][0]) if violations else None
                ),
                "working_set_bytes": current,
                "peak_working_set_bytes": peak,
            }
        )
        print(
            f"phase=replay iteration={iteration} "
            f"violated={len(violations)}",
            flush=True,
        )
        if not violations:
            equality_failures = replay_equalities(
                candidate, sources, zero_rows
            )
            if equality_failures:
                return {
                    "classification": "UNKNOWN_EQUALITY_REPLAY_FAILURE",
                    "trace": trace,
                    "failures": [
                        [str(label), encode(value)]
                        for label, value in equality_failures
                    ],
                }
            return {
                "format": "wave135-z4-exact-row-generation-v2",
                "classification": "EXACT_RATIONAL_FEASIBLE",
                "claim_label": "CANDIDATE",
                "translation": "x = forced_primal_lower + z",
                "forbidden_basis_rows": independent,
                "forbidden_equalities_replayed": len(zero_rows),
                "torsion_shell_equality": (
                    "sum_{primal states with b=0} x = 2^54"
                ),
                "affine_rank": len(pivots),
                "affine_dimension": len(free),
                "all_inequalities_replayed": len(catalog),
                "trace": trace,
                "primal_orbits": {
                    ",".join(map(str, state)): encode(value)
                    for state, value in zip(sources, candidate)
                    if value
                },
                "limitations": [
                    "Formal rational enumerator only.",
                    "No Z4 code, graph, or adjacency matrix is constructed.",
                ],
            }
        additions = [
            index for _, index in violations if index not in working
        ][:batch_size]
        if not additions:
            return {
                "classification": "UNKNOWN_ROW_GENERATION_STALL",
                "trace": trace,
            }
        working.update(additions)
    return {
        "classification": "UNKNOWN_ITERATION_LIMIT",
        "trace": trace,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wall-seconds", type=float, default=180)
    parser.add_argument("--batch-size", type=int, default=24)
    args = parser.parse_args()
    payload = solve(args.wall_seconds, args.batch_size)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["classification"])


if __name__ == "__main__":
    main()
