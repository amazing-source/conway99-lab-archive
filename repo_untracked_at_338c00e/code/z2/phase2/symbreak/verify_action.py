"""Verification of the induced action (task 1): homomorphism, constraint-set invariance at m=7,
solution-to-solution on k=4 (all 8 group elements, all solutions), and soundness/completeness of the
lex-leader encoding on a relaxed (R,D,I) model at m=7 for the 'one' stabiliser."""
import sys, random, time, itertools
sys.path.insert(0, r"C:\Users\RESEARCHER\Desktop\conway99-involution\code\z2\phase2\symbreak")
from symgroup import *
from pysat.solvers import Solver
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
import numpy as np

random.seed(1)
# ---------- 1. m=7: homomorphism + constraint-set invariance
m = 7; t0 = time.time()
cnf, pool, outer, rep, trep, A, B = build(m, "none")
prim = sorted(set(A.values()) | set(B.values()))
print("m=7 primary vars:", len(prim), "top:", pool.top, "clauses:", len(cnf.clauses))
G = full_group(m); print("|G| =", len(G))
gens = generators_full(m)
sample = gens + [random.choice(G) for _ in range(6)]
# homomorphism: Pi_{g h} = Pi_g o Pi_h
for _ in range(20):
    g, h = random.choice(G), random.choice(G)
    Pg, Ph, Pgh = var_perm(g, outer, A, B), var_perm(h, outer, A, B), var_perm(compose(g, h), outer, A, B)
    assert all(Pgh[x] == Pg[Ph[x]] for x in prim), "not a homomorphism"
print("homomorphism check OK (20 random pairs)")
# permutation property
for g in sample:
    P = var_perm(g, outer, A, B); assert sorted(P.values()) == prim
print("bijection OK")
cons = semantic_constraints(m, A, B, outer)
cset = set(cons); print("semantic constraints:", len(cons), "distinct:", len(cset))
by_type = {}
for c in cons: by_type.setdefault(c[0], set()).add(c)
for g in sample:
    P = var_perm(g, outer, A, B)
    mapped = set(map_constraint(c, P) for c in cons)
    assert mapped == cset, "constraint set NOT invariant under %s" % (g,)
    for typ, s in by_type.items():
        assert set(map_constraint(c, P) for c in s) == s, "family %s not invariant" % typ
print("constraint set (R,D,I,P) invariant under generators + 6 random elements, each family separately: OK  (%.1fs)" % (time.time() - t0))
# case groups
for case in ("sib", "one", "dis"):
    print("case", case, "set-stabiliser order:", len(case_group(m, case)))

# ---------- 2. m=2 (k=4): every group element maps every solution to a solution (lift check)
m2 = 2
cnf2, pool2, outer2, rep2, trep2, A2, B2 = build(m2, "none")
prim2 = sorted(set(A2.values()) | set(B2.values()))
sols = []
with Solver(name="cadical195", bootstrap_with=cnf2.clauses) as s:
    while s.solve():
        mod = s.get_model(); val = [l for l in mod if abs(l) in set(prim2)]
        sols.append(frozenset(l for l in val if l > 0)); s.add_clause([-l for l in val])
print("k=4: number of solutions (primary projection):", len(sols))
G2 = full_group(m2)
for g in G2:
    P = var_perm(g, outer2, A2, B2)
    for sol in sols:
        img = frozenset(P[x] for x in sol)
        assert img in sols, "image not a solution"
        model = [x if x in img else -x for x in prim2]
        M, ok = lift(m2, outer2, rep2, trep2, A2, B2, model); assert ok
print("k=4: all %d group elements map all solutions to solutions, lifts verified" % len(G2))

