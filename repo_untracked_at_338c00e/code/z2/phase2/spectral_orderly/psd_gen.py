"""Row-by-row generator for the joint (Q_out, S_out) orbit table with spectral (interlacing / PSD / rank) domain filters.

Baseline constraints = those of code/z2/joint_dfs.py (Q-row, Q-block, S-block, Q-Gram, S-Gram, with suffix-capacity bounds).
Added (exact) spectral constraints, all consequences of A^2+A-(k-2)I=2J (see involution_frame.py):
  Ps = (r I - S_out - r/(k-2) G)/(r-s)   is an orthogonal projector of rank gout   (k=14: rank 15)
  Pr = (S_out - s I + s/(k-2) G)/(r-s)   is an orthogonal projector of rank fout   (k=14: rank 20)
  Es = (r I - Qt)/(r-s) + (k-r)/((r-s)n) w w^T   projector of rank gQ on the 1+m+N space (k=14: rank 22 on 50)
  Er = (Qt - s I)/(r-s) - (k-s)/((r-s)n) w w^T   projector of rank fQ                (k=14: rank 27 on 50)
Cauchy interlacing for a projector of rank rho: every principal submatrix is PSD, has eigenvalues in [0,1] and rank <= rho.
Row-r filter (rows 0..r-1 complete; B = block on the known index set K; u = row r restricted to K; v_c = row c restricted to K):
  u, v_c in range(B);  d_r = diag - u^T B^+ u >= 0;  d_c = diag - v_c^T B^+ v_c >= 0;  t = entry (r,c);  cv = u^T B^+ v_c;
  rank(B) <= rho-2 : |t - cv| <= sqrt(d_r d_c)        (PSD of the block K+{r,c})
  rank(B)  = rho-1 : |t - cv|  = sqrt(d_r d_c)        (block K+{r,c} has rank <= rho, so the 2x2 Schur complement is singular)
  rank(B)  = rho   : d_r = 0, d_c = 0, t = cv          (everything determined)
Applied to all four projectors; the joint value v in {0,1,2,3} (Q=[0,1,1,2], S=[0,1,-1,0]) must pass every filter.
"""
import argparse, json, math, random, sys, time
import numpy as np
from involution_frame import Frame

TOL = 1e-7


class SpectralFilter:
    """One projector family: given the known entries, compute per-column allowed value sets."""
    def __init__(self, name, rho, diag_val, tval_fn, tol=TOL):
        self.name, self.rho, self.diag, self.tval, self.tol = name, rho, diag_val, tval_fn, tol

    def domains(self, B, u, Vc, r, cols, G_rc_list, ncand):
        """B: (K x K) known block; u: (K,) row r; Vc: (ncols x K) rows c; returns list of allowed sets over
        candidate index 0..ncand-1 (tval(cand, G_rc) gives the matrix entry), or None if infeasible."""
        tol = self.tol
        K = B.shape[0]
        if K == 0:
            return [set(range(ncand)) for _ in cols], 0, None
        lam, V = np.linalg.eigh(B)
        keep = lam > 1e-6
        rho = int(keep.sum())
        if rho > self.rho:
            return None, rho, "rankB"
        Vk = V[:, keep]; lk = lam[keep]
        # range checks
        pu = Vk @ (Vk.T @ u)
        if np.abs(pu - u).max() > 1e-5: return None, rho, "range_u"
        Wu = Vk @ ((Vk.T @ u) / lk)
        dr = self.diag - u @ Wu
        if dr < -1e-6: return None, rho, "dr<0"
        dr = max(dr, 0.0)
        if rho == self.rho and dr > 1e-6: return None, rho, "dr>0 at full rank"
        if len(cols) == 0:
            return [], rho, None
        PV = (Vc @ Vk) @ Vk.T
        if np.abs(PV - Vc).max() > 1e-5: return None, rho, "range_c"
        cv = Vc @ Wu
        dc = self.diag - np.einsum("ij,ij->i", Vc @ Vk / lk, Vc @ Vk)
        if dc.min() < -1e-6: return None, rho, "dc<0"
        dc = np.maximum(dc, 0.0)
        w = np.sqrt(dr * dc)
        if rho == self.rho and dc.max() > 1e-6: return None, rho, "dc>0 at full rank"
        doms = []
        for ci, c in enumerate(cols):
            allowed = set()
            for cand in range(ncand):
                t = self.tval(cand, G_rc_list[ci])
                dev = abs(t - cv[ci])
                if rho <= self.rho - 2:
                    ok = dev <= w[ci] + tol
                elif rho == self.rho - 1:
                    ok = abs(dev - w[ci]) <= tol
                else:
                    ok = dev <= tol
                if ok: allowed.add(cand)
            if not allowed: return None, rho, "empty"
            doms.append(allowed)
        return doms, rho, None


