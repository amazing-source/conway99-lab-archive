"""s=1 / s=0 structure of the outer graph H (involution branch of Conway-99).

Inner vertices (i,s), i=1..7, s in {0,1}; sigma flips s.  Labels = unordered pairs of inner vertices in
different blocks (84).  For a label u={a,b}: exactly one H-neighbour contains a, one contains b, one contains a',
one contains b', and two contain each of the other 10 inner vertices (constraint (I) of the orbit model).
Hence for every inner c the 12 labels L_c carry a perfect matching M_c (the 's=1' edges, |u cap v|=1) and the
remaining 10 edges per vertex ('s=0', u cap v = empty) lie in 140 edge-disjoint triangles of pairwise disjoint
labels (lambda=1).  This module provides the combinatorial objects and exact counts; nothing here is a solver.
"""
import itertools, random
from collections import Counter

M = 7
INNER = [(i, s) for i in range(1, M + 1) for s in (0, 1)]
def sig(p): return (p[0], 1 - p[1])
LABELS = [frozenset((p, q)) for p, q in itertools.combinations(INNER, 2) if p[0] != q[0]]
assert len(LABELS) == 84
LIDX = {u: k for k, u in enumerate(LABELS)}
def sigl(u): return frozenset(sig(p) for p in u)
def Lc(c): return [u for u in LABELS if c in u]
# orbit representatives exactly as in orbit_sat.py
OUTER = [(i, j, e) for i in range(1, M + 1) for j in range(i + 1, M + 1) for e in (0, 1)]
REP = [frozenset([(i, 0), (j, e)]) for (i, j, e) in OUTER]
TREP = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in OUTER]
ORB = {}
for U, (r, t) in enumerate(zip(REP, TREP)):
    ORB[r] = (U, 0); ORB[t] = (U, 1)

def bit(u, w):
    """Return ('a'|'b', U, V) such that A[u,w] equals the orbit-model variable a_UV or b_UV (U != V)."""
    U, su = ORB[u]; V, sv = ORB[w]
    assert U != V
    return ('a' if su == sv else 'b', U, V)

def perfect_matchings(items):
    """All perfect matchings of the list `items` (as lists of frozenset pairs)."""
    items = list(items)
    if not items:
        yield []
        return
    first = items[0]
    for k in range(1, len(items)):
        rest = items[1:k] + items[k + 1:]
        for m in perfect_matchings(rest):
            yield [frozenset((first, items[k]))] + m

def matching_type(c, Mc):
    """Cycle type of M_c together with the block matching, as a partition of 6 (lengths of the 2l-cycles)."""
    # vertices of L_c <-> the 12 inner vertices d with block(d) != block(c)
    # M_c u {block edges d-d'} is a 2-regular multigraph on 12 vertices: components are even cycles
    other = lambda u: next(iter(u - {c}))
    verts = [d for d in INNER if d[0] != c[0]]
    parent = {d: d for d in verts}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y): parent[find(x)] = find(y)
    for e in Mc:
        u, v = tuple(e); union(other(u), other(v))
    for d in verts: union(d, sig(d))
    sizes = Counter(find(d) for d in verts)
    return tuple(sorted((n // 2 for n in sizes.values()), reverse=True))

def random_matching(c, rng):
    L = Lc(c); rng.shuffle(L)
    return [frozenset((L[2 * k], L[2 * k + 1])) for k in range(6)]

def s1_edges_from(matchings):
    """matchings: dict c -> M_c for c=(i,0). Returns set of all 84 s=1 edges (sigma closure)."""
    E = set()
    for c, Mc in matchings.items():
        for e in Mc:
            E.add(e); E.add(frozenset(sigl(u) for u in e))
    return E

def c1_violations(E):
    """Number of label triangles {p,q},{q,r},{r,p} (p,q,r in three distinct blocks) all of whose edges are s=1."""
    n = 0
    for p, q, r in itertools.combinations(INNER, 3):
        if len({p[0], q[0], r[0]}) < 3: continue
        u, v, w = frozenset((p, q)), frozenset((q, r)), frozenset((r, p))
        if frozenset((u, v)) in E and frozenset((v, w)) in E and frozenset((w, u)) in E: n += 1
    return n

def candidate_triangles():
    T = []
    for u, v, w in itertools.combinations(LABELS, 3):
        if not (u & v) and not (u & w) and not (v & w): T.append(frozenset((u, v, w)))
    return T

if __name__ == "__main__":
    import sys, time
    t0 = time.time()
    # --- matchings: count and types under the block stabiliser
    c = (1, 0)
    allM = list(perfect_matchings(Lc(c)))
    print("perfect matchings of L_c:", len(allM))
    types = Counter(matching_type(c, m) for m in allM)
    print("types (partition of 6 -> number of matchings):")
    for t in sorted(types, key=lambda t: (-len(t), t)): print("   ", t, types[t])
    print("number of types:", len(types), " sum:", sum(types.values()))
    # --- candidate triangles
    T = candidate_triangles()
    print("candidate s=0 triangles (pairwise disjoint labels):", len(T))
    per_label = Counter(); per_pair = Counter()
    for tri in T:
        for u in tri: per_label[u] += 1
        for u, v in itertools.combinations(tri, 2): per_pair[frozenset((u, v))] += 1
    print("  per label: min/max", min(per_label.values()), max(per_label.values()))
    print("  disjoint label pairs:", len(per_pair), " triangles per pair: ", sorted(Counter(per_pair.values()).items()))
    # sigma-orbits of triangles
    def sigt(tri): return frozenset(sigl(u) for u in tri)
    fixed = sum(1 for tri in T if sigt(tri) == tri)
    print("  sigma-fixed triangles:", fixed, " sigma-orbits:", (len(T) - fixed) // 2 + fixed)
    # block-disjoint triangles (6 distinct blocks)
    bd = sum(1 for tri in T if len({p[0] for u in tri for p in u}) == 6)
    print("  block-disjoint triangles (6 distinct blocks):", bd)
    # --- C1: fraction of random 7-tuples of matchings that violate the no-s=1-triangle rule
    rng = random.Random(1)
    N = 20000; bad = 0; viol = Counter()
    for _ in range(N):
        mt = {(i, 0): random_matching((i, 0), rng) for i in range(1, M + 1)}
        E = s1_edges_from(mt); v = c1_violations(E); viol[v] += 1
        if v: bad += 1
    print("C1 (s=1 triangles) on %d random 7-tuples: violating fraction = %.4f ; distribution %s" % (N, bad / N, sorted(viol.items())))
    print("label triangles (3 blocks, one vertex each): 35*8 =", 35 * 8, " expected violations per tuple 280/11^3 = %.4f" % (280 / 1331))
    print("time %.1fs" % (time.time() - t0))
