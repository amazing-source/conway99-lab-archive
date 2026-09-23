# Conway-99, branche C3 : obstruction locale de relèvement sur les six orbites triangulaires

**Date : 21 septembre 2026.** Note de travail produite pendant cette conversation. La preuve ci-dessous est accompagnée d'un petit vérificateur exact. Elle n'a pas été évaluée par un tiers. Sa priorité bibliographique n'est pas établie.

## Résultat et limites

Soit G un graphe fortement régulier de paramètres (99,14,1,2), muni d'un automorphisme g d'ordre 3 sans point fixe. Supposons que les orbites de g qui induisent un triangle soient exactement T_0,...,T_5, et que le graphe des adjacences entre ces six orbites soit **exactement un cycle C6** (sans corde).

Entre deux orbites triangulaires adjacentes, les arêtes forment un appariement équivariant. En coordonnées (i,a), a dans F3, cet appariement s'écrit

    (i,a) ~ (i+1,a+epsilon_i).

Alors nécessairement

    epsilon_0 + ... + epsilon_5 = 0 dans F3.

Autrement dit, la composée des six appariements autour du cycle est l'identité. Les deux holonomies non nulles sont impossibles.

**Ce résultat n'exclut pas C3.** Il n'exclut même pas le cas où les six orbites triangulaires forment C6 : l'holonomie nulle n'est pas éliminée par cet argument. Il ne construit aucun graphe. Le C6 considéré ici est sur les **six orbites triangulaires**, et non une composante du 2-facteur des doubles adjacences sur les 27 orbites indépendantes. Il ne faut donc pas le confondre avec le type déjà étudié `(6,3^7)` de ce dernier 2-facteur.

La démonstration ne suppose PAS que la branche involution est exclue. Elle est valable indépendamment des recherches C2 en cours.

## 1. Contexte externe effectivement consulté

- Y. Ishida, *No involutions in the missing Moore graph*, arXiv:2606.29183v2, 8 juillet 2026, proposition 8.7 : dans le cas d'ordre 3 sans point fixe, a_1(g)=18. Chaque orbite triangulaire contribue trois sommets à a_1 ; les autres orbites de taille trois sont indépendantes. Ainsi il y a six orbites triangulaires et 27 orbites indépendantes. Il s'agit d'un résultat repris de cette source, **pas d'une nouveauté de cette note**.
- `ibenarb/conway99-research`, branche main, fichiers `README.md`, `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md` et `docs/reviews/STRATEGY_REVIEW_PROMPT_2026-09-06_v2.md` : modèle de quotient Q de taille 33 avec Q*1=14*1 et Q^2+Q=12I+6J. Le dépôt distingue expressément la faisabilité du quotient de celle du relèvement en graphe à 99 sommets. Les exclusions computationnelles annoncées par ce dépôt n'ont pas été rejouées dans cette session.
- `infinityscroll/conway99-order3-f27`, README : exclusion annoncée du sous-cas à 27 orbites triangulaires, avec paquet de certificats. Aucun rejeu de ce paquet ici.
- La mémoire accessible du dépôt de l'utilisateur `amazing-source/conway99-involution` a été lue avant les calculs. Aucun fichier de ce dépôt n'a été modifié et aucun de ses processus n'a été lancé ou arrêté.

La recherche bibliographique a été ciblée et non exhaustive. Aucun énoncé identique n'a été identifié dans les documents lus. Cela ne démontre ni l'inédit du lemme, ni l'absence d'une formulation équivalente ailleurs.

## 2. Pourquoi les blocs d'incidence sont binaires

Un sommet extérieur à un triangle ne peut être adjacent à deux de ses sommets : ceux-ci auraient alors deux voisins communs, le troisième sommet du triangle et le sommet extérieur, alors que lambda=1.

Par équivariance, les arêtes entre une orbite triangulaire et toute autre orbite de taille trois sont donc soit absentes, soit un appariement parfait. Ceci vaut en particulier entre deux orbites triangulaires.

Notons F la matrice d'adjacence du C6 sur T_0,...,T_5 et B la matrice binaire 6 x 27 des adjacences vers les orbites indépendantes. Le bloc triangulaire du quotient vaut 2I+F. Le bloc correspondant dans Q^2+Q=12I+6J donne

    B B^T = 6I + 6J - 5F - F^2 =: G0.                (1)

## 3. Deux contraintes exactes sur chaque colonne de B

Les vecteurs entiers

    u = (-1,-1,0,1,1,0)^T,
    v = ( 1, 0,-1,-1,0,1)^T

vérifient Fu=u, Fv=v et J*u=J*v=0. Ainsi G0*u=G0*v=0.

Par (1), 0=u^T G0*u=||B^T*u||^2 ; donc B^T*u=0. De même B^T*v=0.

Toute colonne s de B satisfait par conséquent

    u^T s = v^T s = 0                                (2)

**dans les entiers**, avant toute réduction modulo 3.

Les dix supports binaires possibles sont : le vide, une paire de sommets opposés du C6 (trois choix), l'un des deux triples alternés, le complément d'une paire de sommets opposés (trois choix), et les six sommets.

## 4. Une condition de compatibilité des phases, absente du seul quotient

Sur les 18 sommets appartenant aux six triangles, soit P la matrice d'adjacence induite. Soit Y la matrice 18 x 81 des adjacences de ces sommets vers les 81 sommets restants. L'identité SRG impose

    Y Y^T = 12I_18 + 2J_18 - P^2 - P =: R.           (3)

