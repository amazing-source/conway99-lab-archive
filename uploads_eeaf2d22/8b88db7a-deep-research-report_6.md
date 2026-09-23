# Dossier de recherche : Conway-99 et l’existence d’un `srg(99,14,1,2)`

## Statut actuel et fiabilité documentaire

**À la date du 21 septembre 2026, le problème reste ouvert dans les sources primaires et maintenues que j’ai pu vérifier.** La table de Brouwer marque toujours le paramètre `(99,14,1,2)` par `?`; le préprint de Reimbayev du 19 août 2026 parle encore explicitement d’un problème non résolu; surtout, la version **v2 du 18 septembre 2026** de Thakkar–Severini dit sans ambiguïté que ses résultats « do not resolve the existence problem ». Je n’ai trouvé ni matrice d’adjacence certifiée, ni preuve de non-existence accompagnée d’un argument ou certificat primaire vérifiable postérieur à cette version. citeturn0search0turn20view0turn20view1turn17view1turn17view0

Cette conclusion doit être formulée comme un **état de la littérature vérifiée**, non comme une garantie logique qu’aucune annonce extrêmement récente n’existe ailleurs. C’est particulièrement important ici : le dépôt `conway-99-research` a lui-même gelé son dernier audit bibliographique au **29 juillet 2026**, avec statut `NO_RESOLUTION_FOUND_IN_SOURCES_SEARCHED`, et précisait déjà que la non-découverte était bornée. Cet audit est maintenant matériellement dépassé, puisqu’il ne pouvait pas intégrer le recensement complet des sous-graphes à 7 sommets de Reimbayev du 19 août ni la v2 Thakkar–Severini du 18 septembre. fileciteturn7file0L2-L2 fileciteturn11file0L2-L2 citeturn20view0turn17view1

Les versions qu’il faut distinguer sont les suivantes.

| Source | Statut utile au 21-09-2026 | Ce qu’il faut en retenir |
|---|---|---|
| Brouwer, table SRG | table maintenue | `(99,14,1,2)` toujours `?`; signal de statut, pas preuve d’ouverture à lui seul. citeturn0search0 |
| Cesarz–Woldar | **article publié**, *Algebraic Combinatorics* 8 (2025), 379–398 | restrictions rigoureuses sur `Aut(G)`; le papier lui-même présente toujours l’existence comme ouverte. citeturn6view0turn7view0 |
| Lou–Murin | manuscrit MIT PRIMES-USA, 2014/2015, non équivalent à un article évalué en revue | plusieurs contraintes locales importantes, notamment graphe des triangles et obstruction liée à `srg(9,4,1,2)`. citeturn22view0turn23view0turn23view1 |
| Reimbayev, hexagones | arXiv `2409.10620` v1, avec version article 2024 référencée dans la bibliographie du dépôt | identité exacte pour le nombre d’hexagones, faisant apparaître le paramètre libre `n3`. citeturn14search27turn12view2 |
| Reimbayev, ordre 6 | arXiv `2508.03377` **v2, 3 novembre 2025** | recensement des 62 types d’ordre 6; `n3` reste libre. citeturn11search18turn12view1 |
| Keramatipour | mémoire MPhil daté de juin 2023, mis sur arXiv en 2026, **v2 du 28 avril 2026** | encodages SAT/PB, résultats locaux, et surtout diagnostic de difficulté des encodages génériques; aucun verdict sur Conway-99. citeturn18view0turn18view1 |
| Reimbayev, ordre 7 | arXiv `2608.19410` **v1, 19 août 2026** | 208 types d’ordre 7, fréquences affines en deux variables libres `n3,z11`; non intégré au dépôt de juillet. citeturn20view1turn20view2 |
| Thakkar–Severini | arXiv `2608.11211` **v2, 18 septembre 2026** | réduction exacte à 84 sommets, recherches CP-SAT/orbites, borne exhaustive dans les classes abéliennes testées, artefact heuristique à 70,73 %; existence toujours ouverte. citeturn17view1turn17view0 |
| `conway-99-research` | dépôt de recherche, résultats audités en interne, non évalués par les pairs | plusieurs contraintes exactes et vérificateurs réutilisables; dernière vague intégrée 205, 29 juillet 2026. fileciteturn7file0L2-L2 |

Un piège bibliographique mérite d’être enregistré : le dépôt recense un texte de Hideto Ishihara de 2022 dont un théorème annonce la non-existence de `srg(99,14,1,2)`, mais son audit interne affirme que l’équation décisive (88) suppose à tort un degré résiduel uniforme. Je **ne considère donc pas ce texte comme une résolution**. Comme cette réfutation est elle-même, dans les sources que j’ai examinées, un audit de dépôt plutôt qu’une correction publiée par l’auteur, un futur chercheur qui voudrait faire reposer quoi que ce soit sur ce point devrait refaire localement la vérification de l’équation fautive. citeturn13view0

