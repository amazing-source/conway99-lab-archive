# Retained run failures

None of the failures below is mathematical evidence.

1. The first combined workspace inventory timed out after 20 seconds while
   traversing the OneDrive worktree.  It had already printed the objective and
   part of the directory inventory.  Subsequent reads were narrowed to exact
   paths.

2. Both the repository virtual environment and the system Python lacked
   `networkx`:

   ```text
   ModuleNotFoundError: No module named 'networkx'
   ```

   No dependency was installed.  The final checker instead implements its own
   exact graph masks, vertex permutations, canonicalization, and deletion
   decks using only the Python standard library.

3. A first brute canonicalizer canonicalized every one of 13,174 admissible
   labeled six-vertex masks separately.  It completed in 16.7 seconds and
   returned 62 classes, but was discarded as needlessly repetitive.  The
   final orbit-removal implementation regenerates the same 62 classes in
   about 0.2 seconds on the development machine.

4. The first inline Hamiltonian-seven census had a Python indentation error at
   the initialization of the fixed cycle.  The corrected exploratory command
   returned 19 classes.  The final implementation is covered by hostile tests
   and does not reuse the failed snippet.

5. The first exact-checker run expected only `N3` to attain the lower
   nonnegativity facet.  Exact calculation correctly found that both
   `N3=n3` and `N4=2n3` attain zero at `n3=0`.  The expected provenance list
   was corrected from `[3]` to `[3,4]`; the feasibility interval did not
   change.

6. The first `unittest` invocation from the repository root could not import
   the sibling `exact_check.py` because the hyphenated attempt directory was
   not on `sys.path`.  The test file now inserts its own resolved directory
   before import.  The full 16-test run then passed.

