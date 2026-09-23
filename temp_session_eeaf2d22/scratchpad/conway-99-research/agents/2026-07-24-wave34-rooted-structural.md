# Wave 34 rooted structural proof: cycle-space/projector reduction

```yaml
role: proof_a
date_utc: 2026-07-24T20:08:16Z
git_commit: 0fa5b8161baf8b2a5404a67051b7d61cbc906da3
claim_label: DERIVED
scope: >-
  The unrestricted labeled Wave 33 six-block binary rooted graph-extension
  criterion on fixed cells |S|=14, |O|=70, |Q|=15. No automorphism quotient
  and no fixed O-Q design are assumed. Derive an exact cycle-space and
  rank-16 integral-projector reparameterization; do not claim a binary
  solution or exclusion.
inputs:
  - path: AGENTS.md
    sha256: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  - path: verification/wave34-continuation-protocol.md
    sha256: 60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4
  - path: CONJECTURE.md
    sha256: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  - path: STATUS.yaml
    sha256: feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864
  - path: verification/2026-07-24-wave33-clean-clone.md
    sha256: d83e18052114affaed873ddaa7bdc6a26c63afc6432345e1027aeef5bd66d052
  - path: verification/wave33-rooted-extension/comparison-results.json
    sha256: 2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd
  - path: verification/wave33-rooted-extension/comparison-audit.md
    sha256: fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a
  - path: verification/wave33-rooted-construction-chronology/chronology-results.json
    sha256: b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957
  - path: verification/wave33-rooted-construction-chronology/audit.md
    sha256: 1346992e11db72c4c94018293d3827214e2ee79e074490b8f905028e20fa30f1
method: >-
  Exact rational linear algebra on the fixed signed-Fano support, an SNF
  witness for its support-to-O incidence, centering of every unrestricted
  O-Q incidence matrix, orthogonal decomposition of R^70, and conversion of
  the nonlinear O-O equation into an integral rank-16 projector equation.
  A separate exact dynamic program counts all labeled binary columns allowed
  by the support coupling; a full enumeration records their cycle types.
command: >-
  python -I -B attempts/wave34-rooted-structural/check_results.py
  --full-census
outputs:
  - path: attempts/wave34-rooted-structural/reduction.py
    sha256: c3ad0a5b764e6e5045082ba28fc7c5ddfb2727859eac990f2845a8e5dd4c60e1
  - path: attempts/wave34-rooted-structural/check_results.py
    sha256: 9a4912cb4875d0ec7e54366491484fdf21c218ba2361858ea5d28a0e9af9ad1c
  - path: attempts/wave34-rooted-structural/test_reduction.py
    sha256: 3e9f2f95d44fda18c0733267a58fd101fa904bc94e283baa75b7b1616dcede4f
  - path: attempts/wave34-rooted-structural/results.json
    sha256: bd68070b172329e161f46d85e634aecf2348da16de785331e60e4b93a1f4dfc5
limitations: >-
  This is a strict exact reparameterization, not a complete search,
  construction, or infeasibility certificate. The canonical signed-Fano
  coordinates used by the checker are permutation-equivalent coordinates
  for invariant arithmetic; the permitted frozen comparison inputs do not
  expose the actual Wave 33 arrays for a direct byte-for-byte label binding.
  A verifier must perform that binding independently.
```

## 1. Exact domain and imported premises

Write the fixed support adjacency as \(A_S\), the fixed support-to-\(O\)
incidence as \(P\), the unknown symmetric hollow binary \(O\)-adjacency as
\(H\), and the unknown binary \(O\)-to-\(Q\) incidence as \(B\). Their sizes
are

```text
A_S: 14 x 14
P:   14 x 70
H:   70 x 70
B:   70 x 15.
```

The imported six blocks are

\[
\begin{aligned}
A_S^2+PP^\top&=12I-A_S+2J,\\
A_SP+PH&=2J-P,\\
PB&=2J,\\
P^\top P+H^2+BB^\top&=12I-H+2J,\\
HB&=2J-B,\\
B^\top B&=12I+2J.
\end{aligned}
\]

The binary/shape gates include \(H=H^\top\), \(\operatorname{diag}H=0\),
\(H_{ij}\in\{0,1\}\), row weight 9 for \(H\), row weight 3 and column weight
14 for \(B\), and no repeated \(B\)-row in any full solution. The \(B\)-rows
are therefore the 70 distinct triples of an otherwise unrestricted simple
\(2\!-\!(15,3,2)\) design. No design, automorphism, orbit representative, or
coordinate symmetry is fixed here.