class Generator:
    def __init__(self, fr, use_S=True, use_Q=True, seed=None, verbose=True):
        self.fr = fr; self.N = N = fr.N; self.m = m = fr.m
        self.QV, self.SV = fr.QV, fr.SV
        self.C = fr.C.tolist(); self.G = fr.G.tolist(); self.SH = fr.SH.tolist(); self.BL = fr.BL
        r, s, k, n = fr.r, fr.s, fr.k, fr.n
        self.filters = []
        if use_S:
            # Ps: entries (r d - S - r/(k-2) G)/(r-s); candidate index = joint value v; S = SV[v]
            self.filters.append(("S", SpectralFilter("Ps", fr.gout, (r - r / (k - 2) * 2) / (r - s),
                                                    lambda v, g: (-fr.SV[v] - r / (k - 2) * g) / (r - s))))
            self.filters.append(("S", SpectralFilter("Pr", fr.fout, (-s + s / (k - 2) * 2) / (r - s),
                                                    lambda v, g: (fr.SV[v] + s / (k - 2) * g) / (r - s))))
        if use_Q:
            cs = (k - r) / ((r - s) * n); cr = (k - s) / ((r - s) * n)
            self.filters.append(("Q", SpectralFilter("Es", fr.gQ, r / (r - s) + 2 * cs,
                                                    lambda v, g: -fr.QV[v] / (r - s) + 2 * cs)))
            self.filters.append(("Q", SpectralFilter("Er", fr.fQ, -s / (r - s) - 2 * cr,
                                                    lambda v, g: fr.QV[v] / (r - s) - 2 * cr)))
            self.cs, self.cr = cs, cr
        self.rng = random.Random(seed)
        self.verbose = verbose
        self.reset()

    def reset(self):
        N = self.N
        self.T = [[0] * N for _ in range(N)]
        self.st = {"nodes": [0] * (N + 1), "row_events": [0] * (N + 1), "prep_fail": [0] * (N + 1),
                   "dom_stats": [[0, 0, 0, 0, 0] for _ in range(N + 1)], "rows_max": 0}

    # ----- spectral matrices restricted to known index sets -----
    def _S_known(self, r):
        """S-side: block B (r x r) of the matrix (delta-scaled) built from T; rows u (row r) and Vc (rows c>r)."""
        fr = self.fr; SVa = np.array(self.SV, dtype=float)
        T = np.array(self.T)
        S_full_known = SVa[T]          # entries valid where known
        return S_full_known

    def prepare_row(self, r):
        """Compute joint domains for row r (columns c>r). Returns (domains list over cols, info) or (None, reason)."""
        fr = self.fr; N = self.N; m = self.m
        cols = list(range(r + 1, N)); nc = len(cols)
        Ta = np.array(self.T)
        SVa = np.array(self.SV, dtype=float); QVa = np.array(self.QV, dtype=float)
        Sm = SVa[Ta]; Qm = QVa[Ta]
        G = fr.G.astype(float); rr, ss, k, n = fr.r, fr.s, fr.k, fr.n
        doms = [set(range(4)) for _ in cols]
        info = {}
        for side, f in self.filters:
            if side == "S":
                if f.name == "Ps":
                    Mfull = (rr * np.eye(N) - Sm - rr / (k - 2) * G) / (rr - ss)
                else:
                    Mfull = (Sm - ss * np.eye(N) + ss / (k - 2) * G) / (rr - ss)
                B = Mfull[:r, :r]; u = Mfull[r, :r]; Vc = Mfull[r + 1:, :r]
                Gl = [G[r, c] for c in cols]
            else:
                Qt = np.zeros((1 + m + N, 1 + m + N))
                Qt[0, 1:1 + m] = Qt[1:1 + m, 0] = math.sqrt(2)
                for i in range(m): Qt[1 + i, 1 + i] = 1.0
                Qt[1 + m:, 1:1 + m] = fr.Nb; Qt[1:1 + m, 1 + m:] = fr.Nb.T
                Qt[1 + m:, 1 + m:] = Qm
                if f.name == "Es":
                    Mfull = (rr * np.eye(1 + m + N) - Qt) / (rr - ss) + self.cs * np.outer(fr.w, fr.w)
                else:
                    Mfull = (Qt - ss * np.eye(1 + m + N)) / (rr - ss) - self.cr * np.outer(fr.w, fr.w)
                Kidx = list(range(1 + m + r))
                B = Mfull[np.ix_(Kidx, Kidx)]; u = Mfull[1 + m + r, Kidx]; Vc = Mfull[1 + m + r + 1:, Kidx]
                Gl = [0] * nc
            d, rho, reason = f.domains(B, u, Vc, r, cols, Gl, 4)
            info[f.name] = rho
            if d is None:
                info["fail"] = f.name + ":" + reason
                return None, info
            for ci in range(nc):
                doms[ci] &= d[ci]
                if not doms[ci]:
                    info["fail"] = "joint-empty"; return None, info
        return doms, info

    # ----- row DFS -----
    def search(self, node_cap, time_cap, randomize=False, max_rows=None, first_row=None):
        N, M = self.N, self.m; K2 = self.fr.k - 2
        T = self.T; st = self.st; QV, SV, C, BL, G, SH = self.QV, self.SV, self.C, self.BL, self.G, self.SH
        t0 = time.time(); sol = [None]; total = [0]
        rng = self.rng

        def fill_row(r):
            if r == N or (max_rows is not None and r == max_rows):
                sol[0] = [row[:] for row in T]; return True
            doms, info = self.prepare_row(r)
            if doms is None:
                st["prep_fail"][r] += 1; return False
            ds = st["dom_stats"][r]
            for d in doms: ds[len(d)] += 1
            ds[4] += 0
            cols = list(range(r + 1, N)); nc = len(cols)
            if first_row is not None and r == 0:
                doms = [set([first_row[c]]) & doms[ci] for ci, c in enumerate(cols)]
                if any(not d for d in doms): return False
            qs = sum(QV[T[r][j]] for j in range(r)); two = sum(1 for j in range(r) if T[r][j] == 3)
            qb = [sum(QV[T[r][j]] for j in range(r) if C[j][l]) for l in range(M)]
            sb = [sum(SV[T[r][j]] * C[j][l] for j in range(r)) for l in range(M)]
            qd = [sum(QV[T[r][j]] * QV[T[rp][j]] for j in range(r)) for rp in range(r)]
            sd = [sum(SV[T[r][j]] * SV[T[rp][j]] for j in range(r)) for rp in range(r)]
            qt = [4 - QV[T[r][rp]] - SH[r][rp] for rp in range(r)]
            stt = [-SV[T[r][rp]] - G[r][rp] for rp in range(r)]
            qbt = [2 if l in BL[r] else 4 for l in range(M)]
            # domain-aware suffix capacities
            maxq = [max(QV[v] for v in doms[p]) for p in range(nc)]
            maxs = [max(abs(SV[v]) for v in doms[p]) for p in range(nc)]
            remb = [[0] * (nc + 1) for _ in range(M)]      # max Q contribution to block l from suffix
            rems = [[0] * (nc + 1) for _ in range(M)]      # max |S| contribution to block l
            remq = [[0] * (nc + 1) for _ in range(r)]      # max Q*Q contribution to row rp
            remd = [[0] * (nc + 1) for _ in range(r)]      # max |S*S| contribution to row rp
            remQ = [0] * (nc + 1)
            for p in range(nc - 1, -1, -1):
                c = cols[p]
                remQ[p] = remQ[p + 1] + maxq[p]
                for l in range(M):
                    remb[l][p] = remb[l][p + 1] + (maxq[p] if C[c][l] else 0)
                    rems[l][p] = rems[l][p + 1] + (maxs[p] if C[c][l] else 0)
                for rp in range(r):
                    remq[rp][p] = remq[rp][p + 1] + maxq[p] * QV[T[rp][c]]
                    remd[rp][p] = remd[rp][p + 1] + maxs[p] * abs(SV[T[rp][c]])
            vals_order = [sorted(doms[p]) for p in range(nc)]

            def rec(p, qs, two):
                st["nodes"][r] += 1; total[0] += 1
                if total[0] > node_cap or ((total[0] & 0x3FFF) == 0 and time.time() - t0 > time_cap): return "cap"
                if qs > K2 or two > 1 or qs + remQ[p] < K2: return False
                for l in range(M):
                    if qb[l] > qbt[l] or qb[l] + remb[l][p] < qbt[l]: return False
                    if abs(sb[l]) > rems[l][p]: return False
                for rp in range(r):
                    if qd[rp] > qt[rp] or qd[rp] + remq[rp][p] < qt[rp]: return False
                    if abs(sd[rp] - stt[rp]) > remd[rp][p]: return False
                if p == nc:
                    if qs != K2 or two != 1: return False
                    for l in range(M):
                        if qb[l] != qbt[l] or sb[l] != 0: return False
                    for rp in range(r):
                        if qd[rp] != qt[rp] or sd[rp] != stt[rp]: return False
                    for f in range(r + 1, N):
                        fq = sum(QV[T[f][j]] for j in range(r + 1)); ftwo = sum(1 for j in range(r + 1) if T[f][j] == 3)
                        if fq > K2 or ftwo > 1: return False
                        for l in range(M):
                            tq = 2 if l in BL[f] else 4
                            pq = sum(QV[T[f][j]] for j in range(r + 1) if C[j][l]); ps = sum(SV[T[f][j]] * C[j][l] for j in range(r + 1))
                            capl = sum(1 for j in range(r + 1, N) if j != f and C[j][l])
                            if pq > tq or pq + 2 * capl < tq or abs(ps) > capl: return False
                    st["row_events"][r + 1] += 1
                    if r + 1 > st["rows_max"]:
                        st["rows_max"] = r + 1
                        if self.verbose: print("  rows completed: %d  nodes %d  t=%.1fs" % (r + 1, total[0], time.time() - t0), flush=True)
                    return fill_row(r + 1)
                c = cols[p]
                vo = vals_order[p]
                if randomize: vo = vo[:]; rng.shuffle(vo)
                for v in vo:
                    q, s = QV[v], SV[v]
                    T[r][c] = v; T[c][r] = v
                    if q:
                        for l in BL[c]: qb[l] += q; sb[l] += s * C[c][l]
                        for rp in range(r): qd[rp] += q * QV[T[rp][c]]; sd[rp] += s * SV[T[rp][c]]
                    res = rec(p + 1, qs + q, two + (v == 3))
                    if q:
                        for l in BL[c]: qb[l] -= q; sb[l] -= s * C[c][l]
                        for rp in range(r): qd[rp] -= q * QV[T[rp][c]]; sd[rp] -= s * SV[T[rp][c]]
                    T[r][c] = 0; T[c][r] = 0
                    if res: return res
                return False
            return rec(0, qs, two)
        res = fill_row(0)
        st["time"] = time.time() - t0; st["total_nodes"] = total[0]
        st["result"] = "SOLUTION" if sol[0] else ("CAP" if res == "cap" else "EXHAUSTED_NO_SOLUTION")
        return sol[0], st


