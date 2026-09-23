# Wave196 four-fiber Hilton--Milner verifier

Status: `VERIFIED_WITH_SCOPE`.

Under the frozen prism-free rank-11 endpoint assumptions, this package
independently verifies

```text
j_x<=36,
J<=3564,
S36=3564-C+n1+2*n2-a3-b3>=0,
Q>=7029.
```

The independent mathematical result was frozen before either Wave196 source
package was opened.  The verifier then compared the sealed primary proof,
replayed a distinct source arithmetic null, and used the sealed proof-B
hostile audit only as a secondary cross-check.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave196-four-fiber-hilton-milner-verifier\independent_check.py --verify-math verification\wave196-four-fiber-hilton-milner-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave196-four-fiber-hilton-milner-verifier\independent_check.py --verify verification\wave196-four-fiber-hilton-milner-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave196-four-fiber-hilton-milner-verifier\test_independent_check.py
```

The finite code checks instantiate the two theorem-classified
Hilton--Milner equality templates and expand exact rational identities.  No
graph, code, cover, SAT, LP, construction, configuration, family,
isomorphism, or brute-force search is performed.

This is a conditional analytic theorem.  It neither constructs nor excludes
the endpoint, and Conway-99 remains `UNKNOWN`.
