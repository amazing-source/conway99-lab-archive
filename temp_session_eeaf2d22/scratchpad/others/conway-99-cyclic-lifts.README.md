# Conway’s 99-Graph: An Exact Modular Completion Criterion

*For strongly regular graph lifts with free order-three symmetry.*

**Unreviewed research note — 5 September 2026**

For a legal graph lift with a fixed-point-free cyclic action of order three, an exact orbit quotient and a small Fourier congruence can force the full strongly regular graph equation. For the family $\operatorname{SRG}(v,k,1,2)$, the required modulus is $(1-\omega)^3$, independently of $v$ and $k$. 

This AI-assisted note has received automated mathematical checks but no independent human peer review or formal proof-assistant verification. No worldwide novelty claim is made. It neither constructs a Conway 99-graph nor excludes its existence or order-three automorphisms.

## 1. A nonnegative coefficient lemma

Let $\mathcal E=\mathbb Z[\omega]$, where $\omega^2+\omega+1=0$, and put $\pi=1-\omega$. Since $\pi^2=-3\omega$, the ideals $(\pi^2)$ and $(3)$ coincide.

**Lemma.** If $c_0,c_1,c_2$ are nonnegative integers with sum six, then

$$
\pi^3\mid c_0+c_1\omega+c_2\omega^2
\quad\Longleftrightarrow\quad
c_0=c_1=c_2=2.
$$

**Proof.** Set $a=c_0-c_2$ and $b=c_1-c_2$. Divisibility by $\pi^3$ is equivalent to

$$
3\mid a,\qquad 3\mid b,\qquad 9\mid a+b.
$$

Indeed, first divide by three, then use $\omega\equiv1\pmod\pi$. Since $a+b=6-3c_2$, the last condition gives $c_2\equiv2\pmod3$. All three coefficients are therefore congruent to two modulo three. Nonnegativity makes each at least two; their sum forces equality. The converse follows from $1+\omega+

The modulus cannot be reduced to $\pi^2$ under these scalar hypotheses: $(c_0,c_1,c_2)=(1,1,4)$ gives $3\omega^2$, which has valuation exactly two. This does not establish minimal precision for every global graph problem.

## 2. Exact Fourier completion

Let $A$ be the adjacency matrix of a finite simple undirected $k$-regular graph on $3m$ vertices, with a specified fixed-point-free automorphism of order three. Order each vertex orbit cyclically. Then $A$ consists of $3\times3$ circulant blocks.

Evaluating each circulant polynomial at $1$ gives the ordinary orbit quotient $R$; evaluation at $\omega$ gives a Hermitian matrix $W$ over $\mathcal E$. Evaluation preserves matrix products. Identity and all-one matrices below have the dimensions indicated by their equations.

**Theorem.** Assume the exact quotient identity

$$
R^2+R-(k-2)I=6J.
$$

Then

$$
A^2+A-(k-2)I=2J
\quad\Longleftrightarrow\quad
W^2+W-(k-2)I\equiv0\pmod{\pi^3}.
$$

**Proof.** Put $K=A^2+A-(k-2)I$. In a block between distinct vertex orbits, its three coefficients count common neighbors plus adjacency. They are nonnegative, and the quotient equation makes their sum six. The Fourier congruence and the lemma force each coefficient to be two.

In a diagonal orbit block, the identity coefficient is $k-(k-2)=2$. Symmetry makes the other two coefficients equal, and their total with the identity coefficient is six. They too are two. Thus every entry of $K$ equals two. Conversely, evaluating a constant block at $\omega$ gives zero. $\square$

The theorem assumes a **legal simple graph lift**, not an arbitrary Hermitian matrix. The Conway alphabet below ensures this hypothesis directly. For nontrivial strongly regular parameters, the full adjacency equation is exactly the required common-neighbor condition.

## 3. Two equations over $\mathbb F_3$ for Conway quotients

