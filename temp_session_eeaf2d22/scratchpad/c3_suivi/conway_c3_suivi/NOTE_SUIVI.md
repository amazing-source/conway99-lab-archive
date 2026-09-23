# Conway-99 / C3 : suivi du lemme de l’hexagone

**21 septembre 2026 — note de travail.**

Ce suivi répond à deux suggestions : confronter le lemme local à la note de
Lundle22 et généraliser son filtre aux graphes F sur les six orbites
triangulaires. Il ne prouve ni l’existence ni la non-existence d’un Conway-99,
et ne suppose aucune exclusion de la branche involution.

## Résumé des résultats et des limites

1. Le lemme de l’hexagone se rattache directement à **l’équation linéaire** du
   critère de relèvement de Lundle22, combinée aux relations du noyau entier
   du Gram d’incidence. Sa démonstration locale explicite reste valable, mais
   le filtre n’est pas indépendant de ce système global déjà documenté.
2. Le filtre précis `noyau entier du Gram → moment antisymétrique` a été
   calculé pour les **156 graphes simples à six sommets à isomorphisme près**.
   Parmi ceux qui passent les premiers tests nécessaires de Gram, **seul C6
   donne une contrainte de phase non triviale**, de rang un : son holonomie
   est nulle. La généralisation directe ne fournit donc pas de nouvelle
   obstruction sur d’autres motifs à six sommets.
3. Cette conclusion concerne **ce filtre**, pas tous les raisonnements sur
   les six triangles, les contraintes quadratiques de phase, d’autres Grams
   comprenant des orbites indépendantes, ou toutes les méthodes C3.
4. La priorité bibliographique de l’énoncé local exact n’est pas établie.
   Être un corollaire d’un cadre existant ne dit pas si ce corollaire avait
   déjà été écrit. Aucune revendication de percée ou de nouveauté mondiale.

## 1. Hypothèses et notations

On considère un éventuel srg(99,14,1,2) muni d’une action libre de C3 et
**exactement six orbites triangulaires**. Toute la suite est conditionnelle à
ce sous-cas ; aucune preuve externe imposant le nombre six n’est nécessaire
à la validité des calculs présentés ici.

Les arêtes entre une orbite triangulaire et toute autre orbite sont soit
absentes, soit un appariement : un sommet extérieur ne peut être adjacent à
deux sommets du même triangle, car cela violerait lambda=1.

Soit F le graphe simple des adjacences entre les six orbites triangulaires,
et B leur incidence binaire 6 x 27 avec les autres orbites. On écrit le
quotient ordinaire

    Q = [[2I + F, B], [B^T, C]].

L’identité `Q² + Q = 12I + 6J` donne

    G0 := BB^T = 6I + 6J - 5F - F².                         (1)

La somme de chaque ligne de B est `12 - deg_F(i)`, également la diagonale
G0_ii. L’énumération ci-dessous **n’exige pas encore** l’existence d’une
factorisation binaire B à 27 colonnes : elle utilise un sur-ensemble sûr de
candidats, obtenu par la non-négativité de G0 et sa semi-définie positivité.

Soit K une matrice dont les colonnes forment une base du noyau **entier** de
G0. La positivité donne, dans les entiers,

    B^T K = 0,

puisque `u^T G0 u = ||B^T u||²`. On ne remplace pas ce noyau par le noyau
modulo trois, qui peut être plus grand.

## 2. Forme générale du filtre local

Numérotons les sommets de chaque orbite par F3. Pour une arête ij de F, soit
E_ij la phase de l’appariement de i vers j, avec E_ji=-E_ij ; E_ij=0 en
l’absence d’arête. Tous les calculs de phase ci-après sont sur F3.

Notons P la matrice du sous-graphe sur les 18 sommets triangulaires. Les
voisinages extérieurs doivent fournir le résidu

    R = 12I_18 + 2J_18 - P² - P.

Le premier moment des blocs circulants est

    D_ij = somme_{a=0,1,2} a R[(i,0),(j,a)]  modulo 3.

