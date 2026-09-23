# Wave201 source-blind verifier protocol

Frozen before opening either Wave201 source package.

1. Freeze the conditional claim: at every center, for arbitrary
   nonprivate selected-orientation multiplicities in the four-point
   pair fibres,

   ```text
   delta_x >= sum_y (m_x(y)-2).
   ```

2. Use only the sealed Wave196 fixed-center theorem and Wave198
   orientation/full-pool accounting.
3. Treat an arbitrary number of distinct selected labels in one fibre.
   Do not assume saturated multiplicity, one label per fibre, or
   `m>=2`; explicitly include `m=1`.
4. Separate `c_x<=12` from `c_x=13`.  In the equality case use only the
   two fixed Hilton--Milner formulas and exactly their three
   degree-five pair fibres.
5. Audit selected-versus-full incidence: selected multiplicity is at
   most the full multiplicity of the same oriented label, and all
   full-pool labels, selected or not, contribute to fibre union loss.
6. Sum the local theorem to obtain

   ```text
   delta >= 3q-epsilon.
   ```

7. Eliminate `q` using the independently reconstructed Wave198 identity
   and derive a nonnegative exact certificate with target

   ```text
   (19C-85V)/10.
   ```

8. Check the integer consequence `Q>=7059`, the 693 edge-isolated
   addition, and projective/scalar totals.
9. Seek an explicit integer near-equality accounting row and a
   multiplicity profile containing `m=1`; label both as arithmetic
   controls, not graph, flag-family, code, or cover objects.
10. Freeze the independent result and its hashes before opening proof A
    or hostile proof B.
11. After the freeze, replay and compare both sealed source packages.
    Record any correction explicitly; do not silently repair a claim.
12. Preserve rank 11, endpoint existence, strict original `n3`
    improvement, external novelty, and Conway-99 as `UNKNOWN`.

No graph, configuration, cover, SAT, LP, family enumeration,
isomorphism, or brute-force search is part of the mathematical audit.
