# Exact-to-VeriPB-to-CakePB calibration

Status: `VERIFIED` for the exporter and small controls; target result:
`UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-22T21:43:10Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
claim_label: VERIFIED
scope: native-cardinality OPB semantics and pair-count 2/3 certificate replay
inputs:
  code/sat_model.py: c29744c4835306d576a8625b3951b51815f0a5f806a9c93c6c8eff494639276c
  code/test_sat_model.py: 6c35d8bfad0110abf6808a68fe82d4af6cdbace9fe978404d079f2c979b46344
  formal/opb-calibration/pair2.opb: 62dc2aacf5b4793e36a6550fa04319a93b184b4abdc0e1fbdb9a569ab622b4b8
  formal/opb-calibration/pair3.opb: 4cf9b8f5dc2b205d8e376f700469c4a4d6dbb67bd646e60ee5a6968dab31e003
method: exhaustive truth tables, Exact proof generation, strict VeriPB replay and elaboration, and CakePB kernel replay
command: |
  .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
  .venv/Scripts/python code/sat_model.py --pair-count 2 --cardinality native --opb formal/opb-calibration/pair2.opb
  .venv/Scripts/python code/sat_model.py --pair-count 3 --cardinality native --opb formal/opb-calibration/pair3.opb
  # Run the Exact, VeriPB, and CakePB replay block below.
outputs:
  formal/opb-calibration/pair2.pbp: 9e5f7991dd66886424a97a7020a05e3f7e702b6c87a9710e1ff3fe1b24a0d104
  formal/opb-calibration/pair2.kernel.pbp: a35302332cd6b55273d626b36d21940488cee3467fee3a22d5c02dfdf406a08d
  formal/opb-calibration/pair3.pbp: ad9f8cb98b88ee98e23f77aade39f48a5e28a1cdeec9f154803045075b7504bd
  formal/opb-calibration/pair3.kernel.pbp: 4b8264195a538e1088db6ff388bde3e9993a3985f92ac66c687acde768ec3f80
limitations: both bounded target runs terminated UNKNOWN and every checker reported NO CONCLUSION
```

## Tool lock

