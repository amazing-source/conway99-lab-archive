"""Exact invariant-basis model for the Wave139 GF(4) graph-state LP."""

from __future__ import annotations

import itertools
from functools import lru_cache
from math import comb


N = 99
ORDER = 1 << 99
TARGET_STATE = (41, 4, 54)  # (nI, nY, nR)

IMAGE_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    0: 1,
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    99: 1,
}
SUPPORT_LOWER = {
    (84, 0, 15): 99,
    (73, 2, 24): 693,
    (73, 0, 26): 4158,
    (66, 0, 33): 70686,
    (62, 0, 37): 27720,
    (66, 2, 31): 41580,
    (62, 2, 35): 8316,
    (64, 2, 33): 8316,
    (60, 0, 39): 231,
}
PURE_Y_ZERO_WEIGHTS = set(range(2, 14, 2)) | {94, 96, 98}


def states() -> list[tuple[int, int, int]]:
    """Allowed states in the documented order ``(nI,nY,nR)``."""
    return [
        (ni, ny, N - ni - ny)
        for ny in range(0, N + 1, 2)
        for ni in range(N - ny, -1, -1)
    ]


def partitions3(total: int = N) -> list[tuple[int, int, int]]:
    return [
        (a, b, total - a - b)
        for a in range(total, -1, -1)
        for b in range(min(a, total - a), -1, -1)
        if b >= total - a - b >= 0
    ]


def distinct_permutations(partition):
    return sorted(set(itertools.permutations(partition)))


@lru_cache(maxsize=None)
def signed_convolution(a: int, b: int, degree: int) -> int:
    """Coefficient of v^degree in (z+v)^a(z-v)^b."""
    return sum(
        comb(a, left) * comb(b, degree - left) * (-1) ** (degree - left)
        for left in range(max(0, degree - b), min(a, degree) + 1)
    )


def ordered_term_coefficient(
    exponents: tuple[int, int, int],
    state: tuple[int, int, int],
) -> int:
    """Coefficient after x1=u+v+2w, x2=u-v+2w, x3=2u."""
    a, b, c = exponents
    ni, ny, nr = state
    if ni + ny + nr != N or ny > a + b:
        return 0
    remaining = a + b - ny
    if nr > remaining:
        return 0
    if ni != remaining - nr + c:
        return 0
    return (
        (1 << (nr + c))
        * comb(remaining, nr)
        * signed_convolution(a, b, ny)
    )


def basis_coefficient(
    partition: tuple[int, int, int],
    state: tuple[int, int, int],
) -> int:
    return sum(
        ordered_term_coefficient(exponents, state)
        for exponents in distinct_permutations(partition)
    )


def basis_evaluation(partition: tuple[int, int, int]) -> int:
    """Evaluate m_partition(x1,x2,x3) at (u,v,w)=(1,1,1)."""
    return sum(
        (4 ** exponents[0])
        * (2 ** exponents[1])
        * (2 ** exponents[2])
        for exponents in distinct_permutations(partition)
    )


def lower_bounds() -> dict[tuple[int, int, int], int]:
    lower = dict(SUPPORT_LOWER)
    lower[(99, 0, 0)] = 1
    # Pure-Y graph-state words are exactly im(A).
    for weight, value in IMAGE_LOWER.items():
        state = (N - weight, weight, 0)
        lower[state] = max(lower.get(state, 0), value)
    # The merged nY=0 shell contains every pure-X word from ker(A).
    dual = dict(DUAL_BASE_LOWER)
    for weight, value in list(dual.items()):
        dual[N - weight] = max(dual.get(N - weight, 0), value)
    for weight, value in dual.items():
        state = (N - weight, 0, weight)
        lower[state] = max(lower.get(state, 0), value)
    lower[TARGET_STATE] = max(lower.get(TARGET_STATE, 0), 708)
    return lower


def exact_rank_record() -> dict:
    allowed = len(states())
    invariant_dimension = len(partitions3())
    return {
        "format": "wave139-gf4-invariant-rank-v1",
        "claim_label": "DERIVED",
        "state_order": ["nI", "nY", "nR"],
        "raw_composition_states": comb(N + 2, 2),
        "odd_nY_zero_states": comb(N + 2, 2) - allowed,
        "even_nY_variables_before_self_duality": allowed,
        "self_dual_even_nY_solution_dimension": invariant_dimension,
        "combined_equality_rank": allowed - invariant_dimension,
        "derivation": (
            "Normalized MacWilliams S and nY-parity P are involutions "
            "with (SP)^3=1 and traces of the 3D permutation representation. "
            "Their common fixed ring is Q[e1,e2,e3] of degrees 1,2,3; "
            "the degree-99 dimension is the number of partitions of 99 "
            "into at most three parts."
        ),
        "invariant_generators": {
            "permuted_linear_forms": [
                "x1=u+v+2w",
                "x2=u-v+2w",
                "x3=2u",
            ],
            "basis": (
                "monomial symmetric functions m_lambda(x1,x2,x3), "
                "lambda partitions 99 with at most three parts"
            ),
        },
        "target_state": list(TARGET_STATE),
        "target_logic": (
            "P[41,4,54] is at least n3 because every induced N3 input "
            "maps injectively to this composition."
        ),
    }
