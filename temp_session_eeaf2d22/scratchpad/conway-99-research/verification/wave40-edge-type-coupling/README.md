# Wave 40 clean-room edge-type coupling verification

Verdict: **`VERIFIED_SCOPED`** for the conditional identities and exact finite
enumerations below. The prism-free endpoint, an upper bound below `4158`, the
Conway-99 graph, and novelty remain `UNKNOWN`.

This package was written without reading, importing, or executing
`attempts/wave40-edge-type-coupling`.

## Verified results

At `n3=4158`, every edge of the opposite-edge graph `J` is nontriangular.
The previously audited nontriangular-`J`-edge correspondence therefore gives
a bijection

```text
E(J) <-> {induced N3 copies} <-> E(L),
|E(J)|=|E(L)|=4158.
```

Using the local link types `222,24,33,6`, with type counts
`t222,t24,t33,t6`, the global closed two-complex has

```text
t222+t24+t33+t6 = 693,
f4  = 3*t222+t24,
f6  = 2*t33,
f8  = t24,
f12 = t6,
4*f4+6*f6+8*f8+12*f12 = 8316 = 2*4158.
```

The unsplit complex need not be a surface: a triangle-vertex link may have
several cycles. Splitting each triangle-vertex by link component produces a
closed, possibly disconnected surface. Its Euler characteristic is negative
throughout the coarse feasible range, so Euler theory gives no contradiction.

In the all-`222` one-triangle quotient, the complete normalization has

```text
3 relative pairing types * 15 * 15 * 6 = 4050
```

representatives. They are complete representatives, not claimed to be
pairwise nonisomorphic. For the exact pair-incidence quotient `2I+A_Q` over
`F_3`, the rank distribution is

```text
11:8, 12:1, 13:400, 14:46, 15:2616, 16:979.
```

For the canonical first rank-eleven quotient, all `2^18` relative
endpoint-pairing masks were checked. Exactly `37,378` lifts are triangle-free.
Their ranks are

```text
rank_F7(3I-A_X): 32:264, 33:7348, 34:29766,
rank_F7(K_39):   33:264, 34:7348, 35:29766.
```

The one-rank shift is exact:

```text
rank_F7(K_39) = 1 + rank_F7(3I-A_X).
```

The verifier also emits the lexicographically first rank-33 `K_39` witness.
It is a genuine 36-vertex cubic triangle-free one-triangle control with all
three base edges of type `222`. It is not a 99-vertex graph or an extension
certificate.

## Reproduce

```powershell
python -B verification\wave40-edge-type-coupling\independent_check.py `
  --verify verification\wave40-edge-type-coupling\independent-results.json
python -B -m unittest discover `
  -s verification\wave40-edge-type-coupling -p "test_*.py" -v
```

The exhaustive command takes about 30 seconds on the verifier host.
