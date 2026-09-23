#!/usr/bin/env python3
"""Exact count-feasibility audit for the Conway-99 six/seven-vertex formulas.

This checker uses only the Python standard library and exact rational
arithmetic.  It transcribes the formula tables in:

* Reimbayev, arXiv:2508.03377v2, The Subgraphs of Order Six...
* Reimbayev, arXiv:2511.06572v1, Hamiltonian Subgraphs of Order Seven...

It also regenerates the locally admissible unlabeled graphs on 4, 5, and 6
vertices, aligns their vertex-deletion decks with the paper's indices, and
regenerates the locally admissible Hamiltonian graphs on 7 vertices.

Canonical graph masks use the lexicographic edge order
    (0,1),(0,2),...,(0,n-1),(1,2),...,(n-2,n-1).
The least mask over all vertex permutations is the canonical representative.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterable, Mapping


N = 99
K = 14

SOURCE_FREEZE = {
    "hexagon_archive": {
        "url": "https://export.arxiv.org/e-print/2409.10620v1",
        "sha256": "9e31eb63e878531124cb20df306698827b93057b4ef9feed207654aea8f31112",
    },
    "hexagon_tex": {
        "archive_path": "lower_bound_for_hexagons.tex",
        "sha256": "f6b4fc65043f825e1888b3aff4552c883bb38ba9a15745d1822037ceba1800df",
        "identity_lines": "367,397-401",
    },
    "six_archive": {
        "url": "https://export.arxiv.org/e-print/2508.03377v2",
        "sha256": "f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834",
    },
    "six_tex": {
        "archive_path": "The_Subgraphs_of_Order_Six.tex",
        "sha256": "823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f",
        "formula_lines": "345-407",
        "four_five_deck_lines": "428-477",
        "five_six_deck_lines": "493-518",
    },
    "six_figure": {
        "archive_path": "all_six_vertex.jpg",
        "sha256": "62714c46172bb949f00cc82c13394cc2edb87ff264f71a998ec4b094ed043608",
    },
    "seven_archive": {
        "url": "https://export.arxiv.org/e-print/2511.06572v1",
        "sha256": "10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a",
    },
    "seven_tex": {
        "archive_path": "Hamiltonian_Subgraphs_of_Order_Seven.tex",
        "sha256": "0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a",
        "derivation_lines": "95-167",
        "formula_lines": "177-195",
    },
    "seven_figure": {
        "archive_path": "hamiltonian_7.jpg",
        "sha256": "e37f794e7765c947d3ea76104e9c4c61a00517b649d8b7bea9eb67644fe08a2e",
    },
}


def Q(numerator: int, denominator: int = 1) -> Fraction:
    return Fraction(numerator, denominator)


@dataclass(frozen=True)
class Affine:
    """c + x*n3 + y*h11 with exact rational coefficients."""

    c: Fraction = Q(0)
    x: Fraction = Q(0)
    y: Fraction = Q(0)

    def __add__(self, other: object) -> "Affine":
        value = as_affine(other)
        return Affine(self.c + value.c, self.x + value.x, self.y + value.y)

    __radd__ = __add__

    def __neg__(self) -> "Affine":
        return Affine(-self.c, -self.x, -self.y)

    def __sub__(self, other: object) -> "Affine":
        return self + (-as_affine(other))

    def __rsub__(self, other: object) -> "Affine":
        return as_affine(other) - self

    def __mul__(self, scalar: object) -> "Affine":
        factor = Fraction(scalar)
        return Affine(self.c * factor, self.x * factor, self.y * factor)

    __rmul__ = __mul__

    def __truediv__(self, scalar: object) -> "Affine":
        return self * (Q(1) / Fraction(scalar))

    def evaluate(self, n3: int, h11: int = 0) -> Fraction:
        return self.c + self.x * n3 + self.y * h11

    def to_json(self) -> dict[str, str]:
        return {
            "constant": fraction_text(self.c),
            "n3_coefficient": fraction_text(self.x),
            "h11_coefficient": fraction_text(self.y),
        }


def as_affine(value: object) -> Affine:
    if isinstance(value, Affine):
        return value
    return Affine(Fraction(value))


def A(c: object = 0, x: object = 0, y: object = 0) -> Affine:
    return Affine(Fraction(c), Fraction(x), Fraction(y))


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def affine_sum(values: Iterable[Affine]) -> Affine:
    return sum(values, A())


def four_counts(n: int = N, k: int = K) -> dict[int, Affine]:
    common = n * k * (k - 2)
    return {
        1: A(Q(common * (k - 4) * (k**3 - 6 * k**2 + 10 * k - 12), 192)),
        2: A(Q(common * (k - 4) * (k**2 - 4 * k + 6), 16)),
        3: A(Q(common * (k**2 - 6 * k + 10), 16)),
        4: A(Q(common * (n - 3 * k + 4), 2)),
        5: A(Q(common * (k - 3), 2)),
        6: A(Q(common * (k - 4), 6)),
        7: A(Q(common * (k - 4), 12)),
        8: A(Q(common, 8)),
        9: A(Q(common, 2)),
    }


def five_counts(n: int = N, k: int = K) -> dict[int, Affine]:
    common = n * k * (k - 2)
    return {
        1: A(Q(common * (k - 4) * (n - 4 * k + 6) * (k**3 - 6 * k**2 + 14 * k - 36), 960)),
        2: A(Q(common * (k - 4) ** 2 * (k**3 - 8 * k**2 + 26 * k - 48), 96)),
        3: A(Q(common * (k - 4) * (k**3 - 10 * k**2 + 38 * k - 60), 16)),
        4: A(Q(common * (k - 4) * (k**3 - 10 * k**2 + 40 * k - 68), 32)),
        5: A(Q(common * (k - 4) * (n - 4 * k + 8), 6)),
        6: A(Q(common * (k - 4) * (k**2 - 8 * k + 20), 8)),
        7: A(Q(common * (k - 4) * (k**2 - 7 * k + 16), 4)),
        8: A(Q(common * (k - 4) * (n - 4 * k + 8), 24)),
        9: A(Q(common * (k - 4) * (k - 6), 24)),
        10: A(Q(common * (n - 4 * k + 8), 8)),
        11: A(Q(common * (k - 4) ** 2, 2)),
        12: A(Q(common * (k - 4) ** 2, 4)),
        13: A(Q(common * (k**2 - 8 * k + 17), 2)),
        14: A(Q(common * (k - 4) * (k - 6), 24)),
        15: A(Q(common * (k - 4), 2)),
        16: A(Q(common * (k - 3), 2)),
        17: A(Q(common * (k - 4), 4)),
        18: A(Q(common * (k - 4), 5)),
        19: A(Q(common, 8)),
        20: A(Q(common, 2)),
        21: A(Q(common * (k - 4), 2)),
    }


def six_counts(n: int = N, k: int = K) -> dict[int, Affine]:
    common = n * k * (k - 2)
    b = common * (k - 4)
    return {
        1: A(Q(common, 12), Q(-1, 3)),
        2: A(Q(common, 2)),
        3: A(0, 1),
        4: A(0, 2),
        5: A(Q(b, 8), -1),
        6: A(Q(common * (k - 3), 2), -2),
        7: A(Q(b, 4)),
        8: A(b, -2),
        9: A(Q(b, 4), -1),
        10: A(Q(b, 2), -2),
        11: A(Q(b * (k - 6), 2), 4),
        12: A(Q(common * (2 * k**2 - 21 * k + 53), 12), 1),
        13: A(Q(b * (k**2 - 12 * k + 42), 32), -1),
        14: A(Q(b * (k - 12), 144), Q(1, 3)),
        15: A(Q(b, 8)),
        16: A(Q(b, 2)),
        17: A(b),
        18: A(b, -4),
        19: A(Q(b * (k - 6), 12)),
        20: A(Q(b * (k - 4), 2)),
        21: A(Q(common * (k - 3) * (k - 4), 6), Q(2, 3)),
        22: A(Q(b * (k - 5), 2)),
        23: A(b * (k - 5), 4),
        24: A(Q(b * (k - 6), 4), 2),
        25: A(Q(b * (k - 7), 2), 4),
        26: A(Q(b * (k - 6), 4)),
        27: A(Q(b * (k - 5), 2), 2),
        28: A(Q(b * (k - 6), 4), 2),
        29: A(b * (k - 6), 6),
        30: A(Q(b * (k - 6) * (k - 8), 120)),
        31: A(Q(b * (k - 5) * (k - 6), 6)),
        32: A(Q(b * (k**2 - 10 * k + 26), 8), -1),
        33: A(Q(b * (k**2 - 10 * k + 28), 2), -6),
        34: A(Q(b * (k**2 - 11 * k + 34), 2), -8),
        35: A(Q(b * (k**2 - 11 * k + 36), 2), -10),
        36: A(
            Q(
                b
                * (
                    k**7
                    - 24 * k**6
                    + 248 * k**5
                    - 1520 * k**4
                    + 6436 * k**3
                    - 19520 * k**2
                    + 38896 * k
                    - 40704
                ),
                23040,
            ),
            Q(1, 3),
        ),
        37: A(
            Q(
                b
                * (
                    k**6
                    - 22 * k**5
                    + 212 * k**4
                    - 1208 * k**3
                    + 4484 * k**2
                    - 10456 * k
                    + 12288
                ),
                768,
            ),
            -3,
        ),
        38: A(
            Q(
                b
                * (
                    k**5
                    - 20 * k**4
                    + 172 * k**3
                    - 828 * k**2
                    + 2300 * k
                    - 3048
                ),
                96,
            ),
            6,
        ),
        39: A(
            Q(
                b
                * (
                    k**5
                    - 20 * k**4
                    + 176 * k**3
                    - 884 * k**2
                    + 2588 * k
                    - 3624
                ),
                128,
            ),
            6,
        ),
        40: A(Q(b * (k**4 - 18 * k**3 + 130 * k**2 - 460 * k + 696), 48), -2),
        41: A(Q(b * (k**4 - 18 * k**3 + 136 * k**2 - 524 * k + 892), 16), -14),
        42: A(Q(b * (k**4 - 17 * k**3 + 120 * k**2 - 430 * k + 684), 16), -10),
        43: A(Q(b * (k**4 - 18 * k**3 + 130 * k**2 - 460 * k + 720), 288), Q(-2, 3)),
        44: A(Q(b * (k - 6) * (n - 5 * k + 13), 24)),
        45: A(Q(b * (k - 6) * (k**2 - 8 * k + 26), 64), 1),
        46: A(Q(b * (k**3 - 14 * k**2 + 72 * k - 140), 4), 8),
        47: A(Q(b * (k - 6) * (k**2 - 8 * k + 22), 16), 2),
        48: A(Q(b * (k**3 - 14 * k**2 + 75 * k - 160), 4), 14),
        49: A(Q(b * (k**3 - 16 * k**2 + 94 * k - 216), 48), 2),
        50: A(Q(b * (k**2 - 10 * k + 30), 4), -4),
        51: A(Q(b * (k**2 - 9 * k + 22), 4), -2),
        52: A(Q(b * (n - 5 * k + 12), 4)),
        53: A(Q(b * (n - 5 * k + 15), 5), -2),
        54: A(Q(b * (k - 6), 16)),
        55: A(Q(b * (k - 6), 4), 2),
        56: A(Q(b * (k**2 - 10 * k + 30), 4), -4),
        57: A(Q(b * (k**4 - 18 * k**3 + 140 * k**2 - 564 * k + 996), 192), Q(-4, 3)),
        58: A(Q(b * (k**3 - 15 * k**2 + 86 * k - 190), 8), 8),
        59: A(Q(b * (k - 6) * (k**2 - 10 * k + 34), 24), 2),
        60: A(Q(b * (k**2 - 12 * k + 38), 8), -2),
        61: A(Q(b * (k**3 - 16 * k**2 + 96 * k - 220), 16), 5),
        62: A(Q(b * (k**2 - 14 * k + 54), 24), -2),
    }


def seven_counts(n: int = N, k: int = K) -> dict[int, Affine]:
    common = n * k * (k - 2)
    b = common * (k - 4)
    return {
        0: A(Q(b * (2 * k**2 - 30 * k + 133), 14), -10, -1),
        1: A(Q(common * (2 * k**2 - 25 * k + 68), 2), 16, Q(3, 2)),
        2: A(b * (k - 8), 12, Q(5, 2)),
        3: A(b, -2, Q(-1, 2)),
        4: A(b, -4),
        5: A(Q(b, 2), 0, Q(-1, 2)),
        6: A(b, -8),
        7: A(Q(b, 2), 0, Q(-3, 2)),
        8: A(2 * b, -8, -2),
        9: A(b, -2, Q(-3, 2)),
        10: A(0, 2),
        11: A(0, 0, 1),
        12: A(Q(common, 4), -1, Q(1, 4)),
        13: A(0, 0, Q(1, 2)),
        14: A(0, 4),
        15: A(0, 2),
        16: A(0, -2, 1),
        17: A(Q(common, 4), -1),
        18: A(0, 1, Q(-1, 4)),
    }


FOUR_TO_FIVE: dict[int, dict[int, int]] = {
    1: {1: 5, 2: 2, 3: 1, 5: 1, 9: 1},
    2: {2: 3, 3: 2, 4: 4, 6: 1, 7: 2, 8: 3, 11: 1, 12: 1, 17: 1},
    3: {4: 1, 6: 2, 13: 1, 14: 3, 19: 1, 21: 1},
    4: {3: 2, 5: 3, 6: 2, 7: 2, 10: 4, 11: 1, 12: 2, 13: 2, 15: 1, 16: 2},
    5: {7: 1, 11: 2, 13: 2, 15: 2, 16: 1, 18: 5, 20: 2, 21: 2},
    6: {5: 1, 9: 4, 11: 1, 15: 1, 17: 2},
    7: {8: 2, 12: 1, 14: 2, 21: 1},
    8: {10: 1, 15: 1, 20: 1},
    9: {12: 1, 16: 2, 17: 2, 19: 4, 20: 2, 21: 1},
}


FIVE_TO_SIX_RAW: dict[int, dict[int, int]] = {
    1: {30: 1, 36: 6, 37: 2, 38: 1, 40: 1, 44: 1},
    2: {19: 1, 31: 1, 37: 4, 38: 2, 39: 4, 41: 1, 42: 2, 43: 3, 46: 1, 47: 1, 52: 1, 59: 1},
    3: {20: 1, 26: 1, 32: 2, 34: 1, 38: 3, 40: 3, 41: 2, 42: 2, 45: 4, 46: 1, 47: 2, 48: 2, 50: 1, 51: 2, 61: 2},
    4: {15: 1, 22: 1, 33: 1, 39: 2, 41: 2, 48: 1, 49: 3, 54: 1, 56: 1, 57: 6, 58: 2, 60: 1},
    5: {20: 1, 28: 2, 31: 1, 34: 1, 40: 2, 44: 4, 46: 1, 50: 1, 52: 2, 59: 2},
    6: {7: 1, 11: 1, 13: 4, 16: 1, 23: 1, 24: 1, 25: 1, 34: 1, 35: 2, 41: 1, 58: 2, 59: 3, 60: 2, 61: 4, 62: 3},
    7: {17: 1, 21: 3, 27: 2, 29: 1, 33: 2, 35: 2, 42: 2, 46: 2, 48: 2, 50: 2, 51: 1, 53: 5, 55: 2, 56: 2, 58: 2},
    8: {24: 1, 43: 3, 47: 1, 49: 2, 56: 1, 62: 1},
    9: {19: 2, 26: 1, 30: 5, 31: 1, 44: 1},
    10: {6: 1, 11: 1, 13: 2, 45: 2, 50: 1, 55: 1},
    11: {10: 2, 11: 1, 17: 1, 18: 1, 20: 1, 22: 2, 24: 2, 26: 2, 27: 2, 29: 2, 31: 3, 32: 4, 33: 2, 34: 1, 46: 1},
    12: {16: 1, 18: 1, 22: 1, 23: 1, 25: 1, 47: 2, 51: 2, 52: 2, 54: 4, 55: 2, 56: 1, 60: 2},
    13: {2: 1, 6: 2, 8: 2, 9: 2, 11: 2, 12: 6, 18: 1, 23: 1, 25: 2, 28: 2, 29: 2, 33: 1, 34: 2, 35: 2, 48: 1},
    14: {5: 2, 14: 6, 25: 1, 49: 1, 60: 1, 62: 2},
    15: {4: 2, 7: 2, 9: 4, 10: 2, 11: 1, 17: 1, 18: 1, 26: 2, 27: 2, 28: 2, 50: 1},
    16: {2: 2, 4: 1, 6: 2, 8: 1, 16: 2, 17: 1, 20: 2, 21: 3, 23: 1, 51: 1},
    17: {7: 1, 15: 4, 17: 1, 19: 3, 20: 1, 22: 1, 52: 1},
    18: {4: 1, 8: 1, 10: 2, 29: 1, 53: 1},
    19: {2: 1, 15: 1, 16: 1, 54: 1},
    20: {1: 6, 2: 2, 3: 2, 4: 2, 6: 1, 17: 1, 18: 1, 55: 1},
    21: {3: 4, 5: 4, 7: 2, 8: 2, 16: 1, 18: 1, 22: 1, 23: 1, 24: 2, 25: 1, 56: 1},
}


def corrected_five_to_six() -> dict[int, dict[int, int]]:
    corrected = {row: dict(entries) for row, entries in FIVE_TO_SIX_RAW.items()}
    # The published TeX column for N_23 has only five vertex deletions.  Direct
    # deck reconstruction shows that the omitted sixth term is +n_23 in the
    # m_7 equation.  Keep the raw table above unchanged and apply the repair
    # only in this explicitly named function.
    corrected[7][23] = 1
    return corrected


def sparse_rhs(forms: Mapping[int, Affine], entries: Mapping[int, int]) -> Affine:
    return affine_sum(forms[index] * coefficient for index, coefficient in entries.items())


def seven_identities(
    m: Mapping[int, Affine],
    n6: Mapping[int, Affine],
    h: Mapping[int, Affine],
) -> dict[str, Affine]:
    """Return left-minus-right for every displayed seven-vertex identity."""

    return {
        "h10=2n3": h[10] - 2 * n6[3],
        "h17=3n1": h[17] - 3 * n6[1],
        "h14=2n4": h[14] - 2 * n6[4],
        "h6=8n5": h[6] - 8 * n6[5],
        "h4=4n9": h[4] - 4 * n6[9],
        "2n8=2h6+4h15+h14": 2 * n6[8] - (2 * h[6] + 4 * h[15] + h[14]),
        "2n4=h11+4h18": 2 * n6[4] - (h[11] + 4 * h[18]),
        "2n8=2h3+h11": 2 * n6[8] - (2 * h[3] + h[11]),
        "n4=h16+4h18": n6[4] - (h[16] + 4 * h[18]),
        "2n4=2h13+4h18": 2 * n6[4] - (2 * h[13] + 4 * h[18]),
        "2m19=h12+h18": 2 * m[19] - (h[12] + h[18]),
        "4n9=h9+2h16+2h18": 4 * n6[9] - (h[9] + 2 * h[16] + 2 * h[18]),
        "2n8=h8+2h16+4h15": 2 * n6[8] - (h[8] + 2 * h[16] + 4 * h[15]),
        "2n9=h7+2h16+2h18": 2 * n6[9] - (h[7] + 2 * h[16] + 2 * h[18]),
        "n17=2h5+2h13": n6[17] - (2 * h[5] + 2 * h[13]),
        "4n11=2h2+2h7+2h5+h8+h11": 4 * n6[11] - (2 * h[2] + 2 * h[7] + 2 * h[5] + h[8] + h[11]),
        "6n12=h1+h8+2h12": 6 * n6[12] - (h[1] + h[8] + 2 * h[12]),
        "2n35=7h0+2h1+2h2+h3+h4+h5": 2 * n6[35] - (7 * h[0] + 2 * h[1] + 2 * h[2] + h[3] + h[4] + h[5]),
    }


def edge_data(order: int) -> tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], int]]:
    edges = tuple(combinations(range(order), 2))
    return edges, {edge: index for index, edge in enumerate(edges)}


@lru_cache(maxsize=None)
def permutation_bit_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges, positions = edge_data(order)
    maps = []
    for permutation in permutations(range(order)):
        maps.append(
            tuple(
                1 << positions[tuple(sorted((permutation[left], permutation[right])))]
                for left, right in edges
            )
        )
    return tuple(maps)


def transform_mask(mask: int, bit_map: tuple[int, ...]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        transformed |= bit_map[bit.bit_length() - 1]
        remaining -= bit
    return transformed


def canonical_mask(mask: int, order: int) -> int:
    return min(transform_mask(mask, bit_map) for bit_map in permutation_bit_maps(order))


def locally_admissible(mask: int, order: int) -> bool:
    """Necessary induced-subgraph condition for lambda=1, mu=2."""

    edges, positions = edge_data(order)
    adjacency = [0] * order
    for index, (left, right) in enumerate(edges):
        if mask >> index & 1:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    for left, right in edges:
        common = (adjacency[left] & adjacency[right]).bit_count()
        if mask >> positions[(left, right)] & 1:
            if common > 1:
                return False
        elif common > 2:
            return False
    return True


@lru_cache(maxsize=None)
def locally_admissible_classes(order: int) -> tuple[int, ...]:
    """All unlabeled locally admissible graphs for order <= 6."""

    if order > 6:
        raise ValueError("Use hamiltonian_seven_classes for order seven")
    edges, _ = edge_data(order)
    remaining = {
        mask
        for mask in range(1 << len(edges))
        if locally_admissible(mask, order)
    }
    classes: list[int] = []
    maps = permutation_bit_maps(order)
    while remaining:
        representative = next(iter(remaining))
        orbit = {transform_mask(representative, bit_map) for bit_map in maps}
        classes.append(min(orbit))
        remaining.difference_update(orbit)
    return tuple(sorted(classes))


@lru_cache(maxsize=None)
def hamiltonian_seven_classes() -> tuple[int, ...]:
    """All locally admissible order-7 graphs containing a Hamiltonian cycle.

    Any Hamiltonian graph can be relabeled so one Hamiltonian cycle is
    0-1-...-6-0.  Enumerating every subset of the fourteen remaining chords
    therefore covers every isomorphism class without a hidden symmetry
    restriction.
    """

    order = 7
    edges, positions = edge_data(order)
    cycle = 0
    for vertex in range(order):
        edge = tuple(sorted((vertex, (vertex + 1) % order)))
        cycle |= 1 << positions[edge]
    chord_positions = tuple(
        index for index in range(len(edges)) if not (cycle >> index & 1)
    )
    classes = set()
    for subset in range(1 << len(chord_positions)):
        mask = cycle
        for offset, edge_index in enumerate(chord_positions):
            if subset >> offset & 1:
                mask |= 1 << edge_index
        if locally_admissible(mask, order):
            classes.add(canonical_mask(mask, order))
    return tuple(sorted(classes))


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    old_edges, _ = edge_data(order)
    _, new_positions = edge_data(order - 1)
    remaining_vertices = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(remaining_vertices)}
    result = 0
    for edge_index, (left, right) in enumerate(old_edges):
        if left == deleted or right == deleted or not (mask >> edge_index & 1):
            continue
        new_edge = tuple(sorted((relabel[left], relabel[right])))
        result |= 1 << new_positions[new_edge]
    return result


def deck_vector(mask: int, order: int, lower_classes: tuple[int, ...]) -> tuple[int, ...]:
    index = {representative: position for position, representative in enumerate(lower_classes)}
    vector = [0] * len(lower_classes)
    for deleted in range(order):
        card = canonical_mask(delete_vertex(mask, order, deleted), order - 1)
        vector[index[card]] += 1
    return tuple(vector)


def source_columns(
    rows: Mapping[int, Mapping[int, int]],
    row_count: int,
    column_count: int,
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(rows.get(row, {}).get(column, 0) for row in range(1, row_count + 1))
        for column in range(1, column_count + 1)
    )


def align_four_five() -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return source L_i and M_i indices mapped to canonical-class positions."""

    classes4 = locally_admissible_classes(4)
    classes5 = locally_admissible_classes(5)
    decks = tuple(deck_vector(mask, 5, classes4) for mask in classes5)
    source = source_columns(FOUR_TO_FIVE, 9, 21)

    l_mapping = []
    for source_row in range(9):
        signature = sorted(column[source_row] for column in source)
        candidates = [
            canonical_row
            for canonical_row in range(9)
            if sorted(column[canonical_row] for column in decks) == signature
        ]
        if len(candidates) != 1:
            raise AssertionError(f"L_{source_row + 1} row alignment is not unique: {candidates}")
        l_mapping.append(candidates[0])

    m_mapping = []
    for source_column in source:
        canonical_vector = [0] * 9
        for source_row, canonical_row in enumerate(l_mapping):
            canonical_vector[canonical_row] = source_column[source_row]
        candidates = [
            canonical_column
            for canonical_column, deck in enumerate(decks)
            if deck == tuple(canonical_vector)
        ]
        if len(candidates) != 1:
            raise AssertionError(f"M column alignment is not unique: {candidates}")
        m_mapping.append(candidates[0])
    if len(set(m_mapping)) != 21:
        raise AssertionError("M source-to-canonical mapping is not bijective")
    return tuple(l_mapping), tuple(m_mapping)


