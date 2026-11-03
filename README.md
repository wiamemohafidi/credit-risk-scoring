# Credit Risk Scoring — guide de départ

Projet pour Wiame : Python, SQL, statistiques et restitution Power BI.
Objectif : estimer la probabilité de défaut au mois suivant à partir de l'historique client et expliquer les résultats. Prototype académique, sans usage de décision de crédit ni conformité IRB revendiquée.

## Commencer en 10 minutes

1. Décompresser le dossier.
2. Ouvrir `01_credit_risk.ipynb` dans Jupyter ou VS Code. Sur Google Colab, importer le notebook puis le dossier décompressé dans `/content/credit_risk_project`.
3. Exécuter les cellules dans l'ordre. Les données sont déjà incluses : aucun téléchargement de données nécessaire.
4. Lire les résultats dans `outputs/`. Ils proviennent d'une première exécution, à reproduire et interpréter toi-même.

Alternative terminal (depuis le dossier du projet) :

```bash
python -m pip install -r requirements.txt
python pipeline.py
```

## Ton parcours sur 7 séances

| Séance | Travail personnel | Résultat attendu |
|---|---|---|
| 1 — Comprendre | Examiner 10 clients, compter les défauts, lire le dictionnaire | Expliquer la cible, l'unité et l'horizon |
| 2 — Qualité | Lire `data_quality.csv`, compter les codes inhabituels, chercher les doublons hors ID | Justifier les regroupements et la conservation des valeurs négatives |
| 3 — Explorer | Tracer taux de défaut par retard de paiement et distribution des montants | 3 observations chiffrées, sans causalité revendiquée |
| 4 — Modéliser | Comparer dummy, régression logistique et forêt calibrée | Expliquer les écarts sur validation |
| 5 — Évaluer | Lire ROC, précision/rappel, calibration et faux négatifs | Distinguer classement, seuil et qualité des probabilités |
| 6 — Restituer | Construire le rapport Power BI décrit dans `POWER_BI.md` | Rapport interactif à 3 pages |
| 7 — Présenter | Rédiger 1 page et faire une démonstration de 3 minutes | Présenter méthode, résultats et limites sans lire le code |

## Méthode intégrée

- Split stratifié déterministe : train 18 000 / validation 6 000 / test 6 000. L'ID ne sert pas à prédire.
- Imputation, standardisation et encodage appris dans les pipelines, jamais sur le test.
- SEX exclu des prédicteurs, conservé pour un audit descriptif. AGE reste utilisé. Cela ne démontre pas une absence de biais : des variables peuvent agir comme proxys.
- Historique de paiement traité en catégories : ne pas interpréter 0 et -2 comme des retards négatifs.
- EDUCATION hors {1,2,3,4} regroupé dans « autres » (4), MARRIAGE hors {1,2,3} dans « autres » (3).
- Pas de suppression automatique des factures négatives : inspecter les crédits/avoirs possibles.
- Régression logistique de référence et forêt aléatoire avec calibration sigmoïde sur 3 plis internes au train. Le pipeline entier est réappris dans chaque pli.
- Sélection du modèle par log-loss de validation. Choix du seuil par F1 de validation : choix pédagogique, sans coût bancaire connu.
- Test utilisé à la fin sur le seul modèle retenu. Ne pas modifier le modèle après lecture du test puis continuer à le présenter comme indépendant.
- Importance par permutation sur validation : association prédictive globale, ni explication individuelle ni preuve de causalité.

## Dictionnaire compact

| Colonne | Sens / décision |
|---|---|
| ID | Identifiant ; exclu du modèle |
| LIMIT_BAL | Limite de crédit en dollars taïwanais (NT$) |
| SEX | Code 1/2 selon UCI ; audit descriptif uniquement |
| EDUCATION | 1 supérieur avancé, 2 université, 3 lycée, 4 autres ; autres codes regroupés |
| MARRIAGE | 1 marié, 2 célibataire, 3 autres ; autres codes regroupés |
| AGE | Âge en années |
| PAY_0, PAY_2…PAY_6 | Statuts de paiement de septembre à avril 2005 ; il n'y a pas de PAY_1 |
| BILL_AMT1…6 | Factures de septembre à avril 2005 en NT$ |
| PAY_AMT1…6 | Paiements historiques en NT$ |
| default payment next month | Cible binaire : défaut de paiement au mois suivant, 1 oui, 0 non |

UCI documente -1 comme paiement à temps et 1…9 comme retard de 1…9 mois ou plus. Les codes 0 et -2 observés ne sont pas explicités dans la fiche : ne pas inventer leur signification.

## Limites à expliquer en entretien

Données historiques de Taïwan, 2005 : aucune validation sur une clientèle bancaire actuelle ou française. Un échantillon par client : ce split aléatoire ne prouve pas une robustesse temporelle. Les doublons de caractéristiques peuvent correspondre à des profils identiques : à investiguer, pas à effacer sans justification. Les segments de risque sont des bornes illustratives fixées à 10 % et 30 %, sans validation métier. Le Brier combine plusieurs dimensions : une courbe de calibration complète son interprétation. Aucune EAD/LGD ni estimation de perte attendue n'est calculée. Ne pas appeler LIMIT_BAL « exposition au défaut ». Aucun intervalle d'incertitude ni audit d'équité complet dans cette version.

## Extensions utiles, après maîtrise de cette base

1. Comparer les modèles sur plusieurs splits uniquement dans les données de développement ; préserver un test final indépendant.
2. Introduire un scénario explicite de coûts des erreurs puis choisir le seuil sur validation.
3. Auditer les performances par tranche d'âge et sexe avec effectifs et incertitude, sans conclusion juridique.
4. Écrire une model card en anglais et publier le projet sur GitHub après avoir exécuté et compris le code.

## Présentation sur le CV

Après réalisation et compréhension : « Developed an academic credit-default scoring prototype using Python and SQL; compared logistic regression with a calibrated random forest, evaluated discrimination and probability quality on a held-out test set, and built a Power BI dashboard. »
Ne mentionner Power BI qu'une fois le rapport effectivement construit. Ajouter uniquement les chiffres issus de ta propre exécution, avec la métrique et le périmètre.

## Sources et licence des données

Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository. DOI : https://doi.org/10.24432/C55S3H. Données sous CC BY 4.0 : https://creativecommons.org/licenses/by/4.0/.
Fiche : https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
Le CSV inclus est une conversion du fichier XLS officiel (en-tête en seconde ligne), sans modification des valeurs. Les regroupements se font dans le pipeline. La licence des données ne détermine pas celle de ton futur code.
Documentation calibration : https://scikit-learn.org/stable/modules/calibration.html
