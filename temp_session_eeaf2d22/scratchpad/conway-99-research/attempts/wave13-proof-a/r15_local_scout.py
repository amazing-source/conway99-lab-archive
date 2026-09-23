"""Scout abstract r=15 point-hypergraph/K premise models.

The models here deliberately stop before exact global H/L coverage.  A found
model is therefore only a counterexample to overly strong *local* shortcuts.
No absence result from this random scout is used as evidence.
"""

from __future__ import annotations

import argparse
import random
from itertools import combinations


Pair = tuple[int, int]


def edge(a: int, b: int) -> Pair:
    return (a, b) if a < b else (b, a)


def random_simple_graph(degrees: list[int], rng: random.Random, tries: int = 1000):
    n = len(degrees)
    for _ in range(tries):
        stubs = [v for v, degree in enumerate(degrees) for _ in range(degree)]
        rng.shuffle(stubs)
        edges: set[Pair] = set()
        good = True
        while stubs:
            a = stubs.pop()
            candidates = [
                idx
                for idx, b in enumerate(stubs)
                if b != a and edge(a, b) not in edges
            ]
            if not candidates:
                good = False
                break
            idx = rng.choice(candidates)
            b = stubs.pop(idx)
            edges.add(edge(a, b))
        if good:
            actual = [0] * n
            for a, b in edges:
                actual[a] += 1
                actual[b] += 1
            if actual == degrees:
                return edges
    return None


def point_hypergraph_ok(points: list[frozenset[int]]) -> bool:
    # Linear.
    for p, q in combinations(points, 2):
        if len(p & q) > 1:
            return False
    # Every triangle in the point-intersection graph must have one common root.
    for p, q, r in combinations(points, 3):
        if p & q and p & r and q & r and not (p & q & r):
            return False
    return True


def mandatory_and_forbidden(
    points: list[frozenset[int]], n: int
) -> tuple[set[Pair], set[Pair]] | None:
    incident = [[] for _ in range(n)]
    mandatory: set[Pair] = set()
    forbidden: set[Pair] = set()
    for index, point in enumerate(points):
        for label in point:
            incident[label].append(index)
        for a, b in combinations(point, 2):
            mandatory.add(edge(a, b))
    if any(len(items) != 3 for items in incident):
        return None
    for root, items in enumerate(incident):
        for left, right in combinations(items, 2):
            p = points[left] - {root}
            q = points[right] - {root}
            if len(p) == 2 and len(q) == 2:
                # In the surviving r=15 modes, a size3/size3 meeting is full L.
                for a in p:
                    for b in q:
                        forbidden.add(edge(a, b))
            else:
                # At least one side is a singleton, so the L crossing is empty.
                for a in p:
                    for b in q:
                        mandatory.add(edge(a, b))
    if mandatory & forbidden:
        return None
    return mandatory, forbidden


