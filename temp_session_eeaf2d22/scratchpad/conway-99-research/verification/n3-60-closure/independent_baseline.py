#!/usr/bin/env python3
"""Independent exact helpers for the conditional n3=60 closure audit.

This module uses only the Python standard library and imports no discovery
implementation.  It checks algebraic and finite combinatorial consequences
of the frozen audited SRG and indexed-point premises.  It is not, by itself,
a certificate that either Wave 19 residual is empty.
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb
from typing import Callable, Iterable, Iterator, Sequence


V = 99
K = 14
LAMBDA = 1
MU = 2

Edge = tuple[int, int]
Adjacency = tuple[frozenset[int], ...]


def normalize_edge(a: int, b: int) -> Edge:
    if a == b:
        raise ValueError("loops are forbidden")
    return (a, b) if a < b else (b, a)


def adjacency_from_edges(n: int, edges: Iterable[Edge]) -> Adjacency:
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    rows = [set() for _ in range(n)]
    seen: set[Edge] = set()
    for raw_a, raw_b in edges:
        if not isinstance(raw_a, int) or not isinstance(raw_b, int):
            raise ValueError("vertex labels must be integers")
        if not (0 <= raw_a < n and 0 <= raw_b < n):
            raise ValueError("vertex label out of range")
        edge = normalize_edge(raw_a, raw_b)
        if edge in seen:
            raise ValueError("parallel or duplicate edge")
        seen.add(edge)
        a, b = edge
        rows[a].add(b)
        rows[b].add(a)
    return tuple(frozenset(row) for row in rows)


def validate_adjacency(adj: Sequence[Iterable[int]]) -> Adjacency:
    n = len(adj)
    rows = tuple(frozenset(row) for row in adj)
    for a, row in enumerate(rows):
        if a in row:
            raise ValueError("loop in adjacency")
        for b in row:
            if not isinstance(b, int) or not (0 <= b < n):
                raise ValueError("invalid neighbor label")
            if a not in rows[b]:
                raise ValueError("asymmetric adjacency")
    return rows


def edge_indicator(adj: Sequence[Iterable[int]], a: int, b: int) -> int:
    if a == b:
        return 0
    return int(b in adj[a])


def srg_square_entry(
    adj: Sequence[Iterable[int]],
    a: int,
    b: int,
    *,
    k: int = K,
    lam: int = LAMBDA,
    mu: int = MU,
) -> int:
    """Entry of A^2 implied by the SRG equation."""
    if a == b:
        return k
    return lam if b in adj[a] else mu


def rectangle_identity_lhs_from_square(
    adj: Sequence[Iterable[int]],
    a: int,
    b: int,
    c: int,
    d: int,
) -> int:
    """<row_a-row_b,row_c-row_d>, using the SRG A^2 entries."""
    return (
        srg_square_entry(adj, a, c)
        - srg_square_entry(adj, a, d)
        - srg_square_entry(adj, b, c)
        + srg_square_entry(adj, b, d)
    )


def rectangle_identity_rhs(
    adj: Sequence[Iterable[int]],
    a: int,
    b: int,
    c: int,
    d: int,
    *,
    k_minus_mu: int = K - MU,
    lambda_minus_mu: int = LAMBDA - MU,
) -> int:
    """Exact four-index identity, including all repeated-index terms.

    From A^2=(k-mu)I+(lambda-mu)A+mu J, the J terms cancel:

      <r_a-r_b,r_c-r_d>
       =(k-mu)(delta_ac-delta_ad-delta_bc+delta_bd)
        +(lambda-mu)(A_ac-A_ad-A_bc+A_bd).
    """
    delta = (
        int(a == c) - int(a == d) - int(b == c) + int(b == d)
    )
    alternating_a = (
        edge_indicator(adj, a, c)
        - edge_indicator(adj, a, d)
        - edge_indicator(adj, b, c)
        + edge_indicator(adj, b, d)
    )
    return k_minus_mu * delta + lambda_minus_mu * alternating_a


def enumerate_simple_graphs(n: int) -> Iterator[Adjacency]:
    possible = tuple(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield adjacency_from_edges(
            n, (edge for bit, edge in enumerate(possible) if mask & (1 << bit))
        )


def rectangle_identity_exhaustive(max_n: int = 4) -> int:
    checked = 0
    for n in range(1, max_n + 1):
        for adj in enumerate_simple_graphs(n):
            for a, b, c, d in product(range(n), repeat=4):
                lhs = rectangle_identity_lhs_from_square(adj, a, b, c, d)
                rhs = rectangle_identity_rhs(adj, a, b, c, d)
                if lhs != rhs:
                    raise AssertionError((n, a, b, c, d, lhs, rhs))
                checked += 1
    return checked


def adjacent_edge_rectangle_parameters(
    *,
    k: int = K,
    lam: int = LAMBDA,
    mu: int = MU,
) -> dict[str, int | bool]:
    """Local arithmetic around an edge uv.

    Each side has k-lambda-1 neighbors exclusive of the other endpoint and
    the lambda common neighbors.  Every exclusive x is nonadjacent to the
    opposite endpoint and hence has mu common neighbors with it.  One is the
    near endpoint; the other mu-1 lie across.  For Conway's mu=2 this is a
    1-regular bipartite graph, hence a perfect matching.
    """
    exclusive = k - lam - 1
    cross_degree = mu - 1
    return {
        "common_neighbors": lam,
        "exclusive_per_side": exclusive,
        "cross_degree": cross_degree,
        "is_perfect_matching": exclusive >= 0 and cross_degree == 1,
        "cross_edges": exclusive * cross_degree,
    }


def integer_partitions(total: int, minimum: int = 1) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def rectangle_component_lengths(total_vertices: int = 24) -> tuple[tuple[int, ...], ...]:
    """All component-length multisets for the two-matchings local graph.

    Triangle-pair edges stay on a side and rectangle edges switch sides.
    Every component of their union is a cycle.  It uses an even number of
    switching edges, so its length is divisible by four.
    """
    if total_vertices < 0 or total_vertices % 4:
        raise ValueError("total must be a nonnegative multiple of four")
    units = total_vertices // 4
    return tuple(tuple(4 * part for part in partition) for partition in integer_partitions(units))


def crossing_components(
    rows: int, columns: int, edges: Iterable[tuple[int, int]]
) -> tuple[int, ...]:
    """Classify a two-sided zero-or-two crossing.

    Nonisolated vertices must all have degree two, so every nontrivial
    component is an even bipartite cycle.
    """
    if rows < 0 or columns < 0:
        raise ValueError("negative part size")
    normalized: set[tuple[int, int]] = set()
    row_neighbors = [set() for _ in range(rows)]
    col_neighbors = [set() for _ in range(columns)]
    for r, c in edges:
        if not (0 <= r < rows and 0 <= c < columns):
            raise ValueError("crossing endpoint out of range")
        if (r, c) in normalized:
            raise ValueError("duplicate crossing edge")
        normalized.add((r, c))
        row_neighbors[r].add(c)
        col_neighbors[c].add(r)
    if any(len(nbrs) not in (0, 2) for nbrs in row_neighbors):
        raise ValueError("row degree is not zero or two")
    if any(len(nbrs) not in (0, 2) for nbrs in col_neighbors):
        raise ValueError("column degree is not zero or two")

    graph: dict[tuple[str, int], set[tuple[str, int]]] = {}
    for r, c in normalized:
        rv = ("r", r)
        cv = ("c", c)
        graph.setdefault(rv, set()).add(cv)
        graph.setdefault(cv, set()).add(rv)
    unseen = set(graph)
    sizes: list[int] = []
    while unseen:
        start = next(iter(unseen))
        queue = deque([start])
        component: set[tuple[str, int]] = set()
        while queue:
            vertex = queue.popleft()
            if vertex in component:
                continue
            component.add(vertex)
            queue.extend(graph[vertex] - component)
        unseen -= component
        if any(len(graph[vertex]) != 2 for vertex in component):
            raise AssertionError("non-cycle component passed degree check")
        row_count = sum(kind == "r" for kind, _ in component)
        col_count = len(component) - row_count
        if row_count != col_count or len(component) < 4 or len(component) % 2:
            raise AssertionError("invalid bipartite cycle")
        sizes.append(len(component))
    return tuple(sorted(sizes))


def enumerate_crossing_shapes(
    rows: int, columns: int
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    possible = tuple(product(range(rows), range(columns)))
    shapes: set[tuple[int, tuple[int, ...]]] = set()
    for mask in range(1 << len(possible)):
        edges = tuple(
            edge for bit, edge in enumerate(possible) if mask & (1 << bit)
        )
        try:
            components = crossing_components(rows, columns, edges)
        except ValueError:
            continue
        shapes.add((len(edges), components))
    return tuple(sorted(shapes))


def edge_pair_is_induced_matching(
    base: Sequence[Iterable[int]], first: Edge, second: Edge
) -> bool:
    """Whether two base-graph edges form an induced 2K2."""
    adj = validate_adjacency(base)
    a, b = normalize_edge(*first)
    c, d = normalize_edge(*second)
    if b not in adj[a] or d not in adj[c]:
        raise ValueError("declared pair is not made of base edges")
    if {a, b} & {c, d}:
        return False
    return all(y not in adj[x] for x in (a, b) for y in (c, d))


def line_graph(base: Sequence[Iterable[int]]) -> tuple[tuple[Edge, ...], Adjacency]:
    adj = validate_adjacency(base)
    edges = tuple(
        (a, b) for a in range(len(adj)) for b in adj[a] if a < b
    )
    line_edges = []
    for i, first in enumerate(edges):
        for j in range(i + 1, len(edges)):
            second = edges[j]
            if set(first) & set(second):
                line_edges.append((i, j))
    return edges, adjacency_from_edges(len(edges), line_edges)


def cross_edges_between(
    adj: Sequence[Iterable[int]], left: Iterable[int], right: Iterable[int]
) -> tuple[Edge, ...]:
    rows = validate_adjacency(adj)
    left_set = frozenset(left)
    right_set = frozenset(right)
    if left_set & right_set:
        raise ValueError("the two local sides must be disjoint")
    return tuple(
        (a, b) for a in sorted(left_set) for b in sorted(right_set) if b in rows[a]
    )


def is_matching_between(
    adj: Sequence[Iterable[int]], left: Iterable[int], right: Iterable[int]
) -> bool:
    edges = cross_edges_between(adj, left, right)
    used_left: set[int] = set()
    used_right: set[int] = set()
    for a, b in edges:
        if a in used_left or b in used_right:
            return False
        used_left.add(a)
        used_right.add(b)
    return True


def check_disjoint_point_edge_local(
    base: Sequence[Iterable[int]],
    induced: Sequence[Iterable[int]],
    first_edge_index: int,
    second_edge_index: int,
    expected_crossing_edges: int,
) -> bool:
    """Check the residual-B local rectangle consequence for one edge.

    `base` is F and `induced` is D on the edge-points E(F).  A disjoint
    actual graph edge must join an induced matching in F.  Its four line
    neighbors on either side are disjoint.  Their D-cross edges must form a
    matching, with size four for a positive 2-by-2 crossing and zero for a
    zero crossing.
    """
    base_edges, line = line_graph(base)
    d = validate_adjacency(induced)
    if len(d) != len(base_edges):
        raise ValueError("D is not indexed by all edges of F")
    if not (0 <= first_edge_index < len(d) and 0 <= second_edge_index < len(d)):
        raise ValueError("edge-point index out of range")
    if second_edge_index not in d[first_edge_index]:
        raise ValueError("the two point vertices are not adjacent in D")
    first = base_edges[first_edge_index]
    second = base_edges[second_edge_index]
    if not edge_pair_is_induced_matching(base, first, second):
        return False
    left = line[first_edge_index]
    right = line[second_edge_index]
    if len(left) != 4 or len(right) != 4 or left & right:
        return False
    cross = cross_edges_between(d, left, right)
    return len(cross) == expected_crossing_edges and is_matching_between(d, left, right)


def validate_point_family(
    points: Sequence[Iterable[int]],
    label_count: int,
    *,
    expected_sizes: Counter[int] | None = None,
    occurrences_per_label: int = 3,
) -> tuple[frozenset[int], ...]:
    """Strict parser/property check for an indexed linear point family."""
    if label_count < 0 or occurrences_per_label < 0:
        raise ValueError("invalid point-family parameter")
    normalized = tuple(frozenset(point) for point in points)
    if any(len(point) < 2 for point in normalized):
        raise ValueError("active singleton or empty point")
    if len(set(normalized)) != len(normalized):
        raise ValueError("duplicate point value")
    for point in normalized:
        if any(not isinstance(label, int) or not (0 <= label < label_count) for label in point):
            raise ValueError("point label out of range")
    if expected_sizes is not None and Counter(map(len, normalized)) != expected_sizes:
        raise ValueError("wrong point-size multiset")
    occurrences = Counter(label for point in normalized for label in point)
    if occurrences != Counter({label: occurrences_per_label for label in range(label_count)}):
        raise ValueError("wrong label-occurrence multiset")
    for first, second in combinations(normalized, 2):
        if len(first & second) > 1:
            raise ValueError("point family is not linear")
    for first, second, third in combinations(normalized, 3):
        ab = first & second
        ac = first & third
        bc = second & third
        if ab and ac and bc:
            intersection_labels = set(ab | ac | bc)
            if len(intersection_labels) == 3:
                raise ValueError("forbidden Berge triangle")
            if len(intersection_labels) != 1:
                raise AssertionError("linear triple has impossible intersection pattern")
    return normalized


def meeting_graph(points: Sequence[Iterable[int]]) -> Adjacency:
    normalized = tuple(frozenset(point) for point in points)
    return adjacency_from_edges(
        len(normalized),
        (
            (a, b)
            for a, b in combinations(range(len(normalized)), 2)
            if normalized[a] & normalized[b]
        ),
    )


def validate_two_factor(
    vertex_count: int, support_vertices: Iterable[int], edges: Iterable[Edge]
) -> tuple[Edge, ...]:
    support = frozenset(support_vertices)
    if any(not isinstance(vertex, int) or not (0 <= vertex < vertex_count) for vertex in support):
        raise ValueError("two-factor support vertex out of range")
    normalized: set[Edge] = set()
    degrees = Counter()
    for raw_edge in edges:
        edge = normalize_edge(*raw_edge)
        if edge in normalized:
            raise ValueError("duplicate two-factor edge")
        if edge[0] not in support or edge[1] not in support:
            raise ValueError("two-factor edge leaves support")
        normalized.add(edge)
        degrees.update(edge)
    if any(degrees[vertex] != 2 for vertex in support):
        raise ValueError("support is not covered with degree two")
    if set(degrees) - support:
        raise AssertionError("unexpected degree key")
    return tuple(sorted(normalized))


def check_disjoint_point_edge_from_meeting(
    meeting: Sequence[Iterable[int]],
    induced: Sequence[Iterable[int]],
    first: int,
    second: int,
    expected_crossing_edges: int,
) -> bool:
    """General local check used by both residuals.

    A disjoint actual edge cannot have a common active-triangle meeting
    neighbor: that vertex would make the edge's unique triangle active at
    both endpoints.  The meeting-neighbor sides must therefore be disjoint.
    Rectangle cross edges between them must be a matching.
    """
    lgraph = validate_adjacency(meeting)
    d = validate_adjacency(induced)
    if len(lgraph) != len(d):
        raise ValueError("meeting and induced graph orders differ")
    if second in lgraph[first]:
        raise ValueError("point edge is not disjoint")
    if second not in d[first]:
        raise ValueError("point edge is absent from D")
    left = lgraph[first]
    right = lgraph[second]
    if left & right:
        return False
    cross = cross_edges_between(d, left, right)
    return len(cross) == expected_crossing_edges and is_matching_between(d, left, right)


def matrix_square(adj: Sequence[Iterable[int]]) -> list[list[int]]:
    rows = validate_adjacency(adj)
    n = len(rows)
    return [
        [len(rows[a] & rows[b]) for b in range(n)]
        for a in range(n)
    ]


def outside_gram(
    induced: Sequence[Iterable[int]],
    *,
    k: int = K,
    lam: int = LAMBDA,
    mu: int = MU,
) -> tuple[tuple[int, ...], ...]:
    """Compute BB^T forced by the top-left SRG block equation."""
    d = validate_adjacency(induced)
    n = len(d)
    d2 = matrix_square(d)
    result = []
    for a in range(n):
        row = []
        for b in range(n):
            value = (
                (k - mu) * int(a == b)
                + (lam - mu) * edge_indicator(d, a, b)
                + mu
                - d2[a][b]
            )
            row.append(value)
        result.append(tuple(row))
    return tuple(result)


def gram_local_defects(
    induced: Sequence[Iterable[int]],
) -> tuple[tuple[int, int, str, int], ...]:
    """List negative or semantically impossible forced Gram entries."""
    d = validate_adjacency(induced)
    gram = outside_gram(d)
    defects: list[tuple[int, int, str, int]] = []
    for a in range(len(d)):
        expected_diag = K - len(d[a])
        if gram[a][a] != expected_diag:
            defects.append((a, a, "diagonal", gram[a][a]))
        if gram[a][a] < 0:
            defects.append((a, a, "negative diagonal", gram[a][a]))
        for b in range(a + 1, len(d)):
            if gram[a][b] < 0:
                kind = "adjacent excess common neighbors" if b in d[a] else "nonadjacent excess common neighbors"
                defects.append((a, b, kind, gram[a][b]))
    return tuple(defects)


def exact_psd(matrix: Sequence[Sequence[int | Fraction]]) -> tuple[bool, int]:
    """Exact rational Schur-complement PSD test and rank."""
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix is not square")
    work = [[Fraction(value) for value in row] for row in matrix]
    if any(work[a][b] != work[b][a] for a in range(n) for b in range(n)):
        raise ValueError("matrix is not symmetric")
    rank = 0
    for pivot in range(n):
        diagonal = work[pivot][pivot]
        if diagonal < 0:
            return False, rank
        if diagonal == 0:
            if any(work[pivot][j] != 0 for j in range(pivot + 1, n)):
                return False, rank
            continue
        rank += 1
        for a in range(pivot + 1, n):
            for b in range(a, n):
                value = work[a][b] - work[a][pivot] * work[pivot][b] / diagonal
                work[a][b] = value
                work[b][a] = value
        for j in range(pivot + 1, n):
            work[pivot][j] = Fraction(0)
            work[j][pivot] = Fraction(0)
    return True, rank


def binary_gram_entry_defects(
    gram: Sequence[Sequence[int]],
) -> tuple[tuple[int, int, str], ...]:
    """Cheap necessary entrywise conditions for a binary Gram factor."""
    n = len(gram)
    if any(len(row) != n for row in gram):
        raise ValueError("Gram matrix is not square")
    defects: list[tuple[int, int, str]] = []
    for a in range(n):
        if not isinstance(gram[a][a], int) or gram[a][a] < 0:
            defects.append((a, a, "invalid diagonal"))
        for b in range(a + 1, n):
            value = gram[a][b]
            if gram[b][a] != value:
                defects.append((a, b, "asymmetric"))
            elif not isinstance(value, int) or value < 0:
                defects.append((a, b, "invalid intersection"))
            elif value > min(gram[a][a], gram[b][b]):
                defects.append((a, b, "intersection exceeds row weight"))
    return tuple(defects)


def verify_binary_factor(
    gram: Sequence[Sequence[int]], factor: Sequence[Sequence[int]]
) -> bool:
    m = len(gram)
    if any(len(row) != m for row in gram):
        raise ValueError("Gram matrix is not square")
    if len(factor) != m:
        raise ValueError("factor row count mismatch")
    width = len(factor[0]) if factor else 0
    if any(len(row) != width for row in factor):
        raise ValueError("ragged factor")
    if any(value not in (0, 1) for row in factor for value in row):
        raise ValueError("factor is not binary")
    for a in range(m):
        for b in range(m):
            product = sum(factor[a][z] * factor[b][z] for z in range(width))
            if product != gram[a][b]:
                return False
    return True


def srg_block_defects(
    induced: Sequence[Iterable[int]],
    factor: Sequence[Sequence[int]],
    outside: Sequence[Iterable[int]],
) -> tuple[str, ...]:
    """Replay all three block equations for A=[[D,B],[B^T,C]]."""
    d = validate_adjacency(induced)
    c = validate_adjacency(outside)
    m = len(d)
    n = len(c)
    defects: list[str] = []
    if m + n != V:
        defects.append(f"order {m+n} != {V}")
    if len(factor) != m:
        return tuple(defects + ["factor row count mismatch"])
    if any(len(row) != n for row in factor):
        return tuple(defects + ["factor column count mismatch"])
    if any(value not in (0, 1) for row in factor for value in row):
        return tuple(defects + ["factor is not binary"])

    gram = outside_gram(d)
    if not verify_binary_factor(gram, factor):
        defects.append("top-left block equation fails")

    for x in range(m):
        for z in range(n):
            left = sum(factor[y][z] for y in d[x]) + sum(
                factor[x][w] for w in c[z]
            )
            right = MU + (LAMBDA - MU) * factor[x][z]
            if left != right:
                defects.append(f"cross block fails at ({x},{z}): {left}!={right}")

    c2 = matrix_square(c)
    for z in range(n):
        for w in range(n):
            left = sum(factor[x][z] * factor[x][w] for x in range(m)) + c2[z][w]
            right = (
                (K - MU) * int(z == w)
                + (LAMBDA - MU) * edge_indicator(c, z, w)
                + MU
            )
            if left != right:
                defects.append(f"bottom-right block fails at ({z},{w}): {left}!={right}")
    return tuple(defects)


def degree_moment_formula(
    induced: Sequence[Iterable[int]], outside_count: int
) -> tuple[int, int]:
    """Return sum a_z and sum a_z^2 forced for outside column degrees."""
    d = validate_adjacency(induced)
    if outside_count != V - len(d):
        raise ValueError("outside count does not match v=99")
    degrees = [len(row) for row in d]
    total = K * len(d) - sum(degrees)
    square_total = (
        MU * len(d) * len(d)
        + (K - MU) * len(d)
        + (LAMBDA - MU) * sum(degrees)
        - sum(value * value for value in degrees)
    )
    # For (99,14,1,2), the preceding general expansion simplifies to
    # 2m^2+12m-sum(d^2+d).  Assert the exact specialization explicitly.
    specialized = 2 * len(d) * len(d) + 12 * len(d) - sum(
        value * value + value for value in degrees
    )
    if square_total != specialized:
        raise AssertionError("general/specialized moment mismatch")
    gram_total = sum(sum(row) for row in outside_gram(d))
    if specialized != gram_total:
        raise AssertionError("moment formula does not equal 1^T Gram 1")
    return total, specialized


def excess_moments(m: int, excess_degrees: Sequence[int]) -> tuple[int, int]:
    if len(excess_degrees) != m or any(value < 0 for value in excess_degrees):
        raise ValueError("invalid excess sequence")
    total_excess = sum(excess_degrees)
    square_excess = sum(value * value for value in excess_degrees)
    outside_sum = 8 * m - total_excess
    outside_square_sum = (
        2 * m * m - 30 * m - 13 * total_excess - square_excess
    )
    return outside_sum, outside_square_sum


def integer_minimum_square_sum(count: int, total: int) -> int:
    if count < 0 or total < 0:
        raise ValueError("count and total must be nonnegative")
    if count == 0:
        if total:
            raise ValueError("positive total with zero count")
        return 0
    low, remainder = divmod(total, count)
    return (count - remainder) * low * low + remainder * (low + 1) ** 2


def count_bounded_degree_histograms(
    count: int, total: int, square_total: int, maximum: int = K
) -> int:
    """Count exact histograms, not assignments, by memoized recursion."""
    if min(count, total, square_total, maximum) < 0:
        return 0
    memo: dict[tuple[int, int, int, int], int] = {}

    def rec(cap: int, left_count: int, left_sum: int, left_square: int) -> int:
        key = (cap, left_count, left_sum, left_square)
        if key in memo:
            return memo[key]
        if left_count == 0:
            answer = int(left_sum == 0 and left_square == 0)
            memo[key] = answer
            return answer
        if left_count < 0 or left_sum < 0 or left_square < 0:
            return 0
        if cap == 0:
            answer = int(left_sum == 0 and left_square == 0)
            memo[key] = answer
            return answer
        if left_sum > cap * left_count or left_square > cap * left_sum:
            return 0
        if (left_square - left_sum) % 2:
            return 0
        if integer_minimum_square_sum(left_count, left_sum) > left_square:
            return 0
        full, remainder = divmod(left_sum, cap)
        if full > left_count or (full == left_count and remainder):
            return 0
        maximum_square = full * cap * cap + remainder * remainder
        if maximum_square < left_square:
            return 0
        answer = 0
        max_multiplicity = min(
            left_count,
            left_sum // cap,
            left_square // (cap * cap),
        )
        for multiplicity in range(max_multiplicity + 1):
            answer += rec(
                cap - 1,
                left_count - multiplicity,
                left_sum - multiplicity * cap,
                left_square - multiplicity * cap * cap,
            )
        memo[key] = answer
        return answer

    return rec(maximum, count, total, square_total)


def canonical_unlabeled_graph(edges: Iterable[Edge]) -> tuple[int, tuple[Edge, ...]]:
    normalized = {normalize_edge(*edge) for edge in edges}
    support = sorted({vertex for edge in normalized for vertex in edge})
    if not support:
        return (0, ())
    relabel = {vertex: index for index, vertex in enumerate(support)}
    compact = {
        normalize_edge(relabel[a], relabel[b]) for a, b in normalized
    }
    n = len(support)
    best: tuple[Edge, ...] | None = None
    for permutation in permutations(range(n)):
        candidate = tuple(
            sorted(normalize_edge(permutation[a], permutation[b]) for a, b in compact)
        )
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return (n, best)


def graph_degree_multiset(canonical: tuple[int, tuple[Edge, ...]]) -> tuple[int, ...]:
    n, edges = canonical
    degrees = [0] * n
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    return tuple(sorted(degrees, reverse=True))


def graph_type_name(canonical: tuple[int, tuple[Edge, ...]]) -> str:
    n, edges = canonical
    e = len(edges)
    degrees = graph_degree_multiset(canonical)
    key = (n, e, degrees)
    names = {
        (0, 0, ()): "empty",
        (2, 1, (1, 1)): "K2",
        (4, 2, (1, 1, 1, 1)): "2K2",
        (3, 2, (2, 1, 1)): "P3",
        (6, 3, (1, 1, 1, 1, 1, 1)): "3K2",
        (5, 3, (2, 1, 1, 1, 1)): "P3 + K2",
        (4, 3, (2, 2, 1, 1)): "P4",
        (4, 3, (3, 1, 1, 1)): "K1,3",
        (3, 3, (2, 2, 2)): "K3",
    }
    if key not in names:
        raise ValueError(f"unexpected graph type {key}")
    return names[key]


def enumerate_z_types(max_edges: int = 3) -> tuple[str, ...]:
    """Enumerate every unlabeled simple graph with no isolates and <=3 edges."""
    if not (0 <= max_edges <= 3):
        raise ValueError("this audit helper is scoped through three edges")
    types: dict[tuple[int, tuple[Edge, ...]], str] = {(0, ()): "empty"}
    vertices = 2 * max_edges
    possible = tuple(combinations(range(vertices), 2))
    for edge_count in range(1, max_edges + 1):
        for selected in combinations(possible, edge_count):
            canonical = canonical_unlabeled_graph(selected)
            types[canonical] = graph_type_name(canonical)
    return tuple(
        name
        for _, name in sorted(
            types.items(), key=lambda item: (len(item[0][1]), item[1])
        )
    )


Z_TYPE_EDGES: dict[str, tuple[Edge, ...]] = {
    "empty": (),
    "K2": ((0, 1),),
    "2K2": ((0, 1), (2, 3)),
    "P3": ((0, 1), (1, 2)),
    "3K2": ((0, 1), (2, 3), (4, 5)),
    "P3 + K2": ((0, 1), (1, 2), (3, 4)),
    "P4": ((0, 1), (1, 2), (2, 3)),
    "K1,3": ((0, 1), (0, 2), (0, 3)),
    "K3": ((0, 1), (1, 2), (0, 2)),
}


def z_moment_row(name: str, m: int = 30) -> dict[str, int]:
    if name not in Z_TYPE_EDGES:
        raise ValueError("unknown Z type")
    edges = Z_TYPE_EDGES[name]
    support_size = 1 + max((vertex for edge in edges for vertex in edge), default=-1)
    degrees = [0] * m
    if support_size > m:
        raise ValueError("Z support exceeds m")
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    outside_sum, outside_square = excess_moments(m, degrees)
    return {
        "edges": len(edges),
        "T": sum(degrees),
        "U": sum(value * value for value in degrees),
        "outside_count": V - m,
        "outside_sum": outside_sum,
        "outside_square_sum": outside_square,
        "integer_minimum": integer_minimum_square_sum(V - m, outside_sum),
        "histogram_count": count_bounded_degree_histograms(
            V - m, outside_sum, outside_square, K
        ),
    }


def expected_regular_gram_eigenvalue(m: int, induced_eigenvalue: int | Fraction) -> Fraction:
    """Gram eigenvalue on a D-eigenvector perpendicular to 1."""
    theta = Fraction(induced_eigenvalue)
    return Fraction(12) - theta - theta * theta


def regular_principal_gram_eigenvalue(m: int, degree: int = 6) -> int:
    """Gram eigenvalue on 1 when D is degree-regular."""
    return 12 - degree + 2 * m - degree * degree


def main() -> None:
    rectangle_checks = rectangle_identity_exhaustive()
    parameters = adjacent_edge_rectangle_parameters()
    crossing_shapes = {
        f"{rows}x{columns}": enumerate_crossing_shapes(rows, columns)
        for rows, columns in ((1, 4), (2, 2), (2, 3), (3, 3), (4, 4))
    }
    z_types = enumerate_z_types()
    z_rows = {name: z_moment_row(name) for name in z_types}
    print(f"rectangle_identity_cases={rectangle_checks}")
    print(f"rectangle_local={parameters}")
    print(f"component_partitions_24={rectangle_component_lengths(24)}")
    print(f"crossing_shapes={crossing_shapes}")
    print(f"z_types={z_types}")
    print(f"z_rows={z_rows}")
    print(
        "regular_gram="
        f"A_principal:{regular_principal_gram_eigenvalue(27)},"
        f"B_empty_principal:{regular_principal_gram_eigenvalue(30)},"
        "restricted:(3-theta)(theta+4)"
    )


if __name__ == "__main__":
    main()
