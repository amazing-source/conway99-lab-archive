# Wave 38 coclique-rank boundaries

The characteristic-seven argument strengthens a modular rank condition. It
does not by itself force a prism or exclude the endpoint.

## Rank is not nonexistence

For a 13-coclique `I`, the exact identity

```text
N_I M N_I^T = 27I_13 + J_13
```

is nonsingular modulo seven. Therefore `rank_F7(M)>=13`. The previous lower
bound was eleven, but dimensions thirteen and above are not ruled out.

At the prism-free endpoint `C=2M-21I`, so `C=2M (mod 7)` and the same bound
holds for `C`. Reciprocal Smith pairing remains arithmetically compatible
with this stronger floor.

## The ternary reduction collapses

Modulo three, the star-sum matrix satisfies

```text
M N^T = J.
```

The three possible integer entries `4,-2,1` are all one modulo three.
Consequently differences of vertex-star sums vanish; the 13-coclique does not
directly raise the ternary rank floor.

## No independence-number inflation

The elementary first and second moment equations for a 13-coclique admit
hundreds of nonnegative degree profiles even if every outside vertex has at
least one coclique neighbor. Those moments do not force a 14th independent
vertex.

## Status

```text
rank_F7(M)>=13: VERIFIED scoped
n3=4158:        UNKNOWN
general bound:  n3<=4158
Conway-99:      UNKNOWN
novelty:        UNKNOWN
```
