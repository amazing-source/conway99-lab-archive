# Wave 31 post-freeze addendum: sign involution and `-4` projector

```yaml
role: literature
date_utc: 2026-07-24T06:33:31Z
git_commit: 5652578111999645a9d5427d0716053de79e0902
claim_label: CANDIDATE
scope: >-
  Exact post-freeze statement of a new candidate obstruction to any proper
  coordinate block of E=M/21, plus a bounded prior-art search for its
  diagonal-sign commutant, signed-triangle, and primitive-idempotent
  signature. The missing constancy lemma is not asserted.
```

This addendum was created after `protocol-freeze.md` and does not alter that
pre-search freeze. The target below is a proof route, not a result.

## 1. Exact graph objects

Assume an actual putative `srg(99,14,1,2)`. Let

```text
A: 99 x 99 adjacency matrix,
N: 99 x 231 vertex/graph-triangle incidence matrix,
Gamma=N^T N-3I,
P_-4: orthogonal projector onto ker(A+4I),
E=M/21: orthogonal projector onto ker(Gamma).
```

The audited incidence identities give

```text
N N^T=A+7I,
dim ker(A+4I)=44,
dim ker(Gamma)=44.
```

Consequently

```text
E=(1/3) N^T P_-4 N.                              (A1)
```

Indeed, `N^T` maps the graph `-4` eigenspace into `ker(Gamma)`;
`NN^T=3I` on that eigenspace; and the right side of (A1) is the rank-44
orthogonal projector onto its image.

## 2. Coordinate block and diagonal sign involution

Suppose `I` is a nonempty proper coordinate block of `E`: after ordering the
231 triangles as `I` and its complement,

```text
E=E_I orthogonal_sum E_(I^c).
```

Put

```text
m=|I|,
r=rank(E_I),
delta_T=+1 for T in I and -1 for T outside I,
D=diag(delta_T).
```

Then

```text
D^2=I,
D E=E D.                                        (A2)
```

Since every diagonal entry of `E` is `4/21`, the trace of the coordinate
block gives the already frozen row/rank relation

```text
r=tr(E_I)=4m/21,
m=21r/4.                                        (A3)
```

Thus `r` is a positive multiple of four.

## 3. Transfer to the graph `-4` eigenspace

Define the symmetric integer matrix

```text
K=N D N^T.                                      (A4)
```

Equations (A1)-(A2) imply that `D` preserves
`im(E)=N^T ker(A+4I)`. Hence `K` preserves `ker(A+4I)`. Because `K` is
symmetric,

```text
K P_-4=P_-4 K.                                  (A5)
```

This implication is elementary and is part of the candidate route. No
converse is assumed.

Let

```text
s_v=sum_(T containing v) delta_T.
```

Every vertex lies in seven graph-triangles, so every `s_v` is odd. Entrywise,

```text
K_vv=s_v,
K_uv=delta_T if uv is an edge in its unique triangle T,
K_uv=0 if u and v are distinct and nonadjacent. (A6)
```

Thus the off-diagonal part of `K` is the graph adjacency matrix signed
constantly on each triangle, and its signed net-degree at `v` is `2s_v`.

## 4. Exact missing lemma

The proposed decisive target is:

> **Candidate constancy lemma.** For a putative
> `srg(99,14,1,2)`, if a triangle sign function
> `delta:mathcal T->{+1,-1}` produces the matrix `K` in (A4)-(A6) and
> `K` commutes with `P_-4`, then the signed triangle-incidence vector
> `s=N delta` is constant.

This lemma is **`UNKNOWN`**. It is not a consequence of generic simultaneous
diagonalization alone, and no source located in the bounded search states it.
The search also did not determine whether a weaker congruence or regularity
statement suffices.

## 5. Conditional divisibility contradiction

If the candidate constancy lemma holds, write `s_v=s`. Double-counting
signed point-triangle incidences gives

```text
99s=3 sum_T delta_T=3(2m-231),
2m=231+33s=33(7+s).
```

Since `s` is odd,

```text
m=33(7+s)/2,
33 divides m.                                   (A7)
```

Combining (A3) and (A7),

```text
m=21r/4 and 33|m
=> 44|r.
```

For `0<r<=44`, this forces `r=44` and `m=231`, contrary to a proper
coordinate block. Therefore the candidate lemma would rule out every
nontrivial coordinate block of `E`, and in particular the rootless
`20+24` endpoint decomposition.

The contradiction is conditional on the unproved constancy lemma. It is not
a proof of `n3>708`, Conway-99 nonexistence, or any global statement.

## 6. Exact prior-art search lanes

The post-freeze search added 24 exact queries in six batches covering:

1. diagonal `{+1,-1}` matrices commuting with an orthogonal or primitive
   idempotent;
2. reducibility and support components of projector Gram matrices and tight
   frames;
3. signed adjacency matrices preserving a strongly regular graph eigenspace;
4. triangle-constant signings, signed block designs, and net-regular signed
   graphs;
5. the exact Conway-99 numbers `99,231,44,33`; and
6. strongly regular signed graphs, quasi-balanced weighing matrices, and
   association-scheme signings.

General signed-graph and primitive-idempotent theory was located, including
Stanic (2019), Kharaghani-Pender-Suda (2022), and the
Brouwer-Van Maldeghem monograph. None of the inspected records states the
candidate constancy lemma, the `33|m` consequence, or the exact Conway-99
signature.

The bounded conclusion remains:

> No exact prior result was found in the sources searched as of 2026-07-24.

Novelty, the constancy lemma, the sign-involution obstruction, the surviving
matrix realization, and Conway-99 all remain `UNKNOWN`.
