#!/usr/bin/env python3
"""Independent standard-library verifier for Wave 134.

The algebraic model is reconstructed from the frozen Wave2/Wave131/Wave132
statements.  No Wave134 discovery module is imported.  The mathematical
reconstruction is separate from the sealed discovery artifacts; the latter
are consumed only as JSON data after their manifest hash has been checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Iterable, Mapping, Sequence


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
DISCOVERY_MANIFEST_NAME = "package-manifest.sha256"
EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "581678d37091754f4bf1f197223a120d82f3051020a45b601e84889dfdad81e9"
)
EXPECTED_DISCOVERY_ENTRIES = 13
DISCOVERY_RESULTS_NAME = "exact-results.json"
DISCOVERY_STATUS_NAME = "search-status.json"
EXPECTED_DISCOVERY_RESULTS_SHA256 = (
    "8d3e39c4360341f7d3d6b8ac496853c0ae19e546ab8655cc6939b36edbddb1a2"
)
EXPECTED_DISCOVERY_STATUS_SHA256 = (
    "d5d85b9df1d2664cb808cb9eacfffb069ad6e401e73a6e4cf5e956cbcd02fddb"
)

N = 99
PRIMAL_SIZE = 2**109
DUAL_SIZE = 2**89
PRIMAL_ORDER_TWO_SIZE = 2**55
DUAL_ORDER_TWO_SIZE = 2**45

# (induced edges, common open neighbors, number of degree-two vertices,
#  number of unordered triples)
TRIPLE_TYPES = {
    "independent_c0": (0, 0, 0, 70_686),
    "independent_c1": (0, 1, 0, 27_720),
    "one_edge_c0": (1, 0, 0, 41_580),
    "one_edge_c1": (1, 1, 0, 8_316),
    "path": (2, 0, 1, 8_316),
    "triangle": (3, 0, 3, 231),
}

PRIMAL_TORSION_WEIGHTS = {
    0: 1,
    14: 99,
    24: 4_158,
    26: 693,
    30: 70_686,
    32: 41_580,
    34: 36_036,
    36: 8_547,
}
DUAL_TORSION_WEIGHTS = {
    0: 1,
    15: 99,
    24: 693,
    26: 4_158,
    31: 41_580,
    33: 79_002,
    35: 8_316,
    37: 27_720,
    39: 231,
}

Composition = tuple[int, int, int]  # zeros, odd symbols, twos


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def parse_rational(value: object) -> Q:
    if isinstance(value, int):
        return Q(value)
    if isinstance(value, str):
        return Q(value)
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    ):
        return Q(value[0], value[1])
    raise TypeError(f"unsupported rational encoding: {value!r}")


def swapped(composition: Composition) -> Composition:
    zeros, odd, twos = composition
    return twos, odd, zeros


def add_count(
    table: Counter[Composition], composition: Composition, count: int
) -> None:
    require(sum(composition) == N, f"bad composition: {composition}")
    require(min(composition) >= 0, f"negative composition: {composition}")
    require(count >= 0, "negative forced count")
    table[composition] += count


def smith_type_audit() -> dict[str, object]:
    """Map the frozen integral Smith factors to the two Z4 code types."""

    factors = [1] * 45 + [3] * 9 + [6] + [12] * 43 + [84]
    require(len(factors) == N, "Smith factor count")
    primal_free = sum(factor % 2 for factor in factors)
    primal_two = sum(factor % 4 == 2 for factor in factors)
    dual_free = sum(factor % 4 == 0 for factor in factors)
    dual_two = primal_two
    require((primal_free, primal_two) == (54, 1), "primal Z4 type")
    require((dual_free, dual_two) == (44, 1), "dual Z4 type")
    require(4**primal_free * 2**primal_two == PRIMAL_SIZE, "primal size")
    require(4**dual_free * 2**dual_two == DUAL_SIZE, "dual size")
    require(PRIMAL_SIZE * DUAL_SIZE == 4**N, "duality size product")
    require(2 ** (primal_free + primal_two) == PRIMAL_ORDER_TWO_SIZE,
            "primal order-two size")
    require(2 ** (dual_free + dual_two) == DUAL_ORDER_TWO_SIZE,
            "dual order-two size")
    return {
        "frozen_smith_multiplicities": {
            "1": 45,
            "3": 9,
            "6": 1,
            "12": 43,
            "84": 1,
        },
        "primal_type": "Z4^54 x Z2",
        "dual_type": "Z4^44 x Z2",
        "primal_size": PRIMAL_SIZE,
        "dual_size": DUAL_SIZE,
        "primal_order_two_size": PRIMAL_ORDER_TWO_SIZE,
        "dual_order_two_size": DUAL_ORDER_TWO_SIZE,
    }


def torsion_audit() -> dict[str, object]:
    """Record the residue/torsion identities and their exact distance walls."""

    # A(A+I)=12I+2J gives 2*1 in the Z4 row code.  Its residue is
    # R=im(A mod 2), dimension 54.  The extra Smith Z2 factor therefore
    # extends the torsion shadow by the all-one vector.
    return {
        "primal_residue": "R=im_F2(A), dimension 54",
        "primal_torsion": "T=R+<1>, dimension 55",
        "dual_residue": "T_perp=D intersect even, dimension 44",
        "dual_torsion": "D=R_perp=ker_F2(A), dimension 45",
        "identity_for_extra_torsion": "A(A+I)=12I+2J, hence 2*1 is in C over Z4",
        "primal_torsion_gap": {
            "forced_zero_weights": [1, 2, 3, 4, 5, 6],
            "weight_7_status": "ALLOWED_NOT_FORCED_ZERO",
            "reason": (
                "R has minimum at least 8 and maximum at most 92; "
                "the coset 1+R can therefore first occur at weight 7."
            ),
        },
        "dual_torsion_gap": {
            "forced_zero_weights": [1, 2, 3, 4, 5, 6, 7],
            "minimum_weight_lower_bound": 8,
        },
        "both_torsion_codes_contain_one": True,
        "torsion_complement_symmetry": True,
    }


def structural_zero_audit() -> dict[str, object]:
    """Derive zero regions visible to the symmetrized enumerators."""

    # The odd-symbol count is the Hamming weight of the binary residue.
    # R is even with 8 <= wt <= 92 away from zero.  The dual residue T-perp
    # is an even subcode of D; since D contains 1 and d(D)>=8, a nonzero
    # even dual-residue word has weight between 8 and 90.
    primal_odd_forbidden = [
        weight
        for weight in range(N + 1)
        if weight % 2 or weight in range(1, 8) or weight in range(93, 100)
    ]
    dual_odd_forbidden = [
        weight
        for weight in range(N + 1)
        if weight % 2 or weight in range(1, 8) or weight in range(91, 100)
    ]
    primal_torsion_forbidden = list(range(1, 7)) + list(range(93, 99))
    dual_torsion_forbidden = list(range(1, 8)) + list(range(92, 99))
    require(7 not in primal_torsion_forbidden, "primal torsion weight 7 removed")
    require(7 in dual_torsion_forbidden, "dual torsion weight 7 retained")
    return {
        "odd_symbol_interpretation": "odd-symbol count equals binary residue weight",
        "primal_odd_symbol_forbidden_counts": primal_odd_forbidden,
        "dual_odd_symbol_forbidden_counts": dual_odd_forbidden,
        "primal_even_symbol_slice": {
            "size": PRIMAL_ORDER_TWO_SIZE,
            "forbidden_two_counts": primal_torsion_forbidden,
            "complement_symmetric": True,
            "weight_7_allowed": True,
        },
        "dual_even_symbol_slice": {
            "size": DUAL_ORDER_TWO_SIZE,
            "forbidden_two_counts": dual_torsion_forbidden,
            "complement_symmetric": True,
        },
    }


def structural_orbit_audit() -> dict[str, object]:
    """Count the exact zero/two-symmetry state spaces independently."""

    raw_states = 0
    even_odd_orbits = 0
    primal_allowed = 0
    dual_allowed = 0
    primal_forbidden: Counter[int] = Counter()
    dual_forbidden: Counter[int] = Counter()
    for zeros in range(N + 1):
        for odd in range(N - zeros + 1):
            twos = N - zeros - odd
            raw_states += 1
            if odd % 2 or zeros < twos:
                continue
            even_odd_orbits += 1

            if odd == 0:
                primal_ok = twos not in range(1, 7)
                dual_ok = twos not in range(1, 8)
            else:
                primal_ok = 8 <= odd <= 92
                # Res(Cperp)=D intersect even. Since 1 is in D and d(D)>=8,
                # both d and 1+d have weight at least eight. Therefore an
                # even dual-residue weight is at most 90, not 92.
                dual_ok = 8 <= odd <= 90

            if primal_ok:
                primal_allowed += 1
            else:
                primal_forbidden[odd] += 1
            if dual_ok:
                dual_allowed += 1
            else:
                dual_forbidden[odd] += 1

    require(raw_states == math.comb(N + 2, 2), "raw composition count")
    require(even_odd_orbits == 1_275, "even odd-symbol orbit count")
    require(primal_allowed == 1_119, "primal allowed orbit count")
    require(dual_allowed == 1_114, "dual allowed orbit count")
    require(sum(primal_forbidden.values()) == 156,
            "primal forbidden orbit count")
    require(sum(dual_forbidden.values()) == 161,
            "dual forbidden orbit count")
    require(dual_forbidden[92] == 4, "dual weight-92 orbit wall")
    return {
        "raw_states": raw_states,
        "even_odd_symbol_orbits": even_odd_orbits,
        "primal_allowed_orbits": primal_allowed,
        "primal_forbidden_orbits": sum(primal_forbidden.values()),
        "dual_allowed_orbits": dual_allowed,
        "dual_forbidden_orbits": sum(dual_forbidden.values()),
        "primal_forbidden_orbits_by_odd_count": {
            str(weight): count
            for weight, count in sorted(primal_forbidden.items())
        },
        "dual_forbidden_orbits_by_odd_count": {
            str(weight): count
            for weight, count in sorted(dual_forbidden.items())
        },
        "dual_weight_92_orbits_forced_zero": dual_forbidden[92],
        "dual_weight_92_reason": (
            "Res(Cperp)=D intersect even, 1 is in D, and d(D)>=8; "
            "therefore wt(d)<=91 and even wt(d)<=90."
        ),
    }


def primal_forced_table() -> Counter[Composition]:
    """Forced symmetrized compositions in the Z4 row code C."""

    forced: Counter[Composition] = Counter()

    # Signed sums of one row.  Global negatives are distinct words but have
    # the same symmetrized composition.  Adding 2*1 swaps zero and two counts.
    one = (85, 14, 0)
    add_count(forced, one, 2 * 99)
    add_count(forced, swapped(one), 2 * 99)

    # Signed sums of two rows.  Equal signs give a two on the intersection;
    # opposite signs cancel there.  Each sign class has two global negatives.
    pair_data = {
        "edge": (693, 1),
        "nonedge": (4_158, 2),
    }
    for pair_count, intersection in pair_data.values():
        odd = 28 - 2 * intersection
        plus = (N - odd - intersection, odd, intersection)
        difference = (N - odd, odd, 0)
        for composition in (plus, difference):
            add_count(forced, composition, 2 * pair_count)
            add_count(forced, swapped(composition), 2 * pair_count)

        # One odd row plus twice the other row.  Either endpoint can carry
        # the odd coefficient and that coefficient has two signs.
        mixed_twos = 14 - intersection
        mixed = (N - 14 - mixed_twos, 14, mixed_twos)
        add_count(forced, mixed, 4 * pair_count)
        add_count(forced, swapped(mixed), 4 * pair_count)

    # Three signed rows.  All equal signs use every pair intersection.  In a
    # mixed sign vector, the unique same-sign pair is the only source of 2s.
    for edges, common, _degree_two, triple_count in TRIPLE_TYPES.values():
        odd = 30 + 2 * edges + 4 * common
        all_plus_twos = 6 - edges - 3 * common
        all_plus = (N - odd - all_plus_twos, odd, all_plus_twos)
        add_count(forced, all_plus, 2 * triple_count)
        add_count(forced, swapped(all_plus), 2 * triple_count)

        # Each of the three possible same-sign pairs contributes two global
        # sign vectors.  An edge pair has open-neighborhood intersection one;
        # a nonedge pair has intersection two.
        for pair_multiplicity, intersection in (
            (edges, 1),
            (3 - edges, 2),
        ):
            if not pair_multiplicity:
                continue
            twos = intersection - common
            mixed = (N - odd - twos, odd, twos)
            count = 2 * pair_multiplicity * triple_count
            add_count(forced, mixed, count)
            add_count(forced, swapped(mixed), count)

        # One odd row and two doubled rows.  Choose the doubled pair; its
        # edge status b controls the symmetric difference of the two torsion
        # supports.  There are two signs for the odd row.
        for torsion_pair_is_edge, pair_multiplicity in (
            (1, edges),
            (0, 3 - edges),
        ):
            if not pair_multiplicity:
                continue
            twos = 20 + edges + torsion_pair_is_edge + 2 * common
            mixed_one_odd = (N - 14 - twos, 14, twos)
            count = 2 * pair_multiplicity * triple_count
            add_count(forced, mixed_one_odd, count)
            add_count(forced, swapped(mixed_one_odd), count)

        # Two odd rows and one doubled row.  For every selected odd base pair
        # there are two global signs in the plus class and two in the
        # difference class.
        for base_is_edge, pair_multiplicity in (
            (1, edges),
            (0, 3 - edges),
        ):
            if not pair_multiplicity:
                continue
            odd = 26 if base_is_edge else 24
            plus_twos = 12 + edges - 2 * base_is_edge
            difference_twos = 10 + edges - base_is_edge + 2 * common
            count = 2 * pair_multiplicity * triple_count
            for twos in (plus_twos, difference_twos):
                mixed_two_odd = (N - odd - twos, odd, twos)
                add_count(forced, mixed_two_odd, count)
                add_count(forced, swapped(mixed_two_odd), count)

    # The order-two shadow consists of 2T.  Injective subset words f(S) and
    # their complements give the following disjoint forced words.
    for weight, count in PRIMAL_TORSION_WEIGHTS.items():
        composition = (N - weight, 0, weight)
        add_count(forced, composition, count)
        add_count(forced, swapped(composition), count)
    return forced


def dual_forced_table() -> Counter[Composition]:
    """Forced symmetrized compositions in C-perp."""

    forced: Counter[Composition] = Counter()

    # The order-two shadow is 2D, with D=ker(A mod2).  The g(S) words and
    # their complements are distinct.
    for weight, count in DUAL_TORSION_WEIGHTS.items():
        composition = (N - weight, 0, weight)
        add_count(forced, composition, count)
        add_count(forced, swapped(composition), count)

    # q_u=e_u+r_u obeys A q_u=2*1.  Hence q_u +/- q_v is in the dual.
    # IMPORTANT: plus and minus have different compositions.
    for pair_count, intersection in ((693, 3), (4_158, 2)):
        odd = 30 - 2 * intersection
        plus = (N - odd - intersection, odd, intersection)
        difference = (N - odd, odd, 0)
        require(plus != difference, "q_u+q_v collapsed with q_u-q_v")
        for composition in (plus, difference):
            add_count(forced, composition, 2 * pair_count)
            add_count(forced, swapped(composition), 2 * pair_count)

    # Add the torsion word 2q_w for a third, distinct vertex.  For a selected
    # base pair uv let b indicate whether uv is an edge.  Closed-neighborhood
    # pair intersections are 3 on edges and 2 on nonedges.  For the plus
    # class the triple intersection cancels; for the difference class it
    # contributes twice.
    for edges, common, degree_two, triple_count in TRIPLE_TYPES.values():
        closed_triple = common + degree_two
        for base_is_edge, pair_multiplicity in (
            (1, edges),
            (0, 3 - edges),
        ):
            if not pair_multiplicity:
                continue
            odd = 24 if base_is_edge else 26
            plus_twos = 13 + 2 * base_is_edge - edges
            difference_twos = (
                11 - edges + base_is_edge + 2 * closed_triple
            )
            plus = (N - odd - plus_twos, odd, plus_twos)
            difference = (
                N - odd - difference_twos,
                odd,
                difference_twos,
            )
            count = 2 * pair_multiplicity * triple_count
            for composition in (plus, difference):
                add_count(forced, composition, count)
                add_count(forced, swapped(composition), count)
    return forced


def collision_audit() -> dict[str, object]:
    """State the exact small-support injectivity arguments used by the counts."""

    # Numerical support ceilings make the two binary minimum-distance
    # invocations explicit and machine-checkable.
    require(2 * 3 == 6 < 8, "signed-row collision support ceiling")
    require(3 < 8, "halved signed-row collision support ceiling")
    require(max(PRIMAL_TORSION_WEIGHTS) <= 36, "primal small-word ceiling")
    require(max(DUAL_TORSION_WEIGHTS) <= 39, "dual small-word ceiling")
    return {
        "signed_primal_rows": (
            "If alpha A=beta A mod4 for alpha,beta in Z4^99 "
            "of support at most 3, reduction mod2 puts the odd part of "
            "alpha-beta in D with weight at most 6; d(D)>=8 removes it. "
            "The remaining difference is 2z with wt(z)<=6, and zA=0 "
            "mod2 again forces z=0."
        ),
        "primal_2one_translates": (
            "A collision with the 2*1 translate would require zA=1 mod2 "
            "for wt(z)<=3. This is impossible because im(A mod2) is even."
        ),
        "dual_pairs_and_triples": (
            "Modulo 2, q_u +/- q_v +2q_w has residue g({u,v}); injectivity "
            "of g on subsets of size at most 3 fixes the base pair. "
            "Dividing a remaining equality by 2 gives a g-image of a "
            "subset of at most 3 vertices, so the sign class and w are fixed."
        ),
        "dual_2one_translates": (
            "A translate collision would force a g(S) of weight at most 39 "
            "to equal the all-one word of weight 99."
        ),
        "q_plus_minus_separation": {
            "edge_plus": [72, 24, 3],
            "edge_minus": [75, 24, 0],
            "nonedge_plus": [71, 26, 2],
            "nonedge_minus": [73, 26, 0],
        },
    }


def venn_atoms(
    sizes: Sequence[int],
    pair_intersections: Mapping[tuple[int, int], int],
    triple_intersection: int = 0,
) -> dict[int, int]:
    """Return exact coordinate counts indexed by a nonempty membership mask."""

    set_count = len(sizes)
    require(set_count in (1, 2, 3), "unsupported Venn order")
    atoms: dict[int, int] = {}
    if set_count == 1:
        atoms[1] = sizes[0]
    elif set_count == 2:
        common = pair_intersections[0, 1]
        atoms = {
            1: sizes[0] - common,
            2: sizes[1] - common,
            3: common,
        }
    else:
        atoms[7] = triple_intersection
        for left, right, mask in ((0, 1, 3), (0, 2, 5), (1, 2, 6)):
            atoms[mask] = pair_intersections[left, right] - triple_intersection
        atoms[1] = sizes[0] - atoms[3] - atoms[5] - atoms[7]
        atoms[2] = sizes[1] - atoms[3] - atoms[6] - atoms[7]
        atoms[4] = sizes[2] - atoms[5] - atoms[6] - atoms[7]
    require(all(value >= 0 for value in atoms.values()), "negative Venn atom")
    require(sum(atoms.values()) <= N, "Venn union exceeds length")
    return atoms


def composition_from_atoms(
    atoms: Mapping[int, int], coefficients: Sequence[int]
) -> Composition:
    symbol_counts = [N - sum(atoms.values()), 0, 0, 0]
    for mask, multiplicity in atoms.items():
        symbol = sum(
            coefficient
            for index, coefficient in enumerate(coefficients)
            if mask & (1 << index)
        ) % 4
        symbol_counts[symbol] += multiplicity
    return (
        symbol_counts[0],
        symbol_counts[1] + symbol_counts[3],
        symbol_counts[2],
    )


def brute_small_support_table(side: str) -> Counter[Composition]:
    """Second derivation by exact Venn-atom enumeration."""

    require(side in ("primal", "dual"), "bad brute side")
    table: Counter[Composition] = Counter()

    def consume(
        subset_count: int,
        sizes: Sequence[int],
        pair_intersections: Mapping[tuple[int, int], int],
        triple_intersection: int = 0,
    ) -> None:
        atoms = venn_atoms(sizes, pair_intersections, triple_intersection)
        support = len(sizes)
        for coefficients in product((1, 2, 3), repeat=support):
            if side == "dual" and sum(coefficients) % 2:
                continue
            composition = composition_from_atoms(atoms, coefficients)
            add_count(table, composition, subset_count)
            add_count(table, swapped(composition), subset_count)

    # Empty coefficient support and its 2*1 translate.
    add_count(table, (N, 0, 0), 1)
    add_count(table, (0, 0, N), 1)

    size = 14 if side == "primal" else 15
    consume(N, [size], {})

    for pair_count, edge in ((693, True), (4_158, False)):
        intersection = (
            (1 if edge else 2) if side == "primal" else (3 if edge else 2)
        )
        consume(pair_count, [size, size], {(0, 1): intersection})

    for edges, common, degree_two, triple_count in TRIPLE_TYPES.values():
        edge_flags = [index < edges for index in range(3)]
        pair_keys = ((0, 1), (0, 2), (1, 2))
        intersections = {}
        for key, edge in zip(pair_keys, edge_flags, strict=True):
            intersections[key] = (
                (1 if edge else 2)
                if side == "primal"
                else (3 if edge else 2)
            )
        triple = common if side == "primal" else common + degree_two
        consume(triple_count, [size, size, size], intersections, triple)
    return table


def linear_power(
    degree: int, coefficients: tuple[int, int, int]
) -> dict[Composition, int]:
    """Expand (a*x+b*y+c*z)^degree exactly."""

    a, b, c = coefficients
    output: dict[Composition, int] = {}
    factorial = math.factorial
    numerator = factorial(degree)
    for x_degree in range(degree + 1):
        for y_degree in range(degree - x_degree + 1):
            z_degree = degree - x_degree - y_degree
            coefficient = (
                numerator
                // (
                    factorial(x_degree)
                    * factorial(y_degree)
                    * factorial(z_degree)
                )
                * a**x_degree
                * b**y_degree
                * c**z_degree
            )
            if coefficient:
                output[x_degree, y_degree, z_degree] = coefficient
    return output


def convolve_homogeneous(
    left: Mapping[Composition, int],
    right: Mapping[Composition, int],
) -> dict[Composition, int]:
    output: Counter[Composition] = Counter()
    for (a1, b1, c1), x in left.items():
        for (a2, b2, c2), y in right.items():
            output[a1 + a2, b1 + b2, c1 + c2] += x * y
    return {key: value for key, value in output.items() if value}


def transform_monomial(source: Composition) -> dict[Composition, int]:
    """Symmetrized Z4 character transform of one degree-99 monomial."""

    zeros, odd, twos = source
    require(sum(source) == N, "source degree")
    result: dict[Composition, int] = {(0, 0, 0): 1}
    for degree, form in (
        (zeros, (1, 2, 1)),   # x+2y+z
        (odd, (1, 0, -1)),    # x-z
        (twos, (1, -2, 1)),   # x-2y+z
    ):
        result = convolve_homogeneous(result, linear_power(degree, form))
    require(all(sum(key) == N for key in result), "transform degree")
    return result


def transform_coefficient(source: Composition, target: Composition) -> int:
    """Fast factored coefficient for the symmetrized MacWilliams transform."""

    i, j, k = source
    a, b, c = target
    require(sum(source) == sum(target) == N, "composition degree mismatch")
    first = sum(
        math.comb(i, b - beta)
        * math.comb(k, beta)
        * 2 ** (b - beta)
        * (-2) ** beta
        for beta in range(max(0, b - i), min(k, b) + 1)
    )
    p_degree = i + k - b
    second = sum(
        (-1) ** from_difference
        * math.comb(p_degree, c - from_difference)
        * math.comb(j, from_difference)
        for from_difference in range(
            max(0, c - p_degree), min(j, c) + 1
        )
    )
    return first * second


def macwilliams_audit() -> dict[str, object]:
    """Check the transform convention and involution on hostile monomials."""

    hostile_sources = (
        (N, 0, 0),
        (0, N, 0),
        (0, 0, N),
        (72, 24, 3),  # q_u+q_v on an edge
        (75, 24, 0),  # q_u-q_v on an edge
        (71, 26, 2),  # q_u+q_v on a nonedge
        (73, 26, 0),  # q_u-q_v on a nonedge
    )
    comparisons = 0
    for source in hostile_sources:
        expanded = transform_monomial(source)
        for target, coefficient in expanded.items():
            require(
                coefficient == transform_coefficient(source, target),
                "factored transform coefficient mismatch",
            )
            comparisons += 1
    # The 3x3 substitution matrix squares to 4I.  On homogeneous degree 99,
    # two transforms multiply the enumerator by 4^99.
    matrix = ((1, 2, 1), (1, 0, -1), (1, -2, 1))
    square = tuple(
        tuple(sum(matrix[row][m] * matrix[m][column] for m in range(3))
              for column in range(3))
        for row in range(3)
    )
    require(square == ((4, 0, 0), (0, 4, 0), (0, 0, 4)),
            "symmetrized transform is not 4I-involutive")
    return {
        "primal_to_dual": (
            "swe_Cperp(x,y,z)=|C|^-1 "
            "swe_C(x+2y+z,x-z,x-2y+z)"
        ),
        "dual_to_primal": (
            "swe_C(x,y,z)=|Cperp|^-1 "
            "swe_Cperp(x+2y+z,x-z,x-2y+z)"
        ),
        "substitution_matrix_square": [list(row) for row in square],
        "hostile_coefficients_compared": comparisons,
        "normalization_product": PRIMAL_SIZE * DUAL_SIZE,
        "expected_normalization_product": 4**N,
    }


def table_as_rows(table: Mapping[Composition, int]) -> list[dict[str, object]]:
    return [
        {"composition": list(composition), "lower_bound": count}
        for composition, count in sorted(table.items())
    ]


def table_as_orbits(table: Mapping[Composition, int]) -> dict[str, int]:
    """Collapse a symmetric expanded table to representatives with n0>=n2."""

    orbits: dict[str, int] = {}
    for composition, count in table.items():
        mate = swapped(composition)
        require(table.get(mate) == count, "asymmetric forced table")
        if composition[0] < composition[2]:
            continue
        require(composition != mate, "unexpected fixed zero/two orbit")
        key = ",".join(str(value) for value in composition)
        orbits[key] = count
    return dict(sorted(orbits.items()))


def preseal_derivation() -> dict[str, object]:
    primal = primal_forced_table()
    dual = dual_forced_table()
    brute_primal = brute_small_support_table("primal")
    brute_dual = brute_small_support_table("dual")
    require(primal == brute_primal, "primal formula/Venn derivations disagree")
    require(dual == brute_dual, "dual formula/Venn derivations disagree")
    require(primal[(85, 14, 0)] == 198, "primal row count")
    require(dual[(72, 24, 3)] == 1_386, "dual edge-plus count")
    require(dual[(75, 24, 0)] == 1_386, "dual edge-minus count")
    require(dual[(71, 26, 2)] == 8_316, "dual nonedge-plus count")
    require(dual[(73, 26, 0)] == 8_316, "dual nonedge-minus count")
    expected_primal_small_words = 2 * sum(
        math.comb(N, support) * 3**support for support in range(4)
    )
    require(
        sum(primal.values()) == expected_primal_small_words,
        "primal support<=3 family is incomplete or colliding",
    )
    # For q-coefficients, A q_u=2*1, so the sum of coefficients must be even.
    # The numbers of nonzero coefficient patterns on supports 0,1,2,3 are
    # respectively 1,1,5,13.
    expected_dual_small_words = 2 * (
        1
        + math.comb(N, 1)
        + 5 * math.comb(N, 2)
        + 13 * math.comb(N, 3)
    )
    require(
        sum(dual.values()) == expected_dual_small_words,
        "dual support<=3 family is incomplete or colliding",
    )
    return {
        "format": "wave134-z4-independent-preseal-v1",
        "claim_label": "DERIVED_PRESEAL",
        "smith_and_types": smith_type_audit(),
        "residue_and_torsion": torsion_audit(),
        "structural_zeros": structural_zero_audit(),
        "structural_orbits": structural_orbit_audit(),
        "collision_proofs": collision_audit(),
        "independent_composition_crosscheck": {
            "method": "formula tables equal direct Venn-atom enumeration",
            "primal_match": True,
            "dual_match": True,
        },
        "forced_primal": {
            "nonzero_compositions": len(primal),
            "sum_of_forced_lower_bounds": sum(primal.values()),
            "expected_from_all_Z4_coefficients_support_at_most_3_and_2one_translates":
                expected_primal_small_words,
            "rows": table_as_rows(primal),
        },
        "forced_dual": {
            "nonzero_compositions": len(dual),
            "sum_of_forced_lower_bounds": sum(dual.values()),
            "expected_from_even_coefficient_sum_support_at_most_3_and_2one_translates":
                expected_dual_small_words,
            "rows": table_as_rows(dual),
        },
        "macwilliams": macwilliams_audit(),
        "status_wall": {
            "discovery_seal_bound": False,
            "finite_rational_feasibility": "NOT_YET_AUDITED",
            "finite_integral_feasibility": "UNKNOWN",
            "Z4_code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
    }


def verify_discovery_manifest() -> dict[str, object]:
    require(DISCOVERY_MANIFEST_NAME != "PENDING", "discovery seal is not bound")
    require(
        EXPECTED_DISCOVERY_MANIFEST_SHA256 != "PENDING",
        "discovery manifest hash is not bound",
    )
    manifest = DISCOVERY / DISCOVERY_MANIFEST_NAME
    require(sha256(manifest) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
            "discovery manifest hash drift")
    entries = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = ROOT / relative
        require(
            target.resolve().is_relative_to(DISCOVERY.resolve()),
            f"sealed target escapes discovery package: {relative}",
        )
        require(target.is_file(), f"missing sealed target: {relative}")
        require(sha256(target) == expected, f"sealed target drift: {relative}")
        entries += 1
    require(entries == EXPECTED_DISCOVERY_ENTRIES, "manifest entry count drift")
    return {
        "manifest": DISCOVERY_MANIFEST_NAME,
        "manifest_sha256": EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "entries_checked": entries,
    }


def load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"JSON root is not an object: {path}")
    return data


def audit_sealed_results(
    derived: Mapping[str, object],
) -> dict[str, object]:
    """Compare sealed JSON claims with the clean-room derivation."""

    results_path = DISCOVERY / DISCOVERY_RESULTS_NAME
    status_path = DISCOVERY / DISCOVERY_STATUS_NAME
    require(sha256(results_path) == EXPECTED_DISCOVERY_RESULTS_SHA256,
            "sealed result hash drift")
    require(sha256(status_path) == EXPECTED_DISCOVERY_STATUS_SHA256,
            "sealed status hash drift")
    results = load_json(results_path)
    status = load_json(status_path)

    require(
        results.get("format") == "wave134-z4-derived-checkpoint-v1",
        "unexpected discovery result schema",
    )
    require(
        status.get("format") == "wave134-search-status-v1",
        "unexpected discovery status schema",
    )

    smith = results["smith_replay"]
    require(
        smith["invariant_factors"]
        == derived["smith_and_types"]["frozen_smith_multiplicities"],
        "sealed Smith multiplicities disagree",
    )
    require(smith["rank_F2"] == 54, "sealed F2 rank")
    require(smith["rank_F3"] == 45, "sealed F3 rank")
    require(smith["rank_F7"] == 98, "sealed F7 rank")
    determinant = 3**9 * 6 * 12**43 * 84
    require(
        int(smith["determinant_absolute"]) == determinant,
        "sealed determinant disagrees with Smith factors",
    )

    code_types = results["code_types"]
    require(code_types["C"]["type"] == "4^54 2^1", "sealed primal type")
    require(code_types["Cperp"]["type"] == "4^44 2^1", "sealed dual type")
    require(int(code_types["C"]["order"]) == PRIMAL_SIZE,
            "sealed primal order")
    require(int(code_types["Cperp"]["order"]) == DUAL_SIZE,
            "sealed dual order")
    require(code_types["extra_torsion_word"] == "2*1",
            "sealed torsion generator")
    require(
        code_types["coefficient_symmetry"] == "(n0,nodd,n2)<->(n2,nodd,n0)",
        "sealed coefficient symmetry",
    )

    forced = results["forced_words"]
    primal = primal_forced_table()
    dual = dual_forced_table()
    require(forced["primal_orbits"] == table_as_orbits(primal),
            "sealed primal forced table disagrees")
    require(forced["dual_orbits"] == table_as_orbits(dual),
            "sealed dual forced table disagrees")
    require(forced["primal_expanded_compositions"] == len(primal),
            "sealed primal expanded count")
    require(forced["dual_expanded_compositions"] == len(dual),
            "sealed dual expanded count")
    require(forced["primal_distinct_words"] == sum(primal.values()),
            "sealed primal forced-word total")
    require(forced["dual_distinct_words"] == sum(dual.values()),
            "sealed dual forced-word total")

    orbit_audit = structural_orbit_audit()
    transform = results["transform"]
    require(transform["raw_states"] == orbit_audit["raw_states"],
            "sealed raw-state count")
    require(
        transform["zero_monomial_rows_checked"] == orbit_audit["raw_states"],
        "sealed transform-row check count",
    )
    require(
        transform["primal_orbits"] == orbit_audit["primal_allowed_orbits"],
        "sealed primal transform-orbit count",
    )
    require(
        transform["allowed_dual_orbits"] == orbit_audit["dual_allowed_orbits"],
        "sealed dual allowed-orbit count",
    )
    require(
        transform["forbidden_dual_orbits"]
        == orbit_audit["dual_forbidden_orbits"],
        "sealed dual forbidden-orbit count",
    )

    require(
        results["rational_relaxation"]["classification"]
        == "UNKNOWN_NOT_RUN_CORRECTED_MODEL",
        "sealed rational boundary inflated",
    )
    require(
        set(results["boundaries"].values()) == {"UNKNOWN"},
        "sealed realization boundary inflated",
    )
    require(status["claim_label"] == "UNKNOWN", "search status label")
    for route in (
        "numerical_support_discovery",
        "rational_full_exact",
        "rational_incremental_exact",
    ):
        require(
            status[route]["classification"]
            == "INVALIDATED_PRESEAL_UNDERCOUNTED_MODEL",
            f"stale route was not invalidated: {route}",
        )
        require(
            status[route].get("inference", "NONE") == "NONE",
            f"stale route retained an inference: {route}",
        )
    require(
        status["corrected_model"]["classification"] == "UNKNOWN_NOT_RUN",
        "corrected model status inflated",
    )
    require(
        status["integral_scout"]["classification"]
        == "UNKNOWN_NOT_RUN_CORRECTED_MODEL",
        "integral status inflated",
    )
    corrected = status["corrected_model"]
    require(corrected["primal_orbits"] == 42, "corrected primal forced orbits")
    require(corrected["dual_orbits"] == 22, "corrected dual forced orbits")
    require(corrected["primal_expanded_compositions"] == 84,
            "corrected primal expanded table")
    require(corrected["dual_expanded_compositions"] == 44,
            "corrected dual expanded table")
    require(corrected["primal_forced_words"] == 8_557_760,
            "corrected primal forced-word total")
    require(corrected["dual_forced_words"] == 4_126_784,
            "corrected dual forced-word total")
    return {
        "results_schema": results["format"],
        "results_sha256": EXPECTED_DISCOVERY_RESULTS_SHA256,
        "status_schema": status["format"],
        "status_sha256": EXPECTED_DISCOVERY_STATUS_SHA256,
        "smith_types_and_orders_match": True,
        "forced_composition_tables_match": True,
        "structural_state_counts_match": True,
        "stale_searches_invalidated": True,
        "corrected_rational_feasibility": "UNKNOWN_NOT_RUN",
        "corrected_integral_feasibility": "UNKNOWN_NOT_RUN",
        "rational_witness_present": False,
        "Z4_code_present": False,
        "graph_present": False,
        "Conway_99": "UNKNOWN",
    }


def build_result(*, preseal: bool = False) -> dict[str, object]:
    derived = preseal_derivation()
    if preseal:
        return derived
    seal = verify_discovery_manifest()
    artifact_audit = audit_sealed_results(derived)
    derived["format"] = "wave134-z4-independent-verification-v1"
    derived["claim_label"] = "VERIFIED"
    derived["sealed_discovery"] = seal
    derived["sealed_result_audit"] = artifact_audit
    derived["status_wall"] = {
        "discovery_seal_bound": True,
        "finite_rational_feasibility": "UNKNOWN_NOT_RUN_CORRECTED_MODEL",
        "finite_integral_feasibility": "UNKNOWN_NOT_RUN_CORRECTED_MODEL",
        "Z4_code_constructed": False,
        "graph_constructed": False,
        "Conway_99": "UNKNOWN",
    }
    return derived


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preseal", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_result(preseal=args.preseal)
    rendered = canonical(result)
    if args.verify:
        require(
            json.loads(args.verify.read_text(encoding="utf-8")) == result,
            "stored independent result differs",
        )
        print(f"verified {args.verify}")
    elif args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
