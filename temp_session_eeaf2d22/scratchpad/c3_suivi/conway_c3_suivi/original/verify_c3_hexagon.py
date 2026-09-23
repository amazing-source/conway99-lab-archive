#!/usr/bin/env python3
"""Exact local certificate for the C3 triangle-orbit hexagon obstruction.

Only Python's standard library is used. This does NOT decide Conway-99,
exclude C3, or prove that a quotient has an SRG lift. It checks the arithmetic
in the accompanying human proof: the six triangular orbits induce exactly C6,
and the total phase h around that C6 must be zero in F3.

Run: python verify_c3_hexagon.py
"""
from __future__ import annotations

import itertools
import json
from typing import Sequence

Matrix = list[list[int]]
U = (-1, -1, 0, 1, 1, 0)
V = (1, 0, -1, -1, 0, 1)
PAIRS = tuple(itertools.combinations(range(6), 2))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def dot(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(x * y for x, y in zip(a, b, strict=True))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    require(bool(a) and bool(b), 'Empty matrix')
    require(len(a[0]) == len(b), 'Incompatible matrix shapes')
    bt = list(zip(*b, strict=True))
    return [[dot(row, col) for col in bt] for row in a]


def local_adjacency(h: int) -> Matrix:
    require(h in (0, 1, 2), 'h must lie in F3')
    p = [[0] * 18 for _ in range(18)]
    for i in range(6):
        for a, b in itertools.combinations(range(3), 2):
            p[3 * i + a][3 * i + b] = 1
            p[3 * i + b][3 * i + a] = 1
    for i in range(6):
        j = (i + 1) % 6
        phase = h if i == 5 else 0
        for a in range(3):
            x, y = 3 * i + a, 3 * j + (a + phase) % 3
            p[x][y] = p[y][x] = 1
    require(all(sum(row) == 4 for row in p), 'Local degree must be four')
    return p


def residual(p: Matrix) -> Matrix:
    pp = multiply(p, p)
    return [[12 * int(i == j) + 2 - pp[i][j] - p[i][j]
             for j in range(18)] for i in range(18)]


def phase_moment(r: Matrix) -> Matrix:
    return [[sum(a * r[3 * i][3 * j + a] for a in range(3)) % 3
             for j in range(6)] for i in range(6)]


def wedge_value(d: Matrix) -> int:
    return sum((U[i] * V[j] - U[j] * V[i]) * d[i][j]
               for i, j in PAIRS) % 3


def patterns():
    # One representative of every orbit of phase vectors under common shift.
    yield (-1,) * 6
    for mask in range(1, 64):
        support = [i for i in range(6) if mask & (1 << i)]
        for tail in itertools.product(range(3), repeat=len(support) - 1):
            phase = [-1] * 6
            for i, value in zip(support, (0,) + tail, strict=True):
                phase[i] = value
            yield tuple(phase)


def verify() -> dict:
    f = [[int((i - j) % 6 in (1, 5)) for j in range(6)] for i in range(6)]
    ff = multiply(f, f)
    g = [[6 * int(i == j) + 6 - 5 * f[i][j] - ff[i][j]
          for j in range(6)] for i in range(6)]
    require(all(dot(row, U) == 0 for row in g), 'U is not in ker(G)')
    require(all(dot(row, V) == 0 for row in g), 'V is not in ker(G)')

    total, allowed = 0, 0
    for p in patterns():
        total += 1
        s = tuple(int(a >= 0) for a in p)
        if dot(U, s) != 0 or dot(V, s) != 0:
            continue
        allowed += 1
        d = [[(s[i] * s[j] * (p[j] - p[i])) % 3
              for j in range(6)] for i in range(6)]
        require(wedge_value(d) == 0, 'A compatible pattern breaks the identity')
    require((total, allowed) == (1366, 352), 'Unexpected pattern census')

    cases = []
    for h in range(3):
        r = residual(local_adjacency(h))
        for kernel in (U, V):
            lift = tuple(kernel[i] for i in range(6) for _ in range(3))
            require(all(dot(row, lift) == 0 for row in r), 'Lifted kernel fails')
        d = phase_moment(r)
        require(all((d[i][j] + d[j][i]) % 3 == 0
                    for i in range(6) for j in range(6)), 'D is not skew')
        value = wedge_value(d)
        require(value == (-h) % 3, 'Expected obstruction -h failed')
        cases.append({'holonomy': h, 'forced_residue_mod3': value,
                      'excluded_by_this_test': value != 0})

    # Hostile control: a mutation of one phase moment breaks the zero case.
    broken = phase_moment(residual(local_adjacency(0)))
    broken[0][1] = (broken[0][1] + 1) % 3
    broken[1][0] = -broken[0][1] % 3
    require(wedge_value(broken) != 0, 'Hostile control was not detected')
    return {'status': 'PASS_EXACT_LOCAL_HEXAGON_CERTIFICATE',
            'arithmetic': 'integers and F3, no floating point or SAT solver',
            'phase_orbit_patterns': total,
            'kernel_compatible_phase_patterns': allowed,
            'cases': cases, 'hostile_control': 'detected',
            'scope': 'Only nonzero holonomy on the six triangular orbits when their induced orbit graph is C6; C3 is NOT excluded.'}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