En coordonnées (i,a), définissons la matrice D sur F3 par

    D_ij = sum_{a=0}^2 a R_{(i,0),(j,a)}  (mod 3).

Les blocs de R sont circulants et R est symétrique. On a donc D_ji=-D_ij.

Considérons une orbite extérieure particulière. Soit s son support parmi les six triangles. Choisissons un de ses sommets et notons p_i la phase de son voisin dans T_i lorsque s_i=1. Ses trois sommets contribuent à R par

    contribution a R_{(i,0),(j,a)} = s_i*s_j*1[a=p_j-p_i].

En posant t_i=s_i*p_i, la contribution à D est donc

    s t^T - t s^T.

Les relations (2) impliquent

    u^T (s t^T - t s^T) v = 0.

Après sommation sur les 27 orbites extérieures,

    u^T D v = 0 dans F3.                            (4)

Cette déduction fournit aussi un principe général : si u et v appartiennent au noyau entier du Gram d'incidence d'un ensemble d'orbites triangulaires, le moment antisymétrique des phases doit s'annuler sur (u,v). Il faut conserver le lien aux noyaux entiers ; remplacer sans justification ce noyau par le seul noyau modulo 3 pourrait introduire de faux filtres.

## 5. Calcul autour de l'hexagone

On peut changer l'origine des coordonnées dans chaque orbite. Cinq appariements deviennent alors de phase zéro, tandis que le dernier, de T_5 vers T_0, a pour phase

    h = epsilon_0 + ... + epsilon_5 dans F3.

Le calcul direct de R dans (3) donne, pour i<j, les seuls moments potentiellement non nuls :

    D_05 = -h,
    D_04 = h,
    D_15 = h.

Explication : pour deux triangles consécutifs, le résidu R possède une seule unité dans le décalage de l'appariement ; pour deux triangles à distance deux, il vaut 2 moins l'indicatrice du décalage du chemin de longueur deux ; pour deux triangles opposés, il est constant égal à 2, donc son moment modulo 3 est nul.

En outre,

    u_0*v_5 - u_5*v_0 = -1,
    u_0*v_4 - u_4*v_0 = -1,
    u_1*v_5 - u_5*v_1 = -1.

Par antisymétrie de D,

    u^T D v
      = sum_{i<j} (u_i*v_j-u_j*v_i) D_ij
      = (-1)(-h)+(-1)h+(-1)h
      = -h dans F3.

L'équation (4) force donc h=0. **Fin de la preuve.**

## 6. Vérification reproductible

Le fichier `verify_c3_hexagon.py` utilise uniquement la bibliothèque standard Python, des entiers et la réduction modulo 3. Il reconstruit P et R pour chacun des trois h, contrôle les noyaux et l'antisymétrie, puis vérifie indépendamment le moment par une énumération finie.

Une orbite extérieure a 1366 configurations de support/phases modulo décalage commun. Les deux conditions de noyau laissent exactement 352 configurations. Le programme vérifie que leur contribution à u^T D v est toujours nulle. Les résidus exigés par le motif sont respectivement 0, 2, 1 pour h=0,1,2.

Il vérifie aussi qu'une mutation du moment du cas h=0 est détectée. Ce contrôle ne prouve pas que h=0 s'étend en SRG ; il évite seulement que le filtre soit vacuement toujours négatif ou toujours positif.

Commande :

    python verify_c3_hexagon.py

Résultat observé pendant la session :

    PASS_EXACT_LOCAL_HEXAGON_CERTIFICATE

Le fichier `hexagon_verification.json` contient la sortie complète. Le programme valide l'arithmétique du lemme ; le transfert à tout graphe hypothétique repose sur la preuve écrite ci-dessus. Il ne s'agit pas d'une formalisation dans Lean ni d'une vérification par un tiers.

## 7. Exploration qui a conduit au lemme

Une exploration locale a examiné les 156 graphes à six sommets de l'atlas NetworkX. Pour le système d'incidence agrégée, elle a obtenu 26 témoins entiers vérifiés, 87 matrices comportant une entrée Gram négative, et 43 déclarations d'infaisabilité du solveur MILP. Ces 43 déclarations n'ont pas été certifiées : **aucun théorème de classification en 26 types n'est revendiqué**.

Sur les 26 formes avec témoins, un test de Gram de relèvement a examiné 318 affectations normalisées de phases. Il a trouvé 123 témoins locaux vérifiés, 191 résidus à entrée négative, deux essais indécis à la limite de temps et deux déclarations d'infaisabilité correspondant au C6 tordu. Les témoins locaux ne sont pas des SRG ; ils ne satisfont que le bloc de Gram examiné. Les deux derniers cas ont motivé la preuve exacte des sections 3–5. Ces expériences n'ont pas été une recherche SAT exhaustive de C3 et ne doivent pas être présentées comme telle.

## 8. Utilité potentielle et prochaine question

Le lemme peut devenir un filtre sûr dans une recherche de relèvements lorsqu'on rencontre exactement ce motif des six orbites triangulaires. Il ne remplace pas les contraintes sur les 27 autres orbites. Son effet sur le coût d'une recherche globale n'a pas été mesuré.

La question suivante serait de déterminer si le critère général (4), appliqué aux autres motifs et à des ensembles plus grands d'orbites, retire d'autres affectations de phases réellement encore admissibles. Il n'y a ici ni promesse d'exclusion globale, ni estimation chiffrée de probabilité de réussite.
