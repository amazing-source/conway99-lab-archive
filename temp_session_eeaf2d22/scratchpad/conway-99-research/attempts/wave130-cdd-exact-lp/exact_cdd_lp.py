"""Solve the Wave127 Jacobi relaxation with cddlib GMP rationals.

The equality system is eliminated exactly first.  In the resulting affine
coordinates, cddlib solves the margin LP

    maximize s
    subject to b_i + a_i*t - s >= 0.

If s >= 0, the returned rational t gives a feasible point.  If s < 0, the
exact dual multipliers give a Farkas contradiction.  Every terminal result is
replayed against the original, unreduced rational rows before publication.
"""

from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import math
import pickle
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

import cdd.gmp as cdd
from flint import fmpq, fmpq_mat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE127 = ROOT / "attempts" / "wave127-independent-jacobi-certificate"
SPEC = importlib.util.spec_from_file_location(
    "wave127_jacobi_lp", WAVE127 / "jacobi_lp.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)


def fq(value: Q) -> fmpq:
    return fmpq(value.numerator, value.denominator)


def qtext(value: Q) -> str:
    return MODEL.qtext(value)


def process_memory_bytes() -> tuple[int, int]:
    """Return current and peak working set on Windows, or zeroes elsewhere."""

    if sys.platform != "win32":
        return 0, 0

    class MemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        handle, ctypes.byref(counters), counters.cb
    )
    if not ok:
        return 0, 0
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def load_rows(
    cutoff: int, cache_path: Path
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    int,
]:
    qmax = max(cutoff, 10)
    with cache_path.open("rb") as stream:
        cached = pickle.load(stream)
    if (
        cached.get("version") != MODEL.MODEL_CACHE_VERSION
        or cached.get("qmax", -1) < qmax
    ):
        raise ValueError("incompatible columns cache")
    columns = cached["columns"]
    equalities, inequalities = MODEL.build_constraints(columns, cutoff)
    return equalities, inequalities, len(columns)


def affine_system(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
) -> dict[str, object]:
    solver_equalities, solver_inequalities, reduction = (
        MODEL.reduced_constraints_for_solver(equalities, inequalities)
    )
    augmented = fmpq_mat(
        len(solver_equalities),
        variables + 1,
        [
            fq(value)
            for constraint in solver_equalities
            for value in constraint["row"] + [constraint["right"]]
        ],
    )
    echelon, rank = augmented.rref()
    pivots: list[int] = []
    for row in range(rank):
        pivot = next(
            column
            for column in range(variables + 1)
            if echelon[row, column]
        )
        if pivot == variables:
            raise ValueError("exact equality system is inconsistent")
        pivots.append(pivot)
    free = [column for column in range(variables) if column not in pivots]
    particular = [Q(0)] * variables
    directions = [[Q(0)] * len(free) for _ in range(variables)]
    for index, free_column in enumerate(free):
        directions[free_column][index] = Q(1)
    for row, pivot in enumerate(pivots):
        particular[pivot] = Q(
            int(echelon[row, variables].numerator),
            int(echelon[row, variables].denominator),
        )
        for index, free_column in enumerate(free):
            directions[pivot][index] = -Q(
                int(echelon[row, free_column].numerator),
                int(echelon[row, free_column].denominator),
            )

    constants: list[Q] = []
    rows: list[list[Q]] = []
    for constraint in solver_inequalities:
        constants.append(
            sum(
                coefficient * particular[index]
                for index, coefficient in enumerate(constraint["row"])
            )
        )
        rows.append(
            [
                sum(
                    constraint["row"][index]
                    * directions[index][column]
                    for index in range(variables)
                )
                for column in range(len(free))
            ]
        )
    return {
        "solver_equalities": solver_equalities,
        "solver_inequalities": solver_inequalities,
        "reduction": reduction,
        "rank": rank,
        "free": free,
        "particular": particular,
        "directions": directions,
        "constants": constants,
        "rows": rows,
    }


