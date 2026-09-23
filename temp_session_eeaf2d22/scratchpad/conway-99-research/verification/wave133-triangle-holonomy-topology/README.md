# Independent verification of Wave133

Verdict: **VERIFIED** for the rooted-triangle holonomy identities, the two
opposite-sign local controls, and the endpoint-scale abstract surface
relaxation control.

The verifier binds discovery manifest
`dae34acdfd3a95c99db79567bf9b8ed20aa1423812dcb4dbe7681730b6d9870a`
and imports no Wave133 module. It reconstructs the one-factor controls,
nonabelian voltage cover, deterministic balanced partition, quotient
incidences, link normalization, Euler characteristic, and canonical
certificate hashes with standard-library exact arithmetic.

The reconstruction exactly reproduces:

- local certificate hashes `6965fb11...` and `9034c039...`;
- derangement holonomy signs `+1` and `-1`;
- cubic triangle-free 36-vertex cores, common-neighbor caps 1/2, and forced
  Gram entry range 0..10;
- a connected 693-sheet, 1,386-vertex, simple 6-regular cover with 4,158
  edges and 2,079 quadrilateral faces, two faces per edge;
- seed-133 partition acceptance at iteration 957, partition hash
  `2be1d12d...`, and quotient certificate `9b4c3023...`;
- a simple 36-regular 231-vertex quotient with six `C6` link components at
  every vertex;
- `H=1386`, `chi=-693`, and global holonomy-sign product `+1`; and
- one connected component after link normalization, so odd Euler
  characteristic really forces nonorientability.

Thus derangement and the stated all-`222` surface incidences do not force the
desired sign contradiction. The prism-free endpoint, general bound
improvement, and Conway-99 remain **UNKNOWN**.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification/wave133-triangle-holonomy-topology/verify_wave133.py `
  --repository . `
  --package attempts/wave133-triangle-holonomy-topology `
  --expected-manifest dae34acdfd3a95c99db79567bf9b8ed20aa1423812dcb4dbe7681730b6d9870a `
  --write verification/wave133-triangle-holonomy-topology/verification.json
```
