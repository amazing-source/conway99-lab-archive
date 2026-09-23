# Frozen Hilton--Milner theorem statement

Primary source:

- A. J. W. Hilton and E. C. Milner, "Some Intersection Theorems for
  Systems of Finite Sets," *The Quarterly Journal of Mathematics* 18(1)
  (1967), 369--384.
- DOI: `10.1093/qmath/18.1.369`
- Publisher page:
  <https://academic.oup.com/qjmath/article/18/1/369/1584607>
- Access checked: 2026-07-28.

Exact theorem form used in Wave195:

```text
If n>2k and F is a pairwise-intersecting family of k-subsets of an
n-element set with empty total intersection, then

|F| <= C(n-1,k-1)-C(n-k-1,k-1)+1.
```

Specialization:

```text
n=7, k=3:
C(6,2)-C(3,2)+1=15-3+1=13.
```

The standard sharp family consists of all 3-subsets containing a fixed
point and meeting a fixed disjoint 3-subset, together with that disjoint
3-subset. It has `12+1=13` members and empty total intersection.
