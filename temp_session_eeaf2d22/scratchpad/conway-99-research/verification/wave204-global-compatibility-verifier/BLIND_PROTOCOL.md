# Wave204 source-blind verification protocol

Frozen at `2026-07-29T19:06:57Z`, before opening any file under:

- `attempts/wave204-literature-hostile-controls/`
- `attempts/wave204-global-slot-holonomy-proof-a/`
- `attempts/wave204-projector-fourth-order-proof-b/`

The only inputs used to freeze this protocol were the orchestrator's V1, V2,
and V3 claim text and the repository `AGENTS.md`.  In particular, file names
were visible in directory listings, but no submitted Wave204 manifest,
prose, certificate, or code was opened.

## Frozen claim split

### V1: relaxed 99-center skeleton

The checker will independently construct and validate the following explicit
relaxed model.

1. Centers are `Z/99Z`.  The degree graph joins modular differences
   `+-1,...,+-7`.  Thus it is simple and 14-regular, and its complement is
   84-regular.
2. At center `c`, the seven degree blocks are
   `{c-i,c+i}` for `i=1,...,7`.
3. The 84 complement neighbors at a center are bijected, in canonical order,
   with the 21 unordered pairs of degree blocks times four leaf values.
4. The 13 local triples are the Hilton--Milner family
   `{1,2,3}` together with `{0,a,b}` where
   `1 <= a < b <= 6` and `{a,b}` meets `{1,2,3}`.  The checker tests
   distinctness, pairwise intersection, and empty total core at all 99
   centers.
5. The numerical fields are checked literally:
   `|U|=3360`, `J=3561`, `delta=3`, `n3=1200`, `p3=3123`,
   `q=237`, `epsilon=708`, and
   `L=delta-3q+epsilon=0`.
6. The `n3` and `p3` rows independently occupy respectively three and four
   distinct positions in a canonical 5-slot carrier on `U`, without position
   collisions.  This makes the deficit
   `5|U|-(3n3+4p3)=708` explicit rather than merely recomputing the scalar.
7. There are 237 nonprivate labels: 234 have multiplicity two and three have
   multiplicity three.  Their primary oriented placements are three per
   center at centers 0 through 78 and zero at centers 79 through 98.
   Each primary placement has two injective partial maps into a five-slot
   carrier, both with image `{0,1,2}`.  Hence the maximum combined image size
   is three and the number `b` of fully occupied five-slot carriers is zero.

This formalization deliberately gives no SRG common-neighbor parameters, no
231-column ternary/rank-11 realization, no circuit cover, and no graph/code or
Conway-99 conclusion.  Verification is scoped to this explicit relaxed
certificate semantics.  Any submitted source using a materially different
meaning must be reported as a semantic discrepancy, not silently reconciled.

### V2: coboundary versus projected center-walk defect

The checker will work over `F_3^11` with bilinear Gram matrix
`diag(1,...,1,2)`, whose determinant 2 is nonsquare.

1. For `i=0,...,6`, let `a_i=e_i-sum_{j=0}^6 e_j`.  The seven distinct
   vectors are singular, sum to zero, and have mutual inner product 2.  Their
   negatives give a second distinct normalized local A6 simplex.  In this
   protocol, `b=0` means the checked diagonal singular value of every local
   simplex column is zero.
2. For every true arrow `S->T` and every globally fixed slot `s`, define
   `g_s(S,T)=z[T,s]-z[S,s]`.  Direct vector addition must telescope to zero on
   every tested block cycle.
3. Exact cycles of lengths 3, 4, and 5 use both simplex signs.  Every edge has
   only the one-point partial injection `0->0`.  At each intermediate center,
   the incoming leaf slot is 0 while the next outgoing third-block slot is 1.
   The missing connector is therefore explicit.
4. The projected walk sum
   `sum(z[next,0]-z[current,1])` must be nonzero on all three cycles, while
   every true fixed-slot coboundary sum is zero.
5. The partial injection `0->0` must admit both the identity extension and
   the transposition `(1 2)` in `S_5`.  Thus neither a unique nor a canonical
   total `S_5` map follows from the one-point data.

The source-blind labels are:

- `VERIFIED` for the fixed-column coboundary identity.
- `REFUTED_WITH_SCOPE` for the two implications that edgewise one-point
  injections alone force center-walk slot chaining or a determined total
  `S_5` map.
- `CANDIDATE` only for relevance to any 99-star/global-column system, because
  the controls intentionally omit those premises.

### V3: local fourth-order projector detector

All matrix arithmetic is exact over `F_3`.

1. Set `G=J_6-I_6`, `C=J_6+N`, and `H=G^-1`.
   For each 2-regular bipartite biadjacency `N` with cycle half-length
   partition `6`, `4+2`, `3+3`, or `2+2+2`, the checker will verify directly
   that
   `H C H C^T = N N^T`.
2. It will test `tr(NN^T)=0` and
   `h=tr((NN^T)^2)`, expecting `h=1` only for `4+2` and zero for the other
   three types.
3. Using the exact characteristic-three trace formulas
   `tr(wedge^2 M)=((tr M)^2-tr(M^2))/2` and
   `tr(Sym^2 M)=((tr M)^2+tr(M^2))/2`, it will test exterior trace `h` and
   symmetric trace `2h`.
4. Independently fixed rank-11 witnesses use
   `B=diag(1,...,1,2)`, `P=diag(I_6,0_5)`, and the two explicit 11-by-6
   spanning matrices embedded in `independent_verifier.py`.  The checker will
   prove that both spans are nondegenerate rank six, their orthogonal
   projectors are idempotent and B-self-adjoint, both have
   `tr(PQ)=0` and intersection dimension one, but their fourth traces are
   respectively 2 and 0.  This refutes, with exact local scope, the claim that
   pair trace plus intersection dimension determines fourth trace.

The optional 99-projector global controls are not part of the blind
reconstruction.  If replayed successfully after unsealing, they remain
quarantined as relaxed controls because their stated repeated directions and
missing graph-incidence/dual-distance premises prevent promotion.

## Mutation and acceptance tests

The test suite must reject at least:

- a deleted degree edge;
- a repeated member in one four-valued pair fiber;
- a local triple-family core mutation;
- a colliding 5-slot cover position;
- a false full-occupancy count;
- a matched projected cycle substituted for the nonmatching control;
- an invalid claimed `S_5` extension;
- a changed V3 cycle type expectation;
- a singular rank-11 witness span.

The blind phase is complete only after:

1. the independent checker and tests pass;
2. a canonical result JSON is recorded;
3. SHA-256 hashes of the protocol, checker, tests, certificate parameters, and
   blind result are frozen in `SOURCE_BLIND_FREEZE.sha256`;
4. the freeze manifest is itself hashed and that hash is recorded in the run
   report.

