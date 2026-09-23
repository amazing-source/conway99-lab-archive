#!/usr/bin/env python3
"""Exact finite arithmetic used in the Wave 14 proof-A report.

This script deliberately checks only consequences stated in the report:

* partitions of sum(q)=32 under q>=2 and 3q<=r-1;
* the inherited three-non-singleton-point degree filter d_K>=3;
* the inherited obstruction d_K != 3;
* necessary local (t,a) modes around a size-three point for each surviving
  profile, using literal U-degree inequalities and fixed-point capacity; and
* possible sizes of a simple bipartite crossing whose row and column degrees
  all lie in {0,2}.

It is a regression checker, not a Conway-99 certificate.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product


def partitions(total: int, length: int, minimum: int, maximum: int):
    """Yield nondecreasing integer tuples with the stated bounds and sum."""

    def rec(prefix: tuple[int, ...], remaining: int, slots: int, low: int):
        if slots == 0:
            if remaining == 0:
                yield prefix
            return
        if remaining < slots * low or remaining > slots * maximum:
            return
        for value in range(low, maximum + 1):
            if value * slots > remaining:
                break
            yield from rec(prefix + (value,), remaining - value, slots - 1, value)

    yield from rec((), total, length, minimum)


def active_profiles():
    raw = []
    for r in range(1, 17):
        qmax = (r - 1) // 3
        if qmax < 2:
            continue
        for q in partitions(32, r, 2, qmax):
            dk = tuple(r - 1 - 3 * value for value in q)
            raw.append((r, q, dk))
    degree_feasible = [row for row in raw if min(row[2]) >= 3]
    no_degree_three = [row for row in degree_feasible if 3 not in row[2]]
    return raw, degree_feasible, no_degree_three


def compact(values: tuple[int, ...]) -> str:
    return " ".join(
        str(value) if count == 1 else f"{value}^{count}"
        for value, count in sorted(Counter(values).items())
    )


def local_modes(base_degrees: tuple[int, int, int], q_values: tuple[int, int, int]):
    """Enumerate necessary local modes at a size-three point.

    ``base_degrees[i]`` is d_K at root i.  ``t_i`` counts size-three points
    through root i.  ``a_i`` counts the other size-three co-points at root i
    whose external 2-by-2 L-crossing with the distinguished point is empty.

    Every singleton petal based at j forces one distinct U-neighbour at each
    other root.  Every empty size-three crossing based at j forces two.
    Full crossings are distinct actual graph neighbours and contribute four
    to the fixed-point sum 2*sum(q_values).
    """

    states = []
    fixed_sum = 2 * sum(q_values)
    for t in product(range(1, 4), repeat=3):
        if any(3 + t[i] > base_degrees[i] for i in range(3)):
            continue
        for a in product(*(range(ti) for ti in t)):
            forced = tuple(
                sum(3 - t[j] + 2 * a[j] for j in range(3) if j != i)
                for i in range(3)
            )
            capacity = tuple(base_degrees[i] - 3 - t[i] for i in range(3))
            if any(forced[i] > capacity[i] for i in range(3)):
                continue
            full = sum(t[i] - 1 - a[i] for i in range(3))
            if 4 * full > fixed_sum:
                continue
            states.append(
                {
                    "t": t,
                    "a": a,
                    "forced": forced,
                    "capacity": capacity,
                    "full": full,
                    "fixed_sum": fixed_sum,
                }
            )
    return states


def canonical_modes(states, root_types: tuple[str, str, str]):
    """Canonicalize only by permutations preserving the supplied root types."""

    allowed = [
        permutation
        for permutation in product(range(3), repeat=3)
        if len(set(permutation)) == 3
        and all(root_types[i] == root_types[permutation[i]] for i in range(3))
    ]
    representatives = {}
    for state in states:
        aligned = tuple((state["t"][i], state["a"][i]) for i in range(3))
        orbit = [
            tuple(aligned[permutation[i]] for i in range(3))
            for permutation in allowed
        ]
        key = min(orbit)
        representatives.setdefault(key, state)
    return representatives


def crossing_sizes(left: int, right: int):
    """All edge counts with every row and column degree in {0,2}."""

    pairs = [(i, j) for i in range(left) for j in range(right)]
    sizes = set()
    for mask in range(1 << len(pairs)):
        row = [0] * left
        col = [0] * right
        edges = 0
        for bit, (i, j) in enumerate(pairs):
            if mask >> bit & 1:
                row[i] += 1
                col[j] += 1
                edges += 1
        if all(value in (0, 2) for value in row + col):
            sizes.add(edges)
    return tuple(sorted(sizes))


def main():
    raw, degree_feasible, surviving = active_profiles()
    assert len(raw) == 12
    assert len(degree_feasible) == 4
    assert len(surviving) == 3
    expected = {
        (16, (2,) * 16, (9,) * 16),
        (15, (2,) * 13 + (3,) * 2, (8,) * 13 + (5,) * 2),
        (14, (2,) * 10 + (3,) * 4, (7,) * 10 + (4,) * 4),
    }
    assert set(surviving) == expected

    print("ACTIVE PROFILES")
    for index, (r, q, dk) in enumerate(raw, 1):
        flags = []
        if min(dk) < 3:
            flags.append("dK<3")
        elif 3 in dk:
            flags.append("dK=3")
        else:
            flags.append("survives")
        print(
            f"{index:02d} r={r:2d} q=({compact(q)}) "
            f"dK=({compact(dk)}) status={','.join(flags)}"
        )

    print("\nR15 SIZE-THREE LOCAL MODES")
    cases = {
        "OOO": ((8, 8, 8), (2, 2, 2)),
        "SOO": ((5, 8, 8), (3, 2, 2)),
        "SSO": ((5, 5, 8), (3, 3, 2)),
    }
    for name, (degrees, q_values) in cases.items():
        states = local_modes(degrees, q_values)
        reps = canonical_modes(states, tuple(name))
        print(f"{name}: labeled={len(states)} canonical={len(reps)}")
        for key in sorted(reps):
            t = tuple(pair[0] for pair in key)
            a = tuple(pair[1] for pair in key)
            forced = tuple(
                sum(3 - t[j] + 2 * a[j] for j in range(3) if j != i)
                for i in range(3)
            )
            capacity = tuple(degrees[i] - 3 - t[i] for i in range(3))
            full = sum(t[i] - 1 - a[i] for i in range(3))
            print(
                f"  aligned={key} forced={forced} "
                f"capacity={capacity} full={full} "
                f"fixed={2 * sum(q_values)}"
            )

    print("\nR16 SIZE-THREE LOCAL MODES")
    states = local_modes((9, 9, 9), (2, 2, 2))
    reps = canonical_modes(states, ("O", "O", "O"))
    print(f"OOO: labeled={len(states)} canonical={len(reps)}")
    for key in sorted(reps):
        t = tuple(pair[0] for pair in key)
        a = tuple(pair[1] for pair in key)
        forced = tuple(
            sum(3 - t[j] + 2 * a[j] for j in range(3) if j != i)
            for i in range(3)
        )
        capacity = tuple(6 - value for value in t)
        full = sum(t[i] - 1 - a[i] for i in range(3))
        print(
            f"  aligned={key} forced={forced} "
            f"capacity={capacity} full={full} fixed=12"
        )

    print("\nCROSSING SIZES")
    for left, right in combinations(range(1, 5), 2):
        print(f"{left}x{right}: {crossing_sizes(left, right)}")
    for size in range(1, 5):
        print(f"{size}x{size}: {crossing_sizes(size, size)}")


if __name__ == "__main__":
    main()