La principale lacune de source primaire ancienne reste Makhnev 1988 : les audits du dépôt signalent ne pas avoir obtenu une extraction fiable du texte intégral et passent en partie par les attributions de travaux ultérieurs, notamment pour l’obstruction correspondant à `n3=0`. Wilbrink 1984 est disponible sous forme de scan institutionnel, mais je n’ai pas refait ici son argument complet. En revanche, j’ai vérifié directement les pages pertinentes de Lou–Murin, qui utilisent le lemme Wilbrink–Brouwer. citeturn13view1turn22view0

## Formulations de travail et invariants qui peuvent être utilisés sans ambiguïté

Pour une matrice d’adjacence `A`, l’existence cherchée équivaut exactement à

\[
A^2+A-12I=2J,
\qquad\text{soit}\qquad
A^2=12I-A+2J,
\]

avec `A` symétrique, binaire et de diagonale nulle. Cette formulation est celle à retenir pour tout certificat positif : elle vérifie simultanément le degré `14`, `λ=1` sur les arêtes et `μ=2` sur les non-arêtes. Thakkar–Severini l’utilisent explicitement, et le dépôt l’a également figée comme format de certificat. citeturn17view0 fileciteturn7file0L2-L2

Sur l’orthogonal de `1`, cette identité donne

\[
A^2+A-12I=0,
\]

d’où les deux valeurs propres non triviales `3` et `−4`. Avec `tr(A)=0`, on obtient immédiatement

\[
\operatorname{Spec}(A)=
14^{1},\,3^{54},\,(-4)^{44}.
\]

Ce calcul est élémentaire mais il vaut la peine de le figer, car beaucoup de relaxations spectrales n’apportent rien au-delà : Thakkar–Severini remarquent notamment que les premier et deuxième moments des nombres de voisins communs ont **exactement** les valeurs cibles pour tout candidat régulier répondant aux contraintes spectrales pertinentes. Leur somme de premier ordre vaut `9009`, et le deuxième moment cible vaut `17325`; on ne peut donc espérer une contradiction de simple variance. citeturn17view0

Le graphe hypothétique aurait

\[
|E|=\frac{99\cdot14}{2}=693.
\]

Comme chaque arête appartient à exactement un triangle, ces arêtes se décomposent en

\[
693/3=231
\]

triangles. Chaque sommet appartient à sept triangles. En langage d’incidence, on cherche donc aussi une structure linéaire de `99` points, `231` lignes de taille `3`, sept lignes par point, dont le graphe de collinéarité a exactement deux voisins communs pour deux points non collinéaires. C’est la formulation en **partial quadrangle `PQ(2,6,2)`** du problème; elle est utile lorsqu’on cherche des résultats dans la littérature de géométrie finie plutôt que sous le nom « Conway 99-graph ». La bibliographie du dépôt identifie explicitement cette équivalence comme une autre terminologie pertinente. citeturn12view2

Cette incidence donne aussi une formulation linéaire particulièrement propre. Si `B` est la matrice `99×231` sommet–triangle, alors

\[
BB^{\mathsf T}=A+7I.
\]

Si `T` est le graphe dont les sommets sont les 231 triangles, deux triangles étant adjacents lorsqu’ils partagent un sommet, alors

\[
B^{\mathsf T}B=A_T+3I.
\]

Lou–Murin avaient déjà introduit ce graphe `T` : il est `18`-régulier. À partir du spectre de `A`, les valeurs propres non nulles de `BB^T` sont `21^1,10^54,3^44`; par conséquent

\[
\operatorname{Spec}(A_T)
  =18^1,\,7^{54},\,0^{44},\,(-3)^{132}.
\]

La même structure est traitée plus récemment dans le cadre général des clique graphs par Petro–Phillips; l’audit du dépôt retrouve exactement ce spectre pour Conway-99. citeturn23view0turn14academia40turn13view1

Lou–Murin ont en outre déjà fait une partie du travail local sur `T` qu’il serait facile de redécouvrir inutilement. Autour d’un triangle fixé, ils introduisent trois nombres `α,β,γ` et obtiennent

\[
\alpha+\beta=180,\qquad
\beta+3\gamma=36,\qquad
\alpha-3\gamma=144,
\]

avec `0≤γ≤12`, `γ≠11`; ils montrent également que le cas `γ=12` partout redonnerait une structure impossible de type `srg(9,4,1,2)`. citeturn23view1 Keramatipour formule une information connexe : dans le graphe des triangles d’un `srg(n,k,1,2)`, deux sommets adjacents ont `k/2−2` voisins communs et deux non-adjacents en ont au plus trois; ici cela donne degré `18`, paramètre adjacent `5`, mais un paramètre non-adjacent non constant, seulement borné par `3`. citeturn19view0turn19view1

La **formulation enracinée** est probablement la plus utile pour programmer. Fixons un sommet `0`. Son voisinage de 14 sommets induit nécessairement un appariement parfait `7K_2`. Chacun des 84 sommets restants a exactement deux voisins dans ce premier voisinage; mieux, ces 84 sommets sont en bijection avec les

\[
\binom{14}{2}-7=84
\]

paires qui ne sont pas les sept paires appariées. Toute l’adjacence entre la couche de 14 sommets et celle de 84 sommets est donc forcée. Le seul objet encore inconnu est un graphe `H` **12-régulier sur ces 84 labels**. citeturn17view0

