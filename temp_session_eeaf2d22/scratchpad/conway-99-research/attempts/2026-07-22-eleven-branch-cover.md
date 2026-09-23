# Complete 11-branch endpoint-fiber split

- Status: `VERIFIED` for finite orbit enumeration; branch SAT status remains
  `UNKNOWN`
- Scope: safe relabeling of the rooted scaffold, not an automorphism assumption

For one root-neighbor coordinate `u`, the 12 residual labels containing `u`
form a set `S_u`. The endpoint-profile equation forces the unknown residual
graph induced on `S_u` to be a perfect matching.

The 12 labels are naturally grouped into six fixed scaffold pairs. The
stabilizer of `u` acts on them as the full automorphism group `C2 wreath S6` of
that fixed matching. Superimposing a candidate perfect matching on the fixed
matching produces alternating components. After contracting each fixed edge,
their sizes form an integer partition of six, and that partition completely
classifies the orbit.

The repository's independent enumeration covers all 10,395 labeled perfect
matchings in exactly 11 types. A separate generator-BFS traverses the action of
`C2 wreath S6` and confirms that each type is one full orbit:

| partition | labeled matchings |
|---|---:|
| `6` | 3,840 |
| `5+1` | 2,304 |
| `4+2` | 1,440 |
| `4+1+1` | 720 |
| `3+3` | 640 |
| `3+2+1` | 960 |
| `3+1+1+1` | 160 |
| `2+2+2` | 120 |
| `2+2+1+1` | 180 |
| `2+1+1+1+1` | 30 |
| `1+1+1+1+1+1` | 1 |

The counts sum to 10,395. `code/matching_orbits.py` constructs one canonical
representative of each type and fixes all 66 edge/nonedge decisions inside
`S_u`. Each individual branch is conditional; running all 11 is a complete
split of the unrestricted rooted instance.

Do not combine these branch units with an unrelated global lex-leader scheme
without a proof that the two normalizations are jointly safe.
