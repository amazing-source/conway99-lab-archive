# Wave 55 branch-15 remainder search protocol

1. Reuse the independently verified raw OPB for the exact shard
   `branch15 AND x187=0`; do not transform the formula.
2. Use the pinned Exact binary with SHA-256
   `842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928`.
3. Set `--proof-assumptions=0`, retain the raw proof, and capture the complete
   solver transcript and exit code.
4. Treat `--timeout=120` as a solver setting, not a strict whole-process wall.
5. Keep at least 20% physical memory free while the run is active; abort the
   process if the host approaches that threshold.
6. `UNKNOWN` and a nonterminal proof contribute zero branch coverage.
7. An `UNSAT` status is not evidence until strict VeriPB elaboration/kernel
   replay and CakePB replay pass against the exact OPB.
8. A `SAT` status is not a graph; decode and run the complete SRG and global
   prism checkers before any positive promotion.
9. Do not overwrite the Wave 53 proof or formula artifacts.
