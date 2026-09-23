"""Enumerate labeled all-size-two local-premise models for diagnostics."""

from __future__ import annotations

import itertools
import sys

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def connected(edges):
    adj = {i: set() for i in range(14)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = {0}
    stack = [0]
    while stack:
        stack.extend(adj[stack.pop()] - seen)
        seen |= set(stack)
    return len(seen) == 14


def four_cycles(edges):
    edge_set = set(edges)
    adj = {i: set() for i in range(14)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return sum(
        len(adj[u] & adj[v]) * (len(adj[u] & adj[v]) - 1) // 2
        for u, v in itertools.combinations(range(14), 2)
        if (u, v) not in edge_set
    ) // 2


def main():
    vertices = tuple(range(14))
    edges = tuple(itertools.combinations(vertices, 2))
    pool = IDPool()
    f = {edge: pool.id(("f", edge)) for edge in edges}
    k = {edge: pool.id(("k", edge)) for edge in edges}
    cnf = CNF()

    for j in (1, 2, 3):
        cnf.append([f[(0, j)]])
    for j in range(4, 14):
        cnf.append([-f[(0, j)]])
    if "--force-extra" in sys.argv:
        cnf.append([k[(0, 4)]])
        for j in (1, 2, 3):
            cnf.append([-f[tuple(sorted((j, 4)))]])

    for i in vertices:
        inc_f = [f[tuple(sorted((i, j)))] for j in vertices if i != j]
        inc_k = [k[tuple(sorted((i, j)))] for j in vertices if i != j]
        cnf.extend(CardEnc.equals(inc_f, 3, vpool=pool, encoding=EncType.seqcounter))
        cnf.extend(CardEnc.equals(inc_k, 7, vpool=pool, encoding=EncType.seqcounter))
    for edge in edges:
        cnf.append([-f[edge], k[edge]])
    for a, b, c in itertools.combinations(vertices, 3):
        cnf.append([-f[(a, b)], -f[(a, c)], -f[(b, c)]])
    for root in vertices:
        others = [v for v in vertices if v != root]
        for a, b in itertools.combinations(others, 2):
            cnf.append([
                -f[tuple(sorted((root, a)))],
                -f[tuple(sorted((root, b)))],
                k[tuple(sorted((a, b)))],
            ])

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        for index in range(20):
            if not solver.solve():
                print("UNSAT after", index)
                break
            model = {lit for lit in solver.get_model() if lit > 0}
            selected_f = [edge for edge in edges if f[edge] in model]
            selected_k = [edge for edge in edges if k[edge] in model]
            distance_two = set()
            adj = {i: set() for i in vertices}
            for u, v in selected_f:
                adj[u].add(v)
                adj[v].add(u)
            for root in vertices:
                distance_two.update(tuple(sorted(pair)) for pair in itertools.combinations(adj[root], 2))
            print({
                "index": index,
                "connected": connected(selected_f),
                "C4": four_cycles(selected_f),
                "distance2_edges": len(distance_two),
                "extra_K": len(set(selected_k) - set(selected_f) - distance_two),
                "F": selected_f,
            })
            solver.add_clause([
                -f[edge] if f[edge] in model else f[edge] for edge in edges
            ])


if __name__ == "__main__":
    main()
