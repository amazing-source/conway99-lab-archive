"""Cube-and-conquer feasibility measurement for the orbit-level CNF of the Conway-99 involution branch.

Cubing schemes (all cubes are unit assumptions on primary (a,b) bits of orbit_sat.build):
  row:<d>        the first d (a,b) pairs of U0's row (orbit order: orbits sharing a block with U0 first), sampled
                 by drawing a random *valid* full row of U0 (all (R),(D),(I) row constraints satisfied) and truncating.
  row2:<d>       full row of U0 + the first d pairs of a second orbit's row (second orbit = D(U0) partner by default),
                 the second row sampled valid and consistent with the first (P-constraints between the two rows).
  dmatch:<k>     D-partners of the first k orbits in the orbit order (perfect-matching consistent, random).
Conquer: pysat CaDiCaL 1.9.5 (assumptions, shared incremental solver, wall time limit per cube) or native kissat in
Docker (units appended as clauses, --time limit).  Records result / wall / conflicts / propagations per cube.
Usage examples:
  python cube_measure.py --case one --scheme row:41 --n 10 --time 30 --out res_row41.json
  python cube_measure.py --case one --scheme row2:41 --n 10 --time 60 --engine kissat --out res_row2_kissat.json
  python cube_measure.py --count-rows --case one            (exact count of valid rows of U0)
"""
import argparse, json, os, random, re, subprocess, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from orbit_sat import build  # noqa: E402

CASES = {"sib": (1, 2, 1), "one": (1, 3, 0), "dis": (3, 4, 0)}
SCRATCH = r"C:/home/researcher/AppData/Local/Temp/claude/C--Users-RESEARCHER-Desktop/eeaf2d22-69e1-42a1-97c8-376f05816a6c/scratchpad/z2_signed"
M = 7