Pour deux sommets extérieurs `u,v` de labels `P_u,P_v`, avec

\[
s=|P_u\cap P_v|\in\{0,1\},
\]

la réduction exacte exige

\[
u\sim v \Rightarrow
|N_H(u)\cap N_H(v)|=1-s,
\]

et

\[
u\nsim v \Rightarrow
|N_H(u)\cap N_H(v)|=2-s.
\]

Il existe en plus les contraintes mixtes avec les 14 sommets intérieurs, données explicitement par Thakkar–Severini. Cette formulation reconstruit le problème entier et ne suppose **aucun automorphisme du graphe recherché**. citeturn17view0

Il ne faudrait cependant pas attribuer naïvement toute cette structure à 2026. Keramatipour décrit déjà en détail, dans son encodage depuis un sommet, l’appariement du voisinage et la représentation des sommets extérieurs par les paires non appariées; Lou–Murin utilisent dès 2014 une labellisation analogue de la couche de 84 sommets dans leurs essais de construction. Le mérite actuel de Thakkar–Severini est surtout d’en donner une formulation exacte, compacte et directement encodable, puis de la valider sur `srg(9,4,1,2)`. citeturn19view3turn22view0turn17view0

Enfin, l’approche par petits sous-graphes fournit aujourd’hui l’autre paramétrisation centrale. Reimbayev obtient pour le nombre d’hexagones

\[
p_6=
\frac1{12}nk(k-2)(2k^2-21k+53)+n_3.
\]

Pour `(n,k)=(99,14)`,

\[
p_6=209\,286+n_3.
\]

Le recensement d’ordre six conserve précisément ce `n3` comme variable libre : les fréquences des 62 types sont des fonctions affines de ce paramètre. citeturn5view6turn11search18turn12view1

Le dépôt `conway-99-research` utilise le **même `n3`** — son audit de littérature le vérifie explicitement — et affirme, après une longue chaîne de vérifications internes, la condition nécessaire

\[
708\le n_3\le4158,
\]

donc

\[
p_6\ge209\,994.
\]

C’est, dans le dépôt, l’une des contraintes générales les plus concrètes obtenues sans hypothèse d’automorphisme. Elle n’est toutefois ni publiée ni vérifiée par une source extérieure au dépôt; je n’ai pas rejoué ici la chaîne de vérificateurs qui mène de `n3≥0` à `n3≥708`. Elle doit donc être considérée comme **résultat repo-audité à reproduire avant d’en faire une prémisse d’un article**. fileciteturn7file0L2-L2 citeturn13view1

## Résultats extérieurs qui changent réellement l’espace de recherche

Le résultat publié le plus net sur les symétries reste celui de Cesarz–Woldar, s’appuyant sur Makhnev–Minakova et Behbahani–Lam. Ils renforcent fortement les possibilités pour le groupe d’automorphismes : si son ordre est pair, son ordre divise `6`; si `7` divise l’ordre, le groupe est `Z_7`. Les résultats antérieurs utilisés dans cette chaîne excluent notamment l’ordre `11`, et les synthèses récentes excluent aussi l’ordre `9`. Ainsi un éventuel graphe n’est pas forcé d’avoir une symétrie exploitable; en particulier, une recherche globale qui impose dès le départ un automorphisme non trivial ne traite qu’un sous-problème. citeturn6view0turn7view0turn17view0

C’est une distinction essentielle pour interpréter les recherches informatiques. Une contradiction complète dans une branche `Z_7`, `Z_3` ou `Z_2` éliminerait cette symétrie, **pas** le graphe asymétrique. À l’inverse, une solution dans n’importe laquelle de ces branches construirait évidemment le Conway-99. Le dépôt formalise justement cette discipline en interdisant de transformer une recherche conditionnée par une symétrie en conclusion globale. fileciteturn8file0L2-L2 fileciteturn7file0L2-L2

Sur les petits sous-graphes, Lou–Murin donnent un autre acquis historique à ne pas refaire : ils prouvent qu’une configuration `srg(9,4,1,2)` privée d’une arête, si elle apparaissait de la façon étudiée, forcerait déjà le `srg(9,4,1,2)` induit complet, puis obtiennent une obstruction par le lemme Wilbrink–Brouwer. Leur section sur les triangles précède nettement les formulations récentes. citeturn22view0turn23view0turn23view1

Gray Taylor avait ensuite, en 2020, effectué une classification computationnelle du sous-graphe engendré par **deux sommets adjacents et leurs voisinages combinés**. Son dépôt identifie cette classification comme son résultat principal et utilise Nauty via OApackage pour les tests d’isomorphisme. Le dépôt de 2026 a reconnu ultérieurement que sa propre « edge scaffold » à 27 sommets et ses onze types reproduisaient exactement ce travail antérieur. Il faut donc prendre les notebooks de Taylor comme point de départ chaque fois qu’une piste branche sur une arête fixée; recalculer les onze classes comme découverte serait une répétition. fileciteturn16file0L2-L2 fileciteturn7file0L2-L2

