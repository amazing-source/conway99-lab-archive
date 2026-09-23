# Wave204 global-compatibility independent verification

## Verdict

The three submitted package manifests match all 32 listed files, including
the frozen proof-B manifest SHA-256
`6074ec95b7a92cdf26626a031c9373fa94ccd3ab47c627d31183a64af0bdc181`.
All declared replays pass, and a separate post-source checker that imports no
submitted Python code validates the V1 certificate, the V2 exact-results
controls, and the V3 local compression matrices.

| Claim | Label | Exact verified scope |
|---|---|---|
| V1 relaxed 99-center certificate exists | `VERIFIED` | 99-center 14-regular circulant skeleton; complement degree 84; 99 Hilton--Milner 13-families; four-point fibers; 1,287 full and 1,200 selected flags; exact third-block slots; `J=3561`, `delta=3`, `p3=3123`, `q=237`, multiplicities `234x2+3x3`, `epsilon=708`, `L=0`, `b=0`, and maximum combined orientation multiplicity 3 |
| V1 local interface forces `b>0` | `REFUTED_WITH_SCOPE` | Killed by the exact relaxed certificate only; no SRG, ternary columns, rank-11 code, circuit cover, or endpoint follows |
| V2 fixed-column gain `z_T-z_S` telescopes on true block cycles | `VERIFIED` | Definitional coboundary identity, checked exactly over `F_3` |
| V2 edgewise partial slots force center-walk block chaining | `REFUTED_WITH_SCOPE` | Exact rank-11 relaxed A6 controls of lengths 3, 4, and 5 satisfy `T=S+X_a+X_b` but have unmatched intermediate blocks and nonzero projected defects |
| V2 one-point partial injections determine total `S_5` transport | `REFUTED_WITH_SCOPE` | The same `0->0` data admit identity and `(1 2)` extensions with different monodromy |
| V3 adjacent compression and fourth-order detector | `VERIFIED` | Conditional on `G=J_6-I_6`, `C=J_6+N`, and the four stated 2-regular outer types: `P_xP_yP_x|E_x=NN^T`; pair trace is zero; `h=1` only for `4+2`; exterior trace is `h`; symmetric trace is `2h` |
| V3 pair trace plus intersection dimension determines `h` | `REFUTED_WITH_SCOPE` | Independently reconstructed exact 11-dimensional projector pairs have equal pair trace 0 and intersection dimension 1 but fourth traces 2 and 0 |
| V3 optional 99-projector controls | `SOURCE_REPLAYED_SCOPED_RELAXED`, not independently promoted | Submitted replay reports 3,888 differing ordered fourth traces, but only 21 projective directions among 231 labels and seven explicit failed target premises |

No claim excludes rank 11 or the prism-free endpoint, improves the global
`n3` bound, constructs a graph/code, or changes Conway-99 from `UNKNOWN`.

## Source-blind separation

Before any submitted Wave204 file was opened, the verifier froze:

- `BLIND_PROTOCOL.md`;
- an independent deterministic V1/V2/V3 checker;
- 11 acceptance and hostile-mutation tests;
- `blind_result.json`; and
- `SOURCE_BLIND_FREEZE.sha256`.

All 11 tests passed.  The freeze manifest SHA-256 is
`88f502d4d49f6866a73bff006097f66cf4eefb36b3cdf0eca24280df1d70f7a2`.
The source-blind V3 derivation exactly reproduced the local detector and
also found a different exact rank-11 underdetermination witness.

The blind V1/V2 controls were not silently treated as reproductions of the
submitted certificates:

- blind V1 used an abstract five-slot cover and abstract nonprivate copies,
  not the submitted flag-to-leaf groups and third-block slot `A-P`;
- blind V1 paired the 14 neighbors differently from the submitted seven
  actual circulant triangles;
- blind V2 used local simplices with off-diagonal Gram 2 rather than the
  submitted `J_7-I_7` Gram, and it did not impose the submitted normalized
  flag equation, projective distinctness, or rank-11 span.

After unsealing, `post_source_replay.py` checked the stronger submitted
semantics directly from the sealed JSON without importing discovery code.
Its five tests, including three semantic mutations, all passed.

## Exact replay evidence

Submitted commands:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave204-literature-hostile-controls\build_countermodel.py --verify attempts\wave204-literature-hostile-controls\countermodel.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-literature-hostile-controls\test_countermodel.py
.\.venv\Scripts\python.exe -B attempts\wave204-global-slot-holonomy-proof-a\exact_check.py --verify attempts\wave204-global-slot-holonomy-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-global-slot-holonomy-proof-a\test_exact_check.py
.\.venv\Scripts\python.exe -B attempts\wave204-projector-fourth-order-proof-b\exact_check.py --verify attempts\wave204-projector-fourth-order-proof-b\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-projector-fourth-order-proof-b\test_exact_check.py
```

Results: V1 replay passed and 8/8 tests passed; V2 replay passed and 10/10
tests passed; V3 replay passed and 10/10 tests passed.

Independent commands:

```powershell
python -m unittest -v test_independent_verifier.py
python independent_verifier.py
python -m unittest -v test_post_source_replay.py
python post_source_replay.py
```

Results: 11/11 source-blind tests and 5/5 post-source tests passed.

## Limitations

- V1 refutes only the explicitly frozen local-interface implication.  Its
  pair fibers are declared relaxation data and are not induced by SRG
  common-neighbor geometry.
- V2 controls omit 99 stars, 231 global columns, the global frame, graph
  incidence, cover totals, and endpoint realization.
- V3's detector is conditional and adjacent-pair only; nonedge fourth traces
  and the global distribution of `4+2` edges remain unknown.
- The optional V3 global controls were replayed but not independently
  reconstructed before source exposure.  Repeated directions and failed
  graph/code premises keep them quarantined as relaxed.

