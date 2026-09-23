# Wave 20 global Schur-projector adversarial audit

Verdict: **PASS for the scoped `DERIVED` conditional claim**

```text
putative srg(99,14,1,2)  ==>  n3 >= 705
                              induced_C6_count >= 209991.
```

The proof is exact and global.  It uses no automorphism, catalog, solver
negative, floating-point eigenvalue, or prior equality-case exclusions.  The
argument supplies a necessary condition only: it neither constructs nor
excludes the Conway graph.  Conway-99 remains `UNKNOWN`; novelty and
literature status are out of scope and remain `UNKNOWN`.

One nonblocking documentation defect was found.  The introductory sentence
of `attempts/wave20-global-obstruction/failed-routes.md` still says
`n3>=699`, although that file's later section, the proof, checker, JSON, and
run report all consistently use the strengthened endpoint 705.  No
mathematical inference uses the stale phrase.  It is recorded rather than
silently repaired.

```yaml
role: verifier
date_utc: 2026-07-23T16:25:10Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: DERIVED
audit_verdict: PASS_WITH_NONBLOCKING_DOCUMENTATION_DEFECT
scope: >
  Adversarial verification of the conditional global Schur-projector proof
  that every putative srg(99,14,1,2) has n3>=705, and of the inherited
  induced-C6 translation.
inputs:
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  attempts/wave20-global-obstruction/exact_check.py: a3cbe6dfe018965043903c368932f89f9fade30cf301ffe3454cd638966d00c8
  attempts/wave20-global-obstruction/test_exact_check.py: 597781a740dcc621c448ed7ffaa194e2ed5e004d210630777db8449a8d877231
  attempts/wave20-global-obstruction/exact-checks.json: 6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2
  attempts/wave20-global-obstruction/failed-routes.md: 23355b845f17dac5b4ef260544d1664c8943999634ee8d02f63d5a6b0ef048b2
  attempts/wave20-global-obstruction/failed-runs.md: 7ff19bf3dfb9e144447cbd1021165f463b15c8e2c640c0f08110cd705008e610
  attempts/wave20-global-obstruction/run-report.yaml: 89f9ac63eae81913068b8391eaeb8559b2b5e2b8ce989402946079dffeb7eef2
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  STRUCTURE.md: 7dff67ec4b8796049ed5603b3733d3f4442a1fe607d258f45b835b8a1d7dad5c
method: >
  Blind hash freeze; independent precomparison derivation from the target
  and public structural premises; a separately written exact-integer/Fraction
  checker; sixteen independent tests; hostile scaling, entry, congruence,
  and endpoint mutations; then submitted-source inspection, eighteen-test
  replay, deterministic JSON regeneration, and byte comparison.
command: |
  python -B independent_check.py --output independent-results.json
  python -B -m unittest -v test_independent_check.py
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output independent-verifier/submitted-regenerated.json
outputs:
  attempts/wave20-global-obstruction/independent-verifier/preinspection-baseline.yaml: db6211c9ce36113f8160c41b5d534b2ab201cbe3fb1df4172fc48faaba7d95fb
  attempts/wave20-global-obstruction/independent-verifier/public-premise-freeze.yaml: 9ccd6651cf96c155ecf970d5d5c77876ce6a114eec0a757bf95ad24c0b49c6fa
  attempts/wave20-global-obstruction/independent-verifier/independent-reconstruction.md: 175f9cee0ad254130810e3c3951ffea77913239728d7b8d7faa5cde0e395defc
  attempts/wave20-global-obstruction/independent-verifier/independent_check.py: efd00777b38fc180c11434cb452111ae7745109844d68aba763460b219208cfc
  attempts/wave20-global-obstruction/independent-verifier/test_independent_check.py: 3aeb71a4ce6563a8a189770cdb4a3773ae7355ec0325824d0d78a618fdfb9bd0
  attempts/wave20-global-obstruction/independent-verifier/independent-results.json: 575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637
  attempts/wave20-global-obstruction/independent-verifier/audit-results.json: 9b24e8f521f0e076c2f55e38c6455d0c6ad6bfbc31e315aef0f044c87ebfc608
  attempts/wave20-global-obstruction/independent-verifier/submitted-regenerated.json: 6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2
limitations:
  - The exact scripts accompany rather than replace the human combinatorial bridge.
  - No 231-by-231 triangle graph is instantiated, because target existence is unknown.
  - The submitted git_commit field was not checked because this task prohibited Git.
  - Exact deployment model and reasoning-effort settings were not exposed to the verifier.
  - Novelty and target resolution remain UNKNOWN.
```

