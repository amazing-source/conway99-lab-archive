"""Common orbit/index definitions and exact verification helpers for the
Z2-quotient signed-matrix problem (S*S + S = (k-2) I).
"""
import itertools
import numpy as np


def build_orbits(m):
    """Return (inner, outer) orbit lists.
    inner[i-1] = ('A', i)  for i = 1..m
    outer = [('U', i, j, e) for i<j in 1..m, e in (0,1)]
    """
    inner = [('A', i) for i in range(1, m + 1)]
    outer = []
    for i in range(1, m + 1):
        for j in range(i + 1, m + 1):
            for e in (0, 1):
                outer.append(('U', i, j, e))
    return inner, outer


def outer_inner_sign(U, l):
    """S[U, A_l] for outer orbit U=('U',i,j,e) and inner index l (1-based). 0 if l not in {i,j}."""
    _, i, j, e = U
    if l == i:
        return 1
    if l == j:
        return -1 if e == 1 else 1
    return 0


def cross_const(U, V, m):
    """C_UV = sum_l S[U,A_l]*S[V,A_l] over inner indices l=1..m (a fixed integer)."""
    total = 0
    for l in range(1, m + 1):
        total += outer_inner_sign(U, l) * outer_inner_sign(V, l)
    return total


def build_full_matrix(m, outer, diag, offdiag):
    """Construct the full N x N integer numpy matrix.

    diag: dict outer_orbit -> S[U,U] value (0 or -1)
    offdiag: dict frozenset({U,V}) -> value in {-1,0,1} for U != V outer orbits
    """
    inner, _ = build_orbits(m)
    idx = {orb: k for k, orb in enumerate(inner + outer)}
    N = len(inner) + len(outer)
    S = np.zeros((N, N), dtype=np.int64)
    # inner-inner
    for i in range(1, m + 1):
        S[idx[('A', i)], idx[('A', i)]] = -1
    # outer-inner and inner-outer
    for U in outer:
        uidx = idx[U]
        _, i, j, e = U
        S[uidx, idx[('A', i)]] = 1
        S[idx[('A', i)], uidx] = 1
        sj = -1 if e == 1 else 1
        S[uidx, idx[('A', j)]] = sj
        S[idx[('A', j)], uidx] = sj
    # outer diagonal
    for U in outer:
        S[idx[U], idx[U]] = diag[U]
    # outer-outer off diagonal
    for U in outer:
        for V in outer:
            if U == V:
                continue
            key = frozenset((U, V))
            val = offdiag[key]
            S[idx[U], idx[V]] = val
    return S, idx


def verify(S, k):
    N = S.shape[0]
    lhs = S @ S + S
    rhs = (k - 2) * np.eye(N, dtype=np.int64)
    return np.array_equal(lhs, rhs), lhs
