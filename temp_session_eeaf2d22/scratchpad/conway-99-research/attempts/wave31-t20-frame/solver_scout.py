#!/usr/bin/env python3
"""Optional bounded solver scouts for the Wave 31 T20 frame problem.

These runs are discovery aids only.  A solver timeout/UNKNOWN result is not a
certificate.  Any returned row set must be checked by ``exact_check.py`` and
then independently verified before it can support a public claim.

Optional engines:

* ``highs`` needs highspy 1.15.1;
* ``cpsat`` and ``cpsat-xor`` need OR-Tools 9.15.6755;
* ``cpsat-oriented`` adds zero-sum signs and the complete |inner product|=2
  orientation graph;
* ``scip`` needs PySCIPOpt 6.2.1 with SCIP 10.0.2;
* ``lp`` is the continuous HiGHS box relaxation.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from typing import Any

import exact_check as exact


def problem() -> tuple[
    list[tuple[int, ...]],
    list[tuple[int, ...]],
    tuple[int, ...],
    list[list[int]],
]:
    exact.validate_inputs()
    enumerator = exact.load_module(
        "wave31_solver_scout_enumerator", exact.ENUMERATOR_PATH
    )
    construction = json.loads(
        exact.CONSTRUCTION_PATH.read_text(encoding="utf-8")
    )
    t20_data = construction["rank20_construction"]["T20"]
    t20 = [[int(value) for value in row] for row in t20_data["gram"]]
    vectors_with_norm, _stats = enumerator.enumerate_vectors(
        [[Fraction(value) for value in row] for row in t20], 4
    )
    lines = [
        tuple(int(value) for value in vector)
        for vector, norm in vectors_with_norm
        if int(norm) == 4 and next(value for value in vector if value) > 0
    ]
    pairs = exact.upper_pairs(20)
    features = [exact.outer_feature(line, pairs) for line in lines]
    target_matrix = [
        [int(value) for value in row]
        for row in t20_data["scaled_dual_21_T20_inverse"]
    ]
    target = tuple(target_matrix[i][j] for i, j in pairs)
    return lines, features, target, t20


def selected_indices(values: Any) -> list[int]:
    return [
        index for index, value in enumerate(values) if float(value) > 0.5
    ]


def run_highs(
    features: list[tuple[int, ...]],
    target: tuple[int, ...],
    seconds: float,
    workers: int,
    seed: int,
    continuous: bool,
    verbose: bool,
) -> dict[str, Any]:
    import highspy  # type: ignore

    model = highspy.Highs()
    model.setOptionValue("output_flag", verbose)
    model.setOptionValue("time_limit", seconds)
    model.setOptionValue("threads", workers)
    model.setOptionValue("random_seed", seed)
    variable_type = (
        highspy.HighsVarType.kContinuous
        if continuous
        else highspy.HighsVarType.kInteger
    )
    variables = model.addVariables(
        len(features), lb=0, ub=1, type=variable_type
    )
    for equation, rhs in enumerate(target):
        model.addConstr(
            model.qsum([
                int(feature[equation]) * variables[index]
                for index, feature in enumerate(features)
                if int(feature[equation])
            ]) == int(rhs)
        )
    model.addConstr(model.qsum(variables) == 105)
    model.run()
    values = model.val(variables)
    chosen = selected_indices(values)
    return {
        "engine": "HiGHS",
        "version": model.version(),
        "continuous": continuous,
        "status": model.modelStatusToString(model.getModelStatus()),
        "time_limit_seconds": seconds,
        "workers": workers,
        "seed": seed,
        "selected_above_half": chosen,
        "selected_above_half_count": len(chosen),
        "positive_count": sum(float(value) > 1e-9 for value in values),
        "fractional_count": sum(
            1e-9 < float(value) < 1 - 1e-9 for value in values
        ),
    }


def add_second_moments_cpsat(
    model: Any,
    variables: list[Any],
    features: list[tuple[int, ...]],
    target: tuple[int, ...],
    add_xors: bool,
) -> None:
    constant_one = model.new_constant(1)
    for equation, rhs in enumerate(target):
        nonzero = [
            index
            for index, feature in enumerate(features)
            if int(feature[equation])
        ]
        model.add(
            sum(
                int(features[index][equation]) * variables[index]
                for index in nonzero
            ) == int(rhs)
        )
        if add_xors:
            odd = [
                variables[index]
                for index in nonzero
                if int(features[index][equation]) & 1
            ]
            model.add_bool_xor(
                odd if int(rhs) & 1 else odd + [constant_one]
            )
    model.add(sum(variables) == 105)
    if add_xors:
        model.add_bool_xor(variables)


def run_cpsat(
    lines: list[tuple[int, ...]],
    features: list[tuple[int, ...]],
    target: tuple[int, ...],
    t20: list[list[int]],
    seconds: float,
    workers: int,
    seed: int,
    add_xors: bool,
    oriented: bool,
    verbose: bool,
) -> dict[str, Any]:
    import ortools  # type: ignore
    from ortools.sat.python import cp_model  # type: ignore

    model = cp_model.CpModel()
    if not oriented:
        variables = [
            model.new_bool_var(f"x{index}") for index in range(len(lines))
        ]
        add_second_moments_cpsat(
            model, variables, features, target, add_xors
        )
        positive = variables
        negative: list[Any] = []
        edge_count = 0
    else:
        positive = [
            model.new_bool_var(f"p{index}") for index in range(len(lines))
        ]
        negative = [
            model.new_bool_var(f"n{index}") for index in range(len(lines))
        ]
        for index in range(len(lines)):
            model.add_at_most_one(positive[index], negative[index])
        unsigned = [
            positive[index] + negative[index]
            for index in range(len(lines))
        ]
        for equation, rhs in enumerate(target):
            model.add(
                sum(
                    int(feature[equation]) * unsigned[index]
                    for index, feature in enumerate(features)
                    if int(feature[equation])
                ) == int(rhs)
            )
        model.add(sum(positive) + sum(negative) == 105)
        for coordinate in range(20):
            model.add(
                sum(
                    int(line[coordinate])
                    * (positive[index] - negative[index])
                    for index, line in enumerate(lines)
                    if int(line[coordinate])
                ) == 0
            )
        transformed = [exact.matvec(t20, line) for line in lines]
        edge_count = 0
        for left, transformed_left in enumerate(transformed):
            for right in range(left + 1, len(lines)):
                inner = exact.dot(transformed_left, lines[right])
                if inner == 2:
                    model.add_bool_or(
                        ~positive[left], ~positive[right]
                    )
                    model.add_bool_or(
                        ~negative[left], ~negative[right]
                    )
                    edge_count += 1
                elif inner == -2:
                    model.add_bool_or(
                        ~positive[left], ~negative[right]
                    )
                    model.add_bool_or(
                        ~negative[left], ~positive[right]
                    )
                    edge_count += 1

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = verbose
    status = solver.solve(model)
    rows = []
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        if oriented:
            for index, line in enumerate(lines):
                if solver.value(positive[index]):
                    rows.append(list(line))
                elif solver.value(negative[index]):
                    rows.append([-value for value in line])
        else:
            rows = [
                list(lines[index])
                for index, variable in enumerate(positive)
                if solver.value(variable)
            ]
    return {
        "engine": "OR-Tools CP-SAT",
        "version": ortools.__version__,
        "oriented": oriented,
        "explicit_GF2_xors": add_xors,
        "absolute_two_edges_when_oriented": edge_count,
        "status": solver.status_name(status),
        "time_limit_seconds": seconds,
        "workers": workers,
        "seed": seed,
        "rows": rows,
        "row_count": len(rows),
        "response_stats": solver.response_stats(),
    }


def run_scip(
    features: list[tuple[int, ...]],
    target: tuple[int, ...],
    seconds: float,
    workers: int,
    seed: int,
    verbose: bool,
) -> dict[str, Any]:
    import pyscipopt  # type: ignore
    from pyscipopt import Model, quicksum  # type: ignore

    model = Model("wave31-t20-second-moment")
    if not verbose:
        model.hideOutput()
    model.setParam("limits/time", seconds)
    model.setParam("parallel/maxnthreads", workers)
    model.setParam("randomization/randomseedshift", seed)
    variables = [
        model.addVar(vtype="B", name=f"x{index}")
        for index in range(len(features))
    ]
    for equation, rhs in enumerate(target):
        model.addCons(
            quicksum(
                int(feature[equation]) * variables[index]
                for index, feature in enumerate(features)
                if int(feature[equation])
            ) == int(rhs)
        )
    model.addCons(quicksum(variables) == 105)
    model.setObjective(0)
    model.optimize()
    chosen = []
    if model.getNSols():
        chosen = [
            index
            for index, variable in enumerate(variables)
            if model.getVal(variable) > 0.5
        ]
    return {
        "engine": "SCIP via PySCIPOpt",
        "pyscipopt_version": pyscipopt.__version__,
        "scip_version": (
            f"{model.getMajorVersion()}."
            f"{model.getMinorVersion()}."
            f"{model.getTechVersion()}"
        ),
        "status": str(model.getStatus()),
        "time_limit_seconds": seconds,
        "workers": workers,
        "seed": seed,
        "solutions": model.getNSols(),
        "nodes": model.getNNodes(),
        "selected_indices": chosen,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--engine",
        choices=(
            "highs", "lp", "cpsat", "cpsat-xor",
            "cpsat-oriented", "scip",
        ),
        required=True,
    )
    parser.add_argument("--seconds", type=float, default=40.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    lines, features, target, t20 = problem()

    if args.engine in {"highs", "lp"}:
        result = run_highs(
            features, target, args.seconds, args.workers, args.seed,
            continuous=args.engine == "lp", verbose=args.verbose,
        )
    elif args.engine in {"cpsat", "cpsat-xor", "cpsat-oriented"}:
        result = run_cpsat(
            lines, features, target, t20, args.seconds, args.workers,
            args.seed, add_xors=args.engine == "cpsat-xor",
            oriented=args.engine == "cpsat-oriented",
            verbose=args.verbose,
        )
    else:
        result = run_scip(
            features, target, args.seconds, args.workers,
            args.seed, args.verbose,
        )
    result["scope_warning"] = (
        "A timeout/UNKNOWN/nonhit is not evidence of nonexistence. "
        "A returned row set is unverified discovery output."
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
