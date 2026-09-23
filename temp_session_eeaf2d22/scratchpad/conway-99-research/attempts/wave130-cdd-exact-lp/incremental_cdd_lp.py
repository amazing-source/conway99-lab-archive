"""Incremental exact feasibility for the Wave130 affine Jacobi LP.

Solve a small exact subset, replay its rational point against every reduced
inequality, add the most violated rows, and repeat.  A feasible classification
is emitted only after replay against every original equality and inequality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

import cdd.gmp as cdd

import exact_cdd_lp as BASE


def label_cutoff(label: str) -> int | None:
    match = re.search(r":n(\d+)(?=:)", label)
    return int(match.group(1)) if match else None


def solve(
    cutoff: int,
    cache_path: Path,
    solver_name: str,
    initial_cutoff: int,
    batch_size: int,
    max_iterations: int,
    warm_candidate_path: Path | None,
) -> dict[str, object]:
    if BASE.MODEL.free_memory_percent() < 15:
        raise RuntimeError("free memory below 15% before exact solve")
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    print(f"phase=load cutoff={cutoff}", file=sys.stderr, flush=True)
    equalities, inequalities, variables = BASE.load_rows(cutoff, cache_path)
    print(
        f"phase=affine equalities={len(equalities)} "
        f"inequalities={len(inequalities)} variables={variables}",
        file=sys.stderr,
        flush=True,
    )
    affine = BASE.affine_system(equalities, inequalities, variables)
    rows: list[list[Q]] = affine["rows"]
    constants: list[Q] = affine["constants"]
    dimension = len(affine["free"])
    solver_inequalities: list[dict[str, object]] = affine[
        "solver_inequalities"
    ]
    warm_metadata: dict[str, object] | None = None
    if warm_candidate_path is not None:
        warm_payload = json.loads(
            warm_candidate_path.read_text(encoding="utf-8")
        )
        warm = [Q(value) for value in warm_payload.get("solution", [])]
        if len(warm) != variables:
            raise ValueError("warm candidate has wrong solution length")
        failed_warm_equalities = [
            constraint["label"]
            for constraint in equalities
            if sum(
                coefficient * warm[index]
                for index, coefficient in enumerate(constraint["row"])
            )
            != constraint["right"]
        ]
        if failed_warm_equalities:
            raise ValueError(
                "warm candidate fails equalities: "
                + ",".join(failed_warm_equalities[:5])
            )
        affine["particular"] = warm
        constants = [
            sum(
                coefficient * warm[index]
                for index, coefficient in enumerate(constraint["row"])
            )
            for constraint in solver_inequalities
        ]
        warm_metadata = {
            "path": str(warm_candidate_path),
            "tight_reduced_inequalities": sum(
                value == 0 for value in constants
            ),
            "violated_reduced_inequalities": sum(
                value < 0 for value in constants
            ),
        }
    print(
        f"phase=normalize rank={affine['rank']} "
        f"dimension={dimension} reduced_inequalities={len(rows)}",
        file=sys.stderr,
        flush=True,
    )
    normalized_rows: list[list[int]] = []
    max_integer_bits = 0
    for constant, row in zip(constants, rows, strict=True):
        _scale, normalized = BASE.primitive_scale([constant] + row)
        normalized_rows.append(normalized)
        max_integer_bits = max(
            max_integer_bits,
            max((abs(value).bit_length() for value in normalized), default=0),
        )

    working = {
        index
        for index, constraint in enumerate(solver_inequalities)
        if (
            (
                initial_cutoff >= 0
                and (
                    label_cutoff(constraint["label"]) is None
                    or label_cutoff(constraint["label"]) <= initial_cutoff
                )
            )
            or (
                warm_candidate_path is not None
                and constants[index] <= 0
            )
        )
    }
    if not working:
        working.add(0)
    solver = getattr(cdd.LPSolverType, solver_name)
    trace: list[dict[str, object]] = []
    parameters: list[Q] | None = None
    for iteration in range(max_iterations):
        ordered = sorted(working)
        array = [normalized_rows[index] for index in ordered]
        array.append([0] + [0] * dimension)
        print(
            f"phase=cdd iteration={iteration} working={len(ordered)} "
            f"solver={solver_name}",
            file=sys.stderr,
            flush=True,
        )
        lp = cdd.linprog_from_array(array, obj_type=cdd.LPObjType.MIN)
        solve_started = time.perf_counter()
        cdd.linprog_solve(lp, solver)
        solve_seconds = time.perf_counter() - solve_started
        entry: dict[str, object] = {
            "iteration": iteration,
            "working_inequalities": len(ordered),
            "status": lp.status.name,
            "solve_seconds": solve_seconds,
        }
        if lp.status != cdd.LPStatusType.OPTIMAL:
            trace.append(entry)
            return {
                "format": "wave130-cdd-gmp-incremental-v1",
                "classification": "UNKNOWN_CDD_SUBSYSTEM_NONOPTIMAL",
                "cutoff": cutoff,
                "solver": solver_name,
                "cdd_status": lp.status.name,
                "exact_reduction": affine["reduction"],
                "affine_rank": affine["rank"],
                "affine_free_dimension": dimension,
                "reduced_inequalities": len(rows),
                "max_normalized_integer_bits": max_integer_bits,
                "warm_candidate": warm_metadata,
                "trace": trace,
                "total_wall_seconds": time.perf_counter() - started_wall,
                "total_cpu_seconds": time.process_time() - started_cpu,
                "free_memory_percent_after": (
                    BASE.MODEL.free_memory_percent()
                ),
            }
        parameters = [Q(value) for value in lp.primal_solution]
        if len(parameters) != dimension:
            entry["primal_length"] = len(parameters)
            trace.append(entry)
            return {
                "format": "wave130-cdd-gmp-incremental-v1",
                "classification": "UNKNOWN_CDD_BAD_PRIMAL_LENGTH",
                "cutoff": cutoff,
                "trace": trace,
            }
        slacks = [
            constants[row]
            + sum(
                rows[row][column] * parameters[column]
                for column in range(dimension)
            )
            for row in range(len(rows))
        ]
        violated = [
            index
            for index, value in enumerate(slacks)
            if value < 0
        ]
        violated.sort(key=lambda index: slacks[index])
        entry["violated_inequalities"] = len(violated)
        if violated:
            entry["most_negative_label"] = solver_inequalities[
                violated[0]
            ]["label"]
            entry["most_negative_slack"] = BASE.qtext(
                slacks[violated[0]]
            )
        trace.append(entry)
        print(
            f"phase=replay iteration={iteration} "
            f"violated={len(violated)} solve_seconds={solve_seconds:.6f}",
            file=sys.stderr,
            flush=True,
        )
        if not violated:
            break
        additions = [
            index for index in violated if index not in working
        ][:batch_size]
        if not additions:
            return {
                "format": "wave130-cdd-gmp-incremental-v1",
                "classification": "REFUTED_INCREMENTAL_STALL",
                "cutoff": cutoff,
                "trace": trace,
            }
        working.update(additions)
    else:
        return {
            "format": "wave130-cdd-gmp-incremental-v1",
            "classification": "UNKNOWN_ITERATION_LIMIT",
            "cutoff": cutoff,
            "solver": solver_name,
            "trace": trace,
            "working_inequalities": len(working),
            "total_wall_seconds": time.perf_counter() - started_wall,
            "total_cpu_seconds": time.process_time() - started_cpu,
            "free_memory_percent_after": BASE.MODEL.free_memory_percent(),
        }

    assert parameters is not None
    particular: list[Q] = affine["particular"]
    directions: list[list[Q]] = affine["directions"]
    candidate = [
        particular[row]
        + sum(
            directions[row][column] * parameters[column]
            for column in range(dimension)
        )
        for row in range(variables)
    ]
    failed_equalities = [
        constraint["label"]
        for constraint in equalities
        if sum(
            coefficient * candidate[index]
            for index, coefficient in enumerate(constraint["row"])
        )
        != constraint["right"]
    ]
    failed_inequalities = [
        constraint["label"]
        for constraint in inequalities
        if sum(
            coefficient * candidate[index]
            for index, coefficient in enumerate(constraint["row"])
        )
        < 0
    ]
    tight = [
        constraint["label"]
        for constraint in inequalities
        if sum(
            coefficient * candidate[index]
            for index, coefficient in enumerate(constraint["row"])
        )
        == 0
    ]
    classification = (
        "EXACT_RATIONAL_FEASIBLE"
        if not failed_equalities and not failed_inequalities
        else "REFUTED_CDD_PRIMAL_REPLAY"
    )
    return {
        "format": "wave130-cdd-gmp-incremental-v1",
        "classification": classification,
        "cutoff": cutoff,
        "solver": solver_name,
        "variables": variables,
        "equalities": len(equalities),
        "inequalities": len(inequalities),
        "exact_reduction": affine["reduction"],
        "affine_rank": affine["rank"],
        "affine_free_dimension": dimension,
        "reduced_inequalities": len(rows),
        "final_working_inequalities": len(working),
        "max_normalized_integer_bits": max_integer_bits,
        "warm_candidate": warm_metadata,
        "trace": trace,
        "failed_equalities": failed_equalities,
        "failed_inequalities": failed_inequalities,
        "tight_inequalities": tight,
        "affine_parameters": [BASE.qtext(value) for value in parameters],
        "solution": [BASE.qtext(value) for value in candidate],
        "total_wall_seconds": time.perf_counter() - started_wall,
        "total_cpu_seconds": time.process_time() - started_cpu,
        "free_memory_percent_after": BASE.MODEL.free_memory_percent(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=int, required=True)
    parser.add_argument("--columns-cache", type=Path, required=True)
    parser.add_argument(
        "--solver",
        choices=("DUAL_SIMPLEX", "CRISS_CROSS"),
        default="DUAL_SIMPLEX",
    )
    parser.add_argument("--initial-cutoff", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--max-iterations", type=int, default=32)
    parser.add_argument("--warm-candidate", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = solve(
        args.cutoff,
        args.columns_cache,
        args.solver,
        args.initial_cutoff,
        args.batch_size,
        args.max_iterations,
        args.warm_candidate,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0 if result["classification"] == "EXACT_RATIONAL_FEASIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
