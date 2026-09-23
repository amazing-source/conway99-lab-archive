# Wave 14 independent literature and status audit

## Outcome

The Conway \(99\)-graph existence question and the project's conditional
\(n_3=48\) frontier remain **`UNKNOWN`** in this audit.

Two current authoritative status indicators still mark
\(\operatorname{srg}(99,14,1,2)\) as unresolved: Brouwer's maintained parameter
table has the entry `? 99 14 1 2`, and the 2025 peer-reviewed paper of Cesarz
and Woldar says in its abstract that existence remains open. These are strong
status evidence, not an exhaustive proof that no resolution exists.

No searched primary or authoritative source directly resolved the existence
question, excluded \(n_3=48\), proved \(n_3\ge 51\), or stated the project's
active-triangle/point-hypergraph residual. No novelty claim follows from those
non-hits. The proper target and novelty labels are both `UNKNOWN`.

The important exact overlap is Reimbayev's known identity

\[
 p_6=\frac1{12}nk(k-2)(2k^2-21k+53)+n_3.
\]

For \((n,k)=(99,14)\), this is

\[
 p_6=209286+n_3.
\]

Thus the project's conditional \(n_3=48\) frontier gives
\(p_6\ge 209334\) by substitution. The number \(209334\) is therefore a
`DERIVED` arithmetic consequence of the published identity and the project's
conditional lower bound; this audit found no source that independently states
that stronger bound.

## Run record

```yaml
role: literature
date_utc: 2026-07-23T09:28:36Z
git_commit: 3abb9a0cb3155c96090b0b1493a9bd3916e01926
claim_label: UNKNOWN
scope: >-
  Independent status and prior-art audit, as of 2026-07-23, for
  srg(99,14,1,2), Reimbayev's six-vertex parameter n_3, induced-C6 bounds,
  the values n_3=45,48,51, and the Wave 14 conditional n_3=48
  active-triangle/point-hypergraph formulation.
inputs:
  AGENTS.md: 4D3E4590A8634CAFAF5D87F288BE211497F60A8F5AB40094A83F555724E469B3
  agents/2026-07-22-wave14-n3-48-proof-a.md: F0A7D7B5638415CFF7D5AD4EF176542DE9AA89A2B46A03347F90A2133F18999C
  agents/2026-07-22-wave14-n3-48-computational.md: 54B532035F0AC3C09AAAFD1A825600151D6AE55D3A2FCB87F911CFE37DC8B756
  verification/wave14-status/source-manifest.json: 4A22A50E7AF94FEDF4616F155CB5085FC1576A3F78EE41D8B339E23562935D3B
method: >-
  Searched current web, publisher, arXiv, Math-Net, author-database, and
  institutional sources under exact and alternate terminology before opening
  either Wave 14 discovery report. Froze source versions and SHA-256 hashes,
  checked the cited theorem/formula pages, and only then compared the two
  candidate reports with the sources. Wave 14 verifier work was not inspected.
command: >-
  curl.exe -L --fail <source-url> -o <os-temp-file>;
  Get-FileHash -Algorithm SHA256 <os-temp-file>;
  git rev-parse HEAD
outputs:
  verification/wave14-status/source-manifest.json: 4A22A50E7AF94FEDF4616F155CB5085FC1576A3F78EE41D8B339E23562935D3B
limitations: >-
  Web and indexed-database searching is not exhaustive; some paywalled or
  unindexed material may have been missed. Reimbayev's 2025 six-vertex paper
  and Keramatipour's 2026 SAT work are preprints. Absence of a hit is not
  evidence of novelty or nonexistence. This was a literature/status audit, not
  an independent proof verification. The report's self-hash is necessarily
  computed after finalization and is supplied with the handoff.
```

The recorded commit is the repository `HEAD` observed during this run; the
worktree already contained uncommitted Wave 14 material. No Git mutation was
performed.

## Notation audit: \(N_3\), \(n_3\), and catalog subscripts

Reimbayev's current six-vertex preprint defines \(N_i\) to be catalog graph
number \(i\) in Figure 1 and \(n_i\) to be the number of induced copies of
\(N_i\). Figure 1 and the derivation on pp. 3–4 show:

- \(N_1\), not \(N_3\), is the triangular prism: two disjoint triangles joined
  by all three matching edges.
- \(N_3\) is two disjoint triangles joined by exactly two matching edges.
- \(n_3\) is the global number of induced \(N_3\) copies. The project's
  `n3=48` means that this count has value \(48\).

