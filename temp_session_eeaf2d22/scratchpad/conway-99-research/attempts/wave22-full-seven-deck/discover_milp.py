#!/usr/bin/env python3
"""Discovery-only MILP search for a full seven-vertex deck witness.

This script requires NumPy and SciPy/HiGHS.  Its output is not accepted on a
solver exit code: the rounded candidate is immediately passed to the
standard-library exact verifier in ``exact_check.py``.  Publication relies on
the frozen ``witness.json`` plus that exact verifier, not on this search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

import exact_check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("witness.json"),
    )
    parser.add_argument("--time-limit", type=float, default=300.0)
    arguments = parser.parse_args()

    model = exact_check.build_model()
    classes = tuple(model["classes7"])
    rows = np.asarray(model["matrix_rows"], dtype=float)
    rhs = np.asarray(model["rhs"], dtype=float)

    lower = np.zeros(len(classes), dtype=float)
    upper = np.full(len(classes), np.inf, dtype=float)
    class_index = {mask: index for index, mask in enumerate(classes)}
    for mask, count in zip(model["h_masks"], model["h_counts"]):
        index = class_index[mask]
        lower[index] = count
        upper[index] = count

    # Feasibility only.  A first run used an arbitrary nonconstant objective
    # plus the redundant total-count equation and HiGHS incorrectly reported
    # infeasibility for this badly scaled system.  Removing those numerically
    # unnecessary additions produced an exactly checkable integral point.
    objective = np.zeros(len(classes), dtype=float)
    constraints = LinearConstraint(rows, rhs, rhs)
    result = milp(
        c=objective,
        integrality=np.ones(len(classes), dtype=int),
        bounds=Bounds(lower, upper),
        constraints=constraints,
        options={
            "time_limit": arguments.time_limit,
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )
    if result.x is None:
        raise SystemExit(f"HiGHS returned no candidate: status={result.status} {result.message}")

    rounded = [int(round(value)) for value in result.x]
    maximum_rounding_error = max(
        abs(value - integer) for value, integer in zip(result.x, rounded)
    )
    payload = {
        "schema_version": 1,
        "claim_label": "CANDIDATE_PENDING_EXACT_CHECK",
        "scope": (
            "Nonnegative integer solution of the 62 order-seven deletion-deck "
            "equations at n3=705 with all 19 published Hamiltonian counts "
            "fixed at h11=2820"
        ),
        "parameters": {
            "n": exact_check.N,
            "k": exact_check.K,
            "lambda": exact_check.LAMBDA,
            "mu": exact_check.MU,
            "n3": exact_check.N3,
            "h11": exact_check.H11,
        },
        "discovery": {
            "solver": "scipy.optimize.milp using bundled HiGHS",
            "solver_status": int(result.status),
            "solver_message": str(result.message),
            "solver_success": bool(result.success),
            "objective": float(result.fun) if result.fun is not None else None,
            "maximum_rounding_error": maximum_rounding_error,
            "solver_exit_code_is_not_a_certificate": True,
        },
        "classes": [
            {"canonical_mask": mask, "count": count}
            for mask, count in zip(classes, rounded)
        ],
    }
    # Validate the in-memory object exactly before writing it.
    exact_check.validate_witness(payload, model)
    payload["claim_label"] = "EXACTLY_VALIDATED_CANDIDATE"
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": arguments.output.as_posix(),
                "support_size": sum(count > 0 for count in rounded),
                "total": sum(rounded),
                "maximum_rounding_error": maximum_rounding_error,
                "exact_validation": "PASS",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