# ---------- 3. m=7 relaxed model (R,D,I only) : lex-leader soundness/completeness test for case 'one' stabiliser
def relaxed(m, case):
    k = 2 * m
    outer = outer_orbits(m); N = len(outer)
    rep = [frozenset([(i, 0), (j, e)]) for (i, j, e) in outer]; trep = [frozenset([(i, 1), (j, 1 - e)]) for (i, j, e) in outer]
    pool = IDPool(); cnf = CNF(); A = {}; B = {}
    for U in range(N):
        for V in range(U + 1, N):
            A[U, V] = A[V, U] = pool.id(("a", U, V)); B[U, V] = B[V, U] = pool.id(("b", U, V))
    def prod(x, y):
        p = pool.id(("p", min(x, y), max(x, y))); cnf.extend([[-p, x], [-p, y], [p, -x, -y]]); return p
    def eq(lits, kk): cnf.extend(CardEnc.equals(lits=lits, bound=kk, vpool=pool, encoding=EncType.seqcounter).clauses)
    inner = [(i, s) for i in range(1, m + 1) for s in (0, 1)]
    for U in range(N):
        others = [V for V in range(N) if V != U]
        eq([A[U, V] for V in others] + [B[U, V] for V in others], k - 2)
        eq([prod(A[U, V], B[U, V]) for V in others], 1)
        for c in inner:
            partner = (c[0], 1 - c[1]); lits = []
            for V in others:
                if c in rep[V]: lits.append(A[U, V])
                if c in trep[V]: lits.append(B[U, V])
            eq(lits, 1 if (c in rep[U] or partner in rep[U]) else 2)
    tgt = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}[case]
    D = outer.index(tgt); cnf.append([A[0, D]]); cnf.append([B[0, D]])
    return cnf, pool, outer, A, B

case = "one"
rc, rpool, router, rA, rB = relaxed(7, case)
rprim = sorted(set(rA.values()) | set(rB.values()))
H = case_group(7, case); print("relaxed model: vars", rpool.top, "clauses", len(rc.clauses), "|H| =", len(H))
perms = [var_perm(g, router, rA, rB) for g in H]
def lexkey(sol):  # vector in variable order (0/1), lex-min = smallest
    return tuple(1 if x in sol else 0 for x in rprim)
# (a) sample solutions of relaxed model, check invariance of solution set under H and find orbit lex-min
with Solver(name="cadical195", bootstrap_with=rc.clauses) as s:
    assert s.solve(); mod = s.get_model(); sol = frozenset(l for l in mod if l > 0 and l in set(rprim))
orbit = set(frozenset(P[x] for x in sol) for P in perms)
print("orbit size of a relaxed solution under H:", len(orbit))
# every image is a solution of the relaxed model?
cnt = 0
with Solver(name="cadical195", bootstrap_with=rc.clauses) as s:
    for img in list(orbit)[:50]:
        assert s.solve(assumptions=[x if x in img else -x for x in rprim]); cnt += 1
print("checked %d orbit images are relaxed solutions: OK" % cnt)
# (b) full lex-leader (all elements, full length) on relaxed model: solutions must be lex-min of their orbit
top = rpool.top; extra = []
for P in perms:
    cl, top = lex_leader_clauses(P, rprim, top); extra.extend(cl)
print("lex-leader clauses for %d elements: %d clauses, %d aux vars" % (len(perms), len(extra), top - rpool.top))
with Solver(name="cadical195", bootstrap_with=rc.clauses + extra) as s:
    for trial in range(5):
        assert s.solve(), "relaxed+breaking UNSAT ?!"
        mod = s.get_model(); sol = frozenset(l for l in mod if l > 0 and l in set(rprim))
        keys = [lexkey(frozenset(P[x] for x in sol)) for P in perms]
        assert lexkey(sol) == min(keys), "solution is not lex-min of its orbit"
        s.add_clause([-x for x in sol if True][:0] or [(-x if x in sol else x) for x in rprim])
print("5 solutions of relaxed+full-breaking model are lex-min of their H-orbit: OK")
# (c) the lex-min of the earlier orbit satisfies the breaking clauses (assumption check)
best = min(orbit, key=lexkey)
with Solver(name="cadical195", bootstrap_with=rc.clauses + extra) as s:
    assert s.solve(assumptions=[x if x in best else -x for x in rprim]), "lex-min orbit element rejected by breaking clauses"
    worst = max(orbit, key=lexkey)
    if len(orbit) > 1:
        assert not s.solve(assumptions=[x if x in worst else -x for x in rprim]), "lex-max element accepted?!"
print("orbit lex-min accepted, lex-max rejected: OK")
print("ALL CHECKS PASSED  (%.1fs)" % (time.time() - t0))
