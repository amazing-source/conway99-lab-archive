"""Count the orbits of valid U0-rows under Stab(U0, D(U0)) <= 2^7 x S7 (label symmetries commuting with sigma).
A valid row of U0 = the set N_H(u0) of 12 outer labels (each block-1/2 inner vertex covered once, each other inner vertex
twice, exactly one sigma-pair {v, sigma v} = D(U0) present, no intra-block labels).  The orbit-level row (a_0V, b_0V)
is determined by N_H(u0), and the pair {N_H(u0), sigma N_H(u0)} is what the orbit model sees; sigma is in the
stabilizer, so orbits of 12-subsets under Stab(U0,D0) = orbits of orbit-level rows.
Group element g = (pi, f): inner (i,s) -> (pi(i), s xor f_i).  Stab(U0,D0): pi preserves the block-set structure of
u0 and d0; f consistent (f_i = f_j on each of u0, d0).  Sizes: one/dis 768, sib 15360.
Output: number of orbits (= number of symmetry-reduced full-row cubes) + representatives file.
Usage: python row_orbits.py --case one [--out rows_one.json]
"""
import argparse, itertools, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cube_measure import Model, CASES  # noqa: E402

M = 7


def labels_index():
    inner = [(i, s) for i in range(1, M + 1) for s in (0, 1)]
    labs = []
    for i in range(1, M + 1):
        for j in range(i + 1, M + 1):
            for s in (0, 1):
                for e in (0, 1):
                    labs.append(frozenset([(i, s), (j, e)]))
    return inner, labs, {l: t for t, l in enumerate(labs)}


def stab_elements(case):
    """all (pi, f) in 2^7 x S7 fixing the sigma-orbits of u0 = {(1,0),(2,0)} and d0 = rep of CASES[case]."""
    u0 = frozenset([(1, 0), (2, 0)]); i, j, e = CASES[case]; d0 = frozenset([(i, 0), (j, e)])

    def img(g, lab):
        pi, f = g
        return frozenset((pi[p[0] - 1], p[1] ^ f[p[0] - 1]) for p in lab)

    def sig(lab):
        return frozenset((p[0], 1 - p[1]) for p in lab)
    els = []
    for pi in itertools.permutations(range(1, M + 1)):
        for f in itertools.product((0, 1), repeat=M):
            g = (pi, f)
            if img(g, u0) in (u0, sig(u0)) and img(g, d0) in (d0, sig(d0)):
                els.append(g)
    return els, img


def row_to_labelset(model, row, lab_idx):
    """row: dict V -> (a,b); N_H(u0) = {rep[V] if a} U {trep[V] if b}."""
    s = []
    for V, (a, b) in row.items():
        if a: s.append(lab_idx[model.rep[V]])
        if b: s.append(lab_idx[model.trep[V]])
    assert len(s) == 12
    return sorted(s)


def enumerate_rows(model):
    """all valid rows of U0 (list of dicts) via the DFS in cube_measure (count_only=False variant collecting all)."""
    rows = []
    tgt = model.tgt(0); cnt = {c: 0 for c in model.inner}; order = model.order_for(0); row = {}
    tot = [0]; two = [0]

    def rec(k):
        if tot[0] > 12 or two[0] > 1: return
        if k == len(order):
            if tot[0] == 12 and two[0] == 1 and all(cnt[c] == tgt[c] for c in model.inner):
                rows.append(dict(row))
            return
        V = order[k]
        opts = [(1, 1)] if V == model.D0 else [(0, 0), (1, 0), (0, 1)]
        for (a, b) in opts:
            add = []
            if a: add += list(model.rep[V])
            if b: add += list(model.trep[V])
            if any(cnt[c] + add.count(c) > tgt[c] for c in set(add)): continue
            for c in add: cnt[c] += 1
            tot[0] += a + b; two[0] += (a and b); row[V] = (a, b)
            rec(k + 1)
            for c in add: cnt[c] -= 1
            tot[0] -= a + b; two[0] -= (a and b); del row[V]
    rec(0)
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--case", default="one"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t0 = time.time()
    model = Model(a.case)
    inner, labs, lab_idx = labels_index()
    els, img = stab_elements(a.case)
    print("case", a.case, "|Stab(U0,D0)| =", len(els), flush=True)
    # permutation of the 84 labels for each g
    P = np.zeros((len(els), len(labs)), dtype=np.int32)
    for gi, g in enumerate(els):
        for t, lab in enumerate(labs):
            P[gi, t] = lab_idx[img(g, lab)]
    rows = enumerate_rows(model)
    print("valid rows:", len(rows), "(%.1fs)" % (time.time() - t0), flush=True)
    R = np.array([row_to_labelset(model, r, lab_idx) for r in rows], dtype=np.int32)  # n x 12
    # sanity: group maps valid rows to valid rows (closure): every image must be in the set
    rowset = set(R.astype(np.uint8).tobytes()[q * 12:(q + 1) * 12] for q in range(len(rows)))
    canon = {}
    reps = []
    orbit_sizes = []
    for t in range(len(rows)):
        imgs = np.sort(P[:, R[t]], axis=1)          # |G| x 12
        # lexicographic min
        bb = imgs.astype(np.uint8).tobytes(); keys = [bb[q * 12:(q + 1) * 12] for q in range(len(els))]
        cf = min(keys)
        if t < 200:  # closure check on a sample
            assert all(k in rowset for k in keys), "group does not preserve valid rows!"
        if cf not in canon:
            canon[cf] = t; reps.append(rows[t]); orbit_sizes.append(len(set(keys)))
    print("orbits of rows under Stab(U0,D0):", len(canon), " (lower bound rows/|G| = %.1f)" % (len(rows) / len(els)), "(%.1fs)" % (time.time() - t0))
    print("sum of orbit sizes = %d (must equal #rows)" % sum(orbit_sizes))
    print("orbit size distribution:", sorted(set(orbit_sizes)))
    if a.out:
        json.dump({"case": a.case, "stab_order": len(els), "rows": len(rows), "orbits": len(canon),
                   "reps": [{str(V): r[V] for V in r} for r in reps], "orbit_sizes": orbit_sizes}, open(a.out, "w"))


if __name__ == "__main__":
    main()