Le premier moment d’un produit de blocs circulants satisfait la règle du
produit, les augmentations ordinaires de P étant `2I+F`. Le moment de
l’identité et celui du bloc constant J sont nuls. D’où

    D = -(5E + FE + EF) = E - FE - EF   sur F3.             (2)

Une orbite extérieure de support binaire s et de phases p contribue à D par
`s t^T - t s^T`, où t_i=s_i p_i. Comme K^T s=0 dans les entiers, elle donne
une contribution nulle à K^T D K. Toute réalisation impose donc

    K^T (E - FE - EF) K = 0  sur F3.                       (3)

Ces équations sont linéaires en les phases des arêtes de F.

Pour C6, la base entière

    u = (-1,-1,0,1,1,0)^T,
    v = ( 1, 0,-1,-1,0,1)^T

et une normalisation avec phase totale h donnent `u^T D v=-h`. (3) est donc
exactement la condition h=0 du lemme initial.

## 3. Lien précis avec le critère de Lundle22

La note de Lundle22 contient l’équation linéaire

    B_L Z + Z B_L - Z = 0,  avec B_L = Q+I modulo 3,

ainsi qu’une seconde équation quadratique. Le nom B_L ne désigne pas notre
matrice d’incidence B.

Définissons M comme la matrice des premiers moments des blocs de la matrice
d’adjacence entière, avec la même convention d’orientation que E. Avec les
conventions de la table de Lundle22, **Z=-M**. Son équation linéaire devient

    QM + MQ + M = 0.                                      (4)

Cette identité peut aussi être dérivée directement en prenant le premier
moment de l’équation SRG ; elle ne dépend pas ici d’une acceptation sans
contrôle de l’ensemble du théorème de complétion modulo (1-omega)^3.

En écrivant

    M = [[E,V],[-V^T,N]],

le bloc supérieur gauche de (4) est

    5E + FE + EF - B V^T + V B^T = 0.

La multiplication par K^T à gauche et K à droite annule les deux termes
mixtes, puisque B^T K=0. On retrouve **exactement (3)**.

**Conclusion de comparaison.** Le filtre local est une projection de la
première couche linéaire globale après utilisation du Gram exact. Il peut
être pratique à appliquer avant de construire un quotient ou un système de
phases complet, mais il n’ajoute pas une obstruction indépendante à un
modèle qui impose déjà ce système avec l’incidence correspondante. Aucune
comparaison de performance de solveurs n’a été faite ici. Cette observation
ne tranche pas l’antériorité de l’énoncé C6 pris isolément.

## 4. Généralisation effectivement calculée

Pour chaque graphe F à six sommets, le vérificateur reconstruit G0 et suit
les étapes suivantes :

- une entrée négative de G0 exclut une factorisation BB^T avec B binaire ;
- un mineur principal négatif exclut une factorisation Gram réelle ;
- sinon tous les mineurs principaux sont vérifiés non négatifs exactement ;
- le noyau rationnel est calculé par élimination de Gauss sur des fractions,
  ses vecteurs sont rendus primitifs et la saturation du réseau est contrôlée ;
- toutes les équations (3), une par paire de vecteurs d’une base entière,
  sont formées et leur rang est calculé sur F3.

Le contrôle de saturation est important : une base du noyau rationnel
transformée individuellement en vecteurs entiers n’est pas toujours une
base du réseau entier. Ici le PGCD des mineurs maximaux des matrices de base
est un dans tous les cas non triviaux ; aucune relation modulo trois n’est
perdue par ce choix.

### Résultats

| Test | Nombre de motifs |
|---|---:|
| G0 contient une entrée négative | 87 |
| G0 est à entrées non négatives, mais non PSD | 25 |
| G0 passe ces deux tests nécessaires | 44 |
| **Total** | **156** |

Parmi les 44 survivants :

| Dimension du noyau entier | Nombre | Effet du filtre |
|---|---:|---|
| 0 | 29 | aucune relation de ce type |
| 1 | 13 | contraction alternée identiquement nulle |
| 2, motif 3K2 | 1 | toutes les équations de phase sont nulles |
| 2, motif C6 | 1 | une équation indépendante : holonomie nulle |