Keramatipour apporte deux choses de nature différente. Côté mathématique, il démontre qu’un Conway-99 ne peut pas suivre partout son « Paley(9) pattern ». Il énonce aussi qu’on ne peut pas avoir onze sous-graphes Paley(9) indépendants, mais **le manuscrit omet la preuve de ce second énoncé**; il ne faudrait donc pas lui donner le même niveau de confiance sans reconstruction. Sa conjecture plus forte — aucun Paley(9) du tout — demeure explicitement une conjecture. citeturn19view0turn19view1

Côté SAT, la conclusion de Keramatipour est négative sur **la méthode**, non sur le graphe. Le mémoire présente plusieurs encodages CNF et pseudo-booléens, cite notamment CaDiCaL, et montre même qu’un encodage auquel on impose onze copies du Paley(9), donc censé être insatisfiable selon son théorème, n’est pas certifié `UNSAT` par le solveur après douze heures. Cela illustre pourquoi « lancer plus longtemps l’encodage global » n’est pas, en soi, une nouvelle piste. citeturn18view0turn19view0

Le changement le plus récent côté combinatoire est Reimbayev 2026. Le préprint affirme qu’il y a **208 types de sous-graphes induits à sept sommets** dans `srg(n,k,1,2)` et exprime chacune de leurs fréquences `z_i` à l’aide de `n,k` et de seulement deux variables libres, `n3` et `z11`. Par exemple,

\[
z_2=n_3-\frac{z_{11}}4,\qquad
z_3=z_{11}-2n_3,
\]

de sorte que la simple non-négativité donne déjà

\[
2n_3\le z_{11}\le4n_3.
\]

Les formules deviennent beaucoup plus contraignantes et mêlent `n` et `k` aux deux variables jusqu’à `z_{208}`. Pour Conway-99, l’ensemble forme donc un système arithmétique à **deux dimensions seulement** avant même d’ajouter les contraintes du dépôt. citeturn20view1turn20view2

Il faut néanmoins auditer ce recensement avant de le transformer en axiomes d’un solveur. Le préprint dit explicitement omettre les dérivations, parce qu’elles seraient analogues aux travaux précédents, et indique avoir utilisé intensivement Wolfram Alpha pour les calculs algébriques. Par ailleurs, l’audit bibliographique du dépôt avait déjà signalé dans la v2 du recensement d’ordre six une omission imprimée (`+n23` dans une équation de suppression) sans correction formelle trouvée. Cela ne réfute ni le recensement d’ordre six ni celui d’ordre sept, mais suffit à recommander une vérification indépendante des identités critiques avant exploitation. citeturn20view1turn20view2turn12view2

## Carte sélective des tentatives et de leur portée exacte