## 1. Independence and frozen provenance

At `2026-07-23T16:11:25Z`, before opening, printing, importing, executing, or
otherwise inspecting any submitted content, the seven named candidate
artifacts were hashed in
`attempts/wave20-global-obstruction/independent-verifier/preinspection-baseline.yaml`.
Immediately before comparison, all seven hashes were recomputed and matched
the freeze exactly.

The target and selected previously public premises were separately frozen at
`2026-07-23T16:12:17Z`.  From those inputs alone, the verifier reconstructed
the full argument and wrote:

```text
independent-reconstruction.md
independent_check.py
test_independent_check.py
independent-results.json
```

The independent checker and all 16 tests passed before candidate inspection.
Their hashes were then frozen at `2026-07-23T16:20:37Z`.  The first detached
test invocation from the repository root failed at import time because the
checker directory was absent from `sys.path`; zero tests ran.  That
harness-only failure and the corrected working-directory invocation are
retained in the verifier's `failed-runs.md`.

No candidate code is imported by the independent checker.

## 2. Obligation-by-obligation result

| Obligation | Status | Adversarial conclusion |
|---|---:|---|
| Blind preinspection hash freeze | PASS | All seven submitted byte strings were frozen before inspection and remained unchanged at comparison. |
| Triangle-incidence spectrum of `Gamma` | PASS | Derived solely from `BB^T=7I+X`, `B^TB=3I+Gamma`, and the target spectrum. |
| Combinatorial entries of `C=Gamma^2-5Gamma-18I` | PASS | Diagonal and intersecting entries are zero; disjoint entries are exactly the cross-edge number `r in {0,1,2,3}`. |
| Fixed-side counts `a_r(T)` | PASS | The three moments are `212`, `216`, and `36`; solving gives `(20+q,180-3q,3q,12-q)`. |
| Ordered/unordered scaling | PASS | The second moment uses `72/2=36`; globally `2n3=sum_T a_2(T)`, not `n3=sum_T a_2(T)`. |
| `q/n3` relation and divisibility | PASS | `2n3=3 sum_T q(T)`, hence `3|n3`. |
| Exact projector `E0` | PASS | Lagrange interpolation and the cubic relation both give the submitted formula. |
| `M=21E0` scaling and identities | PASS | `M^2=21M`; diagonal 4; pair entries `0,1,0,-1,-2` by type. |
| Every `M mod 2` row nonzero | PASS | Each row has `a_0+a_2=20+4q` odd entries, and already `a_0=20+q>0` suffices. |
| `W=M o M` PSD | PASS | Exact application of the Schur product theorem to PSD `M`. |
| `mathcal A=MWM` PSD and integral | PASS | `x^T mathcal A x=(Mx)^T W(Mx)>=0`; all factors are integral. |
| `mathcal A congruent M (mod 2)` | PASS | `W congruent M`, so `MWM congruent M^3=441M congruent M`. |
| `D=(W-M)/2` alternating modulo two | PASS | `D` is integral symmetric and `D_ii=(16-4)/2=6` is even. |
| Every `mathcal A_ii` divisible by four | PASS | `M^3_ii=441*4`; the `2MDM` diagonal is a multiple of four by the alternating-form law. |
| PSD zero-diagonal lemma | PASS | If a PSD diagonal entry vanished, every entry in that row would vanish, contradicting the nonzero row modulo two. |
| Trace identity | PASS | `tr(mathcal A)=21 sum M_ij^3=84(n3-693)`. |
| `Delta=3,6,9` hostile endpoints | PASS | Traces `252,504,756` are each below the forced floor `4*231=924`. |
| Final conditional lower bound | PASS | The real threshold is `Delta>=11`; `Delta` is a multiple of three, so `Delta>=12` and `n3>=705`. |
| Induced-six-cycle translation | PASS | The public exact identity gives `209286+705=209991`. |
| Necessary bound versus target resolution | PASS | The report consistently leaves construction, nonexistence, and novelty unresolved. |
| Optional binary-rank extension | PASS | The human determinant argument proves `rank_F2(M)=44`; it is correct and unused by the bound. |
| Submitted executable replay | PASS | 18/18 tests passed; regenerated JSON was byte-identical. |
| Failed-route endpoint wording | FAIL (nonblocking) | One stale introductory `n3>=699` survives in `failed-routes.md`; all operative artifacts use 705. |
| Submitted `git_commit` provenance | UNKNOWN | Deliberately not checked under the explicit no-Git instruction. |
| Conway-99 existence/nonexistence | UNKNOWN | The inequality is compatible with target existence. |
| Novelty/literature status | UNKNOWN | Out of scope by assignment. |