For invariant arithmetic the checker uses the standard signed-Fano
coordinates: seven point vertices, seven line vertices, and \(A_S\) joins a
point to the four Fano lines not containing it. The 70 columns of \(P\) are
the edge copies of the bipartite multigraph \(M\) having multiplicity two on
the 21 incident point-line pairs and multiplicity one on the 28 nonincident
pairs. This is a relabeling for computation, not a quotient of the labeled
search domain.

## 2. Lemma 1 — exact kernel, SNF, and unrestricted \(B\)-columns

**DERIVED.** The matrix \(P\) has

```text
rank_Q(P) = 13,
dim ker(P) = 57,
SNF(P) = diag(1,...,1,0) with thirteen 1s.
```

Proof: after negating the seven line rows, \(P\) is an oriented
vertex-edge incidence matrix of the connected bipartite multigraph \(M\).
The signed bipartition vector

\[
z=(1^7,-1^7)
\]

spans the left kernel. Deleting one row and taking the 13 columns of the
explicit spanning tree in `results.json` gives determinant \(+1\). Thus the
rank is 13 and every nonzero Smith invariant is 1. In particular, the SNF
creates no divisibility obstruction to \(Pb=2\mathbf1\).

For a binary column \(b\), the equation \(Pb=2\mathbf1\) says exactly that
the selected labeled edge copies form a spanning 2-factor of \(M\). This is
already a strict labeled-domain reduction:

```text
weight-14 binary columns before P b = 2*1: 193,253,756,909,160
underlying capacity-bounded 2-factors:           4,946,952
labeled binary 2-factor columns:               574,118,037
```

The exact dynamic program has state

```text
(next point; seven remaining line degrees),
```

uses 1,090 cached states, and weights a singly used doubled incidence edge
by two. The full 4,946,952-leaf enumeration independently partitions the
574,118,037 labeled columns into 15 possible half-cycle types. The complete
distribution is in `results.json`; its largest class is type `7` with
262,332,336 columns, and its smallest is type `1+1+1+1+1+1+1` with 24.

This census is per labeled \(Q\)-column. It does not enumerate compatible
15-tuples and is not negative evidence.

## 3. Lemma 2 — the fixed 13-dimensional action of \(H\)

**DERIVED.** Put

\[
G=PP^\top,\qquad
R=P^\top G^+P,\qquad
C_{SO}=2J-P-A_SP,
\]

where \(G^+\) is the exact rational Moore-Penrose inverse. Then \(R\) is the
orthogonal projector onto

\[
\mathcal R=\operatorname{im}P^\top,\qquad \dim\mathcal R=13,
\]

and every six-block solution has the fixed restriction

\[
H_{\mathcal R}=C_{SO}^\top G^+P.
\]

Indeed, transposing the \(S\)-\(O\) block gives

\[
HP^\top=C_{SO}^\top.
\]

The fixed signed-Fano spectrum follows from the \(7\times7\) nonincidence
matrix \(N\), for which \(NN^\top=2I+2J\):

\[
\operatorname{spec}(A_S)=
4^1,(-4)^1,(\sqrt2)^6,(-\sqrt2)^6.
\]

The \(-4\) eigenspace is killed by \(P^\top\). On \(\mathcal R\), the fixed
eigenvalues of \(H\) are

\[
9^1,\quad(-1-\sqrt2)^6,\quad(-1+\sqrt2)^6,
\]

so

\[
\operatorname{tr}H_{\mathcal R}=-3.
\]

The exact checker confirms \(R^2=R=R^\top\),
\(\operatorname{tr}R=13\), \(H_{\mathcal R}=H_{\mathcal R}^\top\), and
\(PH_{\mathcal R}=C_{SO}\) over `fractions.Fraction`.

Before imposing \(B\), every symmetric real solution of the linear
\(S\)-\(O\) block differs only by a symmetric operator on
\(\ker P\). Thus its continuous affine freedom is at most

\[
\binom{57+1}{2}=1653
\]

rather than the original \(\binom{70}{2}=2415\) hollow symmetric entries
(hollowness and binarity shrink it further).

## 4. Lemma 3 — every unrestricted \(B\) fixes the full \(-1\) space

**DERIVED.** For any admissible, still-unrestricted labeled \(B\), define

\[
Y=B-\frac15J_{70,15}.
\]

The row/column/design equations give

\[
PY=0,\qquad
Y\mathbf1=0,\qquad
Y^\top Y=12I-\frac45J.
\]

Consequently

\[
\mathcal W=\operatorname{im}Y
\]

has dimension 14, lies in \(\ker P\), and is orthogonal to \(\mathcal R\).
Its orthogonal projector is

\[
E_W=\frac1{12}YY^\top
    =\frac1{12}BB^\top-\frac1{20}J.
\]

