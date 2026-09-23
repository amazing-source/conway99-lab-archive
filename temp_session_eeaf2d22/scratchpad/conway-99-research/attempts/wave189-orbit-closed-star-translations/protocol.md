# Wave 189 protocol

## Target

Under the verified conditional endpoint

```text
n3=4158, P=0, rank_F3(D)=11,
```

derive a lower bound for the number `Q` of projective short circuits
cross-realizing nonedges.  Do not enumerate graphs, covers, configurations,
codes, or isomorphism classes.

## Frozen inputs

Use only the manifests listed in `input-freeze.sha256`.

## Proof obligations

1. Reconstruct the type-one majority-star translation and circuit
   extraction.
2. Separate the `n_3` selected-type-three companions from all other private
   label extractions by privacy.
3. Close exact-three extractions under the Wave 180 companion involution.
4. Prove that the two type-two extractions for one label cannot be the two
   members of one exact-three orbit.
5. Verify the coefficient certificate

   ```text
   12Q>=7I+4n1+2(p2-n2)+(3n3-p3)+3p2>=14C.
   ```

6. Derive every equality condition at `Q=4851`.
7. Reconstruct the canonical-C4 containment in the `3+6` leaf translate
   and verify the two weight-seven difference relations.
8. Keep the exact orientation/design and Hoffman rows as null controls, not
   feasibility claims.

## Status rules

- Discovery may label the result only `DERIVED`.
- A solver exit code, human confidence, or the rational vector `1/10` is
  not a certificate of an integral cover.
- The strict conclusion is only `Q>=4852`; do not infer endpoint
  nonexistence.

## Reproducible command

```powershell
.\.venv\Scripts\python.exe -B attempts\wave189-orbit-closed-star-translations\exact_check.py --verify attempts\wave189-orbit-closed-star-translations\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave189-orbit-closed-star-translations\test_exact_check.py
```