def primitive_scale(values: list[Q]) -> tuple[Q, list[int]]:
    """Scale a rational row by a positive rational to primitive integers."""

    denominator_lcm = 1
    for value in values:
        denominator_lcm = math.lcm(denominator_lcm, value.denominator)
    integers = [
        value.numerator * (denominator_lcm // value.denominator)
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if divisor == 0:
        return Q(1), integers
    return (
        Q(denominator_lcm, divisor),
        [value // divisor for value in integers],
    )


def equality_combination(
    equalities: list[dict[str, object]], vector: list[Q]
) -> list[Q]:
    """Find unique mu with sum(mu_i E_i) == vector."""

    equation_count = len(equalities)
    variables = len(vector)
    augmented = fmpq_mat(
        variables,
        equation_count + 1,
        [
            fq(value)
            for column in range(variables)
            for value in (
                [
                    equalities[row]["row"][column]
                    for row in range(equation_count)
                ]
                + [vector[column]]
            )
        ],
    )
    echelon, rank = augmented.rref()
    multipliers = [Q(0)] * equation_count
    pivots: set[int] = set()
    for row in range(rank):
        pivot = next(
            column
            for column in range(equation_count + 1)
            if echelon[row, column]
        )
        if pivot == equation_count:
            raise ValueError("inequality combination is outside equality span")
        pivots.add(pivot)
        multipliers[pivot] = Q(
            int(echelon[row, equation_count].numerator),
            int(echelon[row, equation_count].denominator),
        )
    if len(pivots) != equation_count:
        raise ValueError("equality multipliers are not unique")
    reconstructed = [
        sum(
            multipliers[row] * equalities[row]["row"][column]
            for row in range(equation_count)
        )
        for column in range(variables)
    ]
    if reconstructed != vector:
        raise ValueError("equality multiplier replay failed")
    return multipliers


def solve(
    cutoff: int,
    cache_path: Path,
    solver_name: str,
    mode: str,
) -> dict[str, object]:
    if MODEL.free_memory_percent() < 15:
        raise RuntimeError("free memory below 15% before exact solve")
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    print(f"phase=load cutoff={cutoff}", file=sys.stderr, flush=True)
    equalities, inequalities, variables = load_rows(cutoff, cache_path)
    print(
        f"phase=affine equalities={len(equalities)} "
        f"inequalities={len(inequalities)} variables={variables}",
        file=sys.stderr,
        flush=True,
    )
    affine = affine_system(equalities, inequalities, variables)
    rows: list[list[Q]] = affine["rows"]
    constants: list[Q] = affine["constants"]
    dimension = len(affine["free"])
    print(
        f"phase=normalize rank={affine['rank']} "
        f"dimension={dimension} reduced_inequalities={len(rows)}",
        file=sys.stderr,
        flush=True,
    )

    normalized_rows: list[list[int]] = []
    row_scales: list[Q] = []
    max_integer_bits = 0
    for constant, row in zip(constants, rows, strict=True):
        scale, normalized = primitive_scale([constant] + row)
        row_scales.append(scale)
        normalized_rows.append(normalized)
        max_integer_bits = max(
            max_integer_bits,
            max((abs(value).bit_length() for value in normalized), default=0),
        )

    if mode == "margin":
        # The final variable is the common scaled margin s.
        array = [normalized + [-1] for normalized in normalized_rows]
        array.append([0] + [0] * dimension + [1])
        objective_type = cdd.LPObjType.MAX
    else:
        array = normalized_rows + [[0] + [0] * dimension]
        objective_type = cdd.LPObjType.MIN
    lp = cdd.linprog_from_array(array, obj_type=objective_type)
    solver = getattr(cdd.LPSolverType, solver_name)
    print(
        f"phase=cdd solver={solver_name} mode={mode} "
        f"max_integer_bits={max_integer_bits}",
        file=sys.stderr,
        flush=True,
    )
    solve_started = time.perf_counter()
    cdd.linprog_solve(lp, solver)
    solve_seconds = time.perf_counter() - solve_started
    print(
        f"phase=replay status={lp.status.name} "
        f"solve_seconds={solve_seconds:.6f}",
        file=sys.stderr,
        flush=True,
    )
    current_memory, peak_memory = process_memory_bytes()
    common = {
        "format": "wave130-cdd-gmp-exact-lp-v1",
        "cutoff": cutoff,
        "solver": solver_name,
        "mode": mode,
        "cdd_status": lp.status.name,
        "exact_reduction": affine["reduction"],
        "affine_rank": affine["rank"],
        "affine_free_dimension": dimension,
        "reduced_inequalities": len(rows),
        "max_normalized_integer_bits": max_integer_bits,
        "solve_seconds": solve_seconds,
        "total_wall_seconds": time.perf_counter() - started_wall,
        "total_cpu_seconds": time.process_time() - started_cpu,
        "working_set_bytes": current_memory,
        "peak_working_set_bytes": peak_memory,
        "free_memory_percent_after": MODEL.free_memory_percent(),
    }
    if lp.status != cdd.LPStatusType.OPTIMAL:
        return {
            **common,
            "classification": "UNKNOWN_CDD_NONOPTIMAL",
        }

    primal = [Q(value) for value in lp.primal_solution]
    expected_primal_length = dimension + (1 if mode == "margin" else 0)
    if len(primal) != expected_primal_length:
        return {
            **common,
            "classification": "UNKNOWN_CDD_BAD_PRIMAL_LENGTH",
            "primal_length": len(primal),
        }
    if mode == "margin":
        parameters = primal[:-1]
        margin = primal[-1]
        common["exact_margin"] = qtext(margin)
    else:
        parameters = primal
        margin = Q(0)

    if mode == "feasibility" or margin >= 0:
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
            **common,
            "classification": classification,
            "variables": variables,
            "equalities": len(equalities),
            "inequalities": len(inequalities),
            "failed_equalities": failed_equalities,
            "failed_inequalities": failed_inequalities,
            "tight_inequalities": tight,
            "affine_parameters": [qtext(value) for value in parameters],
            "solution": [qtext(value) for value in candidate],
        }

    scaled_dual = [Q(0)] * len(rows)
    for index, value in lp.dual_solution:
        scaled_dual[index] = Q(value)
    stationarity = [
        sum(
            scaled_dual[row] * normalized_rows[row][column + 1]
            for row in range(len(rows))
        )
        for column in range(dimension)
    ]
    dual_sum = sum(scaled_dual)
    dual_objective = sum(
        scaled_dual[row] * normalized_rows[row][0]
        for row in range(len(rows))
    )
    scaled_dual_verified = (
        all(value >= 0 for value in scaled_dual)
        and dual_sum == 1
        and not any(stationarity)
        and dual_objective == margin
        and margin < 0
    )
    original_dual = [
        scaled_dual[index] * row_scales[index]
        for index in range(len(rows))
    ]
    original_stationarity = [
        sum(
            original_dual[row] * rows[row][column]
            for row in range(len(rows))
        )
        for column in range(dimension)
    ]
    original_objective = sum(
        original_dual[row] * constants[row]
        for row in range(len(rows))
    )
    solver_equalities: list[dict[str, object]] = affine[
        "solver_equalities"
    ]
    solver_inequalities: list[dict[str, object]] = affine[
        "solver_inequalities"
    ]
    original_vector = [
        sum(
            original_dual[row]
            * solver_inequalities[row]["row"][column]
            for row in range(len(rows))
        )
        for column in range(variables)
    ]
    equality_multipliers = equality_combination(
        solver_equalities, original_vector
    )
    equality_constant = sum(
        equality_multipliers[row]
        * solver_equalities[row]["right"]
        for row in range(len(solver_equalities))
    )
    farkas_verified = (
        scaled_dual_verified
        and all(value >= 0 for value in original_dual)
        and not any(original_stationarity)
        and original_objective == margin
        and equality_constant == margin
        and margin < 0
    )
    return {
        **common,
        "classification": (
            "EXACT_FARKAS_VERIFIED"
            if farkas_verified
            else "REFUTED_CDD_DUAL_REPLAY"
        ),
        "variables": variables,
        "equalities": len(equalities),
        "inequalities": len(inequalities),
        "dual_sum": qtext(dual_sum),
        "dual_objective": qtext(dual_objective),
        "scaled_dual_verified": scaled_dual_verified,
        "farkas_identity_constant": qtext(equality_constant),
        "inequality_multipliers": [
            {
                "label": solver_inequalities[index]["label"],
                "multiplier": qtext(value),
            }
            for index, value in enumerate(original_dual)
            if value
        ],
        "equality_multipliers": [
            {
                "label": solver_equalities[index]["label"],
                "multiplier": qtext(value),
            }
            for index, value in enumerate(equality_multipliers)
            if value
        ],
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
    parser.add_argument(
        "--mode",
        choices=("feasibility", "margin"),
        default="feasibility",
    )
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = solve(
        args.cutoff, args.columns_cache, args.solver, args.mode
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0 if result["classification"] in {
        "EXACT_RATIONAL_FEASIBLE",
        "EXACT_FARKAS_VERIFIED",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