Les 44 survivants **ne sont pas 44 quotients réalisables**. Certains peuvent
échouer au test de factorisation binaire ou à d’autres conditions ; cela ne
remet pas en cause la conclusion sur le filtre, puisque tout vrai candidat
doit figurer dans ce sur-ensemble.

Le résultat est : **la généralisation directe de (3) sur le seul Gram des
six orbites triangulaires est saturée par le cas C6**. Il serait incorrect
d’en conclure que toutes les contraintes de phase possibles ont été épuisées.

## 5. Vérification, indépendance et artefacts

L’exploration initiale a utilisé l’atlas NetworkX et SymPy. Le programme
`verify_generalisation.py` livré ici est une seconde implémentation
utilisant uniquement la bibliothèque standard Python, sans solveur SAT,
MILP, accès réseau ou arithmétique flottante.

Il vérifie notamment :

- que les 156 représentants de `cases.json` ont des orbites de réétiquetage
  disjointes sous les 720 permutations et couvrent exactement les 32 768
  graphes étiquetés à six sommets : la complétude ne repose donc pas sur une
  simple confiance dans l’atlas ;
- les certificats d’entrée négative ou de mineur principal négatif ;
- tous les mineurs principaux des 44 cas PSD ;
- les noyaux entiers, leur saturation et les rangs des contraintes ;
- 243 identités de premier moment, une par phase unitaire d’arête dans les
  cas PSD, en reconstruisant directement les matrices 18 x 18 ;
- le rejet d’un jeu d’entrée contenant un représentant dupliqué.

Commande :

    python verify_generalisation.py --out results.json

Sortie observée :

    PASS_EXACT_SIX_MOTIF_KERNEL_SCREEN

`results.json` contient les 156 résultats et les équations explicites.
`run.log` contient la sortie de l’exécution. Le paquet `original/` conserve
la note et le vérificateur de l’hexagone de la session précédente. Ils ont
été rejoués ; la sortie figure dans `original_replay.json` et contient
`PASS_EXACT_LOCAL_HEXAGON_CERTIFICATE`.

Cette vérification algorithmique de petite taille n’est pas une
formalisation Lean et n’a pas encore reçu de revue humaine extérieure.
L’ancienne note reste inchangée, y compris son statut historique de revue.

## 6. Sources effectivement consultées pour ce suivi

- `Lundle22/conway-99-cyclic-lifts`, `README.md`, note datée du 5 septembre
  2026, blob Git `1ddace680c59b60657beccdf9f2da6989b01f131` : critère exact
  annoncé et deux équations de phases. Statut de la source : note de
  recherche non évaluée par les pairs. L’identification de sa première
  équation avec (4) est redérivée ci-dessus.
  https://github.com/Lundle22/conway-99-cyclic-lifts/blob/main/README.md
- `ibenarb/conway99-research`,
  `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md`, blob
  `7b9859fa790de54ed716cf8272180d3933efd1a4` : les types sont définis par
  le 2-facteur L sur les orbites indépendantes, **pas** par le seul F sur
  les six triangles. Un type L ne correspond donc pas à un seul motif F.
  https://github.com/ibenarb/conway99-research/blob/main/docs/breadth1/O3_LAYER_A_MODEL_SPEC.md
- Dépôt privé de l’utilisateur `amazing-source/conway99-involution`,
  `notes/third_party/check_c3_hexagon.py`, commit `7626438`, blob
  `98f8affcf7407a65fe2325993d8e23c18907f0c7` : lecture du contrôle indépendant
  communiqué par Fable. Aucun fichier distant n’a été modifié dans ce suivi.

## 7. Transmission proposée

La prochaine relecture utile de Fable est bornée : vérifier le pont
linéaire (4) → (3), puis rejouer le vérificateur et examiner la saturation
des noyaux. Si cela tient, inscrire en mémoire que la généralisation simple
sur les six triangles ne donne rien au-delà de C6. Les critères quadratiques
ou les sous-Grams incluant d’autres orbites restent des pistes distinctes,
non testées ici. Ce n’est pas un ordre de lancer une nouvelle campagne.
