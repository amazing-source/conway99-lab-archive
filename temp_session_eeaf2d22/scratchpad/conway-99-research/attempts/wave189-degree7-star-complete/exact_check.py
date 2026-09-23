"""Exact Wave 189 checks: degree-seven star lift and cover separation."""

from fractions import Fraction
from math import comb, factorial


N = 231
CODE_SIZE = 3**11
C = 4158

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


# Each entry is a projective scalar-pair mass. A cell (a,b) represents both
# complete compositions (a,b) and (b,a).
TYPE_CELL_MASSES = {
    "singular": {
        (3, 48): Fraction(
            14411387513622084486137560717167,
            238565703738366727873918069925,
        ),
        (6, 21): Fraction(
            151404600678599425990047056072,
            6816162963953335082111944855,
        ),
        (75, 78): Fraction(
            135107001065053933560914945547542,
            6816162963953335082111944855,
        ),
        (78, 78): Fraction(
            2239849573793715820582869720469368,
            238565703738366727873918069925,
        ),
        (36, 162): Fraction(231),
    },
    "norm_plus": {
        (0, 114): Fraction(
            4371071297597773098616451861669,
            1860812489159260477416560945415,
        ),
        (60, 168): Fraction(
            9503222436749466474872623889296,
            238565703738366727873918069925,
        ),
        (75, 78): Fraction(
            89985254810156437594770425249185707,
            3101354148598767462360934909025,
        ),
        (78, 78): Fraction(
            259251231196287938560820521790174,
            524844548224406801322619753835,
        ),
        (111, 111): Fraction(
            149629196671953830109181890067814,
            1574533644673220403967859261505,
        ),
    },
    "norm_minus": {
        (0, 120): Fraction(
            246906431636332574951131748038647,
            477131407476733455747836139850,
        ),
        (18, 189): Fraction(
            45076153929327260205645509344698,
            906549674205793565920888665715,
        ),
        (45, 51): Fraction(
            11255851000663540594262153162806,
            143139422243020036724350841955,
        ),
        (75, 75): Fraction(
            82555981974216485422614393790451983,
            13598245113086903488813329985725,
        ),
        (78, 78): Fraction(
            427776412695344432838928992139975,
            19085256299069338229913445594,
        ),
        (108, 111): Fraction(
            2596662164776425133740490435333,
            9542628149534669114956722797,
        ),
    },
}

PAIR_MASSES: dict[tuple[int, int], Fraction] = {}
for type_cells in TYPE_CELL_MASSES.values():
    for cell, mass in type_cells.items():
        assert mass > 0
        PAIR_MASSES[cell] = PAIR_MASSES.get(cell, Fraction()) + mass


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


def local_vertex_profile(
    symbol_ones: int, symbol_twos: int
) -> dict[tuple[int, int], Fraction]:
    """Rational one-star profile using polygon vertices only."""
    x = Fraction(symbol_ones, 33)
    y = Fraction(symbol_twos, 33)
    if x == 0:
        first, second = (0, 6), (2, 5)
    elif 5 * y <= 2 * x:
        first, second = (6, 0), (5, 2)
    elif 2 * y <= 5 * x:
        first, second = (5, 2), (2, 5)
    else:
        first, second = (2, 5), (0, 6)

    determinant = first[0] * second[1] - first[1] * second[0]
    first_weight = Fraction(
        x * second[1] - y * second[0], determinant
    )
    second_weight = Fraction(
        first[0] * y - first[1] * x, determinant
    )
    zero_weight = 1 - first_weight - second_weight
    profile = {
        (0, 0): zero_weight,
        first: first_weight,
        second: second_weight,
    }
    assert all(weight >= 0 for weight in profile.values())
    assert sum(profile.values()) == 1
    assert sum(r * weight for (r, _), weight in profile.items()) == x
    assert sum(s * weight for (_, s), weight in profile.items()) == y
    return profile


def check_star_polygon_lift() -> None:
    allowed = {
        (r, s)
        for r in range(8)
        for s in range(8 - r)
        if (r - s) % 3 == 0
    }
    assert allowed == {
        (0, 0),
        (0, 3),
        (0, 6),
        (1, 1),
        (1, 4),
        (2, 2),
        (2, 5),
        (3, 0),
        (3, 3),
        (4, 1),
        (5, 2),
        (6, 0),
    }
    for (ones, twos), mass in PAIR_MASSES.items():
        for a, b in ((ones, twos), (twos, ones)):
            assert 2 * a + b <= 396
            assert a + 2 * b <= 396
            profile = local_vertex_profile(a, b)
            assert set(profile) <= allowed
            lifted = {
                pattern: 99 * mass * weight
                for pattern, weight in profile.items()
            }
            assert all(value >= 0 for value in lifted.values())
            assert sum(lifted.values()) == 99 * mass
            assert (
                sum(r * value for (r, _), value in lifted.items())
                == 3 * a * mass
            )
            assert (
                sum(s * value for (_, s), value in lifted.items())
                == 3 * b * mass
            )


