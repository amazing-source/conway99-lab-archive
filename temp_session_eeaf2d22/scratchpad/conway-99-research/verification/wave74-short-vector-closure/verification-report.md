# Wave 74 verification report

Verdict: **VERIFIED within the frozen conditional scope**.

The exact neighbor-incidence derivation is correct. The two norm-18
\(h=2\) graph shapes are exhaustive, and both fail:

1. an adjacent pair of same-sign edges contributes 71 common-neighbor
   incidences through that support side, exceeding the other side's full
   SRG capacity 70;
2. two disjoint edges saturate capacity at 70, leaving outside pair moment
   zero, but require 82 same-side incidences across only 81 outside vertices.

The verifier's independently implemented Cartesian histogram search exactly
matches every frozen discovery histogram: 4 for norm 16 \(h=0\), 20 for
norm 18 \(h=0\), and 6 for norm 18 \(h=1\). The frozen discovery checker and
its six tests also reproduce successfully.

Audit note: the discovery JSON records `outside_pair_incidences=-1` in the
already-impossible adjacent \(h=2\) lane, meaning capacity minus the fatal
opposite-support term. Subtracting the additional one same-support
common-neighbor incidence gives the formal full residual \(-2\). This is a
bookkeeping correction to a dead-lane field, not a change to the verified
\(71>70\) contradiction; no histogram uses that field.

The result is conditional on Wave 71's stated support reduction. It is not a
verification of the modular-form or lattice argument that produces those
supports. The surviving histograms have not been realized as incidence
matrices or graphs. No global nonexistence conclusion follows.

Conway-99 status: `UNKNOWN`.

Novelty status: `UNKNOWN`.