Since \(H\mathbf1=9\mathbf1\), the \(O\)-\(Q\) block
\(HB=2J-B\) is exactly

\[
HY=-Y.
\]

Thus the chosen \(B\) fixes \(H=-I\) on all of \(\mathcal W\); this is not an
assumed eigenspace or a selected design.

Let

\[
Q_U=I-R-E_W,\qquad
\mathcal U=\operatorname{im}Q_U.
\]

Then \(\dim\mathcal U=70-13-14=43\). After \(B\) is chosen, all remaining
symmetric linear freedom in \(H\) is a symmetric \(43\times43\) operator on
\(\mathcal U\), namely 946 continuous coefficients before the nonlinear and
binary gates.

## 5. Lemma 4 — the nonlinear block is exactly a rank-16 projector

**DERIVED.** If \(u\in\mathcal U\), then

\[
Pu=0,\qquad B^\top u=0,\qquad J u=0.
\]

Restricting the \(O\)-\(O\) block to \(\mathcal U\) gives

\[
H^2+H-12I=0.
\]

Because \(H\) is symmetric, its residual eigenvalues are only 3 and \(-4\).
The fixed trace on \(\mathcal R\oplus\mathcal W\) is

\[
-3-14=-17.
\]

Hollowness gives \(\operatorname{tr}H=0\), hence the residual trace is 17.
If \(a+b=43\) and \(3a-4b=17\), then

\[
a=27,\qquad b=16.
\]

Therefore there is a rank-16 orthogonal projector \(E\), supported on
\(\mathcal U\), such that

\[
H=H_{\mathcal R}-E_W+3Q_U-7E.
\]

Conversely, for a \(B\) satisfying the unrestricted incidence/design gates,
any such \(E\) for which the displayed \(H\) is hollow binary satisfies all
six blocks. This converse follows by checking the orthogonal summands:

```text
R: fixed S-O action and the fixed quadratic identity;
W: H=-I and BB^T=12I on W;
U: H=3I-7E, so H^2+H-12I=0;
cross terms: zero because R, W, U are mutually orthogonal invariant spaces;
1-vector: P^T P, H^2, BB^T, and 2J give 20+81+42=143.
```

Thus the nonlinear continuous locus is the Grassmannian of 16-planes in a
43-space, of dimension

\[
16(43-16)=432,
\]

before the entrywise hollow/binary conditions. This is a strict exact
reduction from 946 residual symmetric coefficients.

## 6. Lemma 5 — integral projector and modular/intersection form

**DERIVED.** Define the fixed rational matrices above and then the fixed
integer matrix

\[
C_\star=
21(H_{\mathcal R}+3I-3R)+\frac{21}{5}J.
\]

The exact signed-Fano calculation shows \(C_\star\) is integral. Its entries
have distributions

```text
diagonal:     51^28, 57^42
off-diagonal:
  -6^21, -3^84, 0^336, 3^168, 6^714, 9^840, 12^252.
```

For a putative solution set

\[
L=C_\star-7BB^\top-21H.
\]

The projector formula in Lemma 4 is equivalent to

\[
L=147E.
\]

Hence the entire unrestricted criterion is equivalently reduced to:

1. \(B\) is a binary \(70\times15\) matrix with row weight 3, column weight
   14, \(PB=2J\), and \(B^\top B=12I+2J\);
2. \(L=L^\top\) is integral and
   \[
   PL=0,\qquad B^\top L=0,\qquad L^2=147L;
   \]
3. the uniquely recovered
   \[
   H=\frac{C_\star-7BB^\top-L}{21}
   \]
   is symmetric, hollow, and binary.

No \(H\)-choice remains after \((B,L)\) is supplied. Conversely these three
conditions reconstruct all six blocks, so this does not discard a labeled
solution.

The diagonal is forced:

\[
\operatorname{diag}L=
\begin{cases}
36 &\text{on the 42 doubled-incidence O labels},\\
30 &\text{on the 28 single-nonincidence O labels}.
\end{cases}
\]

Thus

\[
\operatorname{tr}L=42\cdot36+28\cdot30=2352=147\cdot16.
\]

Since \(L\) is symmetric and \(L^2=147L\), it is positive semidefinite with
eigenvalues \(147^{16},0^{54}\). For distinct \(O\)-labels \(i,j\), let

\[
r_{ij}=(BB^\top)_{ij}=|T_i\cap T_j|\in\{0,1,2\}.
\]

Then the exact intersection/nonlinear compatibility is the two-valued rule

\[
L_{ij}=(C_\star)_{ij}-7r_{ij}-21H_{ij}.
\]

It can be combined immediately with the principal-minor bound

\[
L_{ij}^2\le L_{ii}L_{jj}.
\]