def align_five_six(
    m_mapping: tuple[int, ...],
    rows: Mapping[int, Mapping[int, int]],
) -> tuple[int, ...]:
    classes5 = locally_admissible_classes(5)
    classes6 = locally_admissible_classes(6)
    decks = tuple(deck_vector(mask, 6, classes5) for mask in classes6)
    source = source_columns(rows, 21, 62)
    n_mapping = []
    for source_column in source:
        canonical_vector = [0] * 21
        for source_row, canonical_row in enumerate(m_mapping):
            canonical_vector[canonical_row] = source_column[source_row]
        candidates = [
            canonical_column
            for canonical_column, deck in enumerate(decks)
            if deck == tuple(canonical_vector)
        ]
        if len(candidates) != 1:
            raise AssertionError(f"N column alignment is not unique: {candidates}")
        n_mapping.append(candidates[0])
    if len(set(n_mapping)) != 62:
        raise AssertionError("N source-to-canonical mapping is not bijective")
    return tuple(n_mapping)


def n3_shape(mask: int) -> dict[str, object]:
    edges, positions = edge_data(6)
    triangles = []
    for vertices in combinations(range(6), 3):
        if all(mask >> positions[tuple(sorted(edge))] & 1 for edge in combinations(vertices, 2)):
            triangles.append(tuple(vertices))
    if len(triangles) != 2 or set(triangles[0]).intersection(triangles[1]):
        raise AssertionError(f"N_3 does not have two disjoint triangles: {triangles}")
    if set(triangles[0]).union(triangles[1]) != set(range(6)):
        raise AssertionError("N_3 triangles do not cover all vertices")
    cross_edges = [
        (left, right)
        for left in triangles[0]
        for right in triangles[1]
        if mask >> positions[tuple(sorted((left, right)))] & 1
    ]
    degrees = {vertex: 0 for vertex in range(6)}
    for left, right in cross_edges:
        degrees[left] += 1
        degrees[right] += 1
    if len(cross_edges) != 2 or max(degrees.values()) > 1:
        raise AssertionError(f"N_3 cross edges are not an independent pair: {cross_edges}")
    return {
        "triangles": [list(triangle) for triangle in triangles],
        "cross_edges": [list(edge) for edge in cross_edges],
        "cross_edges_form_matching": True,
        "edge_count": mask.bit_count(),
    }


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_multiple(value: Fraction, modulus: int) -> int:
    integer = ceil_fraction(value)
    return integer + (-integer) % modulus


