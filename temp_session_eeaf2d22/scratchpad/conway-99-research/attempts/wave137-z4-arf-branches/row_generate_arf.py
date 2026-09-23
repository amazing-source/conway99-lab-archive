"""Exact cutting planes on one torsion-tightened Arf/Gauss branch."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from fractions import Fraction as Q
from pathlib import Path

import cdd.gmp as cdd
from flint import fmpq_mat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE135 = ROOT / "attempts" / "wave135-z4-exact-face"
SPEC = importlib.util.spec_from_file_location(
    "wave135_row_generate", WAVE135 / "row_generate.py"
)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)
MODEL = BASE.MODEL
ORBIT_TOTAL = 1 << 108
TORSION_SHELL_TOTAL = 1 << 54
ARF_ORBIT_TOTAL = 1 << 81
DUAL_GAUSS_ORBIT_TOTAL = 1 << 66


def arf_coefficients(states):
    return [
        1 if (state[1] // 2) % 2 == 0 else -1
        for state in states
    ]


def affine_face(sign: int):
    sources = MODEL.primal_states()
    shift = [
        MODEL.forced_primal().get(state, 0) for state in sources
    ]
    zero_rows = [
        [
            MODEL.transform_coefficient(source, target)
            for source in sources
        ]
        for target in MODEL.forbidden_dual_states()
    ]
    independent = BASE.independent_row_indices(zero_rows)
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
    arf = arf_coefficients(sources)
    rows.append(arf)
    right.append(
        sign * ARF_ORBIT_TOTAL
        - sum(value * lower for value, lower in zip(arf, shift))
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
    if rank != 147:
        raise AssertionError("unexpected Arf affine rank")
    pivots = []
    for row in range(rank):
        pivot = next(
            column
            for column in range(len(sources) + 1)
            if echelon[row, column]
        )
        if pivot == len(sources):
            raise AssertionError("inconsistent Arf affine face")
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


def exact_gauss_replay(candidate, sources, zero_rows, sign: int):
    failures = BASE.replay_equalities(candidate, sources, zero_rows)
    arf = sum(
        coefficient * value
        for coefficient, value in zip(
            arf_coefficients(sources), candidate
        )
    )
    if arf != sign * ARF_ORBIT_TOTAL:
        failures.append(
            ("primal_arf_gauss", arf - sign * ARF_ORBIT_TOTAL)
        )

    nonzero = [
        (index, value)
        for index, value in enumerate(candidate)
        if value
    ]
    dual_gauss = Q(0)
    for target in MODEL.dual_states():
        numerator = sum(
            MODEL.transform_coefficient(sources[index], target) * value
            for index, value in nonzero
        )
        dual_coefficient = numerator / ORBIT_TOTAL
        weight = 1 if (target[1] // 2) % 2 == 0 else -1
        dual_gauss += weight * dual_coefficient
    expected = -sign * DUAL_GAUSS_ORBIT_TOTAL
    if dual_gauss != expected:
        failures.append(("dual_gauss", dual_gauss - expected))
    return failures


def encode(value: Q) -> str:
    value = Q(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def solve(sign: int, wall_seconds: float, batch_size: int):
    started = time.monotonic()
    free_percent, _, _ = BASE.memory_snapshot()
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
    ) = affine_face(sign)
    catalog = BASE.constraint_catalog(sources)
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
        free_percent, current, peak = BASE.memory_snapshot()
        if remaining <= 1:
            return {
                "format": "wave137-z4-arf-row-generation-v1",
                "claim_label": "UNKNOWN",
                "sign": sign,
                "classification": "UNKNOWN_WALL",
                "trace": trace,
            }
        if free_percent < 15:
            return {
                "format": "wave137-z4-arf-row-generation-v1",
                "claim_label": "UNKNOWN",
                "sign": sign,
                "classification": "UNKNOWN_MEMORY_GUARD",
                "trace": trace,
            }
        if iteration:
            ordered = sorted(working)
            for index in ordered:
                if index not in reduced:
                    reduced[index] = BASE.reduce_constraint(
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
                f"phase=cdd sign={sign} iteration={iteration} "
                f"working={len(ordered)} remaining={remaining:.1f}",
                flush=True,
            )
            lp = cdd.linprog_from_array(
                array, obj_type=cdd.LPObjType.MIN
            )
            cdd.linprog_solve(lp, cdd.LPSolverType.DUAL_SIMPLEX)
            if lp.status != cdd.LPStatusType.OPTIMAL:
                return {
                    "format": "wave137-z4-arf-row-generation-v1",
                    "claim_label": "UNKNOWN",
                    "sign": sign,
                    "classification": "UNKNOWN_CDD_" + lp.status.name,
                    "trace": trace,
                }
            parameters = [Q(value) for value in lp.primal_solution]
            if len(parameters) != len(free):
                return {
                    "format": "wave137-z4-arf-row-generation-v1",
                    "claim_label": "UNKNOWN",
                    "sign": sign,
                    "classification": "UNKNOWN_BAD_PRIMAL",
                    "trace": trace,
                }
        candidate = BASE.reconstruct(
            parameters, sources, shift, pivots, free, block, rhs
        )
        violations = BASE.replay(candidate, catalog, sources)
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
            f"phase=replay sign={sign} iteration={iteration} "
            f"violated={len(violations)}",
            flush=True,
        )
        if not violations:
            equality_failures = exact_gauss_replay(
                candidate, sources, zero_rows, sign
            )
            if equality_failures:
                return {
                    "format": "wave137-z4-arf-row-generation-v1",
                    "claim_label": "UNKNOWN",
                    "sign": sign,
                    "classification": "UNKNOWN_EQUALITY_REPLAY_FAILURE",
                    "trace": trace,
                    "failures": [
                        [str(label), encode(value)]
                        for label, value in equality_failures
                    ],
                }
            return {
                "format": "wave137-z4-arf-row-generation-v1",
                "classification": "EXACT_RATIONAL_FEASIBLE",
                "claim_label": "CANDIDATE",
                "sign": sign,
                "affine_rank": len(pivots),
                "affine_dimension": len(free),
                "all_inequalities_replayed": len(catalog),
                "forbidden_equalities_replayed": len(zero_rows),
                "dual_gauss_replayed": (
                    f"G_E={-sign}*2^22, orbit-scaled by 2^44"
                ),
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
                "format": "wave137-z4-arf-row-generation-v1",
                "claim_label": "UNKNOWN",
                "sign": sign,
                "classification": "UNKNOWN_ROW_GENERATION_STALL",
                "trace": trace,
            }
        working.update(additions)
    return {
        "format": "wave137-z4-arf-row-generation-v1",
        "claim_label": "UNKNOWN",
        "sign": sign,
        "classification": "UNKNOWN_ITERATION_LIMIT",
        "trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign", type=int, choices=(-1, 1), required=True)
    parser.add_argument("--wall-seconds", type=float, default=180)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or (
        HERE
        / (
            "exact-branch-plus.json"
            if args.sign > 0
            else "exact-branch-minus.json"
        )
    )
    payload = solve(args.sign, args.wall_seconds, args.batch_size)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["classification"])


if __name__ == "__main__":
    main()