Two useful exact modular shadows are

\[
L\equiv C_\star\pmod7,\qquad
L\equiv-BB^\top\pmod3.
\]

The fixed matrix \(C_\star\bmod7\) has rank 5 and square zero. Therefore
every solution's rank-16 projector numerator has the same rank-5
square-zero residue modulo 7. These are exact constraints, not a modular
exclusion.

## 7. Exact commands, dependencies, seeds, and observed runtimes

Environment:

```text
Python 3.13.14
standard library only
seed: none (all procedures deterministic)
```

Quick exact result check:

```powershell
python -I -B attempts/wave34-rooted-structural/check_results.py
```

Observed result: `PASS`, about 3 seconds.

Full committed-result check, including all 4,946,952 underlying 2-factors:

```powershell
python -I -B attempts/wave34-rooted-structural/check_results.py --full-census
```

Observed result: `PASS`, 44.4 seconds.

Full tests:

```powershell
$env:WAVE34_FULL_CENSUS='1'
python -B -m unittest discover `
  -s attempts/wave34-rooted-structural `
  -p 'test_*.py' -v
```

Observed result: seven tests passed, 45.769 seconds.

Deterministic regeneration to standard output:

```powershell
python -B attempts/wave34-rooted-structural/reduction.py --full-census
```

Observed runtime: 45.6 seconds. `check_results.py` compares the parsed
regeneration with committed `results.json` and fails closed on any mismatch.

## 8. Complete versus restricted coverage

The algebraic equivalence covers every labeled \(B,H\) in the frozen
six-block graph criterion. It assumes no automorphism and fixes no
\(O\)-\(Q\) design. The 2-factor count covers every labeled binary *single
column* satisfying \(Pb=2\mathbf1\); it does not cover every compatible
15-column design tuple. The projector checker proves fixed-side identities
and the exact reduction, but does not enumerate all rank-16 integral
projectors or all compatible pairs \((B,L)\).

## 9. Failed routes retained

1. **SNF divisibility exclusion failed.** The SNF has thirteen unit factors,
   so \(Pb=2\mathbf1\) has no torsion obstruction. Its value is the exact
   57-dimensional cycle-space description, not an exclusion.
2. **Modulo 7 rank contradiction failed.** The fixed residue has rank 5,
   which is compatible with rational rank 16, and is already square-zero.
3. **Modulo 3 nilpotence failed.** The identity
   \(L\equiv-BB^\top\pmod3\) gives \(L^2=0\) using
   \(B^\top B\equiv-J\) and \(B\mathbf1=3\mathbf1\); it does not contradict
   the design equations.
4. **Two-by-two positivity failed to close.** The bounds on
   \(L_{ij}\) prune local intersection/adjacency combinations but do not
   produce a global contradiction beyond the known nonnegative
   common-neighbour restrictions.
5. **Column enumeration is far from tuple enumeration.** Even after the
   exact reduction, 574,118,037 labeled choices remain per \(Q\)-column.
   The census is not evidence that a compatible 15-tuple exists or does not
   exist.

## 10. Strongest self-objection

The reduction is exact but still leaves a difficult coupled object: an
unrestricted labeled simple \(2\!-\!(15,3,2)\) design whose columns are
2-factors of \(M\), together with a quantized rank-16 projector on a
43-dimensional design-dependent subspace. Dimension 432 is a substantial
shrink, not a solution.

In addition, the permitted frozen comparison artifacts state and hash-check
the fixed support but do not expose its actual arrays. The checker therefore
uses a canonical permutation-equivalent signed-Fano reconstruction.
Everything proved is permutation-equivariant, and no symmetry quotient is
taken, but a separate verifier should evaluate \(C_\star\) on the exact
Wave 33 label order and bind the canonical invariant distributions to those
bytes before publication.

## 11. Strongest justified conclusion

**DERIVED:** Target R-S admits a strict, exact, unrestricted labeled
reduction from \((B,H)\) to:

```text
B: 15 labeled 2-factors satisfying the full simple 2-(15,3,2) incidence
   and row-multiplicity constraints;
L: an integral rank-16 projector numerator supported on the exact
   43-dimensional joint kernel, with L^2=147L and binary H recovery.
```

The free symmetric \(O\)-block falls from 1,653 coefficients after the fixed
support equation, to 946 after an unrestricted \(B\), to a 432-dimensional
rank-16 projector locus before quantization. Each \(B\)-column falls from
193,253,756,909,160 weight-14 vectors to exactly 574,118,037 labeled
2-factors.

**UNKNOWN:** no binary pair, complete exclusion, full rooted endpoint,
`n3=708` exclusion, Conway-99 resolution, or novelty conclusion is supplied.
