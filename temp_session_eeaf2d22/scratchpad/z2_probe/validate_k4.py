"""Task 2: validate the model on k=4 (n=9), control case (Paley(9) / K3 box K3)."""
import itertools
import sys
import numpy as np
from pysat.solvers import Solver
from model import Instance, check_srg

K = 4


def enumerate_all(inst, label):
    lits = sorted(set(abs(l) for cl in inst.clauses for l in cl))
    # the H-variables actually present (some vpool ids are AND-gate aux vars)
    hvars = sorted(set(inst._pair_var.values()))
    solutions = []
    with Solver(name='cadical195', bootstrap_with=inst.clauses) as s:
        while s.solve():
            model = s.get_model()
            truth = {abs(l): (l > 0) for l in model}
            solutions.append({v: truth[v] for v in hvars})
            block = [-l for l in model if abs(l) in set(hvars)]
            # blocking on just the H-vars is enough since AND-vars are determined
            s.add_clause(block)
    print("[%s] CNF: %d vars(H-space=%d distinct incl. AND aux), %d clauses -> %d solutions found"
          % (label, inst.vpool.top, len(hvars), len(inst.clauses), len(solutions)))
    return solutions, hvars


def report(inst, solutions, hvars, label):
    ok_count = 0
    bad = []
    for sol in solutions:
        A = inst.decode(sol)
        good, msg = check_srg(A, inst.k)
        if good:
            ok_count += 1
        else:
            bad.append(msg)
    print("[%s] decoded+checked: %d/%d valid srg(9,4,1,2)" % (label, ok_count, len(solutions)))
    if bad:
        print("[%s] failures: %s" % (label, bad))
    return ok_count


def describe_H_as_cycle(inst, sol):
    L = inst.num_outer
    Hm = inst.outer_H_matrix(sol)
    edges = [(i, j) for i in range(L) for j in range(i + 1, L) if Hm[i, j] == 1]
    deg = Hm.sum(axis=1)
    return edges, deg.tolist()


def main():
    print("=== k=4, n=9 validation ===")

    # (a) without sigma: enumerate all solutions
    inst_a = Instance(K, use_sigma=False, no_self_adjacent=False)
    print("num_outer =", inst_a.num_outer, " C(num_outer,2) =", inst_a.num_outer * (inst_a.num_outer - 1) // 2)
    sols_a, hvars_a = enumerate_all(inst_a, "no-sigma")
    for idx, sol in enumerate(sols_a):
        edges, deg = describe_H_as_cycle(inst_a, sol)
        print("  solution %d: H edges (label indices) = %s, degrees=%s" % (idx, edges, deg))
    ok_a = report(inst_a, sols_a, hvars_a, "no-sigma")

    assert ok_a == len(sols_a), "some solutions failed the independent integer check!"
    assert len(sols_a) >= 1, "expected at least one solution (Paley(9) must appear)"

    # every solution's H should be 2-regular on 4 vertices => must be a 4-cycle
    for sol in sols_a:
        edges, deg = describe_H_as_cycle(inst_a, sol)
        assert all(d == 2 for d in deg), "H not 2-regular: %s" % deg
        # check it's a single 4-cycle (connected)
        adj = {i: set() for i in range(4)}
        for (i, j) in edges:
            adj[i].add(j)
            adj[j].add(i)
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        assert len(seen) == 4, "H is not connected (not a single 4-cycle)"
    print("[no-sigma] confirmed: every solution's H is a single labelled 4-cycle on the 4 labels")
    n_labeled_4cycles = 3
    print("[no-sigma] number of distinct labelled 4-cycles on 4 labels = %d (all found: %d)"
          % (n_labeled_4cycles, len(sols_a)))

    # (b) with sigma-invariance
    inst_b = Instance(K, use_sigma=True, no_self_adjacent=False)
    sols_b, hvars_b = enumerate_all(inst_b, "sigma")
    for idx, sol in enumerate(sols_b):
        edges, deg = describe_H_as_cycle(inst_b, sol)
        print("  sigma-solution %d: H edges = %s, degrees=%s" % (idx, edges, deg))
    ok_b = report(inst_b, sols_b, hvars_b, "sigma")
    assert len(sols_b) >= 1, "expected >=1 sigma-invariant solution (Paley(9) has such an involution)"

    # (b2) with sigma-invariance AND no-self-adjacent
    inst_c = Instance(K, use_sigma=True, no_self_adjacent=True)
    sols_c, hvars_c = enumerate_all(inst_c, "sigma+no-self-adj")
    ok_c = report(inst_c, sols_c, hvars_c, "sigma+no-self-adj")

    # Sanity: derived formula check on an arbitrary solution
    print("=== sanity: derived outer-outer formula |N_H(u) n N_H(v)| = (1-s) or (2-s) ===")
    sol0 = sols_a[0]
    Hm = inst_a.outer_H_matrix(sol0)
    L = inst_a.num_outer
    all_ok = True
    for i in range(L):
        for j in range(i + 1, L):
            a = inst_a.outer_ids[i]
            b = inst_a.outer_ids[j]
            s = len(inst_a.label_of[a] & inst_a.label_of[b])
            common = int(sum(1 for w in range(L) if w != i and w != j and Hm[i, w] == 1 and Hm[j, w] == 1))
            expect = (1 - s) if Hm[i, j] == 1 else (2 - s)
            if common != expect:
                all_ok = False
                print("  MISMATCH i=%d j=%d s=%d Hij=%d common=%d expect=%d" % (i, j, s, Hm[i, j], common, expect))
    print("derived-formula check on solution 0:", "OK" if all_ok else "FAILED")

    # Negative control: flip one H entry of a valid solution and confirm rejection
    print("=== negative control: flipping one H bit must break the identity ===")
    A_good = inst_a.decode(sol0)
    good, msg = check_srg(A_good, K)
    assert good, "baseline solution unexpectedly fails: %s" % msg
    A_bad = A_good.copy()
    # flip an outer-outer edge (pick the first outer-outer 1-entry)
    first_outer = inst_a.first_outer
    flipped = False
    for a in range(first_outer, inst_a.n):
        for b in range(a + 1, inst_a.n):
            if A_bad[a, b] == 1:
                A_bad[a, b] = 0
                A_bad[b, a] = 0
                flipped = True
                break
        if flipped:
            break
    assert flipped
    bad_ok, bad_msg = check_srg(A_bad, K)
    print("flipped-matrix check result: good=%s msg=%s" % (bad_ok, bad_msg))
    assert not bad_ok, "checker FAILED to catch a corrupted adjacency matrix!"
    print("negative control PASSED: checker correctly rejects the corrupted matrix")

    print("\n=== SUMMARY (k=4) ===")
    print("no-sigma solutions:", len(sols_a), " all valid srg:", ok_a == len(sols_a))
    print("sigma-invariant solutions:", len(sols_b), " all valid srg:", ok_b == len(sols_b))
    print("sigma+no-self-adjacent solutions:", len(sols_c), " all valid srg:", ok_c == len(sols_c))


if __name__ == '__main__':
    main()