# ---------------- soundness check along a known solution ----------------
def soundness_along_solution(fr, Tsol, use_S=True, use_Q=True):
    """For each depth r, load rows 0..r-1 of the known solution, compute domains, verify the true row r entries
    are allowed; report the domain size distribution per depth."""
    gen = Generator(fr, use_S, use_Q, verbose=False)
    N = fr.N; rows = []
    for r in range(N):
        for i in range(r):
            for j in range(N):
                gen.T[i][j] = Tsol[i][j]; gen.T[j][i] = Tsol[j][i]
        doms, info = gen.prepare_row(r)
        if doms is None:
            return {"depth": r, "FAIL": info}, rows
        sizes = [len(d) for d in doms]
        viol = [c for ci, c in enumerate(range(r + 1, N)) if Tsol[r][c] not in doms[ci]]
        rows.append({"r": r, "n_cols": len(doms), "forced": sizes.count(1), "size2": sizes.count(2), "size3": sizes.count(3),
                     "size4": sizes.count(4), "mean": float(np.mean(sizes)) if sizes else 0.0, "violations": len(viol),
                     "ranks": {k: v for k, v in info.items()}})
        if viol:
            return {"depth": r, "VIOLATION": viol[:5]}, rows
    return {"ok": True}, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=7)
    ap.add_argument("--mode", default="dfs", choices=["dfs", "sound", "rand"])
    ap.add_argument("--nodes", type=int, default=10 ** 9); ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--noS", action="store_true"); ap.add_argument("--noQ", action="store_true")
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--restarts", type=int, default=1)
    ap.add_argument("--table", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    fr = Frame(a.m)
    if a.mode == "sound":
        Tsol = json.load(open(a.table))["T"]
        res, rows = soundness_along_solution(fr, Tsol, not a.noS, not a.noQ)
        print(json.dumps(res))
        for row in rows: print(json.dumps(row))
        sys.exit(0)
    gen = Generator(fr, not a.noS, not a.noQ, seed=a.seed)
    if a.mode == "dfs":
        sol, st = gen.search(a.nodes, a.time)
        print(json.dumps({k: v for k, v in st.items() if k != "dom_stats"}))
        print("dom_stats (per depth: [empty,1,2,3,4] counts over columns):", json.dumps([d for d in st["dom_stats"] if any(d)]))
        if sol:
            A, ok = fr.lift(sol); print("LIFT VERIFY srg(%d,%d,1,2):" % (fr.n, fr.k), ok)
            if a.out: json.dump({"T": sol}, open(a.out, "w"))
    else:
        # randomized restarts: each restart gets an equal slice of the budget
        agg = None; best = 0; t_start = time.time()
        per = a.time / a.restarts
        for i in range(a.restarts):
            gen = Generator(fr, not a.noS, not a.noQ, seed=a.seed + i, verbose=False)
            sol, st = gen.search(a.nodes, per, randomize=True)
            best = max(best, st["rows_max"])
            print(json.dumps({"restart": i, "rows_max": st["rows_max"], "nodes": st["nodes"][:st["rows_max"] + 1],
                              "row_events": st["row_events"][:st["rows_max"] + 2], "prep_fail": st["prep_fail"][:st["rows_max"] + 2],
                              "result": st["result"], "t": round(st["time"], 1)}), flush=True)
            if sol:
                A, ok = fr.lift(sol); print("LIFT VERIFY:", ok)
                if a.out: json.dump({"T": sol}, open(a.out, "w"))
                break
        print("best rows_max over restarts:", best, "total time %.1f" % (time.time() - t_start))