def triangle_free(edges: set[Pair], n: int) -> bool:
    neighbors = [set() for _ in range(n)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    return all(not (neighbors[a] & neighbors[b]) for a, b in edges)


def complete_regular(
    mandatory: set[Pair],
    forbidden: set[Pair],
    n: int,
    degree: int,
) -> set[Pair] | None:
    """Exact recursive completion to a regular graph."""
    chosen = set(mandatory)
    neighbors = [set() for _ in range(n)]
    for a, b in chosen:
        neighbors[a].add(b)
        neighbors[b].add(a)
    if any(len(row) > degree for row in neighbors):
        return None
    blocked = set(forbidden)

    def rec() -> bool:
        deficits = [degree - len(neighbors[v]) for v in range(n)]
        if not any(deficits):
            return True
        # Most constrained positive-deficit vertex.
        best = None
        options = None
        for v, deficit in enumerate(deficits):
            if deficit <= 0:
                continue
            opts = [
                w
                for w in range(n)
                if w != v
                and deficits[w] > 0
                and edge(v, w) not in chosen
                and edge(v, w) not in blocked
            ]
            if len(opts) < deficit:
                return False
            score = (len(opts), -deficit)
            if best is None or score < best:
                best = score
                options = (v, deficit, opts)
        assert options is not None
        v, need, opts = options
        # Choose all neighbors for v at once.
        for selected in combinations(opts, need):
            added = [edge(v, w) for w in selected]
            for a, b in added:
                chosen.add((a, b))
                neighbors[a].add(b)
                neighbors[b].add(a)
            if all(len(row) <= degree for row in neighbors) and rec():
                return True
            for a, b in added:
                chosen.remove((a, b))
                neighbors[a].remove(b)
                neighbors[b].remove(a)
        return False

    return chosen if rec() else None


def scout_m1(seed: int, rounds: int):
    rng = random.Random(seed)
    n = 15
    size3 = frozenset((0, 1, 2))
    fixed_b = {
        edge(0, 3),
        edge(0, 4),
        edge(1, 5),
        edge(1, 6),
        edge(2, 7),
        edge(2, 8),
    }
    residual_degrees = [0, 0, 0] + [2] * 6 + [3] * 6
    for attempt in range(1, rounds + 1):
        residual = random_simple_graph(residual_degrees, rng, tries=20)
        if residual is None:
            continue
        b_edges = fixed_b | residual
        if not triangle_free(b_edges, n):
            continue
        points = [size3] + [frozenset(pair) for pair in sorted(b_edges)]
        if not point_hypergraph_ok(points):
            continue
        constraints = mandatory_and_forbidden(points, n)
        if constraints is None:
            continue
        mandatory, forbidden = constraints
        mdeg = [0] * n
        for a, b in mandatory:
            mdeg[a] += 1
            mdeg[b] += 1
        if max(mdeg) > 8:
            continue
        completion = complete_regular(mandatory, forbidden, n, 8)
        if completion is None:
            continue
        return {
            "attempt": attempt,
            "size3_points": [sorted(size3)],
            "size2_points": [list(pair) for pair in sorted(b_edges)],
            "mandatory_edges": [list(pair) for pair in sorted(mandatory)],
            "forbidden_edges": [list(pair) for pair in sorted(forbidden)],
            "K_edges": [list(pair) for pair in sorted(completion)],
            "mandatory_degrees": mdeg,
        }
    return None


def points_from_intersection_graph(
    r_order: int, r_edges: set[Pair], n_labels: int = 15
) -> tuple[list[frozenset[int]], list[int]]:
    incident_r = [[] for _ in range(r_order)]
    next_label = 0
    for u, v in sorted(r_edges):
        incident_r[u].append(next_label)
        incident_r[v].append(next_label)
        next_label += 1
    points: list[frozenset[int]] = []
    for v in range(r_order):
        labels = list(incident_r[v])
        while len(labels) < 3:
            labels.append(next_label)
            next_label += 1
        if len(labels) != 3:
            raise ValueError("R degree must be at most three")
        points.append(frozenset(labels))
    if next_label > n_labels:
        raise ValueError("too many active labels")
    t = [0] * n_labels
    for point in points:
        for label in point:
            t[label] += 1
    return points, t


def scout_r(
    r_order: int,
    r_edges: set[Pair],
    seed: int,
    rounds: int,
):
    rng = random.Random(seed)
    n = 15
    size3, t = points_from_intersection_graph(r_order, r_edges, n)
    degrees = [3 - value for value in t]
    for attempt in range(1, rounds + 1):
        b_edges = random_simple_graph(degrees, rng, tries=20)
        if b_edges is None:
            continue
        points = size3 + [frozenset(pair) for pair in sorted(b_edges)]
        if not point_hypergraph_ok(points):
            continue
        constraints = mandatory_and_forbidden(points, n)
        if constraints is None:
            continue
        mandatory, forbidden = constraints
        mdeg = [0] * n
        for a, b in mandatory:
            mdeg[a] += 1
            mdeg[b] += 1
        if max(mdeg) > 8:
            continue
        completion = complete_regular(mandatory, forbidden, n, 8)
        if completion is None:
            continue
        return {
            "attempt": attempt,
            "R_edges": [list(pair) for pair in sorted(r_edges)],
            "size3_points": [sorted(point) for point in size3],
            "size2_points": [list(pair) for pair in sorted(b_edges)],
            "mandatory_edges": [list(pair) for pair in sorted(mandatory)],
            "forbidden_edges": [list(pair) for pair in sorted(forbidden)],
            "K_edges": [list(pair) for pair in sorted(completion)],
            "mandatory_degrees": mdeg,
        }
    return None


def exact_scout_r(
    r_order: int,
    r_edges: set[Pair],
    node_limit: int,
):
    """Deterministic degree-sequence search for one local premise model."""
    n = 15
    size3, t = points_from_intersection_graph(r_order, r_edges, n)
    target = [3 - value for value in t]
    b_edges: set[Pair] = set()
    b_neighbors = [set() for _ in range(n)]
    nodes = 0
    exhausted = True

    forbidden_b: set[Pair] = set()
    for point in size3:
        for a, b in combinations(point, 2):
            forbidden_b.add(edge(a, b))
    for p, q in combinations(size3, 2):
        meet = p & q
        if not meet:
            continue
        root = next(iter(meet))
        for a in p - {root}:
            for b in q - {root}:
                forbidden_b.add(edge(a, b))

    def partial_ok(new_edges: list[Pair]) -> bool:
        # Triangle-free B.
        for a, b in new_edges:
            if b_neighbors[a] & b_neighbors[b]:
                return False
        # A point P plus two B edges may not form a Berge triangle.
        for point in size3:
            for outside in range(n):
                if outside not in point and len(b_neighbors[outside] & point) > 1:
                    return False
        # Whenever a root is complete, expose all crossing constraints.
        points = size3 + [frozenset(pair) for pair in sorted(b_edges)]
        incident_count = [0] * n
        for point in points:
            for label in point:
                incident_count[label] += 1
        completed_roots = {v for v, count in enumerate(incident_count) if count == 3}
        mandatory: set[Pair] = set()
        forbidden: set[Pair] = set()
        incident = [[] for _ in range(n)]
        for index, point in enumerate(points):
            for label in point:
                incident[label].append(index)
            for a, b in combinations(point, 2):
                mandatory.add(edge(a, b))
        for root in completed_roots:
            for left, right in combinations(incident[root], 2):
                p = points[left] - {root}
                q = points[right] - {root}
                target_set = forbidden if len(p) == len(q) == 2 else mandatory
                for a in p:
                    for b in q:
                        target_set.add(edge(a, b))
        if mandatory & forbidden:
            return False
        degrees = [0] * n
        for a, b in mandatory:
            degrees[a] += 1
            degrees[b] += 1
        return max(degrees) <= 8

    def rec() -> dict | None:
        nonlocal nodes, exhausted
        nodes += 1
        if nodes > node_limit:
            exhausted = False
            return None
        residual = [target[v] - len(b_neighbors[v]) for v in range(n)]
        if any(value < 0 for value in residual):
            return None
        if not any(residual):
            points = size3 + [frozenset(pair) for pair in sorted(b_edges)]
            if not point_hypergraph_ok(points):
                return None
            constraints = mandatory_and_forbidden(points, n)
            if constraints is None:
                return None
            mandatory, forbidden = constraints
            completion = complete_regular(mandatory, forbidden, n, 8)
            if completion is None:
                return None
            return {
                "nodes": nodes,
                "R_edges": [list(pair) for pair in sorted(r_edges)],
                "size3_points": [sorted(point) for point in size3],
                "size2_points": [list(pair) for pair in sorted(b_edges)],
                "mandatory_edges": [list(pair) for pair in sorted(mandatory)],
                "forbidden_edges": [list(pair) for pair in sorted(forbidden)],
                "K_edges": [list(pair) for pair in sorted(completion)],
            }
        candidates_by_vertex = []
        for v, need in enumerate(residual):
            if need <= 0:
                continue
            candidates = [
                w
                for w in range(v + 1, n)
                if residual[w] > 0
                and edge(v, w) not in forbidden_b
                and edge(v, w) not in b_edges
            ]
            # A vertex with residual demand but no higher-index candidate means
            # this canonical degree construction has failed.
            candidates_by_vertex.append((len(candidates) - need, v, need, candidates))
        # The first positive-residual vertex is sufficient for unique generation:
        # every edge to a lower vertex has already been decided.
        _, v, need, candidates = min(
            candidates_by_vertex, key=lambda item: item[1]
        )
        if len(candidates) < need:
            return None
        for selected in combinations(candidates, need):
            added = [edge(v, w) for w in selected]
            for a, b in added:
                b_edges.add((a, b))
                b_neighbors[a].add(b)
                b_neighbors[b].add(a)
            if partial_ok(added):
                found = rec()
                if found is not None:
                    return found
            for a, b in added:
                b_edges.remove((a, b))
                b_neighbors[a].remove(b)
                b_neighbors[b].remove(a)
            if not exhausted:
                return None
        return None

    result = rec()
    return result, nodes, exhausted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=45001)
    parser.add_argument("--rounds", type=int, default=200_000)
    parser.add_argument("--case", choices=("m1", "c5", "k23"), default="m1")
    parser.add_argument("--exact", action="store_true")
    parser.add_argument("--node-limit", type=int, default=2_000_000)
    args = parser.parse_args()
    if args.case == "m1":
        result = scout_m1(args.seed, args.rounds)
    elif args.case == "c5":
        r_edges = {edge(i, (i + 1) % 5) for i in range(5)}
        if args.exact:
            result, nodes, exhausted = exact_scout_r(5, r_edges, args.node_limit)
            print(f"exact_nodes={nodes} exhausted={exhausted}")
        else:
            result = scout_r(5, r_edges, args.seed, args.rounds)
    else:
        r_edges = {edge(a, b) for a in range(2) for b in range(2, 5)}
        if args.exact:
            result, nodes, exhausted = exact_scout_r(5, r_edges, args.node_limit)
            print(f"exact_nodes={nodes} exhausted={exhausted}")
        else:
            result = scout_r(5, r_edges, args.seed, args.rounds)
    if result is None:
        if args.exact and args.case != "m1" and exhausted:
            print("NO_LOCAL_MODEL_IN_THIS_FIXED_R_CASE")
        elif args.exact and args.case != "m1":
            print("EXACT_SEARCH_NODE_LIMIT (non-evidentiary)")
        else:
            print("NO_RANDOM_LOCAL_MODEL_FOUND (non-evidentiary)")
        return
    print("LOCAL_MODEL_FOUND")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
