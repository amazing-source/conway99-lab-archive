# Wave 203 proof-A hostile audit: two-center incidence

## Verdict

`ACCEPTED_AS_DERIVED`.

I reconstructed the two five-slot sets, partial third-block map, matched
reverse flag, canonical coefficient normalization, and four-column Gram
obstruction independently, then compared against the sealed Wave203
proof-B source. No mathematical discrepancy survived.

The valid conclusions are:

```text
m_(x->y)+m_(y->x)<=5,
3n3+4p3<=5|U|,
epsilon>=5b,
```

where `b` counts nonprivate selected unordered labels occupying both
orientations.

No `Q>=7060` conclusion follows from this theorem alone because no frozen
row forces `b>0`. This audit does not repair or extend the source.

```yaml
role: proof_a
date_utc: 2026-07-29T07:40:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Hostile independent audit of sealed Wave203: reconstruct the two
  five-slot systems and matched reverse obstruction, attack normalization
  and distinct-column assumptions, verify the selected-incidence and
  epsilon consequences, and test whether any Q>=7060 claim follows.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave203-two-center-incidence-proof-b/package-manifest.sha256: b412cce1a737b3b50718aabb399978ca2956cea0edbbe1c1f955f8083447d5b8
method: >-
  Independent two-center incidence reconstruction, finite-field relation
  addition, exact Gram multiplication and rank, selected/full-pool
  separation, and coefficient counting. No graph, code, cover, SAT, LP,
  configuration, enumeration, isomorphism, or brute-force search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave203-two-center-incidence-proof-a-audit\exact_check.py
  --verify
  attempts\wave203-two-center-incidence-proof-a-audit\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave203-two-center-incidence-proof-a-audit\test_exact_check.py
outputs:
  - agents/2026-07-29-wave203-two-center-incidence-proof-a-audit.md
  - attempts/wave203-two-center-incidence-proof-a-audit/
limitations:
  - This is a proof-agent audit, not clean-room verifier promotion.
  - It is conditional on the prism-free rank-11 endpoint.
  - No row forces any both-oriented selected label, so no 7,060 bound is
    claimed.
  - No endpoint graph, code, cover, or flag system is constructed.
```

## 1. Reconstruct the shared five slots

For a nonedge `xy`, its common neighbors `a,b` lie in distinct triangle
blocks `X_a,X_b` through `x` and `Y_a,Y_b` through `y`. The remaining
five `x`-star blocks are anticomplete to `y`; call this set `C_x(y)`.
The remaining five `y`-star blocks form `C_y(x)`.

An `x->y` exact-three flag has leaf triangle `T in C_y(x)` and

```text
A_x(T)={X_a,X_b,S}
```

for a unique `S in C_x(y)`. Since the fixed-center map
`T -> A_x(T)` is simple/injective, `T -> S` is a partial injection into
five slots.

A reverse `y->x` flag is indexed by its leaf block `S in C_x(y)`.
Different reverse leaf blocks are different slots. Thus forward images
and reverse domains really are subsets of the same five-element set; no
unproved identification of `C_y(x)` with `C_x(y)` is used.

## 2. Attack `j(S,T)=2` and reverse matching

The verified leaf-type rule for

```text
A_x(T)={X_a,X_b,S}
```

assigns pair types `X_aX_b`, `X_aS`, `X_bS` to the three leaves of `T`.
The two noncenter vertices of `S` therefore meet the two leaves of types
`X_aS`,`X_bS`, one each. Hence exactly two graph edges run between the
triangle blocks `S,T`:

```text
j(S,T)=2.
```

If a reverse flag has leaf block `S`, then the leaf `x` has type
`Y_aY_b`, so `Y_a,Y_b` lie in `A_y(S)`. The cross-edge count
`j(S,T)=2` puts `T` in that same exact-three set. Its size is three, so

```text
A_y(S)={Y_a,Y_b,T}.
```

Thus the reverse flag on the matched slot necessarily uses `T` as its
third block. This step is forced, not a surjectivity assumption.

## 3. Normalize and add the two relations

With the globally frozen triangle columns and leaf coefficient normalized
to one, the two canonical relations on column order

```text
(T,S,X_a,X_b,Y_a,Y_b)
```

are

```text
(1,2,2,2,0,0),
(2,1,0,0,2,2).
```

Their sum over `F_3` is

```text
(0,0,2,2,2,2),
```

so matched occupancy would force an all-equal relation on
`X_a,X_b,Y_a,Y_b`.

There is no relative-scaling gap. Each relation is projectively unique,
and setting its own leaf coefficient to one fixes its scalar. The
coefficient of the other leaf block is then canonically two in both
relations.

The four surviving columns are pairwise distinct:

- `X_a!=X_b` and `Y_a!=Y_b` by the local matching geometry;
- an `x`-star triangle cannot equal a `y`-star triangle, because a common
  block would contain the nonadjacent vertices `x,y`.

Their frozen Gram is

```text
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].
```

Exact arithmetic gives rank three, checkerboard kernel
`<(1,2,2,1)>`, and image `(1,1,1,1)` on the all-equal vector. Therefore
the all-equal word is not a relation and matched occupancy is impossible.

## 4. Slot and selected-multiplicity audit

Forward flags occupy distinct image slots by partial injectivity. Reverse
flags occupy distinct domain slots because their leaf blocks differ.
Matched forward/reverse use of one slot is impossible. Hence their two
slot sets are disjoint subsets of five slots:

```text
m_full(x->y)+m_full(y->x)<=5.
```

Selected exact-three circuits form a subset of the full flag pool. A
minimal cover cannot select both companion circuits on one flag, so
selected multiplicity is also bounded by the number of full occupied
flag slots:

```text
s_e<=5.
```

This addresses the possible full-pool/selected-pool gap.

## 5. Exact consequences and boundary

Each selected exact-three circuit contributes three unordered labels.
Every `p3` private label has selected multiplicity one; every other label
in `U` has multiplicity at most five. Therefore

```text
3n3
 <=p3+5(|U|-p3),
3n3+4p3<=5|U|.                                  (1)
```

If both orientations of one nonprivate unordered label are occupied with
multiplicities `r,s>=1`, their total is at most five. Their Wave198
orientation deficit is

```text
(5-r)+(5-s)=10-(r+s)>=5.
```

Summing over the `b` both-oriented labels gives

```text
epsilon>=5b.                                    (2)
```

The low patterns `(1,1),(1,2),(2,2)` cost respectively `8,7,6`.

Equation (2) does not imply `b>0`. In particular, all nonprivate selected
labels may occupy one orientation in the current scalar/incidence rows.
Thus Wave203 strengthens local structure but does not itself exclude
`Q0=7059` or prove `Q>=7060`.

## Boundary

```text
shared five-slot identification:          AUDIT PASS
partial injection and reverse domain:     AUDIT PASS
j(S,T)=2 and reverse third block T:        AUDIT PASS
leaf-normalized relation addition:        AUDIT PASS
four columns pairwise distinct:           AUDIT PASS
all-equal Gram obstruction:               AUDIT PASS
combined full/selected capacity <=5:      AUDIT PASS
3n3+4p3<=5|U| and epsilon>=5b:             AUDIT PASS
Q>=7060 from Wave203 alone:                no
verdict:                                   ACCEPTED AS DERIVED
```
