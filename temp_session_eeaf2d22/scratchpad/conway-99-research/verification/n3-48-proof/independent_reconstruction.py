"""Independent pre-inspection arithmetic for the Wave 14 n3=48 proof audit."""

from itertools import combinations_with_replacement, permutations, product


def active_profiles():
    profiles = []
    for r in range(1, 17):
        qmax = (r - 1) // 3
        if qmax < 2:
            continue
        for profile in combinations_with_replacement(range(2, qmax + 1), r):
            if sum(profile) == 32:
                degrees = tuple(sorted(r - 1 - 3 * q for q in profile))
                profiles.append((r, profile, degrees))
    return profiles


def raw_size_three_modes():
    """Modes surviving only the three cyclic U-capacity inequalities."""
    modes = []
    for mode in combinations_with_replacement(range(1, 4), 3):
        if all(mode[i] <= mode[(i + 1) % 3] + mode[(i + 2) % 3] for i in range(3)):
            modes.append(mode)
    return modes


def aligned_size_three_states(k_degrees, q_values):
    states = []
    fixed_sum = 2 * sum(q_values)
    for t in product(range(1, 4), repeat=3):
        for empty in product(*(range(value) for value in t)):
            u_capacity = tuple(k_degrees[i] - (3 + t[i]) for i in range(3))
            forced = tuple(
                sum(
                    3 - t[j] + 2 * empty[j]
                    for j in range(3)
                    if j != i
                )
                for i in range(3)
            )
            full = sum(t[i] - 1 - empty[i] for i in range(3))
            if min(u_capacity) < 0:
                continue
            if any(forced[i] > u_capacity[i] for i in range(3)):
                continue
            if 4 * full > fixed_sum:
                continue
            states.append((t, empty, forced, u_capacity, full))
    return states


def symmetric_mode_representatives(states):
    representatives = set()
    for t, empty, *_rest in states:
        aligned = tuple((t[i], empty[i]) for i in range(3))
        representatives.add(
            min(tuple(aligned[i] for i in perm) for perm in permutations(range(3)))
        )
    return sorted(representatives)


def main():
    profiles = active_profiles()
    assert len(profiles) == 12
    for r, profile, degrees in profiles:
        print(f"r={r}: q={profile}; dK={degrees}")

    modes = raw_size_three_modes()
    # This is deliberately a pre-submission audit target: the inherited
    # capacity inequalities alone leave nine modes, not eight.
    assert modes == [
        (1, 1, 1),
        (1, 1, 2),
        (1, 2, 2),
        (1, 2, 3),
        (1, 3, 3),
        (2, 2, 2),
        (2, 2, 3),
        (2, 3, 3),
        (3, 3, 3),
    ]
    print("raw size-three modes:", modes)

    r16_states = aligned_size_three_states((9, 9, 9), (2, 2, 2))
    r16_modes = symmetric_mode_representatives(r16_states)
    assert len(r16_states) == 32
    assert len(r16_modes) == 10
    assert sum(sum(pair[0] - 1 - pair[1] for pair in mode) == 0 for mode in r16_modes) == 2
    print("aligned r16 (t,empty) modes:", r16_modes)

    # A size-three point with one or two special roots in the mixed r=15
    # profile has no state even before the later size-two modulus argument.
    assert aligned_size_three_states((5, 8, 8), (3, 2, 2)) == []
    assert aligned_size_three_states((5, 5, 8), (3, 3, 2)) == []
    print("r15 special-root size-three states: none")


if __name__ == "__main__":
    main()