| Axe | Acquis réel | Ce qui a bloqué / portée exacte | Artefact à réutiliser |
|---|---|---|---|
| **Sous-structures historiques** | Lou–Murin : graphe des 231 triangles, équations `α,β,γ`, exclusions locales; obstruction autour de Paley(9). citeturn22view0turn23view0turn23view1 | Les contraintes ne déterminent pas l’assemblage global. Plusieurs constructions Fano essayées échouent, mais ces échecs ne constituent pas une obstruction générale. citeturn22view0 | Les équations locales et les configurations dessinées; à consulter avant toute nouvelle analyse de triangle central. |
| **Voisinages d’une arête** | Gray Taylor : classification en onze types du voisinage combiné de deux sommets adjacents. fileciteturn16file0L2-L2 | Classification locale seulement; aucune extension globale obtenue. | Notebooks, catalogue des onze types, Nauty/OApackage. Le dépôt 2026 reconnaît ce travail comme prior art exact. fileciteturn7file0L2-L2 |
| **Automorphismes** | Restrictions publiées très fortes sur `Aut(G)`, en particulier branches paires et `7`. citeturn6view0turn7view0 | Même l’élimination de toutes les branches symétriques ne résoudrait pas le cas asymétrique. | Méthode orbit-matrix de la littérature; bon domaine pour calculs finis certifiables. |
| **SAT générique** | Keramatipour fournit CNF/PB, symétrie, formulations triangle/Paley. citeturn18view0 | Des instances connues ou structurellement contraintes restent indécises pendant des heures; c’est un échec de stratégie/encodage, pas une preuve. citeturn19view0 | Formules de cardinalité et cas de calibration; utiles comme contrôles négatifs. |
| **Réduction à 84 sommets** | Thakkar–Severini : formulation exacte d’un graphe 12-régulier sur les 84 paires non appariées, validée sur `srg(9,4,1,2)`. citeturn17view0 | Leur modèle Conway comporte `379 987` booléens et `761 221` contraintes; CP-SAT ne trouve ni solution ni preuve d’infaisabilité. citeturn17view0 | C’est aujourd’hui le meilleur squelette général immédiatement programmable. |
| **Classes abéliennes / circulantes** | Exhaustion des `C(49,7)=85 900 584` circulantes : au plus 33 classes de différences satisfaites, score `3366/4950=68 %`; même plafond rapporté pour l’autre groupe abélien d’ordre 99. citeturn17view0 | Élimination quantitative d’une famille hautement symétrique seulement. Elle ne borne pas les graphes généraux. | Code d’autocorrélation et certificat d’exhaustion; utile comme banc d’essai. |
| **Automorphisme prescrit** | Encodage par blocs circulants validé sur des SRG connus. Le cas `Z7` à un point fixe a été attaqué exactement. citeturn17view0 | `UNKNOWN` après 48 h sur 14 cœurs pour le cas `Z7` à un point fixe; `UNKNOWN` aussi après 1800 s pour un cas `Z3` sans point fixe. Un timeout n’élimine aucune branche. citeturn17view0 | Formulation d’orbites; bonne base pour remplacer CP-SAT générique par une énumération d’orbit matrices. |
| **Recherche heuristique** | v2 Thakkar–Severini : meilleur candidat partiel `3501/4950=70,73 %`, 14-régulier, obtenu par commutations à quatre sommets. citeturn17view0 | C’est un artefact de score, ni relaxation certifiant la faisabilité, ni indice mathématique d’existence. Les plateaux précédents à 69,43 % étaient seulement des optima locaux du voisinage choisi. citeturn17view0 | Moteur incrémental et mouvement de switch, intéressants pour une recherche constructive **dans** la réduction à 84 sommets. |
| **Comptage `n3` du dépôt** | Intervalle repo-audité `708≤n3≤4158`; donc au moins `209 994` hexagones dans sa convention. fileciteturn7file0L2-L2 | Pas de contradiction et pas de publication externe. La preuve est une chaîne de nombreuses vagues à rejouer si elle devient une prémisse centrale. | Vérificateurs, certificats et journaux des vagues `n3`; compatibles avec la notation de Reimbayev. |
| **Algèbre, codes, réseaux dans le dépôt** | Le dépôt rapporte entre autres une restriction universelle sur le rang sur `F_7` de matrices associées à `A`, puis de nombreux raffinements de réseaux/formes modulaires. fileciteturn7file0L2-L2 | Aucune branche de rang n’est éliminée au point de résoudre l’existence; plusieurs raccourcis tentants ont dû être corrigés ou bornés soigneusement. | À reprendre uniquement depuis les vérificateurs et obligations, pas depuis une phrase de synthèse. |
| **Traces d’ordre quatre / projecteurs** | La vague 205 factorise exactement la matrice de traces d’ordre quatre et construit des contrôles montrant que les données locales testées ne déterminent pas la trace sur les non-arêtes. fileciteturn12file0L2-L2 | C’est une **réfutation d’une implication locale**, pas une relaxation du SRG devenue faisable. Le contrôle hostile viole massivement `λ=1,μ=2`, est déconnecté, etc. fileciteturn11file0L2-L2 | Les certificats locaux sont précieux pour empêcher de reproposer le même lemme faux; toute reprise doit ajouter une compatibilité globale entre plusieurs centres. |

La réduction de Thakkar–Severini mérite deux commentaires supplémentaires. Premièrement, leur recherche partielle n’est pas un quasi-certificat : le meilleur artefact satisfait tous les degrés, `549/693` contraintes de type `λ` et `2853/4158` de type `μ`, mais l’écart restant est énorme en termes exacts. Deuxièmement, le fait que leur programme-search franchisse l’ancien plateau de `69,43 %` démontre surtout que ce plateau n’avait aucune signification structurelle universelle. citeturn17view0

L’aspect IA est documenté de façon suffisamment précise pour ne pas avoir à spéculer. Dans la première version du travail, les auteurs déclarent avoir utilisé **Anthropic Claude via Claude Code** comme agent de recherche et de programmation, avec Google OR-Tools CP-SAT, Microsoft Z3, NumPy et SciPy; aucun numéro précis de modèle Claude n’est donné dans le passage examiné. La v2 ajoute une expérience distincte avec le système d’évolution de programmes **AlphaEvolve** de Google DeepMind, auquel seule la fonction de score était fournie; le programme généré a trouvé le mouvement à quatre sommets donnant 70,73 %. citeturn16view0turn17view0

Keramatipour documente pour sa part des encodages SAT/pseudo-booléens et cite **CaDiCaL** comme solveur pratique. Gray Taylor documente **Nauty via OApackage** pour les classes d’isomorphisme. citeturn18view0 fileciteturn16file0L2-L2

Le dépôt `conway-99-research` adopte explicitement une architecture multi-agent avec orchestrateur, agents de preuve structurellement distincts, agent de construction et vérificateur indépendant, et sépare `CITED`, `DERIVED`, `VERIFIED`, `CANDIDATE`, `REFUTED`, `UNKNOWN`. Il calibre également des pipelines de preuve SAT/PB et exige qu’un résultat négatif complet ait un artefact vérifiable. Les fichiers d’orientation que j’ai examinés **ne donnent pas un identifiant de modèle IA suffisamment explicite pour que je lui en attribue un**; les noms de branches ou de commits ne sont pas une source suffisante pour le faire. fileciteturn8file0L2-L2 fileciteturn7file0L2-L2

## Ce que le dépôt apporte — et ce qu’il ne faut surtout pas en hériter sans contrôle