def floor_multiple(value: Fraction, modulus: int) -> int:
    integer = floor_fraction(value)
    return integer - integer % modulus


def one_variable_bounds(forms: Mapping[int, Affine]) -> tuple[Fraction, Fraction, list[int], list[int]]:
    lower: Fraction | None = None
    upper: Fraction | None = None
    lower_sources: list[int] = []
    upper_sources: list[int] = []
    for index, form in forms.items():
        if form.y:
            raise ValueError("Expected a one-variable form")
        if form.x > 0:
            candidate = -form.c / form.x
            if lower is None or candidate > lower:
                lower, lower_sources = candidate, [index]
            elif candidate == lower:
                lower_sources.append(index)
        elif form.x < 0:
            candidate = form.c / (-form.x)
            if upper is None or candidate < upper:
                upper, upper_sources = candidate, [index]
            elif candidate == upper:
                upper_sources.append(index)
        elif form.c < 0:
            raise AssertionError(f"Constant count N_{index} is negative")
    if lower is None or upper is None:
        raise AssertionError("Bounds are not finite")
    return lower, upper, lower_sources, upper_sources


def integral_residues_one_variable(forms: Mapping[int, Affine]) -> tuple[int, tuple[int, ...]]:
    modulus = 1
    for form in forms.values():
        modulus = math.lcm(modulus, form.x.denominator)
        if form.c.denominator != 1:
            raise AssertionError("Parameter-independent count is nonintegral")
    residues = tuple(
        residue
        for residue in range(modulus)
        if all(form.evaluate(residue).denominator == 1 for form in forms.values())
    )
    return modulus, residues


