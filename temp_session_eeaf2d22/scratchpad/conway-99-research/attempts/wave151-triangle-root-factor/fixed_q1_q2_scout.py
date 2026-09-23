#!/usr/bin/env python3
"""Exact Z3 scout for extending the stored Q1 to a third incidence group.

An UNSAT status from this script concerns only the stored Q1.  No proof trace
is exported, so the status is retained as discovery metadata rather than a
certificate.  A SAT result is replayed with exact integer matrix products.
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import z3

import exact_check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=int, default=120)
    arguments = parser.parse_args()
    exact_check.demand(1 <= arguments.time_limit <= 1800, "bad time limit")

    parent = json.loads(exact_check.WAVE149_RESULT.read_text(encoding="utf-8"))
    gram = np.asarray(
        parent["minimal_surviving_witness"]["gram_rows"], dtype=np.int16
    )
    target_02 = gram[:12, 24:36]
    target_12 = gram[12:24, 24:36]
    edges = exact_check.edge_universe()
    c0 = np.asarray(exact_check.incidence(edges), dtype=np.int16)
    c1 = c0[:, exact_check.Q1]

    allowed: list[list[int]] = []
    for domain in range(60):
        left0 = np.flatnonzero(c0[:, domain])
        left1 = np.flatnonzero(c1[:, domain])
        row = []
        for image in range(60):
            right = np.flatnonzero(c0[:, image])
            if (
                all(target_02[i, j] > 0 for i in left0 for j in right)
                and all(target_12[i, j] > 0 for i in left1 for j in right)
            ):
                row.append(image)
        allowed.append(row)

    solver = z3.Solver()
    solver.set(timeout=1000 * arguments.time_limit)
    variable = {
        (domain, image): z3.Bool(f"q2_{domain}_{image}")
        for domain in range(60)
        for image in allowed[domain]
    }
    for domain in range(60):
        solver.add(z3.PbEq(
            [(variable[(domain, image)], 1) for image in allowed[domain]], 1
        ))
    for image in range(60):
        solver.add(z3.PbEq(
            [
                (variable[(domain, image)], 1)
                for domain in range(60)
                if (domain, image) in variable
            ],
            1,
        ))
    for left, target in ((c0, target_02), (c1, target_12)):
        for i in range(12):
            domains = np.flatnonzero(left[i])
            for j in range(12):
                terms = [
                    (variable[(domain, image)], 1)
                    for domain in domains
                    for image in allowed[int(domain)]
                    if c0[j, image]
                ]
                if terms:
                    solver.add(z3.PbEq(terms, int(target[i, j])))
                else:
                    exact_check.demand(target[i, j] == 0, "empty positive row")

    started = time.monotonic()
    status = solver.check()
    elapsed = time.monotonic() - started
    candidate = None
    if status == z3.sat:
        model = solver.model()
        q2 = [
            next(
                image
                for image in allowed[domain]
                if z3.is_true(model.eval(variable[(domain, image)]))
            )
            for domain in range(60)
        ]
        c2 = c0[:, q2]
        exact_check.demand(np.array_equal(c0 @ c2.T, target_02),
                           "SAT Q2 failed G02")
        exact_check.demand(np.array_equal(c1 @ c2.T, target_12),
                           "SAT Q2 failed G12")
        candidate = q2
    print(json.dumps(
        {
            "format": "wave151-fixed-q1-q2-scout-v1",
            "status": str(status),
            "elapsed_seconds": elapsed,
            "time_limit_seconds": arguments.time_limit,
            "boolean_variables": len(variable),
            "candidate_Q2": candidate,
            "negative_status_is_not_certificate": True,
            "scope": "extension of the one stored Q1 only",
        },
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
