#!/usr/bin/env python3
"""Heuristic search for the exact all-size-two active residual at n3=54.

This is discovery code, not a complete search.  A returned zero-score object
is checked exactly and may be used as a relaxation certificate.  A non-hit has
no mathematical status.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


def canon_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def random_cubic_triangle_free(rng: random.Random, n: int = 18):
    """Configuration-model sampler for a simple triangle-free cubic graph."""
    for _ in range(10000):
        stubs = [v for v in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        edges = set()
        ok = True
        for j in range(0, len(stubs), 2):
            e = canon_edge(stubs[j], stubs[j + 1])
            if e[0] == e[1] or e in edges:
                ok = False
                break
            edges.add(e)
        if not ok:
            continue
        nbr = [set() for _ in range(n)]
        for a, b in edges:
            nbr[a].add(b)
            nbr[b].add(a)
        if any((nbr[a] & nbr[b]) for a, b in edges):
            continue
        return sorted(edges)
    raise RuntimeError("failed to sample a simple triangle-free cubic graph")


def three_k33():
    edges = []
    for base in (0, 6, 12):
        for a in range(base, base + 3):
            for b in range(base + 3, base + 6):
                edges.append((a, b))
    return edges


def cycle_edges(order):
    return {canon_edge(order[i - 1], order[i]) for i in range(len(order))}


def matrices_from_edges(n, edges):
    a = [[0] * n for _ in range(n)]
    for u, v in edges:
        a[u][v] = a[v][u] = 1
    return a


def evaluate(f_edges, r_edges):
    n_labels = 18
    points = list(f_edges)
    n_points = len(points)
    f_set = set(f_edges)
    r_set = set(r_edges)
    h = [[int(i in e) for e in points] for i in range(n_labels)]

    # Coverage H R H^T, computed directly from the 2-factor edges.
    coverage = [[0] * n_labels for _ in range(n_labels)]
    forbidden_r = 0
    for p, q in r_set:
        ep, eq = points[p], points[q]
        if set(ep) & set(eq):
            forbidden_r += 1
        for i in ep:
            for j in eq:
                coverage[i][j] += 1
                coverage[j][i] += 1

    coverage_penalty = 0
    for i in range(n_labels):
        coverage_penalty += 20 * coverage[i][i]
        for j in range(i + 1, n_labels):
            c = coverage[i][j]
            if (i, j) in f_set:
                coverage_penalty += 20 * c
            elif c not in (0, 2):
                coverage_penalty += min(abs(c), abs(c - 2)) + (10 if c > 2 else 0)

    # C = line graph(F) plus R.
    d_edges = set()
    for p in range(n_points):
        for q in range(p + 1, n_points):
            if set(points[p]) & set(points[q]):
                d_edges.add((p, q))
    overlap = len(d_edges & r_set)
    c_edges = d_edges | r_set
    c_adj = matrices_from_edges(n_points, c_edges)
    cap_penalty = 0
    adjacent_bad = 0
    nonadjacent_bad = 0
    common_hist = {}
    for p in range(n_points):
        for q in range(p + 1, n_points):
            cn = sum(c_adj[p][z] & c_adj[q][z] for z in range(n_points))
            common_hist[cn] = common_hist.get(cn, 0) + 1
            if c_adj[p][q] and cn > 1:
                adjacent_bad += 1
                cap_penalty += 10 * (cn - 1)
            elif not c_adj[p][q] and cn > 2:
                nonadjacent_bad += 1
                cap_penalty += 5 * (cn - 2)

    deg = [0] * n_points
    for p, q in r_set:
        deg[p] += 1
        deg[q] += 1
    degree_penalty = sum(abs(x - 2) for x in deg)
    score = (
        50 * forbidden_r
        + 50 * overlap
        + 20 * degree_penalty
        + coverage_penalty
        + cap_penalty
    )
    l_edges = [
        (i, j)
        for i in range(n_labels)
        for j in range(i + 1, n_labels)
        if coverage[i][j] == 2
    ]
    return {
        "score": score,
        "forbidden_r_edges": forbidden_r,
        "line_support_overlap": overlap,
        "r_degree_penalty": degree_penalty,
        "coverage_penalty": coverage_penalty,
        "cap_penalty": cap_penalty,
        "adjacent_cap_violations": adjacent_bad,
        "nonadjacent_cap_violations": nonadjacent_bad,
        "coverage_histogram": histogram(
            coverage[i][j]
            for i in range(n_labels)
            for j in range(i + 1, n_labels)
        ),
        "common_neighbor_histogram": common_hist,
        "L_edges": l_edges,
        "active_adjacency_edges": sorted(c_edges),
    }


def histogram(values):
    ans = {}
    for value in values:
        ans[str(value)] = ans.get(str(value), 0) + 1
    return ans


def optimize_r(rng, f_edges, steps):
    n_points = len(f_edges)
    order = list(range(n_points))
    rng.shuffle(order)
    r_edges = cycle_edges(order)
    cur = evaluate(f_edges, r_edges)
    best = (cur["score"], sorted(r_edges), cur)
    for step in range(steps):
        # A general 2-switch preserves degree two but may merge or split cycles.
        e1, e2 = rng.sample(tuple(r_edges), 2)
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            continue
        if rng.randrange(2):
            new1, new2 = canon_edge(a, c), canon_edge(b, d)
        else:
            new1, new2 = canon_edge(a, d), canon_edge(b, c)
        if new1 in r_edges or new2 in r_edges or new1 == new2:
            continue
        p_edges = set(r_edges)
        p_edges.remove(e1)
        p_edges.remove(e2)
        p_edges.add(new1)
        p_edges.add(new2)
        nxt = evaluate(f_edges, p_edges)
        temp = max(0.05, 5.0 * (1.0 - step / steps))
        delta = nxt["score"] - cur["score"]
        if delta <= 0 or rng.random() < math.exp(-delta / temp):
            r_edges, cur = p_edges, nxt
        if cur["score"] < best[0]:
            best = (cur["score"], sorted(r_edges), cur)
            if best[0] == 0:
                break
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=54017)
    parser.add_argument("--graphs", type=int, default=100)
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument(
        "--f-family", choices=("random", "three-k33"), default="random"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    overall = None
    for graph_index in range(args.graphs):
        f_edges = (
            random_cubic_triangle_free(rng)
            if args.f_family == "random"
            else three_k33()
        )
        for restart in range(args.restarts):
            score, r_description, details = optimize_r(rng, f_edges, args.steps)
            candidate = {
                "schema": "wave17-n3-54-active-relaxation-search-v1",
                "status": "CANDIDATE" if score == 0 else "HEURISTIC_NONZERO",
                "restrictions": [
                    "all active points have size two (forced at the spectral equality boundary)",
                    "R is a general labeled simple 2-factor sampled by local 2-switches",
                    "F is a labeled sampled simple triangle-free cubic graph on 18 labels",
                ],
                "F_edges": f_edges,
                "R_edges": r_description,
                "details": details,
                "search": {
                    "seed": args.seed,
                    "graph_index": graph_index,
                    "restart": restart,
                    "graphs_limit": args.graphs,
                    "restarts_limit": args.restarts,
                    "steps_limit": args.steps,
                    "f_family": args.f_family,
                },
            }
            if overall is None or score < overall["details"]["score"]:
                overall = candidate
                if args.output:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(
                        json.dumps(overall, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
            if score == 0:
                print(json.dumps({"status": "CANDIDATE", "score": 0}))
                return
    print(
        json.dumps(
            {
                "status": "NO_CONCLUSION",
                "best_score": overall["details"]["score"],
                "restriction": "randomized incomplete search over sampled F and locally switched R",
            }
        )
    )


if __name__ == "__main__":
    main()