def integral_residues_two_variables(forms: Mapping[int, Affine]) -> tuple[int, int, tuple[tuple[int, int], ...]]:
    x_modulus = 1
    y_modulus = 1
    for form in forms.values():
        x_modulus = math.lcm(x_modulus, form.x.denominator)
        y_modulus = math.lcm(y_modulus, form.y.denominator)
        if form.c.denominator != 1:
            raise AssertionError("Parameter-independent count is nonintegral")
    residues = tuple(
        (x_residue, y_residue)
        for x_residue in range(x_modulus)
        for y_residue in range(y_modulus)
        if all(
            form.evaluate(x_residue, y_residue).denominator == 1
            for form in forms.values()
        )
    )
    return x_modulus, y_modulus, residues


def y_interval(forms: Mapping[int, Affine], n3: int, modulus: int = 4) -> tuple[int, int]:
    lower: Fraction | None = None
    upper: Fraction | None = None
    for form in forms.values():
        constant_at_x = form.c + form.x * n3
        if form.y > 0:
            candidate = -constant_at_x / form.y
            lower = candidate if lower is None else max(lower, candidate)
        elif form.y < 0:
            candidate = constant_at_x / (-form.y)
            upper = candidate if upper is None else min(upper, candidate)
        elif constant_at_x < 0:
            raise ValueError(f"No y can make the counts nonnegative at n3={n3}")
    if lower is None or upper is None:
        raise AssertionError("The h11 interval is not bounded")
    return ceil_multiple(lower, modulus), floor_multiple(upper, modulus)


