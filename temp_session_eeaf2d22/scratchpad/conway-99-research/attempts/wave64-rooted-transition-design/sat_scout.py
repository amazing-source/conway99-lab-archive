#!/usr/bin/env python3
"""SAT scout for the Wave-64 linear transition+block master.

This introduces explicit disjoint-adjacency variables, making the endpoint
profile constraints small.  A SAT assignment is exported as a candidate and
must be checked by ``check_witness.py``.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from pathlib import Path

from pysat.solvers import Solver

import transition_design as td

HERE = Path(__file__).resolve().parent


def solve(time_limit: float, output: str) -> dict[str, object]:
    nz = len(td.BLOCKS)
    pairs = tuple(sorted(td.PAIR_TO_BLOCKS))
    ny = len(pairs)
    nt = len(td.TRANSITIONS)
    y_id = {pair: nz + i + 1 for i, pair in enumerate(pairs)}
    t_id = {tid: nz + ny + tid + 1 for tid in range(nt)}
    nprimary = nz + ny + nt
    solver = Solver(name="minicard")
    clause_count = 0
    native_atmost_count = 0

    def add_clause(clause: list[int]) -> None:
        nonlocal clause_count
        solver.add_clause(clause)
        clause_count += 1

    def add_atmost(lits: list[int], bound: int) -> None:
        nonlocal native_atmost_count
        solver.add_atmost(lits, bound)
        native_atmost_count += 1

    def add_exact(lits: list[int], bound: int) -> None:
        add_atmost(lits, bound)
        add_atmost([-lit for lit in lits], len(lits) - bound)

    # y_pq is exactly the unique selected block containing disjoint pair pq.
    for pair in pairs:
        y = y_id[pair]
        zs = [z + 1 for z in td.PAIR_TO_BLOCKS[pair]]
        add_atmost(zs, 1)
        for z in zs:
            add_clause([-z, y])
        add_clause([-y] + zs)

    # Five blocks through each H-edge label.
    for p in range(84):
        add_exact(
            [z + 1 for z, block in enumerate(td.BLOCKS) if p in block],
            5,
        )

    # Twelve doubled blocks at each root mate pair.
    for g in range(7):
        add_exact(
            [
                z + 1
                for z, block in enumerate(td.BLOCKS)
                if g in td.doubled_supports(block)
            ],
            12,
        )

    # The Wave-3 weighted local dichotomy.  There is one full-opposite
    # y-variable f and twenty one-support-opposite variables o_i.  The
    # equation 2f + sum(o_i) = 2 is encoded without an external PB library:
    # sum(o_i)<=2; f=>all o_i=0; and not-f=>sum(o_i)>=2.
    for p in range(84):
        full: list[int] = []
        one: list[int] = []
        for q in range(84):
            if q == p:
                continue
            pair = tuple(sorted((p, q)))
            if pair not in y_id:
                continue
            relation = td.label_relation(p, q)
            if relation == "disjoint_full_opposite":
                full.append(y_id[pair])
            elif relation == "disjoint_one_opposite":
                one.append(y_id[pair])
        assert len(full) == 1 and len(one) == 20
        f = full[0]
        add_atmost(one, 2)
        for o in one:
            add_clause([-f, -o])
        for omitted in range(len(one)):
            add_clause([f] + one[:omitted] + one[omitted + 1 :])

    # Transition system: a perfect matching at each base vertex.
    for s in td.BASE:
        for p, edge in enumerate(td.LABELS):
            if s not in edge:
                continue
            tids = [
                t_id[tid]
                for tid, (common, a, b) in enumerate(td.TRANSITIONS)
                if common == s and p in (a, b)
            ]
            add_exact(tids, 1)

    # All 1,176 rooted endpoint-profile equations.
    for p, edge in enumerate(td.LABELS):
        for s in td.BASE:
            lits = []
            for q in range(84):
                if q == p or not set(td.LABELS[p]).isdisjoint(td.LABELS[q]):
                    continue
                if s not in td.LABELS[q]:
                    continue
                pair = tuple(sorted((p, q)))
                lits.append(y_id[pair])
            for tid, (_common, a, b) in enumerate(td.TRANSITIONS):
                if a == p and s in td.LABELS[b]:
                    lits.append(t_id[tid])
                elif b == p and s in td.LABELS[a]:
                    lits.append(t_id[tid])
            rhs = 2 - int(s in edge) - int(td.mate(s) in edge)
            add_exact(lits, rhs)

    # The 280 transition-triangle cuts.
    transition_triangle_cuts = 0
    for vertices in __import__("itertools").combinations(td.BASE, 3):
        if len({td.support(x) for x in vertices}) < 3:
            continue
        h_edges = tuple(
            td.LABEL_INDEX[td.label(a, b)]
            for a, b in __import__("itertools").combinations(vertices, 2)
        )
        tids = []
        for p, q in __import__("itertools").combinations(h_edges, 2):
            common = next(iter(set(td.LABELS[p]) & set(td.LABELS[q])))
            tids.append(t_id[td.TRANSITION_INDEX[(common, min(p, q), max(p, q))]])
        add_atmost(tids, 2)
        transition_triangle_cuts += 1

    timer = threading.Timer(time_limit, solver.interrupt)
    started = time.time()
    timer.start()
    try:
        sat = solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
    elapsed = time.time() - started

    summary: dict[str, object] = {
        "format": "wave64-rooted-transition-design-sat-search-v1",
        "solver": "PySAT MiniCard 1.41",
        "status": "SAT" if sat is True else "UNSAT" if sat is False else "UNKNOWN",
        "elapsed_seconds": elapsed,
        "time_limit_seconds": time_limit,
        "primary_variables": nprimary,
        "block_variables": nz,
        "disjoint_adjacency_variables": ny,
        "transition_variables": nt,
        "top_variable": nprimary,
        "clauses": clause_count,
        "native_atmost_constraints": native_atmost_count,
        "endpoint_profile_equalities": 1176,
        "transition_triangle_cuts": transition_triangle_cuts,
        "limitations": [
            "UNSAT is not promoted without a proof certificate.",
            "UNKNOWN is not evidence of infeasibility.",
            "SAT is only a candidate until exact witness checking.",
            "The master omits full residual codegree constraints.",
        ],
    }
    if sat is True:
        model = set(lit for lit in solver.get_model() if lit > 0)
        selected_blocks = {z for z in range(nz) if z + 1 in model}
        selected_transitions = {tid for tid in range(nt) if t_id[tid] in model}
        td.emit_strong_witness(
            selected_blocks,
            selected_transitions,
            HERE / output,
            summary,
        )
        summary["selected_blocks"] = len(selected_blocks)
        summary["selected_transitions"] = len(selected_transitions)
    solver.delete()
    (HERE / "sat-search-result.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=180.0)
    parser.add_argument("--output", default="transition-block-witness.json")
    args = parser.parse_args()
    print(json.dumps(solve(args.time_limit, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
