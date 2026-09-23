#!/usr/bin/env python3
"""Discovery-only exact integer solve for the Wave 44 rooted flag system.

Z3 is used only to find a vector.  The retained certificate is checked by
``exact_check.py`` using ordinary Python integer arithmetic and does not
depend on Z3.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave44_rooted_flags_exact", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import exact rooted system")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def discover() -> dict[str, object]:
    system = CHECK.endpoint_system()
    rows = (
        system["base_rows"]
        + system["vertex_rows"]
        + system["edge_rows"]
        + system["nonedge_rows"]
    )
    rhs = (
        system["base_rhs"]
        + system["vertex_rhs"]
        + system["edge_rhs"]
        + system["nonedge_rhs"]
    )
    variables = [z3.Int(f"x_{index}") for index in range(len(rows[0]))]
    solver = z3.Solver()
    solver.add(*(variable >= 0 for variable in variables[:-1]))
    solver.add(variables[-1] >= 2079, variables[-1] <= 4158)
    for row, target in zip(rows, rhs):
        solver.add(
            z3.Sum(
                *(
                    coefficient * variable
                    for coefficient, variable in zip(row, variables)
                    if coefficient
                )
            )
            == target
        )
    status = solver.check()
    if status != z3.sat:
        raise RuntimeError(f"exact integer discovery returned {status}")
    model = solver.model()
    vector = tuple(model.evaluate(variable).as_long() for variable in variables)
    if any(CHECK.residuals(rows, rhs, vector)):
        raise AssertionError("Z3 model failed exact Python replay")
    support = [
        {"canonical_mask": mask, "count": count}
        for mask, count in zip(system["classes"], vector[:-1])
        if count
    ]
    support_payload = json.dumps(
        support, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return {
        "format": "wave44-rooted-flags-witness-v1",
        "h11": 4 * vector[-1],
        "support_size": len(support),
        "zero_classes": len(system["classes"]) - len(support),
        "maximum_count": max(vector[:-1]),
        "support_sha256": hashlib.sha256(support_payload).hexdigest(),
        "support": support,
        "discovery": {
            "engine": f"z3 {z3.get_version_string()}",
            "status": "sat",
            "certificate_checker_dependency": "none",
        },
        "scope_wall": {
            "is_graph": False,
            "endpoint_proved": False,
            "Conway_99": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    result = discover()
    payload = canonical_json(result)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_bytes(payload)
    print(
        f"WROTE {arguments.output} "
        f"sha256={hashlib.sha256(payload).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
