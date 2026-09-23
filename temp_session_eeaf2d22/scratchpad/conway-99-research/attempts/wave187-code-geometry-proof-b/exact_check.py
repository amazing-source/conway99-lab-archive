"""Exact rational hostile control for the Wave 187 code-geometry lane."""

from fractions import Fraction
from math import comb, factorial


N = 231
CODE_SIZE = 3**11


def x_value(weight: int) -> Fraction:
    return Fraction(2 * N - 3 * weight, 2)


def complete_pair_column(ones: int, twos: int) -> tuple[Fraction, ...]:
    weight = ones + twos
    difference = ones - twos
    x = x_value(weight)
    return (
        Fraction(1),
        2 * x,
        x * x - x - Fraction(3, 4) * difference * difference,
        2 * x * x + Fraction(3, 2) * difference * difference - 2 * N,
        x**3
        - x**2
        - 2 * (N - 1) * x
        + Fraction(3, 4) * (x + 1) * difference * difference,
        x**3 / 3
        - x**2
        + Fraction(2 * N, 3)
        - Fraction(3, 4) * (x + 1) * difference * difference,
    )


Eisenstein = tuple[int, int]
ONE: Eisenstein = (1, 0)
OMEGA: Eisenstein = (0, 1)
OMEGA2: Eisenstein = (-1, -1)