This distinction also explains the exact Makhnev connection. Makhnev's
condition \((*)\) says that any pair of triangles joined by at least two edges
is joined by exactly three. Reimbayev explicitly observes on p. 13 that
\(n_3=0\) is the condition that two triangles joined through two edges must
also be joined through the third. Makhnev's Theorem 2 then excludes a
\((99,14,1,2)\) graph satisfying that condition. It does **not** exclude
positive \(n_3\), and in particular it says nothing directly about
\(n_3=48\).

Catalog subscripts are different objects from values assigned to \(n_3\):

| notation | meaning in Reimbayev's catalog | exact displayed formula |
|---|---|---|
| \(n_{45}\) | count of \(N_{45}\), shown in Figure 1 as \(C_4\) plus two isolated vertices | \(\frac1{64}nk(k-2)(k-4)(k-6)(k^2-8k+26)+n_3\) |
| \(n_{48}\) | count of \(N_{48}\), shown in Figure 1 as \(P_6\) | \(\frac14nk(k-2)(k-4)(k^3-14k^2+75k-160)+14n_3\) |
| \(n_{51}\) | count of catalog graph \(N_{51}\) | \(\frac14nk(k-2)(k-4)(k^2-9k+22)-2n_3\) |
| \(n_3=45,48,51\) | three possible numerical values of the single free count \(n_3\) | not catalog indices |

The displayed derivations are on PDF pp. 10, 12, and 13, with the consolidated
formulas on pp. 17–20. The preprint's concluding statement that symmetry
“tell[s]” that \(n_3\) should be zero is not presented as a proved theorem.
The 2024 paper's stronger equality assertion \(p_6\) equal to its lower bound
is explicitly Conjecture 4.1, not Theorem 3.3.

## Direct source checks

Full byte counts, URLs, version dates, and SHA-256 hashes are frozen in
[`source-manifest.json`](wave14-status/source-manifest.json).

### Current status

1. **Brouwer, maintained SRG parameter table.** The
   [51–100 vertex table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html),
   accessed 2026-07-23, lists `? 99 14 1 2 3^54 -4^44`; the table's `?`
   notation denotes unknown existence. This is an authoritative maintained
   database entry, not a theorem of nonresolution.

