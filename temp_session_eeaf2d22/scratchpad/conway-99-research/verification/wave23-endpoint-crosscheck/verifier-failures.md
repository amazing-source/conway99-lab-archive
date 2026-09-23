# Wave 23 endpoint-crosscheck verifier failures

No verifier harness failure had occurred before candidate inspection.

During final packaging, the first draft of `artifact-manifest.sha256`
contained one mistyped hash for the inherited Wave 20 independent-results
artifact.  The validator caught it before closure; the manifest entry was
corrected to the artifact's actual SHA-256.  Candidate files, verifier code,
test results, and the mathematical verdict were unaffected.