def all_nonnegative_integral(forms: Mapping[int, Affine], n3: int, h11: int = 0) -> bool:
    values = [form.evaluate(n3, h11) for form in forms.values()]
    return all(value.denominator == 1 and value >= 0 for value in values)


def affine_digest(forms: Mapping[int, Affine]) -> str:
    payload = json.dumps(
        {str(index): form.to_json() for index, form in sorted(forms.items())},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def build_results() -> dict[str, object]:
    l = four_counts()
    m = five_counts()
    n6 = six_counts()
    h = seven_counts()

    if set(l) != set(range(1, 10)):
        raise AssertionError("Four-vertex formula table is incomplete")
    if set(m) != set(range(1, 22)):
        raise AssertionError("Five-vertex formula table is incomplete")
    if set(n6) != set(range(1, 63)):
        raise AssertionError("Six-vertex formula table is incomplete")
    if set(h) != set(range(19)):
        raise AssertionError("Seven-vertex Hamiltonian formula table is incomplete")

    totals = {
        "four": affine_sum(l.values()),
        "five": affine_sum(m.values()),
        "six": affine_sum(n6.values()),
    }
    expected_totals = {
        "four": A(math.comb(N, 4)),
        "five": A(math.comb(N, 5)),
        "six": A(math.comb(N, 6)),
    }
    if totals != expected_totals:
        raise AssertionError(f"Formula-table totals fail: {totals!r}")

    four_five_residuals = {
        row: l[row] * (N - 4) - sparse_rhs(m, entries)
        for row, entries in FOUR_TO_FIVE.items()
    }
    if any(residual != A() for residual in four_five_residuals.values()):
        raise AssertionError(f"Four-to-five identities fail: {four_five_residuals}")

    raw_five_six_residuals = {
        row: m[row] * (N - 5) - sparse_rhs(n6, entries)
        for row, entries in FIVE_TO_SIX_RAW.items()
    }
    corrected_rows = corrected_five_to_six()
    corrected_five_six_residuals = {
        row: m[row] * (N - 5) - sparse_rhs(n6, entries)
        for row, entries in corrected_rows.items()
    }
    if any(residual != A() for residual in corrected_five_six_residuals.values()):
        raise AssertionError(f"Corrected five-to-six identities fail: {corrected_five_six_residuals}")
    expected_raw_failure = {row: residual for row, residual in raw_five_six_residuals.items() if residual != A()}
    if expected_raw_failure != {7: n6[23]}:
        raise AssertionError(f"Unexpected raw five-to-six residuals: {expected_raw_failure}")

    h_residuals = seven_identities(m, n6, h)
    if any(residual != A() for residual in h_residuals.values()):
        raise AssertionError(f"Seven-vertex identities fail: {h_residuals}")

    classes4 = locally_admissible_classes(4)
    classes5 = locally_admissible_classes(5)
    classes6 = locally_admissible_classes(6)
    classes7h = hamiltonian_seven_classes()
    class_counts = {
        "order_4": len(classes4),
        "order_5": len(classes5),
        "order_6": len(classes6),
        "order_7_hamiltonian": len(classes7h),
    }
    if class_counts != {
        "order_4": 9,
        "order_5": 21,
        "order_6": 62,
        "order_7_hamiltonian": 19,
    }:
        raise AssertionError(f"Unexpected locally admissible class counts: {class_counts}")

    l_mapping, m_mapping = align_four_five()
    raw_column_sums = tuple(
        sum(column) for column in source_columns(FIVE_TO_SIX_RAW, 21, 62)
    )
    if [(index + 1, total) for index, total in enumerate(raw_column_sums) if total != 6] != [(23, 5)]:
        raise AssertionError("The raw five-to-six deck defect is not uniquely N_23")
    n_mapping = align_five_six(m_mapping, corrected_rows)

    source_n3_mask = classes6[n_mapping[2]]
    shape = n3_shape(source_n3_mask)
    expected_n23_deck_source_order = []
    n23_deck = deck_vector(classes6[n_mapping[22]], 6, classes5)
    for source_row in range(21):
        expected_n23_deck_source_order.append(n23_deck[m_mapping[source_row]])
    printed_n23_deck = [
        FIVE_TO_SIX_RAW.get(source_row, {}).get(23, 0)
        for source_row in range(1, 22)
    ]
    difference = [
        expected - printed
        for expected, printed in zip(expected_n23_deck_source_order, printed_n23_deck)
    ]
    if difference != [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        raise AssertionError(f"Unexpected N_23 deck correction: {difference}")

    lower, upper, lower_sources, upper_sources = one_variable_bounds(n6)
    x_modulus, x_residues = integral_residues_one_variable(n6)
    if (lower, upper, lower_sources, upper_sources, x_modulus, x_residues) != (
        Q(0),
        Q(4158),
        [3, 4],
        [1],
        3,
        (0,),
    ):
        raise AssertionError(
            "Unexpected exact six-vertex feasibility envelope: "
            f"{(lower, upper, lower_sources, upper_sources, x_modulus, x_residues)}"
        )
    feasible_x = tuple(
        n3
        for n3 in range(ceil_fraction(lower), floor_fraction(upper) + 1)
        if n3 % x_modulus in x_residues and all_nonnegative_integral(n6, n3)
    )
    expected_x = tuple(range(0, 4159, 3))
    if feasible_x != expected_x:
        raise AssertionError("Six-vertex exact feasible set is not 0,3,...,4158")

    h_x_modulus, h_y_modulus, h_residues = integral_residues_two_variables(h)
    if (h_x_modulus, h_y_modulus, h_residues) != (
        1,
        4,
        ((0, 0),),
    ):
        raise AssertionError(
            f"Unexpected seven-vertex integrality residues: {(h_x_modulus, h_y_modulus, h_residues)}"
        )

    interval_checks = {}
    for n3 in feasible_x:
        low_y, high_y = y_interval(h, n3, 4)
        expected_low = ceil_multiple(Q(2 * n3), 4)
        expected_high = 4 * n3
        if (low_y, high_y) != (expected_low, expected_high):
            raise AssertionError(
                f"Unexpected h11 interval at n3={n3}: {(low_y, high_y)}"
            )
        if low_y > high_y or not all_nonnegative_integral(h, n3, high_y):
            raise AssertionError(f"Seven-vertex formulas unexpectedly infeasible at n3={n3}")
        if n3 in (0, 3, 705, 4158):
            interval_checks[str(n3)] = {
                "h11_min": low_y,
                "h11_max": high_y,
                "number_of_multiples_of_4": (high_y - low_y) // 4 + 1,
            }

    incumbent = tuple(n3 for n3 in feasible_x if n3 >= 705)
    if incumbent != tuple(range(705, 4159, 3)):
        raise AssertionError("Incumbent-feasible n3 values are not 705,708,...,4158")

    finite_upper_bounds = []
    for index, form in n6.items():
        if form.x < 0:
            bound = form.c / (-form.x)
            finite_upper_bounds.append(
                {
                    "count": f"n_{index}",
                    "bound": fraction_text(bound),
                    "floor": floor_fraction(bound),
                }
            )
    finite_upper_bounds.sort(key=lambda item: Fraction(item["bound"]))

    h_edge_distribution: dict[str, int] = {}
    for mask in classes7h:
        key = str(mask.bit_count())
        h_edge_distribution[key] = h_edge_distribution.get(key, 0) + 1

    incumbent_n3 = 705
    incumbent_y_low, incumbent_y_high = y_interval(h, incumbent_n3, 4)
    incumbent_hexagons = n6[12].evaluate(incumbent_n3)
    incumbent_h0_min = h[0].evaluate(incumbent_n3, incumbent_y_high)
    incumbent_h0_max = h[0].evaluate(incumbent_n3, incumbent_y_low)
    if not all(
        value.denominator == 1
        for value in (incumbent_hexagons, incumbent_h0_min, incumbent_h0_max)
    ):
        raise AssertionError("Collateral cycle counts are unexpectedly nonintegral")

    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": "Exact linear, nonnegativity, integrality, and congruence feasibility of published six-vertex and Hamiltonian seven-vertex count formulas at srg(99,14,1,2)",
        "parameters": {"n": N, "k": K, "lambda": 1, "mu": 2},
        "source_freeze": SOURCE_FREEZE,
        "formula_tables": {
            "four_count": len(l),
            "five_count": len(m),
            "six_count": len(n6),
            "hamiltonian_seven_count": len(h),
            "four_affine_sha256": affine_digest(l),
            "five_affine_sha256": affine_digest(m),
            "six_affine_sha256": affine_digest(n6),
            "seven_affine_sha256": affine_digest(h),
            "six": {str(index): form.to_json() for index, form in sorted(n6.items())},
            "seven": {str(index): form.to_json() for index, form in sorted(h.items())},
        },
        "aggregate_checks": {
            "sum_four_counts": math.comb(N, 4),
            "sum_five_counts": math.comb(N, 5),
            "sum_six_counts": math.comb(N, 6),
            "sum_six_n3_coefficient": "0",
        },
        "identity_checks": {
            "four_to_five_raw": "PASS_9_OF_9",
            "five_to_six_raw": "FAIL_1_OF_21",
            "five_to_six_raw_failure": {
                "equation": "m_7(n-5)",
                "residual": "n_23",
                "printed_N23_column_sum": 5,
                "required_vertex_deletion_column_sum": 6,
            },
            "five_to_six_explicit_correction": "add +n_23 to the m_7 equation",
            "five_to_six_corrected": "PASS_21_OF_21",
            "seven_displayed_identities": f"PASS_{len(h_residuals)}_OF_{len(h_residuals)}",
        },
        "independent_graph_census": {
            **class_counts,
            "criterion": "inside common neighbors <=1 for an edge and <=2 for a nonedge",
            "hamiltonian_7_coverage": "fixed labeled C7 plus every subset of its 14 chords, then canonicalized",
            "hamiltonian_7_edge_count_distribution": h_edge_distribution,
            "source_index_alignment": {
                "L_to_canonical_positions_zero_based": list(l_mapping),
                "M_to_canonical_positions_zero_based": list(m_mapping),
                "N_to_canonical_positions_zero_based": list(n_mapping),
                "all_mappings_bijective_after_explicit_N23_repair": True,
            },
            "N3_definition_alignment": {
                "source_index": 3,
                "canonical_mask": source_n3_mask,
                **shape,
                "interpretation": "two disjoint triangles joined by exactly two independent cross edges",
                "not_independent_triples": True,
            },
            "N23_raw_deck_defect": {
                "expected_source_M_order": expected_n23_deck_source_order,
                "printed_source_M_order": printed_n23_deck,
                "difference_source_M_order": difference,
            },
        },
        "six_vertex_feasibility": {
            "exact_n3_min": 0,
            "lower_facet": "n_3=n3>=0",
            "exact_n3_max": 4158,
            "upper_facet": "n_1=1386-n3/3>=0",
            "integrality": "n3 == 0 (mod 3)",
            "feasible_sequence": "0,3,...,4158",
            "feasible_value_count": len(feasible_x),
            "finite_upper_bounds_sorted": finite_upper_bounds,
        },
        "hamiltonian_seven_feasibility": {
            "integrality": "h11 == 0 (mod 4)",
            "lower_facet": "h_16=h11-2n3>=0",
            "upper_facet": "h_18=n3-h11/4>=0",
            "exact_interval": "ceil_to_multiple_of_4(2*n3) <= h11 <= 4*n3",
            "universal_feasible_choice": "h11=4*n3",
            "checks": interval_checks,
            "additional_n3_restriction": "NONE",
        },
        "incumbent_705_intersection": {
            "feasible_n3_sequence": "705,708,...,4158",
            "feasible_n3_value_count": len(incumbent),
            "n3_705_h11_min": interval_checks["705"]["h11_min"],
            "n3_705_h11_max": interval_checks["705"]["h11_max"],
            "n3_705_feasible_h11_count": interval_checks["705"]["number_of_multiples_of_4"],
            "improves_n3_at_least_705": False,
            "conflicts_with_n3_at_least_705": False,
        },
        "collateral_cycle_count_consequences": {
            "hexagon_identity": "n_12=209286+n3",
            "hexagons_at_n3_at_least_705": f">={int(incumbent_hexagons)}",
            "paper_h0_identity": "h_0=1247400-10*n3-h11",
            "paper_h0_range_at_n3_705": [
                int(incumbent_h0_min),
                int(incumbent_h0_max),
            ],
            "paper_h0_nonnegativity_is_not_active_on_full_feasible_domain": True,
        },
        "conclusion": {
            "strongest_published_count_consequence": "n3 is a multiple of 3 and n3<=4158",
            "new_lower_bound_beyond_705": None,
            "upper_bound_below_705": None,
            "status": "RIGOROUS_INCONCLUSIVE_EXHAUSTION_OF_ENCODED_PUBLISHED_COUNTS",
            "target_resolution": "UNKNOWN",
            "novelty": "NOT_ASSESSED",
        },
    }


def canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)

    payload = build_results()
    encoded = canonical_json_bytes(payload)
    if args.verify is not None:
        actual = args.verify.read_bytes()
        if actual != encoded:
            print(f"FAIL: {args.verify} is not the canonical exact result", file=sys.stderr)
            return 1
        print(f"PASS: {args.verify} matches the canonical exact result")
        return 0
    if args.output is not None:
        args.output.write_bytes(encoded)
        print(f"Wrote {args.output}")
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
