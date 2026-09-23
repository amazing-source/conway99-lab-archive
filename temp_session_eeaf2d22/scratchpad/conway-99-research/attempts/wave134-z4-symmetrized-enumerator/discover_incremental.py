"""Bounded incremental exact-rational solve for Wave134.

Start with all exact zero rows and only the graph-forced dual lower rows.
Replay each exact rational point against the complete transform, add a small
batch of violated nonnegativity rows, and repeat.  A CANDIDATE is emitted only
after every one of the 1,114 allowed dual rows passes exact replay.
"""

from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from pathlib import Path

from z3 import Real, Solver, Sum, sat

import discover_rational as model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "rational-witness.json"


def expression(variables, sources, target):
    return Sum(
        [
            coefficient * variables[source]
            for source in sources
            if (
                coefficient := model.transform_coefficient(source, target)
            )
        ]
    )


def encode(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def exact_row(primal, sources, target) -> Fraction:
    return sum(
        Fraction(model.transform_coefficient(source, target))
        * primal[source]
        for source in sources
    ) / model.ORBIT_TOTAL


def solve(wall_seconds: float, batch_size: int) -> dict:
    started = time.monotonic()
    sources = model.primal_orbit_states()
    targets = model.dual_orbit_states()
    forbidden = model.forbidden_dual_states()
    primal_lower = model.forced_primal()
    dual_lower = model.forced_dual()
    variables = {
        state: Real(f"X_{state[0]}_{state[1]}_{state[2]}")
        for state in sources
    }
    solver = Solver()
    for state in sources:
        solver.add(variables[state] >= primal_lower.get(state, 0))
    solver.add(variables[(99, 0, 0)] == 1)
    solver.add(
        Sum([variables[state] for state in sources])
        == model.ORBIT_TOTAL
    )
    print(
        f"phase=build-zero-rows count={len(forbidden)}",
        flush=True,
    )
    for target in forbidden:
        solver.add(expression(variables, sources, target) == 0)
    active = set(dual_lower)
    for target, lower in dual_lower.items():
        solver.add(
            expression(variables, sources, target)
            >= lower * model.ORBIT_TOTAL
        )

    trace = []
    final_primal = None
    final_dual = None
    for iteration in range(20):
        remaining = wall_seconds - (time.monotonic() - started)
        if remaining <= 1:
            return {
                "classification": "UNKNOWN_INCREMENTAL_WALL",
                "trace": trace,
            }
        solver.set(timeout=max(1, int(1000 * remaining)))
        print(
            f"phase=solve iteration={iteration} active={len(active)} "
            f"remaining={remaining:.1f}",
            flush=True,
        )
        status = solver.check()
        if status != sat:
            return {
                "classification": (
                    "UNKNOWN_INCREMENTAL_" + str(status).upper()
                ),
                "trace": trace,
            }
        z3_model = solver.model()
        primal = {
            state: model.decode(
                z3_model.eval(variables[state], model_completion=True)
            )
            for state in sources
        }
        dual = {
            target: exact_row(primal, sources, target)
            for target in targets
        }
        violations = [
            (
                value - Fraction(dual_lower.get(target, 0)),
                target,
            )
            for target, value in dual.items()
            if value < dual_lower.get(target, 0)
        ]
        violations.sort()
        trace.append(
            {
                "iteration": iteration,
                "active_rows": len(active),
                "violated_rows": len(violations),
                "most_negative": (
                    encode(violations[0][0]) if violations else None
                ),
            }
        )
        print(
            f"phase=replay iteration={iteration} "
            f"violated={len(violations)}",
            flush=True,
        )
        if not violations:
            final_primal = primal
            final_dual = dual
            break
        additions = [
            target
            for _, target in violations
            if target not in active
        ][:batch_size]
        if not additions:
            return {
                "classification": "UNKNOWN_INCREMENTAL_STALL",
                "trace": trace,
            }
        for target in additions:
            solver.add(
                expression(variables, sources, target)
                >= dual_lower.get(target, 0) * model.ORBIT_TOTAL
            )
            active.add(target)
    if final_primal is None or final_dual is None:
        return {
            "classification": "UNKNOWN_INCREMENTAL_ITERATION_LIMIT",
            "trace": trace,
        }

    return {
        "format": "wave134-z4-symmetrized-rational-v1",
        "claim_label": "CANDIDATE",
        "classification": "EXACT_RATIONAL_FEASIBLE",
        "scope": (
            "Full three-variable symmetrized Z4 MacWilliams relaxation "
            "with graph-forced words through primal triples and dual pairs."
        ),
        "parameters": {
            "length": model.N,
            "C_type": "4^54 2^1",
            "C_order": str(1 << model.LOG2_C_ORDER),
            "Cperp_type": "4^44 2^1",
            "Cperp_order": str(1 << model.LOG2_D_ORDER),
            "raw_state_count": 5050,
            "primal_orbit_variable_count": len(sources),
            "allowed_dual_orbit_count": len(targets),
            "forbidden_dual_orbit_count": len(forbidden),
        },
        "incremental_trace": trace,
        "primal_orbits": {
            f"{a},{b},{c}": encode(value)
            for (a, b, c), value in final_primal.items()
            if value
        },
        "dual_orbits": {
            f"{a},{b},{c}": encode(value)
            for (a, b, c), value in final_dual.items()
            if value
        },
        "forced_primal_lower": {
            f"{a},{b},{c}": str(value)
            for (a, b, c), value in sorted(primal_lower.items())
        },
        "forced_dual_lower": {
            f"{a},{b},{c}": str(value)
            for (a, b, c), value in sorted(dual_lower.items())
        },
        "limitations": [
            "The witness is a formal exact rational symmetrized enumerator.",
            "It does not realize a Z4 code, adjacency matrix, or graph.",
            "It does not retain labelled-word compatibility beyond forced aggregate counts.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wall-seconds", type=float, default=180.0)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    payload = solve(args.wall_seconds, args.batch_size)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["classification"])


if __name__ == "__main__":
    main()
