#!/usr/bin/env python3
"""Fast parity-first search for an active support 2-factor on F=3 K3,3.

The search is incomplete.  It first enforces H R H^T = 0 (mod 2) by
2-switch local search, then checks the exact 0/2 coverage and active
common-neighbor caps.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


def canon(a, b):
    return (a, b) if a < b else (b, a)


def three_k33():
    return [
        (a, b)
        for base in (0, 6, 12)
        for a in range(base, base + 3)
        for b in range(base + 3, base + 6)
    ]


def label_pair_index():
    pairs = [(i, j) for i in range(18) for j in range(i + 1, 18)]
    return {p: k for k, p in enumerate(pairs)}, pairs


def edge_mask(ep, eq, pair_index):
    ans = 0
    for i in ep:
        for j in eq:
            ans ^= 1 << pair_index[canon(i, j)]
    return ans


def allowed(ep, eq, f_set):
    if set(ep) & set(eq):
        return False
    return all(canon(i, j) not in f_set for i in ep for j in eq)


def initial_triangles():
    # Point ordering in three_k33 is component-major, then its 3x3 cells.
    return {
        canon(k, k + 9)
        for k in range(9)
    } | {
        canon(k + 9, k + 18)
        for k in range(9)
    } | {
        canon(k, k + 18)
        for k in range(9)
    }


def exact_evaluate(points, r_edges, f_set):
    cov = [[0] * 18 for _ in range(18)]
    for p, q in r_edges:
        for i in points[p]:
            for j in points[q]:
                cov[i][j] += 1
                cov[j][i] += 1
    coverage_bad = [
        [i, j, cov[i][j]]
        for i in range(18)
        for j in range(i + 1, 18)
        if cov[i][j] not in (0, 2)
        or (canon(i, j) in f_set and cov[i][j] != 0)
    ]

    d_edges = {
        (p, q)
        for p in range(27)
        for q in range(p + 1, 27)
        if set(points[p]) & set(points[q])
    }
    c_edges = d_edges | set(r_edges)
    nbr = [set() for _ in range(27)]
    for p, q in c_edges:
        nbr[p].add(q)
        nbr[q].add(p)
    cap_bad = []
    hist = {}
    for p in range(27):
        for q in range(p + 1, 27):
            cn = len(nbr[p] & nbr[q])
            hist[cn] = hist.get(cn, 0) + 1
            cap = 1 if q in nbr[p] else 2
            if cn > cap:
                cap_bad.append([p, q, cn, cap])
    return {
        "coverage_bad": coverage_bad,
        "coverage_histogram": {
            str(x): sum(
                cov[i][j] == x
                for i in range(18)
                for j in range(i + 1, 18)
            )
            for x in sorted(
                {
                    cov[i][j]
                    for i in range(18)
                    for j in range(i + 1, 18)
                }
            )
        },
        "common_neighbor_bad": cap_bad,
        "common_neighbor_histogram": hist,
        "C_edges": sorted(c_edges),
        "L_edges": [
            [i, j]
            for i in range(18)
            for j in range(i + 1, 18)
            if cov[i][j] == 2
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=540172)
    parser.add_argument("--restarts", type=int, default=100)
    parser.add_argument("--steps", type=int, default=200000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    points = three_k33()
    f_set = set(points)
    pair_index, _ = label_pair_index()
    masks = {}
    allowed_edges = set()
    for p in range(27):
        for q in range(p + 1, 27):
            if allowed(points[p], points[q], f_set):
                allowed_edges.add((p, q))
                masks[(p, q)] = edge_mask(points[p], points[q], pair_index)

    global_best = None
    for restart in range(args.restarts):
        r_edges = set(initial_triangles())
        # Randomize the valid seed by neutral 2-switches before annealing.
        parity = 0
        for edge in r_edges:
            parity ^= masks[edge]
        score = parity.bit_count()
        best = (score, set(r_edges), parity)
        for step in range(args.steps):
            e1, e2 = rng.sample(tuple(r_edges), 2)
            a, b = e1
            c, d = e2
            if len({a, b, c, d}) < 4:
                continue
            if rng.randrange(2):
                n1, n2 = canon(a, c), canon(b, d)
            else:
                n1, n2 = canon(a, d), canon(b, c)
            if (
                n1 not in allowed_edges
                or n2 not in allowed_edges
                or n1 in r_edges
                or n2 in r_edges
                or n1 == n2
            ):
                continue
            new_parity = parity ^ masks[e1] ^ masks[e2] ^ masks[n1] ^ masks[n2]
            new_score = new_parity.bit_count()
            temp = max(0.05, 4.0 * (1 - step / args.steps))
            if new_score <= score or rng.random() < math.exp(
                (score - new_score) / temp
            ):
                r_edges.remove(e1)
                r_edges.remove(e2)
                r_edges.add(n1)
                r_edges.add(n2)
                parity, score = new_parity, new_score
            if score < best[0]:
                best = (score, set(r_edges), parity)
            if score == 0:
                details = exact_evaluate(points, r_edges, f_set)
                exact = not details["coverage_bad"] and not details[
                    "common_neighbor_bad"
                ]
                record = {
                    "schema": "wave17-n3-54-mod2-support-search-v1",
                    "status": "CANDIDATE" if exact else "PARITY_ONLY",
                    "claim_label": "CANDIDATE" if exact else "UNKNOWN",
                    "scope": "active all-size-two relaxation for F=3K3,3 only",
                    "restrictions": [
                        "F fixed to the disconnected graph 3K3,3",
                        "randomized incomplete 2-switch search",
                    ],
                    "F_edges": points,
                    "R_edges": sorted(r_edges),
                    "details": details,
                    "search": {
                        "seed": args.seed,
                        "restart": restart,
                        "step": step,
                        "restarts_limit": args.restarts,
                        "steps_limit": args.steps,
                    },
                }
                args.output.write_text(
                    json.dumps(record, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                print(
                    json.dumps(
                        {
                            "status": record["status"],
                            "coverage_bad": len(details["coverage_bad"]),
                            "cap_bad": len(details["common_neighbor_bad"]),
                        }
                    )
                )
                if exact:
                    return
                # Preserve the parity object and continue from a perturbed state.
        candidate = {
            "score": best[0],
            "R_edges": sorted(best[1]),
            "restart": restart,
        }
        if global_best is None or candidate["score"] < global_best["score"]:
            global_best = candidate
            args.output.write_text(
                json.dumps(
                    {
                        "schema": "wave17-n3-54-mod2-support-search-v1",
                        "status": "NO_CONCLUSION",
                        "claim_label": "UNKNOWN",
                        "scope": "active all-size-two relaxation for F=3K3,3 only",
                        "restrictions": [
                            "F fixed to the disconnected graph 3K3,3",
                            "randomized incomplete 2-switch search",
                        ],
                        "F_edges": points,
                        "best": global_best,
                        "search": {
                            "seed": args.seed,
                            "restarts_limit": args.restarts,
                            "steps_limit": args.steps,
                        },
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
    print(json.dumps({"status": "NO_CONCLUSION", "best_parity": global_best["score"]}))


if __name__ == "__main__":
    main()
