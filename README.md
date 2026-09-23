# conway99-lab-archive

Archive figée de la session de recherche d'origine sur le graphe de Conway à 99 sommets
(branche involution), constituée le 2026-09-22 avant la session « lab ». Dépôt privé, lecture seule :
rien ici ne doit être modifié. Le travail courant est dans `conway99-involution`.

| Dossier | Contenu |
|---|---|
| `repo_untracked_at_338c00e/` | fichiers non suivis du repo `conway99-involution` au commit 338c00e (dont `code/z2/phase2/`) |
| `temp_session_eeaf2d22/` | dossier temporaire de la session eeaf2d22 (scratchpad, tâches, images) |
| `transcripts/` | transcripts de sessions (`.jsonl`), sous-agents, workflows |
| `uploads_eeaf2d22/` | deux fichiers déposés pendant la session |
| `SHA256SUMS.txt` | sha256 de chacun des 11 593 fichiers de l'archive d'origine |

## Écarts avec l'archive d'origine (et seulement ceux-là)

1. **Trois CNF exclus** (> 100 MB, limite GitHub). Ils sont régénérables par les scripts de `phase2/` et une copie
   identique (mêmes sha256) est dans `conway99-involution/code/z2/phase2/encodings/cnf/` (gitignorée) :
   - `sib_tot.cnf`  `eb8cb74f8651a241e53d24c372acef10976b809ced52b474d140ca991a4f199b`
   - `sib_cnet.cnf` `7e2a986abe6e5324f4452fc1430d3e62db20fc4732983164e247f19b6d63ec03`
   - `sib_mtot.cnf` `7e741b8fe2070e87a33bbf514a4559fde0e2b6ec68ce61f70647177b9c2444a2`
2. **Clone git imbriqué** : `temp_session_eeaf2d22/scratchpad/conway-99-research/` est un clone *shallow*
   (HEAD 85e705cc6c2a14d123120c93a847e30aaab1789e) de https://github.com/YesterdaysLemon/conway-99-research.
   Git ne peut pas versionner un `.git` imbriqué : il est conservé octet pour octet dans
   `temp_session_eeaf2d22/scratchpad/conway-99-research.dotgit.tar` (40 fichiers ; aller-retour tar vérifié par `diff -r`).
   Pour le restaurer : `tar -C temp_session_eeaf2d22/scratchpad/conway-99-research -xf temp_session_eeaf2d22/scratchpad/conway-99-research.dotgit.tar`.
3. Ajouts : ce `README.md` et `.gitattributes`.

## Vérification

Les fichiers sont commités octet pour octet (pas de conversion de fins de ligne). Après un clone :

```
git config core.longpaths true      # Windows
sha256sum -c SHA256SUMS.txt 2>/dev/null | grep -v ': OK$'
```

Sortie attendue : exactement 43 lignes (les 3 CNF ci-dessus + les 40 fichiers du `.git` imbriqué, avant restauration du tar).
Après restauration du tar : 3 lignes.