class Model:
    def __init__(self, case):
        self.case = case
        self.cnf, self.pool, self.outer, self.rep, self.trep, self.A, self.B = build(M, case)
        self.N = len(self.outer)
        self.inner = [(i, s) for i in range(1, M + 1) for s in (0, 1)]
        self.D0 = self.outer.index(CASES[case]) if case in CASES else None

    def order_for(self, U):
        """orbit order for row U: orbits sharing a block with U first, then the rest (deterministic)."""
        bi, bj = self.outer[U][0], self.outer[U][1]
        share = [V for V in range(self.N) if V != U and (self.outer[V][0] in (bi, bj) or self.outer[V][1] in (bi, bj))]
        rest = [V for V in range(self.N) if V != U and V not in share]
        return share + rest

    def tgt(self, U):
        return {c: (1 if (c in self.rep[U] or (c[0], 1 - c[1]) in self.rep[U]) else 2) for c in self.inner}

    # ---------- row enumeration / sampling ----------
    def row_dfs(self, U, order, fixed, rng, count_only=False, max_count=None, dfix=None):
        """Enumerate (count_only) or sample one random valid row of orbit U over the orbits in `order`.
        fixed: dict {(U,V): (a,b)} of already fixed pairs (symmetric lookups) - for pairs of U they are forced;
        also rows fully fixed for other orbits U' impose the (P) constraints with U (checked incrementally).
        dfix: index of forced D-partner (or None)."""
        tgt = self.tgt(U)
        cnt = {c: 0 for c in self.inner}
        row = {}
        full_rows = {}  # U' -> dict V->(a,b) for fully fixed rows
        for (X, Y), _ in fixed.items():
            pass
        others = set(X for (X, Y) in fixed)  # orbits with some fixed entries
        for X in others:
            ents = {Y: fixed[(X, Y)] for (X2, Y) in fixed if X2 == X}
            if len(ents) == self.N - 1 and X != U:
                full_rows[X] = ents
        # P constraints between U and each full row X: same-sum + a_UX = 2-|u∩x|, cross-sum + b_UX = 2-|u∩σx|
        pcons = []
        for X, ents in full_rows.items():
            aUX, bUX = fixed.get((U, X), fixed.get((X, U)))
            same_t = 2 - len(self.rep[U] & self.rep[X]) - aUX
            cross_t = 2 - len(self.rep[U] & self.trep[X]) - bUX
            pcons.append((X, ents, same_t, cross_t))
        state = {"same": [0] * len(pcons), "cross": [0] * len(pcons)}
        res = {"count": 0, "row": None}
        total = [0]; two = [0]

        def check_add(V, a, b, sign):
            for idx, (X, ents, st, ct) in enumerate(pcons):
                if V == X:
                    continue
                ax, bx = ents[V]
                state["same"][idx] += sign * (a * ax + b * bx)
                state["cross"][idx] += sign * (a * bx + b * ax)

        def ok_partial():
            for idx, (X, ents, st, ct) in enumerate(pcons):
                if state["same"][idx] > st or state["cross"][idx] > ct:
                    return False
            return True

        def rec(k):
            if total[0] > 12 or two[0] > 1:
                return False
            if k == len(order):
                if total[0] == 12 and two[0] == 1 and all(cnt[c] == tgt[c] for c in self.inner):
                    for idx, (X, ents, st, ct) in enumerate(pcons):
                        if state["same"][idx] != st or state["cross"][idx] != ct:
                            return False
                    res["count"] += 1
                    if not count_only:
                        res["row"] = dict(row); return True
                    return max_count is not None and res["count"] >= max_count
                return False
            V = order[k]
            key = (U, V) if (U, V) in fixed else ((V, U) if (V, U) in fixed else None)
            if key is not None:
                opts = [fixed[key]]
            else:
                opts = [(0, 0), (1, 0), (0, 1), (1, 1)]
                if dfix is not None:
                    opts = [(1, 1)] if V == dfix else [o for o in opts if o != (1, 1)]
                if not count_only:
                    rng.shuffle(opts)
            for (a, b) in opts:
                add = []
                if a: add += list(self.rep[V])
                if b: add += list(self.trep[V])
                if any(cnt[c] + add.count(c) > tgt[c] for c in set(add)):
                    continue
                for c in add: cnt[c] += 1
                total[0] += a + b; two[0] += (a and b)
                check_add(V, a, b, +1)
                row[V] = (a, b)
                good = ok_partial() and rec(k + 1)
                if good:
                    return True
                check_add(V, a, b, -1)
                for c in add: cnt[c] -= 1
                total[0] -= a + b; two[0] -= (a and b)
                del row[V]
            return False

        rec(0)
        return res["count"] if count_only else res["row"]

    def sample_row(self, U, rng, fixed=None, dfix=None):
        fixed = fixed or {}
        return self.row_dfs(U, self.order_for(U), fixed, rng, dfix=dfix)

    def count_rows(self, U, fixed=None, dfix=None, max_count=None):
        fixed = fixed or {}
        return self.row_dfs(U, self.order_for(U), fixed, None, count_only=True, max_count=max_count, dfix=dfix)

    # ---------- cube generation ----------
    def lits(self, U, V, a, b):
        return [self.A[U, V] if a else -self.A[U, V], self.B[U, V] if b else -self.B[U, V]]

    def gen_cube(self, scheme, rng):
        kind, _, arg = scheme.partition(":")
        d = int(arg) if arg else 0
        U0 = 0
        desc = {}
        if kind == "row":
            row = self.sample_row(U0, rng, dfix=self.D0)
            order = self.order_for(U0)[:d]
            lits = []
            for V in order:
                lits += self.lits(U0, V, *row[V])
            desc = {"row0": {str(V): row[V] for V in order}}
            return lits, desc
        if kind == "row2":
            row = self.sample_row(U0, rng, dfix=self.D0)
            U1 = self.D0 if self.D0 is not None else 1
            fixed = {(U0, V): row[V] for V in row}
            row1 = self.sample_row(U1, rng, fixed=fixed, dfix=U0)
            lits = []
            for V in self.order_for(U0):
                lits += self.lits(U0, V, *row[V])
            order1 = [V for V in self.order_for(U1) if V != U0][:d]
            for V in order1:
                lits += self.lits(U1, V, *row1[V])
            desc = {"row0": {str(V): row[V] for V in row}, "row1": {str(V): row1[V] for V in order1}, "U1": U1}
            return lits, desc
        if kind == "dmatch":
            # random perfect-matching-consistent D partners for the first d orbits in index order (U0's is the case)
            partner = {}
            if self.D0 is not None:
                partner[U0] = self.D0; partner[self.D0] = U0
            lits = []
            for U in range(self.N):
                if len([u for u in partner if u < d or True]) and U >= d:
                    break
                if U in partner:
                    continue
                cands = [V for V in range(self.N) if V != U and V not in partner]
                V = rng.choice(cands)
                partner[U] = V; partner[V] = U
            for U in sorted(partner):
                if U < d or (partner[U] < d):
                    pass
            pairs = sorted(set(tuple(sorted((u, v))) for u, v in partner.items()))
            for (u, v) in pairs:
                lits += self.lits(u, v, 1, 1)
            desc = {"pairs": [[self.outer[u], self.outer[v]] for u, v in pairs]}
            return lits, desc
        raise ValueError(scheme)