def check_complete_rows() -> None:
    for degree in range(1, 4):
        assert all(
            complete_dual_coefficient(ones, degree - ones) == 0
            for ones in range(degree + 1)
        )
    degree_four = [
        complete_dual_coefficient(ones, 4 - ones) for ones in range(5)
    ]
    assert degree_four[0] == degree_four[1] == 0
    assert degree_four[2] > 0
    assert degree_four[3] == degree_four[4] == 0
    for degree in range(5, 8):
        assert all(
            complete_dual_coefficient(ones, degree - ones) >= 0
            for ones in range(degree + 1)
        )
    assert complete_dual_coefficient(7, 0) == 99
    assert complete_dual_coefficient(0, 7) == 99

    # Exact rows forced by the 693 adjacent and 4158 nonadjacent star pairs.
    assert complete_dual_coefficient(6, 6) >= 1386
    assert complete_dual_coefficient(12, 1) >= 693
    assert complete_dual_coefficient(1, 12) >= 693
    assert complete_dual_coefficient(14, 0) >= 4158
    assert complete_dual_coefficient(0, 14) >= 4158
    assert complete_dual_coefficient(7, 7) >= 8316


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
    assert all(
        dual[degree] >= primal.get(degree, 0)
        for degree in range(N + 1)
    )
    assert sum(dual[4:10]) == Fraction(
        303955951136016513013761953327276372487328891,
        2147091333645300550865262629325,
    )
    assert sum(dual[4:10]) >= 18018
    return primal, dual


TYPE_TARGETS_DEGREE_TWO = {
    "singular": (29524, 2273271, 87133200),
    "norm_plus": (29646, 2301453, 88521741),
    "norm_minus": (29403, 2245320, 85771224),
}


def type_moments(type_name: str) -> tuple[Fraction, ...]:
    return tuple(
        sum(
            mass * comb(N - sum(cell), degree)
            for cell, mass in TYPE_CELL_MASSES[type_name].items()
        )
        for degree in range(4)
    )


def check_quadratic_type_moments() -> None:
    for type_name, targets in TYPE_TARGETS_DEGREE_TWO.items():
        assert type_moments(type_name)[:3] == targets
    assert TYPE_CELL_MASSES["singular"][(36, 162)] == 231

    triple_counts = {
        "three_orthogonal_pairs": Fraction(
            7180647277052148633129515561210236,
            429418266729060110173052525865,
        ),
        "two_orthogonal_pairs": Fraction(
            9219695165864115094599706506625844,
            143139422243020036724350841955,
        ),
        "one_orthogonal_pair": Fraction(
            95530879146955891940574034442778796,
            143139422243020036724350841955,
        ),
        "no_orthogonal_plus": Fraction(
            151281112285105230584058395337270808,
            429418266729060110173052525865,
        ),
        "no_orthogonal_minus": Fraction(
            398058731681237045785655912939722711,
            429418266729060110173052525865,
        ),
    }
    assert all(value >= 0 for value in triple_counts.values())
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
            triple_counts[gram_type] * complement_counts[gram_type][index]
            for gram_type in triple_counts
        )
        for index in range(3)
    )
    assert derived == tuple(
        type_moments(type_name)[3]
        for type_name in ("singular", "norm_plus", "norm_minus")
    )


def check_cover_separation_arithmetic() -> None:
    # Coefficients in variables (n1,n2,n3,p2,p3).  The coupled packing
    # inequality gives
    #
    #   2Q >= 3n1+2n2+4n3+2p2+p3.
    #
    # Six copies split into seven private-incidence rows and the displayed
    # nonnegative remainder.
    private = (2, 2, 3, 1, 1)
    six_times_q_row = (18, 12, 24, 12, 6)
    remainder = (4, -2, 3, 5, -1)
    assert tuple(
        7 * private[index] + remainder[index]
        for index in range(5)
    ) == six_times_q_row

    # Sharp integer control for the exact coupled-packing variable system.
    n1, n2, n3, p2, p3 = 0, 0, 1386, 0, 4158
    r, h = 2079, 0
    private_labels = n1 + p2 + p3
    assignments = n1 + 2 * p2 + p3
    assert n1 + 2 * n2 + 3 * n3 >= C
    assert 2 * n1 + 2 * n2 + 3 * n3 + p2 + p3 >= 2 * C
    assert n2 <= p2 <= 2 * n2
    assert n3 <= p3 <= 3 * n3
    assert private_labels <= 2 * r + 3 * h
    assert assignments <= 2 * r + 3 * h
    assert n1 + n2 + 2 * n3 + r + 2 * h == 4851
    assert 12 * 4851 == 14 * C


def check_equality_face_cancellation() -> None:
    # Normalize the 3+6 leaf word to coefficient 2 on all nine coordinates.
    x_side = ("x0", "x1", "x2")
    y_side = ("y0", "y1", "y2", "y3", "y4", "y5")
    leaf_word = {coordinate: 2 for coordinate in x_side + y_side}

    # The checkerboard conic has one coefficient of each sign on either
    # star.  Its support is forced inside the leaf word on the equality face.
    conic = {"x0": 1, "x1": 2, "y0": 2, "y1": 1}
    assert set(conic) < set(leaf_word)

    def subtract_multiple(scalar: int) -> dict[str, int]:
        return {
            coordinate: (
                coefficient - scalar * conic.get(coordinate, 0)
            ) % 3
            for coordinate, coefficient in leaf_word.items()
        }

    for scalar in (1, 2):
        residual = subtract_multiple(scalar)
        residual_support = {
            coordinate
            for coordinate, coefficient in residual.items()
            if coefficient
        }
        assert len(residual_support & set(x_side)) == 2
        assert len(residual_support & set(y_side)) == 5
        assert not set(conic) <= residual_support


def main() -> None:
    check_star_polygon_lift()
    check_complete_rows()
    primal, dual = ordinary_enumerator()
    check_quadratic_type_moments()
    check_cover_separation_arithmetic()
    check_equality_face_cancellation()
    print("Wave 189 exact checks: PASS")
    print("primal support:", sorted(primal.items()))
    print("complete degree 7:", [
        complete_dual_coefficient(ones, 7 - ones)
        for ones in range(8)
    ])
    print("ordinary B4+...+B9:", sum(dual[4:10]))
    print("candidate strict circuit bound Q >= 4852")


if __name__ == "__main__":
    main()