La meilleure qualité du dépôt n’est probablement pas telle ou telle « vague », mais sa discipline de preuve. Il fige le certificat positif comme une matrice binaire `99×99` satisfaisant l’identité matricielle entière; pour un certificat négatif il exige une preuve humaine complète, une preuve formelle vérifiée, ou un encodage exhaustif public accompagné de son artefact et de son vérificateur. Il rejette explicitement comme non-conclusifs les timeouts, les échecs heuristiques, les résidus flottants et les recherches sous symétrie non démontrée. C’est exactement le bon standard à conserver. fileciteturn7file0L2-L2 fileciteturn8file0L2-L2

Il faut également conserver son **historique des réparations**, car il montre où les raisonnements sont fragiles. Le `STATUS.yaml` consigne par exemple un raccourci initial erroné dans une étape autour de `n3=36`, puis sa réparation; une vague ultérieure avait omis un pont vers le complément, utilisé des garde-fous sémantiques insuffisants dans le premier checker et rencontré un problème de reproductibilité de fins de ligne, tous trois réparés publiquement. Ce sont précisément les sortes de détails qui rendent dangereux le fait de ne lire que les derniers nombres annoncés. fileciteturn7file0L2-L2

Le premier acquis interne à préserver est donc le **ledger des contraintes**, et notamment `708≤n3≤4158`, plutôt que de recommencer la succession d’exclusions `n3=30,33,36,…`. Le dépôt note d’ailleurs lui-même que Lou–Murin fournissait déjà des ingrédients en amont de certaines étapes et a corrigé des revendications de nouveauté au fil des audits. L’épisode Gray Taylor est encore plus explicite : une classification reconstruite indépendamment dans la vague 40 avait en réalité un précédent exact de 2020. fileciteturn7file0L2-L2

Le deuxième acquis est un **résultat négatif de sélection de méthode** : la vague 205 montre qu’il est insuffisant d’espérer déterminer la quantité de quatrième ordre `h_xy` d’une non-arête à partir du seul profil de deux centres, même après ajout de plusieurs contraintes locales fortes. Des exemples exacts de rang ambiant maximal réalisent plusieurs valeurs possibles de `h_xy` à données de paire comparables; puis un contrôle plus global conserve des données de traces et toutes les traces d’arêtes tout en faisant varierier 3 888 entrées ordonnées correspondant à des non-arêtes. Ce contrôle ne satisfait pas les axiomes SRG, donc il ne prouve évidemment aucune existence; il prouve seulement que le **lemme de globalisation local envisagé n’est pas valide sous les hypothèses testées**. fileciteturn12file0L2-L2 fileciteturn11file0L2-L2

Par conséquent, refaire « plus de quatrième moment sur deux centres » serait une répétition presque certaine. Ce qui pourrait changer la situation, et que l’audit 205 identifie lui-même, est une condition **simultanée d’extension de plusieurs boules à deux centres qui se chevauchent** : autrement dit, une loi à trois centres ou une classification du noyau de croisement sur l’espace effectivement réalisable. fileciteturn12file0L2-L2

Le troisième point est que l’état bibliographique du dépôt ne doit plus servir tel quel. Son rapport de juillet dit que la source primaire la plus récente trouvée était le travail SAT soumis le 24 avril 2026. C’était raisonnable au moment de l’audit, mais c’est faux comme point de départ en septembre : le nouveau recensement à sept sommets et la v2 Thakkar–Severini doivent être injectés **avant toute vague 206**. fileciteturn11file0L2-L2 citeturn20view1turn17view1

Enfin, un verdict `VERIFIED` du dépôt signifie « vérifié selon son protocole interne », pas « résultat mathématique publié ». Je traiterais donc comme prémisse de travail les objets accompagnés de vérificateurs exacts, mais je **rejouerais au minimum la tranche de dépendances pertinente** avant qu’un nouvel argument décisif ne s’appuie dessus. Il n’est pas nécessaire de rejouer les 205 vagues : pour une piste `n3`, il faut la chaîne minimale qui certifie la borne utilisée; pour une piste de projecteurs, le package 205; pour une piste de rang, le package correspondant. C’est conforme à la philosophie même du dépôt. fileciteturn8file0L2-L2

## Investigations suivantes qui apporteraient réellement de l’information

**Le meilleur point de départ me paraît être l’intégration auditée du recensement d’ordre sept de Reimbayev.** C’est le changement documentaire le plus net depuis le dernier état du dépôt, il est peu coûteux à tester et il touche directement un invariant (`n3`) sur lequel le dépôt a investi beaucoup de travail.

Ce qui changerait par rapport à l’existant est précis : le dépôt connaissait le recensement d’ordre six et des travaux 2025 sur certains sous-graphes hamiltoniens à sept sommets, mais son gel du 29 juillet précède la classification annoncée des **208 types induits d’ordre sept**. Le nouveau système introduit seulement `z11` en plus de `n3`; après substitution `n=99,k=14`, chaque fréquence devient une expression rationnelle affine en deux inconnues. Toute existence exige simultanément `z_i∈Z_{\ge0}` pour les 208 types. citeturn20view1turn20view2 fileciteturn7file0L2-L2

