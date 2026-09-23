"""Numerical support discovery for the exact Wave134 rational LP.

This file is discovery-only.  A support is useful only if the separate exact
rational reconstruction and standard-library replay succeed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import discover_rational as exact_model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "numerical-support.json"


def row(
    sources: list[tuple[int, int, int]],
    target: tuple[int, int, int],
) -> list[int]:
    return [
        exact_model.transform_coefficient(source, target)
        for source in sources
    ]


def discover() -> dict:
    sources = exact_model.primal_orbit_states()
    allowed = exact_model.dual_orbit_states()
    forbidden = exact_model.forbidden_dual_states()
    primal_lower = exact_model.forced_primal()
    dual_lower = exact_model.forced_dual()
    lower = np.array(
        [float(primal_lower.get(state, 0)) for state in sources],
        dtype=np.float64,
    )
    remainder = exact_model.ORBIT_TOTAL - int(lower.sum())

    inequalities = np.empty((len(allowed), len(sources)), dtype=np.float64)
    inequality_right = np.empty(len(allowed), dtype=np.float64)
    for index, target in enumerate(allowed):
        integers = row(sources, target)
        scale = float(max(abs(value) for value in integers))
        lower_image = sum(
            value * primal_lower.get(source, 0)
            for source, value in zip(sources, integers)
        )
        right = (
            dual_lower.get(target, 0) * exact_model.ORBIT_TOTAL
            - lower_image
        )
        inequalities[index, :] = [
            -float(value) / scale for value in integers
        ]
        inequality_right[index] = -float(right) / (remainder * scale)

    equalities = np.empty(
        (1 + len(forbidden), len(sources)), dtype=np.float64
    )
    equality_right = np.empty(1 + len(forbidden), dtype=np.float64)
    equalities[0, :] = 1.0
    equality_right[0] = 1.0
    for index, target in enumerate(forbidden, start=1):
        integers = row(sources, target)
        scale = float(max(abs(value) for value in integers))
        lower_image = sum(
            value * primal_lower.get(source, 0)
            for source, value in zip(sources, integers)
        )
        equalities[index, :] = [
            float(value) / scale for value in integers
        ]
        equality_right[index] = -float(lower_image) / (remainder * scale)

    bounds = [(0.0, None) for _ in sources]
    zero_index = sources.index((99, 0, 0))
    bounds[zero_index] = (0.0, 0.0)
    result = linprog(
        np.zeros(len(sources), dtype=np.float64),
        A_ub=inequalities,
        b_ub=inequality_right,
        A_eq=equalities,
        b_eq=equality_right,
        bounds=bounds,
        method="highs-ipm",
        options={
            "disp": True,
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
            "time_limit": 120.0,
        },
    )

    positive = []
    if result.x is not None:
        positive = [
            {
                "state": list(state),
                "scaled_remainder_value": repr(float(value)),
            }
            for state, value in zip(sources, result.x)
            if value > 1e-11
        ]
    return {
        "format": "wave134-numerical-support-v1",
        "classification": (
            "NUMERICAL_SUPPORT_ONLY" if result.success
            else "UNKNOWN_NUMERICAL"
        ),
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "source_orbits": len(sources),
        "allowed_dual_rows": len(allowed),
        "forbidden_dual_rows": len(forbidden),
        "positive_support_threshold": "1e-11",
        "positive_support_count": len(positive),
        "positive_support": positive,
        "limitations": [
            "Floating-point output is not a certificate.",
            "All claimed feasibility requires a fresh exact reconstruction.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = discover()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["classification"])
    print(f"positive support: {payload['positive_support_count']}")


if __name__ == "__main__":
    main()