## 3. Triangle-incidence and cross-edge quantifiers

Let `X` be the target adjacency matrix and `B` the `99 x 231`
vertex-triangle incidence matrix.  Every target edge lies in its unique
triangle and every vertex lies in seven triangles.  Distinct triangles
cannot share an edge.  Therefore

```text
BB^T = 7I+X,
B^TB = 3I+Gamma.
```

The eigenvalues of `BB^T` are `21^1,10^54,3^44`, all positive.  Thus `B`
has rank 99; no unproved rank assumption is hidden.  The 99 nonzero
eigenvalues transfer to `B^TB`, whose remaining 132 eigenvalues vanish.
Subtracting three gives exactly

```text
spec(Gamma)=18^1,7^54,0^44,(-3)^132.
```

For

```text
C=Gamma^2-5Gamma-18I,
```

the three entry cases were checked separately.

1. On the diagonal, `Gamma^2_TT=18`.
2. If `T,U` meet at `x`, the other five triangles through `x` meet both.
   A further common neighbor meeting the two sides at distinct vertices
   would require an extra edge between different matched pairs in
   `G[N(x)]=7K2`; meeting one side again at `x` would reuse a unique
   triangle on an edge.  Hence there are exactly five.
3. If `T,U` are disjoint, a common `Gamma`-neighbor contains a unique
   cross-edge and every cross-edge has a unique graph-triangle.  A triangle
   cannot contain two cross-edges without reusing an internal side edge.
   This is a bijection, not merely a count in one direction.

Two cross-edges cannot share an endpoint: the internal edge between their
opposite endpoints would acquire a second common neighbor.  Hence the
disjoint entry is exactly `r(T,U) in {0,1,2,3}`.

The spectral images

```text
18 -> 216, 7 -> -4, 0 -> -18, -3 -> 6
```

were independently recomputed.

## 4. Fixed-triangle arithmetic and pair orientation

For fixed `T`, 18 of the other 230 triangles intersect `T`, leaving 212.
There are `3*(14-2)=36` edges leaving `T`.  For a leaving edge `xy`, six of
the seven triangles through the external endpoint `y` are disjoint from
`T`; the seventh is the unique triangle containing `xy`.  This gives the
first moment 216 without assuming that external endpoints are uniformly
distributed.

For the second moment, there are

```text
3*2*12=72
```

ordered choices `(x,z,y)`.  The pair `y,z` is nonadjacent; its common
neighbors are `x` and one other vertex, which supplies the paired
cross-edge.  Every unordered pair of cross-edges is generated twice, once
from either end.  The correct moment is therefore 36.  A hostile mutation
retaining 72 is detected.

The unique nonnegative solution with `q=12-a_3` is

```text
(a_0,a_1,a_2,a_3)=(20+q,180-3q,3q,12-q), 0<=q<=12.
```

The verifier checked every one of the 13 possible `q` rows.  Since `r=2`
means exactly two independent cross-edges and there are no other cross
edges, these pairs are precisely induced `N3`s.  Fixing either side orders
each unordered pair twice:

```text
2n3=sum_T a_2(T)=3sum_T q(T).
```

This verifies both the factor and all quantifiers.

## 5. Projector normalization and Schur trace

The exact zero-eigenspace projector is

```text
E0=((Gamma-18I)(Gamma-7I)(Gamma+3I))/378.
```

Using

```text
Gamma^3-4Gamma^2-21Gamma=18J
```

gives

```text
E0=(21I+4Gamma-Gamma^2+J)/21
  =(3I-Gamma-C+J)/21.
```

Therefore

```text
M=21E0,
M^2=21M,
M_TT=4,
M_TU=0                 for intersecting pairs,
M_TU=1-r(T,U)          for disjoint pairs.
```

The scaling 21 is essential for the displayed integral matrix.  The hostile
scale 20 gives diagonal `80/21` and is rejected.  Omitting the intersecting
zero category or mutating it to one is also detected; the latter changes
the row sum by 18 and the cubic row sum by 18.

For `W=M o M`, Schur positivity gives `W` PSD.  Hence
`mathcal A=MWM` is PSD and integral.  Its trace is

```text
tr(mathcal A)=tr(WM^2)=21tr(WM)=21sum_(T,U) M_TU^3.
```

At a fixed `T`, including every zero category, the cubic row sum is

```text
4^3+a_0-a_2-8a_3=6q(T)-12.
```

Summation and `sum q=2n3/3` give

