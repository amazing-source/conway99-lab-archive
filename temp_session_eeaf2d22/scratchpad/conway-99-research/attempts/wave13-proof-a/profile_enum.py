"""Exact active-q and local point-pattern arithmetic for Wave 13 proof A.

This is an exploratory standard-library checker.  It does not encode a
completed strongly regular graph and its output is not a nonexistence
certificate.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations_with_replacement, product


def partitions(total: int, length: int, lower: int, upper: int):
    for values in combinations_with_replacement(range(lower, upper + 1), length):
        if sum(values) == total:
            yield values


def active_profiles() -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    result = []
    for r in range(1, 16):
        upper = (r - 1) // 3
        if upper < 2:
            continue
        for q in partitions(30, r, 2, upper):
            kdeg = tuple(sorted((r - 1 - 3 * value for value in q), reverse=True))
            result.append((r, q, kdeg))
    return result


def local_size_patterns(k_degree: int, max_size: int):
    """Three non-singleton point sizes through one active label."""
    for sizes in combinations_with_replacement(range(2, max_size + 1), 3):
        if sum(size - 1 for size in sizes) <= k_degree:
            yield sizes


def size_incidence_solutions(r: int, max_size: int):
    """All multisets of point sizes whose total incidence is 3r."""
    target = 3 * r
    sizes = tuple(range(2, max_size + 1))
    bounds = [target // size for size in sizes]
    for counts in product(*(range(bound + 1) for bound in bounds)):
        if sum(size * count for size, count in zip(sizes, counts)) == target:
            yield dict(zip(sizes, counts))


def size3_local_modes():
    """Local F/U modes around a size-three point in the r=15 profile.

    For root r, ``a_r`` counts other size-three points whose crossing with
    the distinguished point is empty in L (and hence a full 2x2 in U).
    """
    records = []
    for t in combinations_with_replacement(range(1, 4), 3):
        for a in product(*(range(value) for value in t)):
            forced_u = tuple(
                sum(3 - t[j] + 2 * a[j] for j in range(3) if j != i)
                for i in range(3)
            )
            capacity = tuple(5 - value for value in t)
            full_l = sum((t[i] - 1) - a[i] for i in range(3))
            if all(used <= cap for used, cap in zip(forced_u, capacity)):
                if 4 * full_l <= 12:
                    records.append((t, a, forced_u, capacity, full_l))
    return records


def main() -> None:
    profiles = active_profiles()
    print(f"raw_profiles={len(profiles)}")
    for r, q, kdeg in profiles:
        counter_q = Counter(q)
        counter_k = Counter(kdeg)
        print(
            f"r={r:2d} q={dict(sorted(counter_q.items()))} "
            f"Kdeg={dict(sorted(counter_k.items()))} "
            f"minK={min(kdeg)}"
        )
    survivors = [record for record in profiles if min(record[2]) >= 3]
    print(f"degree_at_least_three_survivors={len(survivors)}")
    for r, q, kdeg in survivors:
        print(f"  r={r}, q={q}, Kdeg={kdeg}")

    for r, degree, max_size in ((15, 8, 5), (14, 7, 4), (14, 4, 4)):
        print(
            f"local_patterns(r={r}, Kdegree={degree})="
            f"{list(local_size_patterns(degree, max_size))}"
        )

    for r, max_size in ((15, 5), (14, 4)):
        solutions = list(size_incidence_solutions(r, max_size))
        print(f"point_size_incidence_solutions(r={r})={len(solutions)}")
        for solution in solutions:
            print(f"  {solution}")

    local_modes = size3_local_modes()
    grouped = Counter(t for t, *_ in local_modes)
    print(f"r15_size3_feasible_t_profiles={dict(sorted(grouped.items()))}")
    for record in local_modes:
        print(f"  t={record[0]} a={record[1]} U={record[2]}/{record[3]} fullL={record[4]}")


if __name__ == "__main__":
    main()
