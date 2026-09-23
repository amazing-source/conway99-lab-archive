# Wave 26 \(A_2\)-frame verifier failures and edge-case ledger

No checker assertion failed in the retained verifier run.  The first complete
suite passed all 14 tests.

The following proof hazards were identified before publication and are
retained as adversarial obligations:

1. **Wrong basis change.**  If \(T=P^TSP\), the row-coordinate matrix is
   \(Y=XP^{-T}\), not \(XP\).  The checker verifies both frame identities
   after a nontrivial unimodular change.
2. **Unoriented-root collapse.**  \(u\) and \(-u\) cannot share a fiber cap.
   An explicit allowed pair with total inner product zero keeps all six
   oriented roots distinct.
3. **Overstated cap two.**  Three rows in one oriented-root fiber are locally
   possible via an \(A_2\) residual triple.  The proved cap is three.
4. **Hidden \(+2\).**  Admitting off-diagonal \(+2\) permits four mutually
   orthogonal residual roots in one fiber and destroys the contradiction.
5. **Dropping the tight-frame equation.**  Local norm and inner-product rules
   alone do not force \(A_2\)-energy 42; an explicit zero-energy relaxation is
   checked.
6. **Status inflation.**  The proof rejects the projector-frame origin of an
   orthogonal-\(A_2\) scaled dual.  It does not reject every primitive
   embedding, every \(h=9\) form, \(n_3=708\), or Conway-99.