Le premier test proportionné ne devrait pas être une nouvelle recherche de graphes. Il devrait être un petit programme exact indépendant qui :

1. retranscrit les 208 expressions en rationnels exacts;
2. vérifie un échantillon systématique puis, si possible, l’ensemble des identités de suppression/double comptage qui les engendrent;
3. impose intégralité et non-négativité;
4. projette l’ensemble des solutions `(n3,z11)` sur `n3`;
5. intersecte cette projection avec `708≤n3≤4158`.

Ce calcul est essentiellement une étude d’un polyèdre/lattice de dimension deux et devrait être trivial en ressources une fois les formules fiables. Le résultat est informatif dans tous les cas : soit l’intervalle `n3` se resserre, soit certaines classes deviennent forcées/interdites, soit les 208 équations n’ajoutent rien au domaine déjà connu, soit une incohérence de transcription ou de formule est détectée. Étant donné que les dérivations sont omises dans le préprint et qu’un audit avait déjà détecté une omission imprimée dans le papier d’ordre six, **la validation indépendante fait partie de l’expérience**, elle n’est pas une formalité. citeturn20view1turn20view2turn12view2

La deuxième investigation que je privilégierais est une **reprise de la réduction à 84 sommets, mais sous forme d’énumération canonique structurée plutôt que d’un nouveau lancement CP-SAT générique**. Elle a, contrairement à une branche d’automorphisme, la capacité de résoudre le problème général dans les deux sens.

Ce qui changerait par rapport à Keramatipour, aux runs SAT du dépôt et au modèle CP-SAT de Thakkar–Severini serait le grain de recherche. Les 84 sommets ne sont pas anonymes : ils sont les arêtes de `K_14` privées d’un appariement parfait, avec action naturelle du groupe hyperoctaédral

\[
2^7\rtimes S_7
\]

d’ordre `645 120`. Les relations possibles entre deux labels dépendent de leur intersection et de l’appariement fixé. Gray Taylor fournit en outre les onze possibilités autour d’une arête du graphe original, et le nouveau recensement à sept sommets fournit des compteurs globaux. Au lieu de laisser CP-SAT découvrir cette combinatoire via près de 380 000 booléens, on peut envisager une génération canonique qui ne construit que des extensions non isomorphes compatibles avec ces types locaux. citeturn17view0 fileciteturn16file0L2-L2

Il ne faut cependant pas investir d’emblée des semaines dans un générateur complet. Le bon premier test est un **benchmark de profondeur faible** : fixer un sommet extérieur ou une arête extérieure, quotienter exactement par son stabilisateur dans `2^7⋊S_7`, propager les contraintes de degrés et de voisins communs, puis mesurer le nombre de classes canoniques après quelques niveaux. Faire le même test avec et sans les onze types de Taylor et les contraintes `n3/z11`. Si le nombre de branches ne baisse pas de plusieurs ordres de grandeur par rapport au CP-SAT de référence, la piste aura donné une réponse rapide : la symétrie de labels n’est pas le verrou recherché. Si elle baisse fortement, on dispose d’une voie vers une recherche exhaustive qui peut être couplée à un certificat SAT/LRAT plutôt qu’à un simple verdict de programme. La première étape, avant de coder, reste de chercher dans `attempts/` si une canonical augmentation équivalente existe déjà : je n’en ai pas établi l’absence par lecture exhaustive de tous les codes du dépôt.

Sur le versant constructif, le mouvement à quatre sommets découvert par program-search pourrait être réutilisé **à l’intérieur** de cette représentation sur 84 sommets, où le degré `12` et toute la couche intérieure sont satisfaits par construction. Ce serait substantiellement différent de l’heuristique v2, à laquelle le système d’évolution n’avait pas reçu la réduction forcée. Un succès fournirait un candidat exact vérifiable; un nouvel échec heuristique ne vaudrait toujours aucune preuve. citeturn17view0

La troisième investigation, plus risquée mais mathématiquement distincte, est la **compatibilité à trois centres** suggérée par la fin de la vague 205. Je ne recommanderais cette piste qu’en respectant strictement le résultat négatif déjà obtenu : ne pas chercher une nouvelle fonction de la paire `(x,y)` censée forcer la trace de quatrième ordre.

Ce qui changerait est l’hypothèse. Les contre-modèles de la vague 205 montrent que les contraintes locales de deux centres, le rang local, la distance du code de relations, le nombre moyen de certaines entrées croisées et plusieurs conditions de type prisme ne fixent pas `h_xy`. Ils ne montrent pas que trois boules à deux centres partageant des sommets peuvent être réalisées indépendamment. C’est précisément cette compatibilité d’extension simultanée qui reste non testée. fileciteturn12file0L2-L2

Le premier test devrait donc rester petit : choisir, dans la réduction enracinée, un triplet de centres représentant chaque type d’adjacence possible; prendre les catalogues exacts de deux-centres déjà générés par la vague 205; et calculer par énumération si toutes les valeurs locales de `h_xy` survivantes s’étendent à un même troisième centre. Une réduction substantielle du nombre de signatures justifierait de chercher une identité globale. Si toutes les ambiguïtés de la vague 205 survivent déjà à trois centres, il faudrait arrêter cette famille d’arguments plutôt que passer immédiatement aux moments d’ordre cinq ou six. C’est exactement le genre de test discriminant qui évite une nouvelle série de vagues techniques sans information nouvelle.

