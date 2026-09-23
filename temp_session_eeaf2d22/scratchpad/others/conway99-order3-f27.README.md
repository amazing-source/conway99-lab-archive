# Conway's 99-graph problem: exact exclusion of the f=27 order-three quotient

This repository contains an unrefereed, certificate-backed exclusion of one
symmetry subcase of Conway's 99-graph problem.

## Theorem

Let `B` be the symmetric `33 x 33` orbit matrix induced by a fixed-point-free
automorphism of order three of a hypothetical `srg(99,14,1,2)`. If exactly 27
vertex orbits induce triangles, then no such orbit matrix exists.

This does **not** solve Conway's 99-graph problem. The trace-compatible cases
`f=6,13,20` remain open, as does the possibility of a graph without an
order-three automorphism. See [THEOREM.md](THEOREM.md) for the reduction and
exact certificate boundary.

## Proof package

The source repository contains:

- the exact 12-orbit support enumeration;
- deterministic CNF generators for the binary-Gram, aggregate type-edge, and
  final `C3+C3` graph problems; and
- a fail-closed verifier that checks manifests, replays all exact witnesses,
  regenerates seven CNFs byte for byte, and optionally replays all 13 DRAT
  proofs.

The 103 MiB generated certificate packet is distributed as the GitHub Release
asset `conway99-f27-certificates-v0.1.0.tar.gz`, not as Git objects.

## Reproduce the fast audit

Python 3.12 and `python-sat==1.9.dev13` are required.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

gh release download v0.1.0 \
  --pattern conway99-f27-certificates-v0.1.0.tar.gz
shasum -a 256 -c RELEASE_ASSET.sha256
tar -xzf conway99-f27-certificates-v0.1.0.tar.gz

.venv/bin/python verification/verify_f27_certificate_bundle.py
```

The final line must be:

```text
PASS_F27_CERTIFICATE_BUNDLE fresh_proofs=False proofs=13
```

The fast audit checks the archived proof-verification logs but does not trust a
solver status alone: it also checks file hashes, regenerates the formulas, and
replays the complete SAT-control assignment.

## Replay all DRAT proofs independently

Build or otherwise obtain an independent `drat-trim` executable, then run:

