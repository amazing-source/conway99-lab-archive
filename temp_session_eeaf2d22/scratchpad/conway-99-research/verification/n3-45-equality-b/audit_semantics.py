#!/usr/bin/env python3
"""Independent finite checks for the Wave 13 n3=45 semantic audit.

This program intentionally uses only the Python standard library and does not
import the discovery implementation or the first verifier's implementation.
It checks the finite arithmetic that accompanies the human semantic proof:
active profiles, rooted size-three modes, all small labeled crossing graphs,
the t=3 parity obstruction, and the open-neighborhood injection for
L(K_3,3).  It also emits two minimal motifs showing why two commonly elided
premises (two-sided crossing degrees and the common-point rule) are necessary.
"""

from __future__ import annotations

from itertools import combinations, product


def active_profiles() -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    found: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = []

    def extend(
        r: int, cap: int, remaining_count: int, remaining_sum: int,
        minimum: int, prefix: tuple[int, ...]
    ) -> None:
        if remaining_count == 0:
            if remaining_sum == 0:
                degrees = tuple(r - 1 - 3 * q for q in prefix)
                found.append((r, prefix, degrees))
            return
        for q in range(minimum, cap + 1):
            rest = remaining_sum - q
            if rest < q * (remaining_count - 1):
                break
            if rest > cap * (remaining_count - 1):
                continue
            extend(r, cap, remaining_count - 1, rest, q, prefix + (q,))

    for r in range(1, 16):
        extend(r, (r - 1) // 3, r, 30, 2, ())
    return found


def r15_root_modes() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    modes: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for t in product(range(1, 4), repeat=3):
        for a in product(*(range(value) for value in t)):
            forced_u = tuple(
                sum(3 - t[j] + 2 * a[j] for j in range(3) if j != i)
                for i in range(3)
            )
            capacity = tuple(5 - value for value in t)
            full_crossings = sum(t[i] - 1 - a[i] for i in range(3))
            if (
                all(forced_u[i] <= capacity[i] for i in range(3))
                and full_crossings <= 3
            ):
                modes.append((t, a))
    return modes


def r14_ordinary_modes() -> list[tuple[int, ...]]:
    modes: list[tuple[int, ...]] = []
    for t in product(range(1, 4), repeat=3):
        if sum(t) > 8:
            continue
        if all(
            4 - t[i] >= sum(3 - t[j] for j in range(3) if j != i)
            for i in range(3)
        ):
            modes.append(t)
    return modes


def crossing_edge_counts(left: int, right: int) -> set[int]:
    """Simple bipartite masks with every row/column degree in {0,2}."""
    counts: set[int] = set()
    for mask in range(1 << (left * right)):
        rows = [0] * left
        columns = [0] * right
        for i in range(left):
            for j in range(right):
                if mask & (1 << (i * right + j)):
                    rows[i] += 1
                    columns[j] += 1
        if all(value in (0, 2) for value in rows + columns):
            counts.add(sum(rows))
    return counts


def k33_line_open_neighborhoods() -> dict[tuple[int, int], frozenset]:
    cells = tuple(product(range(3), repeat=2))
    neighborhoods: dict[tuple[int, int], frozenset] = {}
    for cell in cells:
        neighborhoods[cell] = frozenset(
            other
            for other in cells
            if other != cell
            and (other[0] == cell[0] or other[1] == cell[1])
        )
    return neighborhoods


def intersection_label(left: frozenset, right: frozenset) -> object:
    overlap = left & right
    assert len(overlap) == 1
    return next(iter(overlap))


def main() -> None:
    profiles = active_profiles()
    expected_profiles = {
        (15, (2,) * 15),
        (14, (2,) * 13 + (4,)),
        (14, (2,) * 12 + (3, 3)),
        (13, (2,) * 11 + (4, 4)),
        (13, (2,) * 10 + (3, 3, 4)),
        (13, (2,) * 9 + (3,) * 4),
        (12, (2,) * 6 + (3,) * 6),
        (11, (2,) * 3 + (3,) * 8),
        (10, (3,) * 10),
    }
    assert {(r, q) for r, q, _ in profiles} == expected_profiles
    degree_feasible = [
        (r, q, degrees)
        for r, q, degrees in profiles
        if min(degrees) >= 3
    ]
    assert [(r, q) for r, q, _ in degree_feasible] == [
        (13, (2,) * 9 + (3,) * 4),
        (14, (2,) * 12 + (3, 3)),
        (15, (2,) * 15),
    ]

    mixed_modes = r14_ordinary_modes()
    assert set(mixed_modes) == {
        (2, 2, 2),
        (2, 3, 3),
        (3, 2, 3),
        (3, 3, 2),
    }

    labeled_modes = r15_root_modes()
    assert len(labeled_modes) == 8
    canonical_modes = {
        tuple(sorted(zip(t, a)))
        for t, a in labeled_modes
    }
    assert canonical_modes == {
        ((1, 0), (1, 0), (1, 0)),
        ((1, 0), (2, 0), (2, 0)),
        ((2, 0), (2, 0), (2, 0)),
        ((2, 0), (2, 0), (3, 1)),
    }

    # If t_x=3, each of the three size-three points through x would have
    # exactly one empty crossing at x.  No simple graph on three vertices has
    # degree sequence (1,1,1).
    one_regular_graphs = 0
    vertex_pairs = tuple(combinations(range(3), 2))
    for mask in range(1 << len(vertex_pairs)):
        degree = [0, 0, 0]
        for index, (u, v) in enumerate(vertex_pairs):
            if mask & (1 << index):
                degree[u] += 1
                degree[v] += 1
        if degree == [1, 1, 1]:
            one_regular_graphs += 1
    assert one_regular_graphs == 0

    disjoint_crossings = {
        (2, 2): crossing_edge_counts(2, 2),
        (2, 3): crossing_edge_counts(2, 3),
        (3, 2): crossing_edge_counts(3, 2),
        (3, 3): crossing_edge_counts(3, 3),
    }
    assert disjoint_crossings == {
        (2, 2): {0, 4},
        (2, 3): {0, 4},
        (3, 2): {0, 4},
        (3, 3): {0, 4, 6},
    }
    meeting_crossings = {
        (2, 2): crossing_edge_counts(1, 1),
        (2, 3): crossing_edge_counts(1, 2),
        (3, 2): crossing_edge_counts(2, 1),
        (3, 3): crossing_edge_counts(2, 2),
    }
    assert meeting_crossings == {
        (2, 2): {0},
        (2, 3): {0},
        (3, 2): {0},
        (3, 3): {0, 4},
    }

    # After mode 111 and t=3 are removed, a size-three point has mode 122 or
    # 222.  Its mandatory full meeting crossings consume 8 or 12 of its
    # fixed sum 12, so the sole six-edge crossing type has no capacity.
    remaining_capacity = {"122": 12 - 2 * 4, "222": 12 - 3 * 4}
    assert remaining_capacity == {"122": 4, "222": 0}
    assert all(capacity < 6 for capacity in remaining_capacity.values())
    final_h_degrees = {0, 4}
    assert (2 * 45) % 4 == 2

    neighborhoods = k33_line_open_neighborhoods()
    assert len(neighborhoods) == 9
    assert len(set(neighborhoods.values())) == 9

    # Diagnostic 1: one-sided checking is too weak.  A full 1-by-2 row has
    # allowed row degree two but forbidden column degrees one.
    one_by_two = ((1, 1),)
    assert [sum(row) for row in one_by_two] == [2]
    assert [
        sum(one_by_two[i][j] for i in range(1)) for j in range(2)
    ] == [1, 1]

    # Diagnostic 2: linearity alone does not separate petals or put a forced
    # K-edge outside F.  These three linear sets form exactly the prohibited
    # three-point (Berge-triangle) motif; the third set owns the would-be
    # forced cross-pair {1,3}.
    root = frozenset({0, 1, 2})
    petal = frozenset({0, 3})
    attempted_owner = frozenset({1, 3})
    motif = (root, petal, attempted_owner)
    assert all(len(a & b) == 1 for a, b in combinations(motif, 2))
    assert {
        intersection_label(a, b) for a, b in combinations(motif, 2)
    } == {0, 1, 3}

    print("PASS independent n3=45 arithmetic and crossing semantics")
    print(f"active_profiles={len(profiles)}")
    print(f"degree_feasible_profiles={len(degree_feasible)}")
    print(f"r14_labeled_modes={len(mixed_modes)}")
    print(f"r15_labeled_modes={len(labeled_modes)}")
    print(f"t3_one_regular_graphs={one_regular_graphs}")
    print(f"disjoint_crossing_counts={disjoint_crossings}")
    print(f"meeting_crossing_counts={meeting_crossings}")
    print("line_K33_open_neighborhoods_distinct=9")
    print(f"post_capacity_H_degrees={sorted(final_h_degrees)}")
    print("handshake_residue_mod4=2")
    print("diagnostic_one_sided_crossing=REJECTED")
    print("diagnostic_common_point_omission=COUNTERMODEL")


if __name__ == "__main__":
    main()
