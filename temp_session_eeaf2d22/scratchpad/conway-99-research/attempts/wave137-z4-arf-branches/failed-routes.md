# Failed and bounded routes

## Full Z4 floating scouts

Both Arf signs were tested on the full corrected 1,119-variable Wave135
relaxation with 147 equalities and 1,114 allowed dual inequalities.

The default HiGHS configuration returned an unrecognized
unknown/primal-infeasible status for `+` and a solve error for `-`. An
interior-point retry without presolve swapped these failure modes. No
floating solution, exact dual certificate, or inference was retained.

Classification: `UNKNOWN_NUMERICAL`.

## K5 points before shadow cuts

The first exact K5 witnesses violate only degrees 6 and 93, both below the
approved lower shadow bound. These are refuted witness points, not refuted
branches. Adding exactly the two violated inequalities yields new exact
rational witnesses satisfying all degree-6-through-99 shadow bounds.

## Not yet attempted

- exact 1,119-variable Z4 Arf row generation;
- integral/divisibility constraints on signed moments;
- the candidate `S_6(n3)` equality;
- full genus-two MacWilliams constraints.