Les branches d’automorphismes méritent enfin une remarque, mais je ne les placerais pas devant ces trois investigations. Le timeout de 48 h du cas `Z_7` n’interdit nullement de le reprendre : ce qui changerait serait de remplacer le bloc-circulant CP-SAT générique par une **énumération spécialisée d’orbit matrices**, avec contraintes de spectre/interlacement et génération canonique. Thakkar–Severini eux-mêmes indiquent cette direction. Un tel calcul pourrait fournir une vraie élimination certifiée de la branche `Z_7` à un point fixe. Sa portée demeurerait cependant conditionnelle à cette action et ne traiterait ni les autres nombres de points fixes éventuellement admissibles ni le cas asymétrique; c’est donc un bon projet borné, pas le meilleur axe principal pour résoudre Conway-99. citeturn17view0

## À transmettre au prochain chercheur

**Statut.** Au 21 septembre 2026, aucun graphe ni certificat de non-existence vérifiable n’est connu dans les sources primaires contrôlées; Brouwer marque toujours `?`, Reimbayev v1 du 19 août et Thakkar–Severini v2 du 18 septembre traitent explicitement le problème comme ouvert. citeturn0search0turn20view1turn17view0

**Formulation de départ.** Utiliser soit `A²+A−12I=2J` avec spectre `14^1,3^54,(−4)^44`, soit — de préférence pour programmer — la réduction depuis un sommet : `N(0)=7K2`, 84 sommets extérieurs identifiés aux paires non appariées des 14 voisins, et un graphe extérieur 12-régulier soumis aux règles exactes de voisins communs. Cette réduction ne suppose aucune symétrie. citeturn17view0

**Acquis local à ne pas redécouvrir.** Lou–Murin ont déjà le graphe des 231 triangles et ses équations `α,β,γ`; Gray Taylor a déjà classé les onze voisinages combinés d’une arête; Keramatipour a déjà la vue enracinée et des encodages SAT; le dépôt a explicitement reconnu le prior art Taylor après l’avoir indépendamment retrouvé. citeturn23view0turn23view1 fileciteturn16file0L2-L2 fileciteturn7file0L2-L2

**Acquis interne important mais à rejouer avant publication.** Le dépôt donne `708≤n3≤4158`, où `p6=209286+n3`, et possède les certificats/vérificateurs correspondants. Il ne faut pas reprendre la chaîne d’exclusion des petites valeurs de `n3` depuis zéro, mais il faut rejouer la portion pertinente avant de l’utiliser dans une preuve extérieure. fileciteturn7file0L2-L2

**Répétitions à éviter, avec leur portée exacte.** Un timeout SAT/CP-SAT ne dit rien sur existence; le plafond circulant `68 %` ne concerne que cette classe; le score heuristique `70,73 %` n’est ni une relaxation faisable ni une indication d’existence; la vague 205 a réfuté la détermination de la trace de quatrième ordre par les seules données locales de deux centres, pas l’ensemble des méthodes de traces; une recherche imposant un automorphisme ne traite qu’un sous-problème. citeturn17view0 fileciteturn12file0L2-L2

**Hypothèses fragiles.** Ne pas importer aveuglément toutes les formules Reimbayev : le papier d’ordre sept omet les dérivations et documente un usage intensif de Wolfram Alpha, tandis que l’audit du dépôt avait déjà relevé une omission imprimée dans le papier d’ordre six. Ne pas utiliser non plus comme fait l’énoncé Keramatipour sur onze Paley(9) indépendants sans reconstruire la preuve, puisqu’elle est omise. Le théorème Makhnev 1988 utilisé pour certaines affirmations `n3=0` mérite également un retour au texte original. citeturn20view1turn20view2turn12view2turn19view1turn13view1

**Sources prioritaires à ouvrir en premier.** `STATUS.yaml`, `AGENTS.md` et l’audit d’intégration Wave 205 du dépôt; Reimbayev `2608.19410v1`; Thakkar–Severini `2608.11211v2`; puis Lou–Murin et Gray Taylor lorsqu’une branche touche aux triangles ou à une arête fixée. L’audit bibliographique interne du 29 juillet ne suffit plus à lui seul. fileciteturn7file0L2-L2 fileciteturn8file0L2-L2 fileciteturn12file0L2-L2 citeturn20view1turn17view1turn23view1

**Point de départ recommandé.** Avant une nouvelle recherche lourde, auditer et spécialiser les 208 fréquences d’ordre sept à `(99,14)` puis intersecter exactement leurs contraintes d’intégralité/non-négativité avec `708≤n3≤4158`. C’est une information apparue après le dernier état du dépôt, elle est de faible coût computationnel, elle peut renforcer immédiatement l’invariant central `n3`, et son échec à le faire serait lui-même une information nette permettant de passer ensuite, sans répétition, à la réduction globale sur 84 sommets ou à une vraie compatibilité à trois centres.