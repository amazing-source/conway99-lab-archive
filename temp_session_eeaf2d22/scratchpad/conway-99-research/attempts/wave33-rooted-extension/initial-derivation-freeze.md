# Wave 33 rooted-extension initial derivation freeze

```yaml
role: proof_a
date_utc: 2026-07-24T09:52:47Z
base_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: DERIVED
scope: >-
  Initial consequences of the independently verified Wave 32 signed
  Fano-complement support, recorded before inspecting any Wave 33 sibling
  discovery package.
```

## Imported premises

Assume a strongly regular graph with parameters

```text
(v,k,lambda,mu)=(99,14,1,2)
```

and the verified Wave 32 rooted reduction.  Thus a signed minus-four
eigenvector has positive and negative support sets `P,R`, each of size
seven.  Their induced graph is bipartite and 4-regular, with cross
incidence the complement of a Fano-plane incidence matrix.

Every vertex outside `S=P union R` has either one neighbor in each sign
class or no support neighbor.  Write:

```text
S = signed support,                         |S|=14;
O = vertices with one P and one R neighbor, |O|=70;
Q = vertices with no support neighbor,      |Q|=15.
```

No automorphism is assumed.  The only normalization is relabeling the
already-forced Fano support.

## Initially derived consequences

1. For `q in Q`, count two-walks from `q` to `S`.  Every pair `(q,s)` is
   nonadjacent and has two common neighbors, so there are `28` such
   two-walks.  An `O` neighbor contributes its two support neighbors and a
   `Q` neighbor contributes zero.  Hence `q` has 14 neighbors in `O` and
   none in `Q`.  Therefore `Q` is independent.

2. For `o in O`, count two-walks from `o` to `S`.  Its two adjacent
   support vertices contribute one common neighbor each and the other
   twelve support vertices contribute two each, for `26`.  Its two
   support neighbors each contribute four support neighbors; each `O`
   neighbor contributes two and each `Q` neighbor zero.  Hence

   ```text
   26=8+2 deg_O(o),
   deg_O(o)=9,
   deg_Q(o)=3.
   ```

   The partition `(S,O,Q)` is equitable with quotient

   ```text
   [[4,10,0],
    [2, 9,3],
    [0,14,0]],
   ```

   whose spectrum is `{14,3,-4}`.

3. Let `B` be the `70 x 15` incidence matrix between `O` and `Q`.  Since
   `Q` is independent, every pair of distinct `Q` vertices has exactly
   two common `O` neighbors.  Thus

   ```text
   B 1=3 1,
   B^T 1=14 1,
   B^T B=12I+2J.
   ```

   The 70 rows are distinct: repeated triples would give two `O` vertices
   at least three common `Q` neighbors, exceeding both `lambda` and `mu`.
   Hence the row supports form a simple `2-(15,3,2)` design.

4. Every `q in Q` has exactly two common neighbors with every support
   vertex.  Its 14 `O` neighbors therefore label a spanning simple
   2-regular bipartite graph on `P union R`.  Its cycle type is one of

   ```text
   14;
   10+4;
   8+6;
   6+4+4.
   ```

5. Let `D` be the adjacency matrix induced by `O`.  The strongly regular
   identity

   ```text
   A^2=12I-A+2J
   ```

   gives

   ```text
   DB=2J-B.
   ```

   Therefore each `q`-neighborhood induces a perfect matching in `D`;
   every `O` vertex outside that neighborhood has exactly two neighbors
   into it.  Centered `q`-neighborhood vectors span a 14-dimensional
   `-1` eigenspace of `D`.

6. With `A_S` the fixed Fano-complement support adjacency and `F` the
   fixed `14 x 70` support-to-`O` incidence, the full rooted extension is
   equivalent to finding binary matrices `D,B` with `D` symmetric and
   zero-diagonal satisfying all block equations of
   `A^2=12I-A+2J`:

   ```text
   A_S^2+FF^T             =12I-A_S+2J,
   A_S F+F D              =2J-F,
   F B                    =2J,
   F^T F+D^2+B B^T        =12I-D+2J,
   D B                    =2J-B,
   B^T B                  =12I+2J.
   ```

   This is an exact finite extension criterion, not an existence result.

## Initial status and strongest objection

No contradiction has been obtained.  A `2-(15,3,2)` design alone is not
rare enough to exclude an extension, and the decisive compatibility is
the coupled `D,B,F` system.  The largest risk in this initial derivation is
mistaking consequences of the strongly regular block identity for
sufficient conditions without checking every block, binary constraint,
and fixed support multiplicity.  The exact checker and final report must
audit both directions.

Rooted endpoint existence, `n3=708`, Conway-99, and novelty remain
`UNKNOWN`.