def eadd(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    return left[0] + right[0], left[1] + right[1]


def emul(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    p, q = left
    r, s = right
    return p * r - q * s, p * s + q * r - q * s


def epow(value: Eisenstein, exponent: int) -> Eisenstein:
    result = ONE
    for _ in range(exponent):
        result = emul(result, value)
    return result


def group_term(
    count: int,
    ones: int,
    twos: int,
    one_phase: Eisenstein,
    two_phase: Eisenstein,
) -> Eisenstein:
    coefficient = comb(count, ones) * comb(count - ones, twos)
    phase = emul(epow(one_phase, ones), epow(two_phase, twos))
    return coefficient * phase[0], coefficient * phase[1]


def complete_krawtchouk(
    symbol_ones: int,
    symbol_twos: int,
    dual_ones: int,
    dual_twos: int,
) -> Eisenstein:
    groups = (
        (N - symbol_ones - symbol_twos, ONE, ONE),
        (symbol_ones, OMEGA, OMEGA2),
        (symbol_twos, OMEGA2, OMEGA),
    )
    result: Eisenstein = (0, 0)
    for r0 in range(dual_ones + 1):
        for r1 in range(dual_ones - r0 + 1):
            r = (r0, r1, dual_ones - r0 - r1)
            for s0 in range(dual_twos + 1):
                for s1 in range(dual_twos - s0 + 1):
                    s = (s0, s1, dual_twos - s0 - s1)
                    if any(
                        r[index] + s[index] > groups[index][0]
                        for index in range(3)
                    ):
                        continue
                    term = ONE
                    for index, (count, one_phase, two_phase) in enumerate(groups):
                        term = emul(
                            term,
                            group_term(
                                count,
                                r[index],
                                s[index],
                                one_phase,
                                two_phase,
                            ),
                        )
                    result = eadd(result, term)
    return result


def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** h
        * 2 ** (degree - h)
        * comb(weight, h)
        * comb(N - weight, degree - h)
        for h in range(degree + 1)
    )


def falling_binomial(value: int, degree: int) -> int:
    return comb(value, degree)


# Scalar-pair masses, already resolved by ambient quadratic type.  A cell
# (a,b) represents the two word compositions (a,b) and (b,a).
TYPE_CELL_MASSES = {
    "singular": {
        (0, 81): Fraction(1, 1700),
        (6, 24): Fraction(45334, 697),
        (36, 162): Fraction(231),
        (72, 81): Fraction(2142276162781519, 576217218500),
        (75, 78): Fraction(2368455943056339, 144054304625),
        (78, 78): Fraction(226718, 25),
    },
    "norm_plus": {
        (0, 120): Fraction(1663, 84),
        (0, 228): Fraction(81673674496579188347, 3569527376475060000),
        (33, 195): Fraction(1459598804117088331, 100114860628282500),
        (75, 78): Fraction(12502563, 425),
        (102, 102): Fraction(160341, 952),
        (114, 114): Fraction(59981815805188283, 23787060262812000),
    },
    "norm_minus": {
        (0, 114): Fraction(445838499187, 2044229600),
        (0, 120): Fraction(957613632057, 3212360800),
        (72, 78): Fraction(2033920953923, 292032800),
        (78, 78): Fraction(8822683455071, 408845920),
        (108, 111): Fraction(481518113773, 1405407850),
    },
}

PAIR_MASSES: dict[tuple[int, int], Fraction] = {}
for type_cells in TYPE_CELL_MASSES.values():
    for cell, mass in type_cells.items():
        PAIR_MASSES[cell] = PAIR_MASSES.get(cell, Fraction()) + mass


def check_complete_strength_three() -> None:
    targets = (
        Fraction((CODE_SIZE - 1) // 2),
        Fraction(-N),
        Fraction(-comb(N, 2)),
        Fraction(-N * (N - 1)),
        Fraction(-3 * comb(N, 3)),
        Fraction(-comb(N, 3)),
    )
    totals = tuple(
        sum(
            mass * complete_pair_column(*cell)[index]
            for cell, mass in PAIR_MASSES.items()
        )
        for index in range(6)
    )
    assert totals == targets
    assert TYPE_CELL_MASSES["singular"][(36, 162)] == 231


def complete_dual_coefficient(dual_ones: int, dual_twos: int) -> Fraction:
    zero_word = Fraction(
        factorial(N)
        // (
            factorial(dual_ones)
            * factorial(dual_twos)
            * factorial(N - dual_ones - dual_twos)
        )
    )
    numerator = zero_word
    for (ones, twos), mass in PAIR_MASSES.items():
        forward = complete_krawtchouk(
            ones, twos, dual_ones, dual_twos
        )
        reverse = complete_krawtchouk(
            twos, ones, dual_ones, dual_twos
        )
        assert forward[1] + reverse[1] == 0
        numerator += mass * (forward[0] + reverse[0])
    return numerator / CODE_SIZE


def check_complete_through_degree_six() -> None:
    degree_four = [
        complete_dual_coefficient(ones, 4 - ones) for ones in range(5)
    ]
    assert degree_four == [
        0,
        0,
        Fraction(126079749915623, 131414760),
        0,
        0,
    ]
    for degree in (5, 6):
        assert all(
            complete_dual_coefficient(ones, degree - ones) >= 0
            for ones in range(degree + 1)
        )

    # This particular sparse control stops here.  The negative coefficient
    # records the exact boundary; it is not evidence that every control fails.
    assert complete_dual_coefficient(7, 0) == Fraction(
        -10151603437954385741, 508426957500
    )


def ordinary_enumerator() -> tuple[dict[int, Fraction], list[Fraction]]:
    primal = {0: Fraction(1)}
    for cell, mass in PAIR_MASSES.items():
        weight = sum(cell)
        primal[weight] = primal.get(weight, Fraction()) + 2 * mass
    assert sum(primal.values()) == CODE_SIZE

    dual = [
        sum(
            multiplicity * krawtchouk(degree, weight)
            for weight, multiplicity in primal.items()
        )
        / CODE_SIZE
        for degree in range(N + 1)
    ]
    assert dual[:4] == [1, 0, 0, 0]
    assert all(value >= 0 for value in dual)
    assert all(dual[degree] >= primal.get(degree, 0) for degree in range(N + 1))
    assert dual[4] == Fraction(126079749915623, 131414760)
    assert sum(dual[4:10]) == Fraction(
        721437869830147204193861, 3066344400
    )
    assert dual[4] > 18018
    return primal, dual


# Projective ambient-point masses keyed by b_v, obtained from the typed
# composition table above.
TYPE_MASSES: dict[str, dict[int, Fraction]] = {}
for type_name, type_cells in TYPE_CELL_MASSES.items():
    masses: dict[int, Fraction] = {}
    for cell, mass in type_cells.items():
        b_value = N - sum(cell)
        masses[b_value] = masses.get(b_value, Fraction()) + mass
    TYPE_MASSES[type_name] = masses

TYPE_TARGETS = {
    "singular": (29524, 2273271, 87133200, 2233980128),
    "norm_plus": (29646, 2301453, 88521741, 2242872288),
    "norm_minus": (29403, 2245320, 85771224, 2174315184),
}


def check_quadratic_type_moments() -> None:
    by_weight = {}
    for cell, mass in PAIR_MASSES.items():
        b_value = N - sum(cell)
        by_weight[b_value] = by_weight.get(b_value, Fraction()) + mass

    all_b_values = set(by_weight)
    for masses in TYPE_MASSES.values():
        all_b_values.update(masses)
    for b_value in all_b_values:
        assert sum(
            masses.get(b_value, 0) for masses in TYPE_MASSES.values()
        ) == by_weight.get(b_value, 0)

    for type_name, masses in TYPE_MASSES.items():
        moments = tuple(
            sum(
                mass * falling_binomial(b_value, degree)
                for b_value, mass in masses.items()
            )
            for degree in range(4)
        )
        assert moments == TYPE_TARGETS[type_name]

    assert sum(target[3] for target in TYPE_TARGETS.values()) == (
        comb(N, 3) * 3280
    )


def check_triple_gram_types() -> None:
    # Counts by number of orthogonal pairs, with the no-orthogonal-pair
    # class split by the two Gram determinant/chirality types.
    triple_counts = {
        "three_orthogonal_pairs": 38192,
        "two_orthogonal_pairs": 0,
        "one_orthogonal_pair": 731808,
        "no_orthogonal_plus": 302968,
        "no_orthogonal_minus": 954827,
    }
    assert sum(triple_counts.values()) == comb(N, 3)
    assert (
        triple_counts["one_orthogonal_pair"]
        + 2 * triple_counts["two_orthogonal_pairs"]
        + 3 * triple_counts["three_orthogonal_pairs"]
        == 3696 * 229
    )
    assert (
        triple_counts["two_orthogonal_pairs"]
        + 3 * triple_counts["three_orthogonal_pairs"]
        == N * comb(32, 2)
    )

    complement_counts = {
        "three_orthogonal_pairs": (1093, 1215, 972),
        "two_orthogonal_pairs": (1093, 1134, 1053),
        "one_orthogonal_pair": (1093, 1134, 1053),
        "no_orthogonal_plus": (1066, 1107, 1107),
        "no_orthogonal_minus": (1120, 1080, 1080),
    }
    derived = tuple(
        sum(
            triple_counts[type_name] * complement_counts[type_name][index]
            for type_name in triple_counts
        )
        for index in range(3)
    )
    assert derived == tuple(
        TYPE_TARGETS[type_name][3]
        for type_name in ("singular", "norm_plus", "norm_minus")
    )


def main() -> None:
    check_complete_strength_three()
    check_complete_through_degree_six()
    primal, dual = ordinary_enumerator()
    check_quadratic_type_moments()
    check_triple_gram_types()
    print("exact rational hostile control: PASS")
    print("ordinary primal support:", sorted(primal.items()))
    print("B4:", dual[4])
    print("B4+...+B9:", sum(dual[4:10]))


if __name__ == "__main__":
    main()
