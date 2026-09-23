# Wave 38 coclique rank strengthening

This package combines a public 13-coclique construction with the integral
triangle-projector identity.

Choose an edge `xy`, and let `z` be its unique common neighbor. The remaining
twelve neighbors of `x` and twelve neighbors of `y` each carry a perfect
matching. The common-neighbor rule supplies a third matching between the two
twelve-point sets. Their union consists of even cycles, so one color class
has twelve vertices. The vertex `z` is nonadjacent to all 24, giving a
13-vertex independent set.

If `N` is the vertex-triangle incidence matrix and `M=21E_0` is the integral
rank-44 triangle projector, then

```text
N M N^T = 27I - 9A + J.
```

Restricting to an independent set `I` of size thirteen gives

```text
N_I M N_I^T = 27I_13 + J_13.
```

Its determinant is `27^12*40`, which is `5 mod 7`. Hence

```text
rank_F7(M) >= 13.
```

At the prism-free endpoint, `C=2M-21I` is congruent to `2M` modulo seven, so
the same lower bound holds for the endpoint reflection rank.

Reproduce with:

```powershell
.\.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave38-coclique-rank\test_exact_check.py
.\.venv\Scripts\python.exe -B `
  attempts\wave38-coclique-rank\exact_check.py `
  --verify attempts\wave38-coclique-rank\exact-results.json
```

This is a necessary modular restriction, not an endpoint contradiction. The
13-coclique construction was publicly described by Misha Lavrov in comments
on a Mathematics Stack Exchange discussion in 2025; this package does not
claim it as new. Novelty of the combined rank consequence is `UNKNOWN`.

The independent verifier reconstructed the graph argument, all 10,395 local
matching states, the incidence-projector transport, and the modular rank
calculation without importing discovery code. Its ten hostile tests pass.
The scoped consequence `rank_F7(M)>=13` is therefore `VERIFIED`; the
discovery JSON deliberately retains its historical `CANDIDATE` label. With
the previously verified ternary floor and rank parity, 528 arithmetic endpoint
rank pairs remain. They are not endpoint matrices or graphs.

See `verification/wave38-coclique-rank/audit.md`.