```text
sum M_TU^3=4n3-2772=4(n3-693),
tr(mathcal A)=84(n3-693).
```

Positivity alone proves the intermediate necessary bound `n3>=693`.

## 6. Mod-two and mod-four lift

Integer squaring gives `W congruent M (mod 2)`.  Thus

```text
mathcal A=MWM congruent M^3=441M congruent M (mod 2).
```

Each row of `M mod 2` is nonzero: it has exactly
`a_0+a_2=20+4q` odd entries.  This holds even for the possible `q=0` rows
and uses no active-triangle gap.

Now

```text
D=(W-M)/2
```

is integral symmetric, and `D_TT=6` is even.  Therefore `D mod 2` is a
symmetric zero-diagonal matrix.  For every integral row vector `v`,
off-diagonal terms in `v^TDv` occur in pairs and diagonal terms vanish, so

```text
v^TDv=0 (mod 2).
```

Since

```text
mathcal A=M^3+2MDM,  M^3=441M,
```

each diagonal entry is divisible by four.  A mutation with one odd
`D`-diagonal entry has witness vector `(1,0)` and produces quadratic value
one modulo two, so the proof correctly depends on the zero-diagonal
premise.

For a real PSD matrix, `A_ii=0` implies `A_ij=0` for all `j`, either from
the nonnegative `2 x 2` principal minors or PSD Cauchy--Schwarz.  Such a
zero row would contradict `mathcal A congruent M (mod 2)`.  Hence all 231
diagonal entries are positive multiples of four:

```text
tr(mathcal A)>=231*4=924.
```

The exact hostile endpoint table is:

| `Delta=n3-693` | `tr(mathcal A)=84Delta` | versus 924 | Result |
|---:|---:|---:|---|
| 0 | 0 | below | rejected |
| 3 | 252 | below | rejected |
| 6 | 504 | below | rejected |
| 9 | 756 | below | rejected |
| 12 | 1008 | above | not rejected by this arithmetic |

Thus `Delta>=11`.  Because `3|n3` and `3|693`, `3|Delta`; the first allowed
value is 12.  This proves the scoped endpoint 705 but makes no existence
claim at equality.

## 7. Submitted artifacts and retained routes

The submitted tests replayed as

```text
Ran 18 tests in 0.081s
OK
```

Regenerating the JSON into the verifier directory produced 4,625 bytes and
SHA-256

```text
6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2,
```

byte-for-byte identical to the submitted `exact-checks.json`.

The submitted checker correctly labels itself an arithmetic checker rather
than a validator of the prose-to-combinatorics bridge.  Its 40 mixed Schur
triples were independently parsed without importing the submitted module.
The strongest lower endpoint is 693 from `(0,0|0)`, the closest feasible
upper endpoint is 17010 from `(0,0|7)`, and every displayed affine triple is
nonnegative at both endpoints of `[693,4158]`.  Thus the retained
non-improvement claim is arithmetically consistent.  Gegenbauer and
opposite-edge routes are not premises of the 705 proof and are not promoted
to evidence for target resolution.

The optional binary-rank paragraph is also correct.  `M` has 44 nonzero real
eigenvalues, all 21.  The sum of its principal 44-minors is `21^44`, hence
odd, so some 44-minor is odd.  Every 45-minor vanishes over the integers.
Therefore `rank_F2(M)=44`.  Since `mathcal A mod 2=M` and
`rank_R(mathcal A)<=rank_R(M)=44`, both ranks of `mathcal A` equal 44.
This extension is unused in the trace bound.

The only artifact inconsistency is the stale `n3>=699` phrase in the first
paragraph of `failed-routes.md`.  The same file later says
“after `n3>=705`,” and every operative formula and output uses 705.

## 8. Model, runtime, and status boundary

The verifier surface identifies this agent as Codex based on GPT-5.  The
exact deployment model name, reasoning-effort setting, and service tier were
not exposed; the subagent inherited the parent configuration without an
explicit override.  Runtime versions were:

```text
Python 3.13.14
PowerShell 5.1.26100.8875
Microsoft Windows NT 10.0.26200.0
```

Final status:

```text
core global Schur proof:                 PASS
submitted arithmetic/tests/provenance:  PASS
nonblocking failed-routes wording:       FAIL (stale 699)
conditional necessary bound:            n3>=705
conditional induced-C6 bound:           >=209991
construction at n3=705:                 NOT CLAIMED
Conway-99 existence/nonexistence:        UNKNOWN
novelty/literature status:               UNKNOWN / OUT OF SCOPE
```