# ---------- conquer engines ----------
class PysatEngine:
    def __init__(self, model, name="cadical195"):
        from pysat.solvers import Solver
        t0 = time.time()
        self.s = Solver(name=name, bootstrap_with=model.cnf.clauses, use_timer=True)
        self.load = time.time() - t0
        self.last = self._stats()

    def _stats(self):
        try:
            return dict(self.s.accum_stats())
        except Exception:
            return {}

    def run(self, lits, tlim):
        timer = threading.Timer(tlim, lambda: self.s.interrupt()); timer.start()
        t0 = time.time()
        r = self.s.solve_limited(assumptions=lits, expect_interrupt=True)
        wall = time.time() - t0
        timer.cancel()
        try:
            self.s.clear_interrupt()
        except Exception:
            pass
        st = self._stats(); delta = {k: st.get(k, 0) - self.last.get(k, 0) for k in st}; self.last = st
        return {True: "SAT", False: "UNSAT", None: "UNKNOWN"}[r], wall, delta


class PysatUnitsEngine:
    """fresh CaDiCaL per cube, cube literals added as unit clauses (like row_fix.py)."""
    def __init__(self, model, name="cadical195"):
        self.model = model; self.name = name; self.load = 0.0

    def run(self, lits, tlim):
        from pysat.solvers import Solver
        t0 = time.time()
        with Solver(name=self.name, bootstrap_with=self.model.cnf.clauses + [[l] for l in lits], use_timer=True) as s:
            timer = threading.Timer(tlim, lambda: s.interrupt()); timer.start()
            r = s.solve_limited(expect_interrupt=True); timer.cancel()
            try: st = dict(s.accum_stats())
            except Exception: st = {}
        return {True: "SAT", False: "UNSAT", None: "UNKNOWN"}[r], time.time() - t0, st


