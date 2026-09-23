#!/usr/bin/env python3
"""Exact, standard-library audit of the six-triangular-orbit kernel screen.

Input: cases.json (156 representatives). No SAT, floating point or network.
The checker verifies completeness up to isomorphism by covering all 2^15
labelled simple graphs with disjoint relabelling orbits. It then reconstructs
all Grams, integral kernels and phase equations independently.

This is NOT an enumeration of Conway graphs or of complete orbit quotients.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd, lcm
from pathlib import Path
import json
import time

N = 6
PAIRS = list(combinations(range(N), 2))
INDEX = {e: i for i, e in enumerate(PAIRS)}
Matrix = list[list[int]]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def zeros(n: int, m: int | None = None) -> Matrix:
    return [[0] * (n if m is None else m) for _ in range(n)]


def mul(a: Matrix, b: Matrix) -> Matrix:
    bt = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in bt] for row in a]


def det(a: Matrix) -> int:
    """Fraction-free Bareiss determinant with exact divisions and pivoting."""
    n = len(a)
    if n == 0:
        return 1
    b = [row[:] for row in a]
    old = 1
    sign = 1
    for k in range(n-1):
        p = next((i for i in range(k, n) if b[i][k]), None)
        if p is None:
            return 0
        if p != k:
            b[k], b[p] = b[p], b[k]
            sign *= -1
        pivot = b[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = pivot*b[i][j] - b[i][k]*b[k][j]
                require(numerator % old == 0, 'Non-exact Bareiss division')
                b[i][j] = numerator // old
            b[i][k] = 0
        old = pivot
    return sign*b[-1][-1]


def integer_kernel(a: Matrix) -> list[list[int]]:
    """Primitive rational-nullspace vectors, followed by a saturation check."""
    b = [[Fraction(x) for x in row] for row in a]
    n, m = len(b), len(b[0])
    pivots = []
    r = 0
    for j in range(m):
        p = next((i for i in range(r, n) if b[i][j]), None)
        if p is None:
            continue
        b[r], b[p] = b[p], b[r]
        q = b[r][j]
        b[r] = [x/q for x in b[r]]
        for i in range(n):
            if i != r and b[i][j]:
                q = b[i][j]
                b[i] = [x-q*y for x,y in zip(b[i],b[r])]
        pivots.append(j)
        r += 1
        if r == n:
            break
    basis = []
    for free in (j for j in range(m) if j not in pivots):
        v = [Fraction(0)]*m
        v[free] = Fraction(1)
        for i, pivot in enumerate(pivots):
            v[pivot] = -b[i][free]
        den = lcm(*(x.denominator for x in v))
        w = [int(den*x) for x in v]
        g = gcd(*w)
        w = [x//g for x in w]
        require(all(sum(x*y for x,y in zip(row,w)) == 0 for row in a),
                'Invalid kernel vector')
        basis.append(w)
    # Without saturation a rational basis could miss mod-3 constraints.
    if basis:
        d = 0
        for ii in combinations(range(m), len(basis)):
            minor = [[v[i] for v in basis] for i in ii]
            d = gcd(d, abs(det(minor)))
        require(d == 1, 'Kernel lattice basis not saturated')
    return basis


def rank3(a: Matrix) -> int:
    if not a:
        return 0
    b = [[x % 3 for x in row] for row in a]
    n, m, r = len(b), len(b[0]), 0
    for j in range(m):
        p = next((i for i in range(r,n) if b[i][j]), None)
        if p is None:
            continue
        b[r], b[p] = b[p], b[r]
        inv = pow(b[r][j], -1, 3)
        b[r] = [(x*inv) % 3 for x in b[r]]
        for i in range(n):
            if i != r and b[i][j]:
                q = b[i][j]
                b[i] = [(x-q*y) % 3 for x,y in zip(b[i],b[r])]
        r += 1
        if r == n:
            break
    return r


def adjacency(mask: int) -> Matrix:
    a = zeros(N)
    for k,(i,j) in enumerate(PAIRS):
        if mask & (1 << k):
            a[i][j] = a[j][i] = 1
    return a


def gram(f: Matrix) -> Matrix:
    f2 = mul(f,f)
    return [[6*int(i==j)+6-5*f[i][j]-f2[i][j]
             for j in range(N)] for i in range(N)]


def moment_direct(f: Matrix, e: Matrix) -> Matrix:
    """Construct the 18-vertex motif and take moments of 12I+2J-P^2-P."""
    p = zeros(18)
    for i in range(N):
        for a in range(3):
            for b in range(3):
                if a != b:
                    p[3*i+a][3*i+b] = 1
    for i,j in PAIRS:
        if f[i][j]:
            for a in range(3):
                u, v = 3*i+a, 3*j+(a+e[i][j]) % 3
                p[u][v] = p[v][u] = 1
    p2 = mul(p,p)
    d = zeros(N)
    for i in range(N):
        for j in range(N):
            d[i][j] = sum(a*(12*int(3*i==3*j+a)+2
                             -p2[3*i][3*j+a]-p[3*i][3*j+a])
                          for a in range(3)) % 3
    return d


def moment_formula(f: Matrix, e: Matrix) -> Matrix:
    fe, ef = mul(f,e), mul(e,f)
    return [[(e[i][j]-fe[i][j]-ef[i][j]) % 3
             for j in range(N)] for i in range(N)]


def bilinear(u: list[int], a: Matrix, v: list[int]) -> int:
    return sum(u[i]*a[i][j]*v[j] for i in range(N) for j in range(N)) % 3


def coverage(cases: list[dict]) -> None:
    all_perms = list(permutations(range(N)))
    seen = set()
    for case in cases:
        mask = case['mask']
        require(0 <= mask < 1 << len(PAIRS), 'Invalid graph mask')
        edges = [e for k,e in enumerate(PAIRS) if mask & (1 << k)]
        orbit = set()
        for p in all_perms:
            new = 0
            for i,j in edges:
                edge = tuple(sorted((p[i],p[j])))
                new |= 1 << INDEX[edge]
            orbit.add(new)
        require(seen.isdisjoint(orbit), 'Repeated isomorphism class')
        seen.update(orbit)
    require(len(seen) == 1 << len(PAIRS), 'Incomplete labelled-graph coverage')


def audit(cases: list[dict]) -> dict:
    coverage(cases)
    counts = Counter()
    nullities = Counter()
    nontrivial = []
    checked_unit_phases = 0
    classified = []
    for case in cases:
        mask = case['mask']
        f = adjacency(mask)
        g = gram(f)
        negative = next(((i,j,g[i][j]) for i in range(N)
                         for j in range(N) if g[i][j] < 0),None)
        if negative is not None:
            require(case['status'] == 'negative_entry', 'Status mismatch')
            counts['negative_entry'] += 1
            classified.append({'mask':mask,'status':'negative_entry',
                               'certificate':negative})
            continue
        bad = None
        for size in range(1,N+1):
            for ix in combinations(range(N),size):
                d = det([[g[i][j] for j in ix] for i in ix])
                if d < 0:
                    bad = (ix,d)
                    break
            if bad is not None:
                break
        if bad is not None:
            require(case['status'] == 'not_psd', 'Status mismatch')
            counts['not_psd'] += 1
            classified.append({'mask':mask,'status':'not_psd',
                               'certificate':bad})
            continue
        require(case['status'] == 'psd', 'Status mismatch')
        counts['psd'] += 1
        u = integer_kernel(g)
        nullities[len(u)] += 1
        require(len(u) == case['nullity'], 'Nullity mismatch')
        edges = [(i,j) for i,j in PAIRS if f[i][j]]
        moments = []
        for i,j in edges:
            e = zeros(N)
            e[i][j],e[j][i] = 1,-1
            formula = moment_formula(f,e)
            require(formula == moment_direct(f,e), 'Phase-sign mismatch')
            checked_unit_phases += 1
            moments.append(formula)
        equations = [[bilinear(a,d,b) for d in moments]
                     for a,b in combinations(u,2)]
        rank = rank3(equations)
        require(rank == case['constraint_rank'], 'Constraint rank mismatch')
        record = {'mask':mask,'status':'psd','edges':edges,
                  'nullity':len(u),'kernel_basis':u,
                  'phase_equations_F3':equations,'phase_rank':rank}
        classified.append(record)
        if rank:
            require(all(sum(row)==2 for row in f), 'Non-cycle survivor')
            # Connectivity, in addition to 2-regularity, distinguishes C6 from 2C3.
            reached, todo = {0},[0]
            while todo:
                i = todo.pop()
                for j in range(N):
                    if f[i][j] and j not in reached:
                        reached.add(j); todo.append(j)
            require(len(reached)==6, 'Not a connected C6')
            nontrivial.append(record)
    require(dict(counts) == {'negative_entry':87,'not_psd':25,'psd':44},
            'Unexpected classification totals')
    require(len(nontrivial)==1 and nontrivial[0]['phase_rank']==1,
            'Unexpected nontrivial first-moment cases')
    return {'verdict':'PASS_EXACT_SIX_MOTIF_KERNEL_SCREEN',
            'isomorphism_classes':len(cases),'labelled_graphs_covered':2**15,
            'gram_screen_counts':dict(counts),
            'nullities_among_psd':dict(sorted(nullities.items())),
            'unit_phase_identity_checks':checked_unit_phases,
            'nontrivial_first_moment_cases':nontrivial,
            'scope':'Only this local kernel/first-moment screen. PSD does not imply binary-Gram feasibility or a Conway lift. No C3 branch exclusion.',
            'classified_cases':classified}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',type=Path,default=Path(__file__).with_name('cases.json'))
    parser.add_argument('--out',type=Path,default=None)
    args = parser.parse_args()
    start = time.monotonic()
    data = json.loads(args.cases.read_text(encoding='utf-8'))
    result = audit(data['cases'])
    if args.out is not None:
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for key,value in result.items():
        if key not in ('classified_cases','nontrivial_first_moment_cases'):
            print(f'{key}: {value}')
    print(f'nontrivial patterns: C6 only, rank {result["nontrivial_first_moment_cases"][0]["phase_rank"]}')
    print(f'elapsed_seconds: {time.monotonic()-start:.3f}')
    print(result['verdict'])


if __name__ == '__main__':
    main()
