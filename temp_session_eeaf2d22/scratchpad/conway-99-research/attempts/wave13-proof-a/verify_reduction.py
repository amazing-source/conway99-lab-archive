"""Deterministic arithmetic checks for the Wave 13 proof-A reduction.

This checker verifies the finite integer enumerations used in the prose.  The
structural graph-theoretic implications remain human proofs; this program is a
regression companion, not a standalone Conway-99 certificate.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations_with_replacement, product


def partitions(total: int, length: int, lower: int, upper: int):
    for values in combinations_with_replacement(range(lower, upper + 1), length):
        if sum(values) == total:
            yield values


def active_profiles():
    records = []
    for r in range(1, 16):
        upper = (r - 1) // 3
        if upper < 2:
            continue
        for q in partitions(30, r, 2, upper):
            k_degrees = tuple(r - 1 - 3 * value for value in q)
            records.append((r, q, k_degrees))
    return records


def size3_modes_r15():
    """All sorted t profiles and empty-crossing counts surviving capacities."""
    modes = []
    for t in combinations_with_replacement(range(1, 4), 3):
        for empty in product(*(range(value) for value in t)):
            forced_u = tuple(
                sum(
                    3 - t[j] + 2 * empty[j]
                    for j in range(3)
                    if j != i
                )
                for i in range(3)
            )
            u_capacity = tuple(5 - value for value in t)
            full_l = sum(t[i] - 1 - empty[i] for i in range(3))
            if all(a <= b for a, b in zip(forced_u, u_capacity)):
                if 4 * full_l <= 12:
                    modes.append((t, empty, forced_u, u_capacity, full_l))
    return modes


def main() -> None:
    profiles = active_profiles()
    assert len(profiles) == 9
    raw = [
        (r, dict(sorted(Counter(q).items())), dict(sorted(Counter(k).items())))
        for r, q, k in profiles
    ]
    expected_raw = [
        (10, {3: 10}, {0: 10}),
        (11, {2: 3, 3: 8}, {1: 8, 4: 3}),
        (12, {2: 6, 3: 6}, {2: 6, 5: 6}),
        (13, {2: 11, 4: 2}, {0: 2, 6: 11}),
        (13, {2: 10, 3: 2, 4: 1}, {0: 1, 3: 2, 6: 10}),
        (13, {2: 9, 3: 4}, {3: 4, 6: 9}),
        (14, {2: 13, 4: 1}, {1: 1, 7: 13}),
        (14, {2: 12, 3: 2}, {4: 2, 7: 12}),
        (15, {2: 15}, {8: 15}),
    ]
    assert raw == expected_raw

    degree_survivors = [
        record for record in raw if min(record[2]) >= 3
    ]
    assert degree_survivors == [
        (13, {2: 9, 3: 4}, {3: 4, 6: 9}),
        (14, {2: 12, 3: 2}, {4: 2, 7: 12}),
        (15, {2: 15}, {8: 15}),
    ]

    modes = size3_modes_r15()
    assert modes == [
        ((1, 1, 1), (0, 0, 0), (4, 4, 4), (4, 4, 4), 0),
        ((1, 2, 2), (0, 0, 0), (2, 3, 3), (4, 3, 3), 2),
        ((2, 2, 2), (0, 0, 0), (2, 2, 2), (3, 3, 3), 3),
        ((2, 2, 3), (0, 0, 1), (3, 3, 2), (3, 3, 2), 3),
    ]

    # The final contradiction once every nonzero H degree is forced to be four.
    assert 2 * 45 == 90
    assert (2 * 45) % 4 == 2

    print("PASS")
    print(f"raw_active_profiles={len(raw)}")
    print(f"degree_at_least_three_profiles={len(degree_survivors)}")
    print("degree_three_lemma_leaves=r14_mixed,r15_all_q2")
    print("r15_size3_modes=111,122,222,223")
    print("post_structural_reduction_nonzero_H_degrees={4}")
    print("handshake=90_not_divisible_by_4")


if __name__ == "__main__":
    main()