2. **Cesarz and Woldar (2025), peer reviewed.** The publisher page and abstract
   for [“On the automorphism group of a putative Conway
   99-graph”](https://alco.centre-mersenne.org/articles/10.5802/alco.418/)
   (Algebraic Combinatorics 8(2), 379–398; DOI
   [10.5802/alco.418](https://doi.org/10.5802/alco.418); published online
   2025-04-24) explicitly describe existence as an open problem. The paper's
   actual result concerns automorphisms: its abstract states that if
   \(2\mid |\operatorname{Aut}(\Gamma)|\), then the group order divides \(6\),
   while divisibility by \(7\) forces the automorphism group to be
   \(\mathbb Z_7\). It does not address \(n_3=48\).

3. **Keramatipour (2026), preprint/thesis-level evidence.** The current
   [arXiv:2604.23037v1](https://arxiv.org/abs/2604.23037), submitted
   2026-04-24, reports a direct SAT encoding and unsuccessful/intractable
   searches. Solver failure is not a certificate and the work does not resolve
   the graph or the \(n_3=48\) case. It was included to cover a recent
   computational approach, not as authoritative openness proof.

### Exact six-vertex and hexagon statements

4. **Reimbayev (2024), journal article.** In
   [“The lower bound for number of hexagons in strongly regular graphs with
   parameters \(\lambda=1\) and \(\mu=2\)”](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf)
   (EJAAM 2024, 1–14; DOI
   [10.62780/ejaam/2024-001](https://doi.org/10.62780/ejaam/2024-001)):

   - p. 3 defines \(p_6\) as the number of induced subgraphs isomorphic to
     \(C_6\);
   - immediately before Theorem 3.3 on p. 12, the derivation gives the exact
     identity
     \[
     p_6=\frac1{12}nk(k-2)(2k^2-21k+53)+n_3;
     \]
   - Theorem 3.3 on p. 12 uses \(n_3\ge0\) to state the lower bound obtained by
     deleting the final \(+n_3\);
   - Conjecture 4.1 on p. 13 conjectures equality with the lower bound.

   Substitution at \((99,14)\) gives the audited table
   \[
   \begin{array}{c|c}
   n_3 & p_6\\\hline
   45&209331\\
   48&209334\\
   51&209337
   \end{array}
   \]
   conditional on the indicated value.

5. **Reimbayev (2025), arXiv preprint.** The current version is
   [arXiv:2508.03377v2](https://arxiv.org/abs/2508.03377), dated
   2025-11-03 (v1 was 2025-08-05). It says there are 62 possible induced
   six-vertex types for sufficiently large
   \(\operatorname{srg}(n,k,1,2)\), defines \(n_i\) by Figure 1, takes \(n_3\)
   as the free variable, and expresses all catalog counts affinely in \(n_3\).
   The source is a preprint; this audit checked the formulas and catalog image,
   but did not elevate the paper's informal symmetry discussion to a theorem.

6. **Makhnev (1988), primary paper.** The Math-Net record and Russian original
   for [“Strongly regular graphs with
   \(\lambda=1\)”](https://www.mathnet.ru/eng/mzm4220), Matematicheskie
   Zametki 44(5), 667–672 (English translation Math. Notes 44(5), 847–850;
   DOI [10.1007/BF01158426](https://doi.org/10.1007/BF01158426)), were
   checked directly. Condition \((*)\) and Theorem 2 are on printed p. 668:
   there is no \(\operatorname{srg}(99,14,1,2)\) or
   \(\operatorname{srg}(115,18,1,3)\) satisfying \((*)\). This is a conditional
   nonexistence theorem, not a solution to Conway's unrestricted problem.

### Triangle-object formulations

7. **Petro and Phillips (2026), peer reviewed.** Their
   [ScienceDirect article](https://www.sciencedirect.com/science/article/pii/S0012365X25004704)
   appeared in Discrete Mathematics 349(3), article 114862, March 2026
   (DOI [10.1016/j.disc.2025.114862](https://doi.org/10.1016/j.disc.2025.114862));
   the full text checked was
   [arXiv:2502.17845v1](https://arxiv.org/abs/2502.17845), dated
   2025-02-25. They define the 3-clique graph \(C_3(\Gamma)\) to have the
   triangles of \(\Gamma\) as vertices, adjacent exactly when the triangles
   intersect. Corollary 4.9 and Example 4, preprint pp. 26–28, give for a
   putative Conway graph
   \[
   \operatorname{Spec}(C_3(\Gamma))
   =\{-3^{132},\,0^{44},\,7^{54},\,18^1\}.
   \]
   This is relevant prior use of triangles as graph vertices, but its adjacency
   is not the project's \(L\)-adjacency.

8. **Lou and Murin (2014), institutional research report.** In
   [“On the strongly regular graph of parameters
   \((99,14,1,2)\)”](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf),
   Theorem 2.1 on p. 2 says that if a putative graph contains the
   \(\operatorname{srg}(9,4,1,2)\) graph \(H\) minus an edge, then it contains
   \(H\) as an induced subgraph. Their proof calls one six-vertex configuration
   a “prism.” This is inside the nine-vertex forbidden-configuration argument;
   it is not a theorem that every triangular prism is forbidden, and it is not
   a bound on Reimbayev's \(n_3\). In any event, Reimbayev's \(N_3\) is not
   the triangular prism.

## Search coverage and non-hits

The independent search was performed before either Wave 14 discovery report
was opened. It covered exact and alternate strings including:

```text
srg(99,14,1,2)
strongly regular graph (99,14,1,2)
Conway 99 graph / Conway's 99-graph / Conway-99
Reimbayev six vertex / subgraphs of order six / six-vertex identities
induced N3 / n_3 / triangular prism / two triangles connected by two edges
n_45 / n_48 / n_51
n3=45 / n3=48 / n3=51
induced C6 / induced hexagons / 209286 / 209334
active triangle / point hypergraph / triangle incidence / triangle graph
opposite-edge graph / exact twofold rectangle coverage
Conway 99 SAT / 2025 / 2026
```

Sources and discovery channels included publisher pages, arXiv and arXiv
version histories, Math-Net, Brouwer's maintained SRG pages, MIT PRIMES
materials, DOI metadata, and reference lists of the located papers.

No pertinent indexed source was located for any of the following exact claims:

- \(n_3=45\), \(48\), or \(51\) as a proved excluded or attained global count;
- \(p_6\ge209334\) as an independently published bound;
- the terms “active triangle” or the exact active-point family
  \(\{S_u\}\) in the project's sense;
- the project's edge graph \(H\), \(N_3\)-side graph \(L\), complement \(K\),
  \(q(T)\), \(r=16,q=2^{16}\) residual, exact twofold rectangle cover, or
  support graph \(R\).

These are search non-hits only. Their literature and novelty status remains
`UNKNOWN`.

## Comparison with the Wave 14 candidate formulations

Only after freezing the literature results above, this audit opened:

- `agents/2026-07-22-wave14-n3-48-proof-a.md`;
- `agents/2026-07-22-wave14-n3-48-computational.md`.

No Wave 14 verifier report, verifier directory, or verifier artifact was
inspected.

| candidate item | located source overlap | audit boundary |
|---|---|---|
| global `n3` | Exact overlap with Reimbayev's \(n_3\): induced \(N_3\) copies, where \(N_3\) is the two-cross-edge pair of disjoint triangles. | The notation and identities are prior art; the value-48 frontier is not thereby resolved. |
| \(p_6\ge209334\) conditional on \(n_3\ge48\) | Immediate substitution into Reimbayev's exact \(p_6=209286+n_3\). | `DERIVED` arithmetic, not independently located as a published theorem. |
| triangles as vertices | Makhnev's triangle graph and Petro–Phillips's \(C_3(\Gamma)\) both use all graph triangles as vertices and adjacency by intersection. | Conceptual overlap only. The project's \(L\) instead joins two disjoint triangles when together they induce \(N_3\). |
| active point sets \(S_u\) | The full triangle-incidence encoding is natural: a putative graph has \(99\cdot14/6=231\) triangles, and a triangle belongs to its three vertex-points. Petro–Phillips studies the intersection graph generated by this incidence. | No searched source located the project's restriction to active labels, \(q(T)\ge2\), each active label in exactly three non-singleton points, its no-Berge-triangle rule, or its fixed-support equations. |
| \(K\) on active triangle labels | Every point \(S_u\) is a clique in project \(K\). Petro–Phillips's intersection graph is therefore a subgraph of this \(K\) on the same active labels. | \(K\) is not Petro–Phillips's clique graph: \(K\) is the complement of the project \(L\) and may contain disjoint non-\(N_3\) pairs. |
| edge graph \(H\) and exact residual | No direct source located for vertices equal to the 693 original graph edges, edges bijective with \(N_3\) copies, the \(H\)-degree set, or the final \(0/4\)-degree and twofold-coverage reduction. | Prior-art/novelty `UNKNOWN`; mathematical correctness was outside this audit. |
| all-size-two active countermodel | The reports expressly omit inactive triangles, most original vertices/edges, and a 99-vertex SRG completion. | It is evidence only about the stated relaxation. It neither constructs nor refutes a Conway graph. |

The reports themselves preserve the correct status boundary: the proof lane
leaves only the conditional \(r=16,q=2^{16}\), \(K\) 9-regular residual and
does not exclude it; the computational lane finds a positive active-local
candidate and leaves other branches bounded-unknown. Neither report claims a
99-vertex completion, conditional exclusion, \(n_3\ge51\), or novelty.

## Final labels

| claim | label | reason |
|---|---|---|
| Brouwer table currently marks \((99,14,1,2)\) unknown | `CITED` | Direct maintained database entry, accessed 2026-07-23. |
| Cesarz–Woldar 2025 describe existence as open | `CITED` | Direct peer-reviewed abstract, published 2025-04-24. |
| Reimbayev's exact identity \(p_6=209286+n_3\) for the Conway parameters | `CITED` / specialized arithmetic `DERIVED` | Exact published identity plus substitution. |
| \(n_3=48\Rightarrow p_6=209334\) | `DERIVED` | Arithmetic conditional on \(n_3=48\). |
| Makhnev excludes \(n_3=0\) for the Conway parameters | `CITED` | Theorem 2 under condition \((*)\), together with the exact \(n_3=0\) interpretation. |
| \(n_3=48\) is impossible | `UNKNOWN` | No direct theorem or checked certificate. |
| \(n_3\ge51\) for every putative Conway graph | `UNKNOWN` | Not established by the checked sources or candidate reports. |
| \(\operatorname{srg}(99,14,1,2)\) exists or does not exist | `UNKNOWN` | No direct resolution located; nonexhaustive audit. |
| Wave 14 formulation or reduction is novel | `UNKNOWN` | Search non-hit is not a novelty certificate. |