| tool | source and pinned identity | binary SHA-256 |
|---|---|---|
| Exact | [source](https://gitlab.com/nonfiction-software/exact.git), commit `b921cd1c4e3b6a7b7ba16dfd9c38c419d5e53ee4` | `842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928` |
| VeriPB | [source](https://gitlab.com/MIAOresearch/software/VeriPB.git), tag `3.0.2`, checkout `c648bac06be995b82bd218e248f005140fc8ce11` | `635b6f2fbd7a7fb98bf7a1f7af038355a1e58438cfdc1ee4e2649979017ace36` |
| CakePB | [source](https://gitlab.com/MIAOresearch/software/cakepb.git), commit `904eed45e2cbe9ac26000475bbdd2f99bcbdaad8` | `5920919642b1c498c2654a849fcd894ea18e7736ebf32919a9a8915861033e46` |

The source-built Exact binary emits VeriPB 3 proofs. A prebuilt Exact 2.2.1
wheel emitted obsolete VeriPB 1.1 output and was rejected for this pipeline.

The binaries were built from detached source checkouts. Set `TOOLS_ROOT` to a
scratch directory, clone the three URLs above, and check out the identities in
the table. Exact used CMake 4.3.3 and Boost 1.89.0:

```bash
export TOOLS_ROOT="/absolute/path/to/conway-tools"
git clone --filter=blob:none https://gitlab.com/nonfiction-software/exact.git \
  "$TOOLS_ROOT/exact"
git -C "$TOOLS_ROOT/exact" checkout --detach \
  b921cd1c4e3b6a7b7ba16dfd9c38c419d5e53ee4
git clone --filter=blob:none https://gitlab.com/MIAOresearch/software/VeriPB.git \
  "$TOOLS_ROOT/veripb"
git -C "$TOOLS_ROOT/veripb" checkout --detach \
  c648bac06be995b82bd218e248f005140fc8ce11
git clone --filter=blob:none https://gitlab.com/MIAOresearch/software/cakepb.git \
  "$TOOLS_ROOT/cakepb"
git -C "$TOOLS_ROOT/cakepb" checkout --detach \
  904eed45e2cbe9ac26000475bbdd2f99bcbdaad8

export CMAKE_BIN="$TOOLS_ROOT/cmake-4.3.3-linux-x86_64/bin/cmake"
export BOOST_CMAKE_DIR="$TOOLS_ROOT/boost-install/lib/cmake/Boost-1.89.0"

"$CMAKE_BIN" -S "$TOOLS_ROOT/exact" -B "$TOOLS_ROOT/exact/build-wave3" \
  -DCMAKE_BUILD_TYPE=Release -DBoost_DIR="$BOOST_CMAKE_DIR" \
  -Dsoplex=OFF -Dcoinutils=OFF -Dzlib=OFF -Dmimalloc=OFF
"$CMAKE_BIN" --build "$TOOLS_ROOT/exact/build-wave3" --parallel 4

export CARGO_TARGET_DIR="$TOOLS_ROOT/veripb-target"
rustup toolchain install 1.97.1
cargo +1.97.1 install --locked --path "$TOOLS_ROOT/veripb" \
  --root "$TOOLS_ROOT/veripb-install"

make -C "$TOOLS_ROOT/cakepb" -j2
```

The CMake 4.3.3 archive SHA-256 was
`927b2368a946c37269c3a66225ab00544e756459cdd0b5d0da438694fb9ff802`;
the Boost 1.89.0 archive SHA-256 was
`85a33fa22621b4f314f8e85e1a5e2a9363d22e4f4992925d4bb3bc631b5a0c7a`.
CakePB's `make` target links the repository's generated `cake_pb.S`; it does
not regenerate the checker from the HOL4/CakeML formal sources.

## Committed calibration artifacts

| file | bytes | SHA-256 | checked conclusion |
|---|---:|---|---|
| `pair2.opb` | 1,078 | `62dc2aacf5b4793e36a6550fa04319a93b184b4abdc0e1fbdb9a569ab622b4b8` | SAT |
| `pair2.pbp` | 572 | `9e5f7991dd66886424a97a7020a05e3f7e702b6c87a9710e1ff3fe1b24a0d104` | SAT |
| `pair2.kernel.pbp` | 715 | `a35302332cd6b55273d626b36d21940488cee3467fee3a22d5c02dfdf406a08d` | SAT |
| `pair3.opb` | 32,101 | `4cf9b8f5dc2b205d8e376f700469c4a4d6dbb67bd646e60ee5a6968dab31e003` | UNSAT |
| `pair3.pbp` | 154,763 | `ad9f8cb98b88ee98e23f77aade39f48a5e28a1cdeec9f154803045075b7504bd` | UNSAT |
| `pair3.kernel.pbp` | 190,276 | `4b8264195a538e1088db6ff388bde3e9993a3985f92ac66c687acde768ec3f80` | UNSAT |

The OPB exporter maps every clause to a unit-weight lower bound and maps

```text
sum(literals) <= k
```

to

```text
sum(complement(literals)) >= number_of_literals-k.
```

The independent verifier compared every pair-2 assignment, every local
pair-3 constraint truth table, and both encoding variants. Canonical LF output
is enforced so the hashes above are identical on Windows and Unix.

## Replay

Generate the formulas on Windows:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 2 `
  --cardinality native --opb formal/opb-calibration/pair2.opb
.venv\Scripts\python code/sat_model.py --pair-count 3 `
  --cardinality native --opb formal/opb-calibration/pair3.opb
```

With the pinned tools available in WSL, replay either `CASE=pair2` or
`CASE=pair3`:

```bash
PROJECT_WSL="/mnt/c/path/to/conway-99-research"
TOOLS_ROOT="/absolute/path/to/conway-tools"
CALIBRATION="$PROJECT_WSL/formal/opb-calibration"
EXACT="$TOOLS_ROOT/exact/build-wave3/Exact"
VERIPB="$TOOLS_ROOT/veripb-install/bin/veripb"
CAKEPB="$TOOLS_ROOT/cakepb/cake_pb"
CASE=pair3

"$EXACT" --proof-assumptions=0 --proof-log="$CALIBRATION/$CASE.pbp" \
  "$CALIBRATION/$CASE.opb"
"$VERIPB" --force-checked-deletion \
  "$CALIBRATION/$CASE.opb" "$CALIBRATION/$CASE.pbp"
"$VERIPB" --force-checked-deletion \
  --elaborate "$CALIBRATION/$CASE.kernel.pbp" \
  "$CALIBRATION/$CASE.opb" "$CALIBRATION/$CASE.pbp"
"$VERIPB" --force-checked-deletion \
  "$CALIBRATION/$CASE.opb" "$CALIBRATION/$CASE.kernel.pbp"
"$CAKEPB" "$CALIBRATION/$CASE.opb" "$CALIBRATION/$CASE.kernel.pbp"
```

For pair 2, strict VeriPB and CakePB report `VERIFIED SATISFIABLE`; for pair 3
they report `VERIFIED UNSATISFIABLE`. An independent audit also replayed both
complete pair-3 matching branches with the same conclusions.

## Full target scale checks

The deterministic formulas regenerated byte-identically from the frozen
technical commit:

| local formula | constraints | bytes | SHA-256 |
|---|---:|---:|---|
| `conway99-native-lf.opb` | 291,690 | 14,240,401 | `c84eb4d82e8c8f848d1d992d7dfdc103360418ad3e893ab836c5be23c29d3001` |
| `conway99-n3-native-lf.opb` | 291,691 | 14,240,415 | `ad7a8bf5d76c3f740f3f65fee5b134cf6b8e6720e22fd780916121edd59fd0de` |

Generate them on Windows with:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 7 `
  --cardinality native --opb logs/local/conway99-native-lf.opb
.venv\Scripts\python code/sat_model.py --pair-count 7 --n3 `
  --cardinality native --opb logs/local/conway99-n3-native-lf.opb
```

For either formula, set `FORMULA`, `RAW_PROOF`, and `KERNEL_PROOF`, then run
the exact bounded producer and checker sequence:

```bash
# Unnormalized target. Replace the three assignments with the N3 names below
# for the normalized run.
FORMULA="$PROJECT_WSL/logs/local/conway99-native-lf.opb"
RAW_PROOF="$PROJECT_WSL/logs/local/conway99-lf-10s.pbp"
KERNEL_PROOF="$PROJECT_WSL/logs/local/conway99-lf-10s.kernel.pbp"

# N3 alternative:
# FORMULA="$PROJECT_WSL/logs/local/conway99-n3-native-lf.opb"
# RAW_PROOF="$PROJECT_WSL/logs/local/conway99-n3-lf-10s.pbp"
# KERNEL_PROOF="$PROJECT_WSL/logs/local/conway99-n3-lf-10s.kernel.pbp"

"$EXACT" --timeout=10 --proof-assumptions=0 \
  "--proof-log=$RAW_PROOF" "$FORMULA"
"$VERIPB" --force-checked-deletion "$FORMULA" "$RAW_PROOF"
"$VERIPB" --force-checked-deletion --elaborate "$KERNEL_PROOF" \
  "$FORMULA" "$RAW_PROOF"
"$VERIPB" --force-checked-deletion "$FORMULA" "$KERNEL_PROOF"
"$CAKEPB" "$FORMULA" "$KERNEL_PROOF"
```

The observed local runs were:

| bounded run | raw proof bytes / SHA-256 | kernel bytes / SHA-256 | Exact conclusion |
|---|---|---|---|
| unnormalized | 155,113,149 / `23eccdc393f5d2e5e278c8050635a1d762692f146abce75bcb45e21a218aeb4c` | 168,464,557 / `fade9aca33e7db761d1afec37fa065abf64982ac7dfe587e7dee1978bb89e4ac` | `UNKNOWN`, 29,962 conflicts |
| N3-normalized | 123,337,900 / `63beae0abe7dd38a80e47f73188d7fe26ff908c27e2bb3d0938fde7d94b84338` | 134,177,757 / `44b6b490795216edcf937978414facd46705b2b47535773d22345e815106004e` | `UNKNOWN`, 23,469 conflicts |

Raw strict VeriPB, elaboration, strict kernel replay, and CakePB returned
`s VERIFIED NO CONCLUSION` for both runs. These files are explicitly
`LOCAL_ONLY_NON_EVIDENTIARY`: they remain under ignored `logs/local/`, have no
public retrieval URL, and satisfy no archival proof obligation. Their
wall-clock-dependent sizes, hashes, and conflict counts can vary by machine.
A checked proof that a bounded run made no claim supplies zero evidence for
existence or nonexistence.

The run used Windows 11 / WSL2, an AMD Ryzen 7 7700 (8 cores, 16 logical
processors), and the tool binaries above.