class KissatEngine:
    def __init__(self, model, base_cnf):
        self.model = model; self.base = base_cnf
        self.nv, self.nc = model.pool.top, len(model.cnf.clauses)
        if not os.path.exists(os.path.join(SCRATCH, base_cnf)):
            model.cnf.to_file(os.path.join(SCRATCH, base_cnf))

    def run(self, lits, tlim, tag="cube", solver="kissat"):
        path = os.path.join(SCRATCH, "%s.cnf" % tag)
        with open(os.path.join(SCRATCH, self.base)) as f, open(path, "w") as g:
            f.readline()
            g.write("p cnf %d %d\n" % (self.nv, self.nc + len(lits)))
            for l in lits:
                g.write("%d 0\n" % l)
            for line in f:
                g.write(line)
        if solver == "kissat":
            cmd = "kissat --time=%d %s.cnf" % (tlim, tag)
        else:
            cmd = "cadical -t %d %s.cnf" % (tlim, tag)
        t0 = time.time()
        p = subprocess.run(["docker", "run", "--rm", "--cpus", "1", "-v", "%s:/work" % SCRATCH, "satbox-cnc", "sh", "-c", cmd],
                           capture_output=True, text=True, timeout=tlim + 120)
        wall = time.time() - t0
        out = p.stdout
        res = "UNKNOWN"
        m = re.search(r"^s (SATISFIABLE|UNSATISFIABLE|UNKNOWN)", out, re.M)
        if m: res = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT", "UNKNOWN": "UNKNOWN"}[m.group(1)]
        st = {}
        for key in ("conflicts", "decisions", "propagations", "eliminated", "process-time"):
            mm = re.search(r"^c %s:\s+([0-9.]+)" % re.escape(key), out, re.M)
            if mm: st[key] = float(mm.group(1))
        return res, wall, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="one"); ap.add_argument("--scheme", default="row:41")
    ap.add_argument("--n", type=int, default=10); ap.add_argument("--time", type=float, default=30)
    ap.add_argument("--engine", default="pysat"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=None); ap.add_argument("--count-rows", action="store_true")
    ap.add_argument("--count-rows2", type=int, default=0, help="count second-row completions for this many random first rows")
    ap.add_argument("--maxcount", type=int, default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    t0 = time.time()
    model = Model(a.case)
    print("case=%s vars=%d clauses=%d build=%.1fs D0=%s" % (a.case, model.pool.top, len(model.cnf.clauses), time.time() - t0, model.outer[model.D0] if model.D0 is not None else None), flush=True)
    if a.count_rows:
        t1 = time.time(); c = model.count_rows(0, dfix=model.D0, max_count=a.maxcount)
        print("valid rows of U0 (case %s): %d  (%.1fs)" % (a.case, c, time.time() - t1), flush=True)
        return
    if a.count_rows2:
        U1 = model.D0
        outs = []
        for i in range(a.count_rows2):
            row = model.sample_row(0, rng, dfix=model.D0)
            fixed = {(0, V): row[V] for V in row}
            t1 = time.time(); c = model.count_rows(U1, fixed=fixed, dfix=0, max_count=a.maxcount)
            outs.append(c); print("row0 sample %d: completions of row U1=%s: %d (%.1fs)" % (i, model.outer[U1], c, time.time() - t1), flush=True)
        print("mean", sum(outs) / len(outs), "min", min(outs), "max", max(outs))
        if a.out: json.dump({"case": a.case, "U1": model.outer[U1], "counts": outs}, open(a.out, "w"), indent=1)
        return
    if a.engine == "pysat":
        eng = PysatEngine(model); print("solver loaded in %.1fs" % eng.load, flush=True)
    elif a.engine == "pysat_units":
        eng = PysatUnitsEngine(model)
    else:
        eng = KissatEngine(model, "k14_%s.cnf" % a.case)
    results = []
    for i in range(a.n):
        lits, desc = model.gen_cube(a.scheme, rng)
        if a.engine in ("pysat", "pysat_units"):
            res, wall, st = eng.run(lits, a.time)
        else:
            res, wall, st = eng.run(lits, int(a.time), tag="cube_%s_%d" % (a.scheme.replace(":", ""), i), solver=a.engine)
        rec = {"i": i, "nlits": len(lits), "result": res, "wall": round(wall, 2), "stats": st, "cube": desc}
        results.append(rec)
        print("cube %2d  lits=%3d  %-8s wall=%6.1fs  conflicts=%s  props=%s" % (i, len(lits), res, wall, st.get("conflicts"), st.get("propagations")), flush=True)
        if a.out:
            json.dump({"case": a.case, "scheme": a.scheme, "engine": a.engine, "time": a.time, "results": results}, open(a.out, "w"), indent=1)
    dec = sum(1 for r in results if r["result"] != "UNKNOWN")
    print("decided %d / %d  (SAT=%d UNSAT=%d)" % (dec, len(results), sum(r["result"] == "SAT" for r in results), sum(r["result"] == "UNSAT" for r in results)))


if __name__ == "__main__":
    main()
