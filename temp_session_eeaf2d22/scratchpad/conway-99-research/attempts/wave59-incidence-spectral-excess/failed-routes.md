# Failed routes and retained boundaries

## Ordinary spectral excess on the incidence graph

The incidence graph is `(7,3)`-biregular, not regular. The ordinary
spectral-excess theorem therefore does not apply to it. Fiol's semiregular
Theorem 6 falls in case (c), because `d=6` and
`m(0)=132=231-99`. The explicit `B/C` predecessor split proves that the
graph would not be distance-biregular; it does not prove that a semiregular
graph with this spectrum cannot exist.

## Treating the strict spectral-excess inequality as nonexistence

The regular triangle graph has spectral excess 50 and actual excess 32.
The theorem says equality characterizes distance-regularity. Strict
inequality is the expected legal outcome for a non-distance-regular graph.
It is not a failed necessary condition for graph existence.

## Forcing the defect to be PSD

The signed defect

```text
F=A_C-2A_B
```

has row eigenvalue 72, trace zero, and is nonzero. It must be indefinite.
No PSD contradiction is available from `F` itself.

## Assuming a coherent algebra

The matrices `A_B,A_C,A_D` are exact entry classes of `K^2`, but no result
here proves that they form a Bose--Mesner algebra or commute with `K`.
Simultaneously diagonalizing the signed defect with `K` would silently add
an association-scheme hypothesis.

## Pair-neighborhood Gram rank

The exact Gram matrix

```text
153I+10K+A_B
```

is positive definite and has rank 231. Its binary feature vectors live in a
space indexed by unordered pairs of 231 triangle vertices, so full row rank
does not exceed the available feature dimension.

## Nonintegral average predecessor counts

The distance-five triangle-root layer has average predecessor count `27/5`.
This proves that the distance partition is not equitable. Individual
vertices can still have integral predecessor counts whose average is
`27/5`; no graph contradiction follows.

## Point-side distance regularity

Every point root has the exact intersection array

```text
{7,2,6,2,5; 1,1,1,2,3}.
```

The triangle-root partition is nevertheless not equitable. No cited theorem
says that distance-regularity around only the smaller stable set forces
distance-biregularity in this case.

## Ihara moments

The Bass determinant gives zero nonbacktracking traces below length eight
and positive integral cycle counts at lengths 8, 10, 12, and 14. These are
constraints on any completion but are fully consistent.

## Moore and generalized-polygon bounds

The girth-eight biregular Moore lower bound is 130 vertices, whereas the
target incidence graph has 330. It is not a cage or generalized-quadrangle
equality case, so equality classifications do not apply.

